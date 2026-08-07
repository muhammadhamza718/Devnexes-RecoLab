"""Enhanced explanation engine for the RecoLab dashboard (Feature 008, Task-009).

Builds on each model's plain-text ``explain()`` output with three structured
enrichments: a feature-importance map (IDF-style genre weights for the content
model, neighbour / rated-item similarity contributions for the CF models), a
content/collaborative/popularity contribution breakdown, and a confidence
score. Every enrichment degrades to a safe fallback when the underlying data
is unavailable on the model (Task-009: "Fallbacks work for missing data").
"""

from __future__ import annotations

import logging
import math
from typing import Any

import numpy as np

logger = logging.getLogger(__name__)

# Canonical contribution slices rendered by the breakdown pie chart (Task-012).
_CONTRIBUTION_KEYS: tuple[str, ...] = (
    "content_contribution",
    "collaborative_contribution",
    "popularity_contribution",
    "confidence_contribution",
)

_FALLBACK_EXPLANATION = "This item was recommended by the selected model."


class ExplanationEnhancer:
    """Enhances a model explanation with importance, contributions, confidence.

    Args:
        model_manager: :class:`ModelManager` used to resolve a model by its
            canonical display name. Model instances are cached per server run,
            so the instance used here is the same one that produced the
            recommendations (including any live-applied parameters).
        provider: Optional :class:`DataProvider` used to resolve movie titles
            in the CF feature-importance labels. When omitted, numeric movie
            ids are used instead.
    """

    def __init__(self, model_manager: Any, provider: Any | None = None) -> None:
        self._model_manager = model_manager
        self._provider = provider

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def enhance_explanation(
        self,
        user_id: int,
        movie_id: int,
        model_name: str,
        detail_level: str = "detailed",
    ) -> dict[str, Any]:
        """Build the enhanced explanation payload for one recommendation.

        The payload is detail-level agnostic: it always contains the base
        explanation, feature importance, contribution breakdown and confidence
        score. The UI panel decides how much of it to reveal based on the
        selected detail level (Task-010).
        """
        model, _ = self._model_manager.get_model(model_name)
        return {
            "model_name": model_name,
            "base_explanation": self._base_explanation(model, user_id, movie_id),
            "feature_importance": self._get_feature_importance(
                model, user_id, movie_id
            ),
            "contribution_breakdown": self._get_contribution_breakdown(
                model, model_name
            ),
            "confidence_score": self._get_confidence_score(model, user_id, movie_id),
            "detail_level": detail_level,
        }

    # ------------------------------------------------------------------
    # Base explanation
    # ------------------------------------------------------------------

    def _base_explanation(self, model: Any, user_id: int, movie_id: int) -> str:
        """Delegate to ``model.explain`` with a safe fallback on failure."""
        explain = getattr(model, "explain", None)
        if not callable(explain):
            return _FALLBACK_EXPLANATION
        try:
            return str(explain(user_id, movie_id))
        except Exception as exc:  # best-effort enrichment
            logger.warning("Explanation failed for %s/%s: %s", user_id, movie_id, exc)
            return _FALLBACK_EXPLANATION

    # ------------------------------------------------------------------
    # Feature importance (Task-009 / Task-011)
    # ------------------------------------------------------------------

    def _get_feature_importance(
        self,
        model: Any,
        user_id: int,
        movie_id: int,
    ) -> dict[str, float]:
        """Extract per-feature importance weights for a recommendation.

        Resolution order:
        1. A ``get_feature_importance`` hook on the model (protocol extension).
        2. Hybrid delegation to the strategy selected during ``recommend()``.
        3. Content model: IDF-style genre weights from its item-feature corpus.
        4. Item-based CF: similarity between the movie and the user's
           highly-rated items.
        5. User-based CF: similarity-weighted contributions of neighbours who
           rated the movie.
        Any missing data degrades to an empty map.
        """
        getter = getattr(model, "get_feature_importance", None)
        if callable(getter):
            try:
                importance = getter(user_id, movie_id)
                if isinstance(importance, dict) and importance:
                    return {str(k): float(v) for k, v in importance.items()}
            except Exception as exc:
                logger.warning("get_feature_importance hook failed: %s", exc)

        # HybridRecommender delegates to whichever strategy actually won.
        if getattr(model, "selected_model", None) and hasattr(model, "content_model"):
            selected = model.selected_model
            if selected == "content" and model.content_model is not None:
                return self._content_feature_importance(model.content_model, movie_id)
            if selected == "collaborative":
                for sub in (model.user_based_cf, model.item_based_cf):
                    if sub is not None:
                        importance = self._cf_feature_importance(sub, user_id, movie_id)
                        if importance:
                            return importance
            return {}

        if hasattr(model, "item_features"):
            return self._content_feature_importance(model, movie_id)
        if hasattr(model, "item_item_matrix") or hasattr(model, "similarity_matrix"):
            return self._cf_feature_importance(model, user_id, movie_id)
        return {}

    def _content_feature_importance(
        self,
        model: Any,
        movie_id: int,
    ) -> dict[str, float]:
        """IDF-style genre weights computed from the model's item features.

        The content model does not persist its TF-IDF vectorizer vocabulary, so
        exact per-token TF-IDF magnitudes cannot be reconstructed. Instead the
        IDF component is computed from the model's own ``item_features``
        corpus: distinctive genres (present in few movies) weigh more than
        ubiquitous ones. Weights are normalised to sum to 1.
        """
        features: dict[int, str] = getattr(model, "item_features", {}) or {}
        genres = str(features.get(movie_id, "")).split()
        if not genres:
            return {}
        n_items = max(len(features), 1)
        weights: dict[str, float] = {}
        for genre in genres:
            docs_with = sum(
                1 for feat in features.values() if genre in str(feat).split()
            )
            weights[genre] = 1.0 + math.log(n_items / (1 + docs_with))
        total = sum(weights.values()) or 1.0
        ordered = sorted(weights.items(), key=lambda kv: kv[1], reverse=True)
        return {genre: round(value / total, 4) for genre, value in ordered}

    def _cf_feature_importance(
        self,
        model: Any,
        user_id: int,
        movie_id: int,
    ) -> dict[str, float]:
        """Similarity-based importance for the collaborative models.

        Item-based CF: the movie's similarity to each of the user's
        positively-rated items, weighted by that user's rating. User-based CF:
        the similarity of each neighbour who rated the movie, weighted by
        their rating. Labels use movie titles when a provider is available.
        Only the best five contributions are kept, normalised to sum to 1.
        """
        if hasattr(model, "item_item_matrix"):
            return self._item_cf_importance(model, user_id, movie_id)
        return self._user_cf_importance(model, user_id, movie_id)

    def _item_cf_importance(
        self,
        model: Any,
        user_id: int,
        movie_id: int,
    ) -> dict[str, float]:
        user_mapping = getattr(model, "user_mapping", {}) or {}
        movie_mapping = getattr(model, "movie_mapping", {}) or {}
        reverse_movie = getattr(model, "reverse_movie_mapping", {}) or {}
        item_item = getattr(model, "item_item_matrix", None)
        user_item = getattr(model, "user_item_matrix", None)
        if (
            item_item is None
            or user_item is None
            or user_id not in user_mapping
            or movie_id not in movie_mapping
        ):
            return {}

        user_row = _row(user_item, user_mapping[user_id])
        movie_sims = _row(item_item, movie_mapping[movie_id])
        if user_row is None or movie_sims is None:
            return {}

        contributions: dict[str, float] = {}
        for col_idx in range(min(len(user_row), len(movie_sims))):
            rating = user_row[col_idx]
            sim = movie_sims[col_idx]
            if rating <= 0 or sim <= 0:
                continue
            item_id = reverse_movie.get(col_idx)
            label = self._title_for(item_id) if item_id is not None else f"Item {col_idx}"
            contributions[label] = sim * float(rating)

        return self._top_normalised(contributions)

    def _user_cf_importance(
        self,
        model: Any,
        user_id: int,
        movie_id: int,
    ) -> dict[str, float]:
        user_mapping = getattr(model, "user_mapping", {}) or {}
        movie_mapping = getattr(model, "movie_mapping", {}) or {}
        reverse_user = getattr(model, "reverse_user_mapping", {}) or {}
        similarity = getattr(model, "similarity_matrix", None)
        user_item = getattr(model, "user_item_matrix", None)
        if (
            similarity is None
            or user_item is None
            or user_id not in user_mapping
            or movie_id not in movie_mapping
        ):
            return {}

        user_sims = _row(similarity, user_mapping[user_id])
        movie_col = movie_mapping[movie_id]
        if user_sims is None or movie_col < 0 or movie_col >= _ncols(user_item):
            return {}

        contributions: dict[str, float] = {}
        for nbr_idx in range(len(user_sims)):
            rating = _cell(user_item, nbr_idx, movie_col)
            sim = user_sims[nbr_idx]
            if rating <= 0 or sim <= 0 or nbr_idx == user_mapping[user_id]:
                continue
            nbr_id = reverse_user.get(nbr_idx)
            contributions[f"User {nbr_id}" if nbr_id is not None else f"User {nbr_idx}"] = (
                sim * float(rating)
            )

        return self._top_normalised(contributions)

    @staticmethod
    def _top_normalised(
        contributions: dict[str, float],
        top_n: int = 5,
    ) -> dict[str, float]:
        """Keep the top-n positive contributions and normalise to sum to 1."""
        ranked = sorted(
            ((label, value) for label, value in contributions.items() if value > 0),
            key=lambda kv: kv[1],
            reverse=True,
        )[:top_n]
        total = sum(value for _, value in ranked) or 1.0
        return {label: round(value / total, 4) for label, value in ranked}

    def _title_for(self, movie_id: int) -> str:
        """Resolve a movie title via the provider, falling back to its id."""
        if self._provider is None:
            return f"Movie {movie_id}"
        movie = self._provider.get_movie(movie_id) or {}
        return str(movie.get("title") or f"Movie {movie_id}")

    # ------------------------------------------------------------------
    # Contribution breakdown (Task-009 / Task-012)
    # ------------------------------------------------------------------

    @staticmethod
    def _get_contribution_breakdown(
        model: Any,
        model_name: str,
    ) -> dict[str, float]:
        """Content / collaborative / popularity contributions for the model.

        Single-strategy models contribute fully to their strategy. The Hybrid
        model contributes according to its ``alpha`` blend unless a specific
        fallback strategy was selected during ``recommend()``. The
        ``confidence_contribution`` slice is always zero (confidence is
        reported separately on the payload).
        """
        breakdown: dict[str, float] = {key: 0.0 for key in _CONTRIBUTION_KEYS}
        canonical = model_name.lower()
        if canonical == "popularity":
            breakdown["popularity_contribution"] = 1.0
        elif canonical == "content":
            breakdown["content_contribution"] = 1.0
        elif canonical in ("user-based cf", "item-based cf"):
            breakdown["collaborative_contribution"] = 1.0
        elif canonical == "hybrid":
            selected = getattr(model, "selected_model", None) or ""
            if selected == "content":
                breakdown["content_contribution"] = 1.0
            elif selected == "collaborative":
                breakdown["collaborative_contribution"] = 1.0
            elif selected == "popularity":
                breakdown["popularity_contribution"] = 1.0
            else:
                alpha = float(getattr(model, "alpha", 0.5))
                breakdown["content_contribution"] = round(alpha, 4)
                breakdown["collaborative_contribution"] = round(1.0 - alpha, 4)
        return breakdown

    # ------------------------------------------------------------------
    # Confidence (Task-009)
    # ------------------------------------------------------------------

    @staticmethod
    def _get_confidence_score(
        model: Any,
        user_id: int,
        movie_id: int,
    ) -> float:
        """Best-effort confidence in [0, 1]; defaults to 0.5 when absent."""
        getter = getattr(model, "get_confidence", None)
        if not callable(getter):
            return 0.5
        try:
            return max(0.0, min(1.0, float(getter(user_id, movie_id))))
        except Exception as exc:
            logger.warning("Confidence lookup failed for %s/%s: %s", user_id, movie_id, exc)
            return 0.5


# ----------------------------------------------------------------------
# Matrix helpers: work for both numpy arrays and scipy sparse matrices.
# ----------------------------------------------------------------------


def _row(matrix: Any, index: int) -> np.ndarray | None:
    """Return one row of a 2D matrix as a dense 1-D array, or None."""
    if matrix is None:
        return None
    try:
        row = matrix[index]
        toarray = getattr(row, "toarray", None)
        if callable(toarray):
            row = toarray()
        arr = np.asarray(row)
        return arr.ravel() if arr.ndim > 1 else arr
    except Exception as exc:
        logger.warning("Matrix row access failed at %s: %s", index, exc)
        return None


def _cell(matrix: Any, row_idx: int, col_idx: int) -> float:
    """Read one cell of a dense or sparse matrix."""
    try:
        return float(matrix[row_idx, col_idx])
    except Exception:
        row = _row(matrix, row_idx)
        if row is None or col_idx < 0 or col_idx >= len(row):
            return 0.0
        return float(row[col_idx])


def _ncols(matrix: Any) -> int:
    """Column count for dense or sparse matrices."""
    shape = getattr(matrix, "shape", None)
    if shape and len(shape) == 2:
        return int(shape[1])
    return 0
