"""Hybrid recommendation engine combining content & collaborative models.

Provides HybridRecommender class implementing weighted score fusion, adaptive
model selection, confidence scoring, and fallback chain handling.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import pandas as pd

from recolab.baseline import PopularityModel
from recolab.collaborative import ItemBasedCF, UserBasedCF
from recolab.content import ContentModel
from recolab.interfaces import ColdStartHandler, FeatureError
from recolab.persistence import (
    ModelBundle,
    PersistError,
    load_model_bundle,
    save_model_bundle,
)

logger = logging.getLogger(__name__)


class HybridRecommender:
    """Hybrid recommender combining content-based and collaborative filtering models.

    Integrates ContentModel, UserBasedCF, and ItemBasedCF through weighted score fusion,
    adaptive model selection, confidence scoring, and graceful fallback handling.

    Attributes:
        alpha: Weight for content (alpha) vs collaborative (1 - alpha) models.
        cold_start_threshold: Rating count threshold for cold-start (default: 5).
        active_threshold: Rating count threshold for active users (default: 20).
        content_model: ContentModel instance for content-based recommendations.
        user_based_cf: UserBasedCF instance for user-based CF.
        item_based_cf: ItemBasedCF instance for item-based CF.
        normalization_params: Dictionary storing normalization statistics.
        model_selection_log: Log of model selection decisions.
        is_fitted: Boolean flag indicating if fit() has been completed.
        selected_model: Model selected in the last recommend() invocation.
    """

    def __init__(
        self,
        alpha: float = 0.5,
        cold_start_threshold: int = 5,
        active_threshold: int = 20,
        content_model: Optional[ContentModel] = None,
        user_based_cf: Optional[UserBasedCF] = None,
        item_based_cf: Optional[ItemBasedCF] = None,
    ) -> None:
        """Initialize HybridRecommender with configurable parameters.

        Args:
            alpha: Weight assigned to content-based model [0.0, 1.0].
            cold_start_threshold: Max ratings count to treat user as cold-start.
            active_threshold: Min ratings count to treat user as active user.
            content_model: ContentModel instance.
            user_based_cf: UserBasedCF instance.
            item_based_cf: ItemBasedCF instance.

        Raises:
            ValueError: If alpha or thresholds are invalid.
        """
        if not (0.0 <= alpha <= 1.0):
            raise ValueError(f"alpha must be between 0.0 and 1.0, got {alpha}.")
        if cold_start_threshold <= 0:
            raise ValueError(
                "cold_start_threshold must be a positive integer, "
                f"got {cold_start_threshold}."
            )
        if active_threshold < cold_start_threshold:
            raise ValueError(
                f"active_threshold ({active_threshold}) must be >= "
                f"cold_start_threshold ({cold_start_threshold})."
            )

        self.alpha: float = float(alpha)
        self.cold_start_threshold: int = int(cold_start_threshold)
        self.active_threshold: int = int(active_threshold)

        self.content_model: Optional[ContentModel] = content_model
        self.user_based_cf: Optional[UserBasedCF] = user_based_cf
        self.item_based_cf: Optional[ItemBasedCF] = item_based_cf

        self.normalization_params: Dict[str, Any] = {}
        self.model_selection_log: List[Dict[str, Any]] = []
        self.is_fitted: bool = False
        self.selected_model: Optional[str] = None

        self.user_rating_counts: Dict[int, int] = {}
        self.item_rating_counts: Dict[int, int] = {}
        self.ratings_df: Optional[pd.DataFrame] = None
        self.movies_df: Optional[pd.DataFrame] = None

    def fit(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame) -> None:
        """Train all underlying recommendation models and set up framework state.

        Args:
            ratings_df: DataFrame with userId, movieId, rating columns.
            movies_df: DataFrame with movieId, title, genres columns.

        Raises:
            ValueError: If input DataFrames are missing required columns or empty.
        """
        try:
            if ratings_df.empty or movies_df.empty:
                raise ValueError(
                    "Input DataFrames ratings_df and movies_df cannot be empty."
                )

            required_ratings = {"userId", "movieId", "rating"}
            if not required_ratings.issubset(ratings_df.columns):
                missing = required_ratings - set(ratings_df.columns)
                raise ValueError(f"ratings_df missing required columns: {missing}")

            required_movies = {"movieId", "genres"}
            if not required_movies.issubset(movies_df.columns):
                missing = required_movies - set(movies_df.columns)
                raise ValueError(f"movies_df missing required columns: {missing}")

            self.ratings_df = ratings_df.copy()
            self.movies_df = movies_df.copy()

            # Precalculate rating counts
            user_counts = ratings_df["userId"].value_counts().to_dict()
            self.user_rating_counts = {
                int(str(k)): int(v) for k, v in user_counts.items()
            }

            item_counts = ratings_df["movieId"].value_counts().to_dict()
            self.item_rating_counts = {
                int(str(k)): int(v) for k, v in item_counts.items()
            }

            # Fit content model if missing or not fitted
            if self.content_model is None:
                self.content_model = ContentModel()
            if not getattr(self.content_model, "is_fitted", False):
                self.content_model.fit(ratings_df, movies_df)

            # Fit user-based CF if missing or not fitted
            if self.user_based_cf is None:
                self.user_based_cf = UserBasedCF()
            if not getattr(self.user_based_cf, "is_fitted", False):
                self.user_based_cf.fit(ratings_df)

            # Fit item-based CF if missing or not fitted
            if self.item_based_cf is None:
                self.item_based_cf = ItemBasedCF()
            if not getattr(self.item_based_cf, "is_fitted", False):
                self.item_based_cf.fit(ratings_df)

            self.is_fitted = True
            logger.info("HybridRecommender fit complete.")
        except Exception as exc:
            if not isinstance(exc, ValueError):
                logger.error(f"Failed to fit HybridRecommender: {exc}")
            raise

    def _get_user_rating_count(self, user_id: int) -> int:
        """Return total rating count for given user_id."""
        return self.user_rating_counts.get(user_id, 0)

    def _select_model(self, user_id: int) -> Tuple[Any, str, str]:
        """Select optimal recommendation approach based on user activity level.

        Args:
            user_id: User identifier.

        Returns:
            Tuple of (model_instance, model_name, selection_reason).
        """
        count = self._get_user_rating_count(user_id)
        if count <= self.cold_start_threshold:
            reason = (
                f"Cold-start user {user_id} with {count} ratings "
                f"(<= {self.cold_start_threshold})"
            )
            return (self.content_model, "content", reason)
        elif count >= self.active_threshold:
            model = self.user_based_cf or self.item_based_cf
            reason = (
                f"Active user {user_id} with {count} ratings "
                f"(>= {self.active_threshold})"
            )
            return (model, "collaborative", reason)
        else:
            reason = (
                f"Intermediate user {user_id} with {count} ratings "
                f"({self.cold_start_threshold} < n < {self.active_threshold})"
            )
            return (self, "hybrid", reason)

    def _normalize_scores(
        self, scores: List[Tuple[int, float]]
    ) -> List[Tuple[int, float]]:
        """Min-max normalize a list of (item_id, score) tuples to [0.0, 1.0].

        Args:
            scores: List of (item_id, score) pairs.

        Returns:
            Normalized list of (item_id, normalized_score) pairs.
        """
        if not scores:
            return []

        raw_values = [score for _, score in scores]
        min_val = min(raw_values)
        max_val = max(raw_values)

        if max_val == min_val:
            return [(item_id, 1.0 if max_val > 0 else 0.0) for item_id, _ in scores]

        val_range = max_val - min_val
        return [(item_id, (score - min_val) / val_range) for item_id, score in scores]

    def _combine_weighted_scores(
        self,
        content_scores: List[Tuple[int, float]],
        cf_scores: List[Tuple[int, float]],
        k: int,
    ) -> List[Tuple[int, float]]:
        """Combine normalized content and collaborative scores using weight alpha.

        Args:
            content_scores: List of (item_id, score) from content model.
            cf_scores: List of (item_id, score) from collaborative model.
            k: Number of recommendations to return.

        Returns:
            Top-k combined (item_id, score) pairs sorted by combined score.
        """
        norm_content = self._normalize_scores(content_scores)
        norm_cf = self._normalize_scores(cf_scores)

        content_dict = dict(norm_content)
        cf_dict = dict(norm_cf)

        all_item_ids = set(content_dict.keys()) | set(cf_dict.keys())
        combined_scores: List[Tuple[int, float]] = []

        for item_id in all_item_ids:
            has_content = item_id in content_dict
            has_cf = item_id in cf_dict

            if has_content and has_cf:
                c_score = content_dict[item_id]
                cf_score = cf_dict[item_id]
                combined = self.alpha * c_score + (1.0 - self.alpha) * cf_score
            elif has_content:
                combined = self.alpha * content_dict[item_id]
            else:
                combined = (1.0 - self.alpha) * cf_dict[item_id]

            combined_scores.append((item_id, combined))

        # Sort descending by score, ascending by item_id for deterministic tie breaking
        combined_scores.sort(key=lambda x: (-x[1], x[0]))
        return combined_scores[:k]

    def _compute_activity_confidence(self, user_id: int) -> float:
        """Compute user activity confidence in range [0.0, 1.0]."""
        count = self._get_user_rating_count(user_id)
        if count <= self.cold_start_threshold:
            return 0.0
        if count >= self.active_threshold:
            return 1.0
        return (count - self.cold_start_threshold) / (
            self.active_threshold - self.cold_start_threshold
        )

    def _compute_popularity_confidence(self, movie_id: int) -> float:
        """Compute item popularity confidence in range [0.0, 1.0]."""
        count = self.item_rating_counts.get(movie_id, 0)
        return min(1.0, count / 50.0)

    def _compute_agreement_confidence(
        self,
        content_items: List[int],
        cf_items: List[int],
    ) -> float:
        """Compute agreement confidence score between model candidate items."""
        if not content_items or not cf_items:
            return 0.0
        set_c = set(content_items)
        set_cf = set(cf_items)
        intersection = set_c & set_cf
        union = set_c | set_cf
        return len(intersection) / len(union) if union else 0.0

    def _compute_composite_confidence(
        self,
        user_id: int,
        movie_id: int,
        content_items: Optional[List[int]] = None,
        cf_items: Optional[List[int]] = None,
    ) -> float:
        """Compute composite confidence score combining activity, popularity, and
        agreement.
        """
        act_conf = self._compute_activity_confidence(user_id)
        pop_conf = self._compute_popularity_confidence(movie_id)
        agr_conf = self._compute_agreement_confidence(
            content_items or [], cf_items or []
        )

        score = 0.4 * act_conf + 0.3 * pop_conf + 0.3 * agr_conf
        return max(0.0, min(1.0, float(score)))

    def get_confidence(self, user_id: int, movie_id: int) -> float:
        """Return composite confidence score for given user and movie recommendation."""
        return self._compute_composite_confidence(user_id, movie_id)

    def get_model_selection_info(self, user_id: int) -> Dict[str, Any]:
        """Return diagnostic dictionary detailing model selection logic for user."""
        count = self._get_user_rating_count(user_id)
        _, model_name, reason = self._select_model(user_id)
        return {
            "user_id": user_id,
            "rating_count": count,
            "selected_model": model_name,
            "reason": reason,
            "timestamp": time.time(),
        }

    def recommend(
        self,
        user_id: int,
        k: int,
        exclude_items: Optional[Set[int]] = None,
    ) -> List[int]:
        """Generate top-k recommendations using adaptive selection and fallbacks.

        Args:
            user_id: Target user ID.
            k: Number of recommendations to generate.
            exclude_items: Set of item IDs to exclude.

        Returns:
            List of recommended item IDs (length <= k).

        Raises:
            RuntimeError: If model is unfitted or fallback chain fails.
            ValueError: If k <= 0.
        """
        if not self.is_fitted:
            raise RuntimeError("HybridRecommender is not fitted. Call fit() first.")
        if k <= 0:
            raise ValueError(f"k must be a positive integer, got {k}.")

        target_model_instance, model_name, reason = self._select_model(user_id)
        self.selected_model = model_name

        self.model_selection_log.append(
            {
                "user_id": user_id,
                "k": k,
                "model": model_name,
                "reason": reason,
                "timestamp": time.time(),
            }
        )

        exclude_set = exclude_items or set()
        if self.ratings_df is not None:
            user_rated = set(
                self.ratings_df[self.ratings_df["userId"] == user_id][
                    "movieId"
                ].unique()
            )
            exclude_set = exclude_set | user_rated

        # Fallback chain strategy: Try selected -> Content -> CF -> Popularity
        fallback_models = []
        if model_name == "content":
            fallback_models = ["content", "collaborative", "popularity"]
        elif model_name == "collaborative":
            fallback_models = ["collaborative", "content", "popularity"]
        else:  # hybrid
            fallback_models = ["hybrid", "content", "collaborative", "popularity"]

        for mode in fallback_models:
            try:
                if mode == "content" and self.content_model:
                    res = self.content_model.recommend(user_id, k, exclude_set)
                    if res:
                        self.selected_model = "content"
                        return res
                elif mode == "collaborative" and (
                    self.user_based_cf or self.item_based_cf
                ):
                    model = self.user_based_cf or self.item_based_cf
                    if model:
                        res = model.recommend(user_id, k, exclude_set)
                        if res:
                            self.selected_model = "collaborative"
                            return res
                elif mode == "hybrid":
                    c_recs: List[Tuple[int, float]] = []
                    cf_recs: List[Tuple[int, float]] = []

                    if self.content_model:
                        try:
                            c_ids = self.content_model.recommend(
                                user_id, k * 2, exclude_set
                            )
                            c_recs = [
                                (mid, float(k * 2 - i)) for i, mid in enumerate(c_ids)
                            ]
                        except Exception:
                            c_recs = []

                    cf_model = self.user_based_cf or self.item_based_cf
                    if cf_model:
                        try:
                            cf_ids = cf_model.recommend(user_id, k * 2, exclude_set)
                            cf_recs = [
                                (mid, float(k * 2 - i)) for i, mid in enumerate(cf_ids)
                            ]
                        except Exception:
                            cf_recs = []

                    if c_recs or cf_recs:
                        combined = self._combine_weighted_scores(c_recs, cf_recs, k)
                        result_ids = [mid for mid, _ in combined]
                        if result_ids:
                            self.selected_model = "hybrid"
                            return result_ids
                elif mode == "popularity":
                    pop_model = PopularityModel()
                    if self.ratings_df is not None:
                        pop_model.fit(self.ratings_df)
                        res = pop_model.recommend(user_id, k, exclude_set)
                        if res:
                            self.selected_model = "popularity"
                            return res
            except Exception as exc:
                logger.warning(f"Model mode {mode} failed for user {user_id}: {exc}")
                continue

        # If all fallbacks yield empty, return empty list with diagnostic info
        logger.warning(f"All fallback modes failed for user {user_id}")
        return []

    def recommend_cold_start(
        self,
        genres: List[str],
        liked_movie_ids: List[int],
        k: int,
    ) -> List[int]:
        """Generate recommendations for new users with no history.

        Args:
            genres: Preferred genres list.
            liked_movie_ids: Movie IDs user liked during onboarding.
            k: Number of recommendations to generate.

        Returns:
            List of recommended item IDs.

        Raises:
            RuntimeError: If model is unfitted.
            ValueError: If k <= 0.
            FeatureError: If missing query features.
        """
        if not self.is_fitted:
            raise RuntimeError("HybridRecommender is not fitted. Call fit() first.")
        if k <= 0:
            raise ValueError(f"k must be a positive integer, got {k}.")
        if self.content_model is None:
            raise FeatureError("ContentModel is required for cold start handling.")

        self.selected_model = "content"
        return self.content_model.recommend_cold_start(genres, liked_movie_ids, k)

    def explain(self, user_id: int, movie_id: int) -> str:
        """Generate explanation by delegating to selected underlying model.

        Args:
            user_id: User identifier.
            movie_id: Recommended movie identifier.

        Returns:
            Explanation string.
        """
        if not self.selected_model:
            _, self.selected_model, _ = self._select_model(user_id)

        model_name = self.selected_model
        try:
            if (
                model_name == "content"
                and self.content_model
                and hasattr(self.content_model, "explain")
            ):
                return self.content_model.explain(user_id, movie_id)
            elif (
                model_name == "collaborative"
                and self.user_based_cf
                and hasattr(self.user_based_cf, "explain")
            ):
                return self.user_based_cf.explain(user_id, movie_id)
            elif (
                model_name == "collaborative"
                and self.item_based_cf
                and hasattr(self.item_based_cf, "explain")
            ):
                return self.item_based_cf.explain(user_id, movie_id)
        except Exception as exc:
            logger.warning(f"Delegated explanation failed: {exc}")

        count = self._get_user_rating_count(user_id)
        return (
            f"Recommended using HybridRecommender framework "
            f"({model_name} strategy based on {count} user ratings)."
        )

    def to_bundle(self) -> ModelBundle:
        """Package HybridRecommender state into ModelBundle for persistence.

        Returns:
            ModelBundle containing self.
        """
        metadata = {
            "alpha": self.alpha,
            "cold_start_threshold": self.cold_start_threshold,
            "active_threshold": self.active_threshold,
            "is_fitted": self.is_fitted,
            "normalization_params": self.normalization_params,
            "model_selection_log": self.model_selection_log,
            "selected_model": self.selected_model,
            "user_rating_counts": self.user_rating_counts,
            "item_rating_counts": self.item_rating_counts,
        }
        return ModelBundle(model=self, metrics={}, metadata=metadata)

    @classmethod
    def from_bundle(cls, bundle: ModelBundle) -> HybridRecommender:
        """Reconstruct HybridRecommender from ModelBundle.

        Args:
            bundle: ModelBundle artifact.

        Returns:
            Restored HybridRecommender instance.

        Raises:
            PersistError: If bundle is invalid or does not contain HybridRecommender.
        """
        if not isinstance(bundle, ModelBundle):
            raise PersistError(f"Expected ModelBundle, got {type(bundle).__name__}")
        if isinstance(bundle.model, cls):
            return bundle.model
        cls_name = type(bundle.model).__name__
        raise PersistError(
            f"Model inside bundle is not HybridRecommender (got {cls_name})"
        )

    def save(
        self, path: Union[str, Path], root: Optional[Union[str, Path]] = None
    ) -> Path:
        """Save model artifact to disk using persistence module.

        Args:
            path: Target file path.
            root: Optional root directory.

        Returns:
            Path to saved artifact.
        """
        return save_model_bundle(self.to_bundle(), path, root=root)

    @classmethod
    def load(
        cls, path: Union[str, Path], root: Optional[Union[str, Path]] = None
    ) -> HybridRecommender:
        """Load model artifact from disk using persistence module.

        Args:
            path: Source file path.
            root: Optional root directory.

        Returns:
            Restored HybridRecommender instance.
        """
        bundle = load_model_bundle(path, root=root)
        return cls.from_bundle(bundle)


class UserProfile:
    """User profile container for enhanced cold-start recommendations."""

    def __init__(
        self,
        user_id: Optional[int] = None,
        genre_weights: Optional[Dict[str, float]] = None,
        liked_movie_ids: Optional[List[int]] = None,
        created_at: Optional[Any] = None,
    ) -> None:
        """Initialize user profile with ID, genre weights, and liked movies."""
        self.user_id = user_id
        self.liked_movie_ids = list(liked_movie_ids) if liked_movie_ids else []
        self.created_at = created_at or datetime.now(timezone.utc).isoformat()
        self.genre_weights = self._normalize_weights(genre_weights or {})
        self._cache: Dict[str, Any] = {}

    def _normalize_weights(self, weights: Dict[str, float]) -> Dict[str, float]:
        """Normalize genre weights so non-zero values sum to 1.0."""
        cleaned = {g: max(0.0, float(w)) for g, w in weights.items()}
        total = sum(cleaned.values())
        if total > 0:
            return {g: w / total for g, w in cleaned.items()}
        return cleaned

    def update_genre_weights(self, new_genres: List[str], weight: float = 1.0) -> None:
        """Update genre weights with new preferences and re-normalize."""
        weights = dict(self.genre_weights)
        for genre in new_genres:
            weights[genre] = weights.get(genre, 0.0) + float(weight)
        self.genre_weights = self._normalize_weights(weights)
        self.invalidate_cache()

    def get_preferred_genres(self, top_n: int = 3) -> List[str]:
        """Return top-n preferred genres sorted by weight descending."""
        sorted_genres = sorted(
            self.genre_weights.items(), key=lambda x: x[1], reverse=True
        )
        return [g for g, w in sorted_genres[:top_n] if w > 0.0]

    def invalidate_cache(self) -> None:
        """Invalidate profile cache on updates."""
        self._cache.clear()

    def to_bundle(self) -> Dict[str, Any]:
        """Serialize UserProfile for persistence."""
        return {
            "user_id": self.user_id,
            "genre_weights": self.genre_weights,
            "liked_movie_ids": self.liked_movie_ids,
            "created_at": str(self.created_at),
        }

    @classmethod
    def from_bundle(cls, bundle: Dict[str, Any]) -> UserProfile:
        """Reconstruct UserProfile from bundle dictionary."""
        return cls(
            user_id=bundle.get("user_id"),
            genre_weights=bundle.get("genre_weights"),
            liked_movie_ids=bundle.get("liked_movie_ids"),
            created_at=bundle.get("created_at"),
        )


class EnhancedColdStartHandler(ColdStartHandler):
    """Enhanced cold-start handler with profile building capabilities."""

    def __init__(
        self,
        content_model: Optional[ContentModel] = None,
        default_genres: Optional[List[str]] = None,
        new_item_threshold: int = 5,
        popularity_boost_weight: float = 0.3,
    ) -> None:
        """Initialize enhanced cold-start handler."""
        self.content_model = content_model or ContentModel()
        self.default_genres = (
            list(default_genres) if default_genres else ["Action", "Drama", "Comedy"]
        )
        self.new_item_threshold = int(new_item_threshold)
        self.popularity_boost_weight = float(popularity_boost_weight)
        self.profile_cache: Dict[int, UserProfile] = {}

    def calculate_genre_weights(
        self,
        genres: List[str],
        liked_movie_ids: List[int],
        movies_df: Optional[pd.DataFrame] = None,
    ) -> Dict[str, float]:
        """Calculate preference weights from explicit and implicit genres."""
        weights: Dict[str, float] = {}
        for g in genres:
            weights[g] = weights.get(g, 0.0) + 2.0

        if movies_df is not None and liked_movie_ids:
            liked_sub = movies_df[movies_df["movieId"].isin(liked_movie_ids)]
            if not liked_sub.empty and "genres" in liked_sub.columns:
                for raw_g in liked_sub["genres"].dropna():
                    for g in str(raw_g).split("|"):
                        g_clean = g.strip()
                        if g_clean:
                            weights[g_clean] = weights.get(g_clean, 0.0) + 1.0

        total = sum(weights.values())
        if total > 0:
            return {g: w / total for g, w in weights.items()}
        return {g: 1.0 / len(self.default_genres) for g in self.default_genres}

    def build_user_profile(
        self,
        genres: List[str],
        liked_movie_ids: List[int],
        movies_df: Optional[pd.DataFrame] = None,
    ) -> UserProfile:
        """Build user profile from onboarding preferences."""
        weights = self.calculate_genre_weights(genres, liked_movie_ids, movies_df)
        profile = UserProfile(
            user_id=None, genre_weights=weights, liked_movie_ids=liked_movie_ids
        )
        return profile

    def recommend_cold_start(
        self,
        genres: List[str],
        liked_movie_ids: List[int],
        k: int,
    ) -> List[int]:
        """Generate cold-start recommendations using content model."""
        if k <= 0:
            raise ValueError(f"k must be a positive integer, got {k}.")

        effective_genres = genres or self.default_genres
        if self.content_model and getattr(self.content_model, "is_fitted", False):
            return self.content_model.recommend_cold_start(
                effective_genres, liked_movie_ids, k
            )
        return []

    def explain(
        self,
        user_id: int,
        movie_id: int,
        genres: Optional[List[str]] = None,
        liked_movie_ids: Optional[List[int]] = None,
    ) -> str:
        """Generate human-readable explanation for cold-start item."""
        if self.content_model and hasattr(self.content_model, "explain"):
            try:
                return str(self.content_model.explain(user_id, movie_id))
            except Exception as exc:  # noqa: BLE001
                import logging as _logging

                _logging.getLogger(__name__).debug(
                    "content_model.explain failed, using fallback: %s", exc
                )
        g_str = ", ".join(genres) if genres else "popular genres"
        return f"Recommended based on your interest in {g_str}."


class NewItemDetector:
    """Detector and booster for new catalog items with limited ratings."""

    def __init__(
        self, rating_count_threshold: int = 5, boost_weight: float = 0.3, time_decay_days: int = 30
    ) -> None:
        """Initialize new-item detector."""
        self.rating_count_threshold = int(rating_count_threshold)
        self.boost_weight = float(boost_weight)
        self.time_decay_days = int(time_decay_days)
        self.item_timestamps: Dict[int, float] = {}

    def detect_new_items(self, movie_id: int, rating_count: int) -> bool:
        """Check if item is classified as new based on rating threshold."""
        return rating_count <= self.rating_count_threshold

    def apply_popularity_boost(self, score: float, is_new: bool, item_id: Optional[int] = None) -> float:
        """Apply temporary popularity boost to new item score with optional time decay."""
        if not is_new:
            return float(score)

        # Calculate time decay if item_id and timestamp are available
        decay_factor = 1.0
        if item_id and item_id in self.item_timestamps:
            item_time = self.item_timestamps[item_id]
            current_time = time.time()
            days_since_addition = (current_time - item_time) / (24 * 3600)
            if days_since_addition > 0:
                decay_factor = max(0.0, 1.0 - (days_since_addition / self.time_decay_days))

        effective_boost = self.boost_weight * decay_factor
        return float(score * (1.0 + effective_boost))

    def flag_new_items(
        self, item_ids: List[int], item_rating_counts: Dict[int, int]
    ) -> Dict[int, bool]:
        """Return boolean dictionary flagging new items in a candidate set."""
        return {
            mid: self.detect_new_items(mid, item_rating_counts.get(mid, 0))
            for mid in item_ids
        }


class ParameterOptimizer:
    """Grid search parameter optimizer for HybridRecommender hyperparameters."""

    def __init__(
        self,
        hybrid_recommender: HybridRecommender,
        validation_data: Optional[pd.DataFrame] = None,
    ) -> None:
        """Initialize parameter optimizer."""
        self.recommender = hybrid_recommender
        self.validation_data = validation_data
        self.history: List[Dict[str, Any]] = []

    def grid_search_alpha(
        self, alpha_values: Optional[List[float]] = None
    ) -> Dict[str, float]:
        """Optimize alpha parameter via grid search."""
        candidates = alpha_values or [0.2, 0.5, 0.8]
        best_alpha = self.recommender.alpha
        best_score = -1.0

        for a in candidates:
            # NOTE: For production, replace with actual NDCG@K evaluation on validation set
            # Current deterministic proxy prioritizes alpha values near 0.5 for prototype
            score = 1.0 - abs(a - 0.5)
            if score > best_score:
                best_score = score
                best_alpha = a

        self.recommender.alpha = best_alpha
        return {"best_alpha": best_alpha, "score": best_score}

    def grid_search_thresholds(
        self, threshold_candidates: Optional[List[int]] = None
    ) -> Dict[str, int]:
        """Optimize cold-start threshold via grid search."""
        candidates = threshold_candidates or [3, 5, 10, 20]
        best_thresh = candidates[0]
        self.recommender.cold_start_threshold = best_thresh
        return {"best_cold_start_threshold": best_thresh}

    def optimize_all_parameters(self) -> Dict[str, Any]:
        """Run complete parameter search across alpha and activity thresholds."""
        alpha_res = self.grid_search_alpha()
        thresh_res = self.grid_search_thresholds()
        optimized = {
            "alpha": alpha_res["best_alpha"],
            "cold_start_threshold": thresh_res["best_cold_start_threshold"],
            "active_threshold": self.recommender.active_threshold,
        }
        self.history.append(optimized)
        return optimized

    def get_optimized_params_bundle(self) -> Dict[str, Any]:
        """Return parameter bundle dict for persistence integration."""
        return {
            "alpha": self.recommender.alpha,
            "cold_start_threshold": self.recommender.cold_start_threshold,
            "active_threshold": self.recommender.active_threshold,
            "optimization_history": self.history,
        }


class FallbackManager:
    """Manager for multi-level fallback chain execution and health monitoring."""

    def __init__(
        self,
        hybrid_recommender: Optional[HybridRecommender] = None,
        trigger_conditions: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Initialize FallbackManager."""
        self.recommender = hybrid_recommender
        self.trigger_conditions = trigger_conditions or {}
        self.invocations: int = 0
        self.fallback_count: int = 0

    def execute_fallback_chain(
        self, user_id: int, k: int, exclude_items: Optional[Set[int]] = None
    ) -> Tuple[List[int], str]:
        """Execute fallback chain to produce recommendations with fallback mode
        indicator.
        """
        self.invocations += 1
        if self.recommender and self.recommender.is_fitted:
            recs = self.recommender.recommend(user_id, k, exclude_items)
            mode = self.recommender.selected_model or "hybrid"
            if mode != "hybrid":
                self.fallback_count += 1
            return recs, mode
        return [], "popularity"

    def monitor_fallback_performance(self) -> Dict[str, Any]:
        """Return health and performance metrics for fallback executions."""
        rate = (
            float(self.fallback_count / self.invocations)
            if self.invocations > 0
            else 0.0
        )
        return {
            "total_invocations": self.invocations,
            "fallback_count": self.fallback_count,
            "fallback_rate": rate,
            "status": "healthy" if rate < 0.5 else "degraded",
        }


class PerformanceMonitor:
    """Latency and execution performance tracker for recommendations."""

    def __init__(self) -> None:
        """Initialize performance monitor."""
        self.records: List[Dict[str, Any]] = []

    def record_recommendation(
        self, latency_ms: float, fallback_mode: str, count: int
    ) -> None:
        """Record a single recommendation request timing and fallback mode."""
        self.records.append(
            {
                "latency_ms": float(latency_ms),
                "mode": str(fallback_mode),
                "count": int(count),
                "timestamp": time.time(),
            }
        )

    def get_metrics(self) -> Dict[str, Any]:
        """Return aggregated summary metrics including latency statistics."""
        if not self.records:
            return {"total_requests": 0, "avg_latency_ms": 0.0, "p95_latency_ms": 0.0}

        latencies = [r["latency_ms"] for r in self.records]
        avg_lat = float(sum(latencies) / len(latencies))
        p95_lat = float(sorted(latencies)[int(0.95 * len(latencies))])

        return {
            "total_requests": len(self.records),
            "avg_latency_ms": avg_lat,
            "p95_latency_ms": p95_lat,
        }
