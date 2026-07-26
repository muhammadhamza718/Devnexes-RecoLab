"""Content-based recommendation model using TF-IDF and cosine similarity.

This module implements ContentModel, which recommends items based on feature
similarity (e.g., movie genres). It satisfies the Recommender and ColdStartHandler
protocols defined in interfaces.py.
"""

from __future__ import annotations

import pickle
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer  # type: ignore[import-untyped]
from sklearn.metrics.pairwise import cosine_similarity  # type: ignore[import-untyped]

from recolab.interfaces import ColdStartHandler, FeatureError, Recommender


@dataclass
class ContentModel(Recommender, ColdStartHandler):
    """Content-based recommender using TF-IDF + cosine similarity on item features.

    The model learns item representations from textual features (e.g., genres)
    and recommends similar items. It handles cold-start users by recommending
    popular items within their preferred genres.

    Attributes:
        item_features: Mapping of item_id -> feature string (e.g., "Action|Sci-Fi")
        item_index: Mapping of item_id -> matrix row index
        tfidf_matrix: TF-IDF matrix of item features (n_items, n_features)
        item_popularity: Mapping of item_id -> rating count
        fitted: Whether the model has been trained
    """

    item_features: dict[int, str] = field(default_factory=dict)
    item_index: dict[int, int] = field(default_factory=dict)
    tfidf_matrix: np.ndarray | None = None
    item_popularity: dict[int, int] = field(default_factory=dict)
    fitted: bool = False
    _ratings: pd.DataFrame = field(init=False)

    def __post_init__(self) -> None:
        """Initialize fields that can't use default_factory with init=False."""
        self._ratings = pd.DataFrame()

    def fit(
        self,
        ratings: pd.DataFrame,
        movies: pd.DataFrame | None = None,
        min_ratings: int = 5,
    ) -> ContentModel:
        """Train the content model on ratings and item metadata.

        Args:
            ratings: DataFrame with columns [userId, movieId, rating, timestamp]
            movies: DataFrame with columns [movieId, title, genres]
            min_ratings: Minimum items per user to include in training

        Returns:
            self for method chaining

        Raises:
            ValueError: If required columns are missing
        """
        # Validate inputs
        required_cols = {"userId", "movieId", "rating"}
        if not required_cols.issubset(ratings.columns):
            missing = required_cols - set(ratings.columns)
            raise ValueError(f"Missing required columns: {missing}")

        if movies is None:
            movies = pd.DataFrame(columns=["movieId", "title", "genres"])

        # Store ratings for user-based recommendations
        self._ratings = ratings.copy()

        # Build item features from genres
        self._build_item_features(movies)

        # Compute TF-IDF matrix
        self._compute_tfidf_matrix()

        # Compute item popularity from ratings
        self._compute_popularity(ratings)

        self.fitted = True
        return self

    def _build_item_features(self, movies: pd.DataFrame) -> None:
        """Build item_features mapping from movies DataFrame."""
        if "movieId" not in movies.columns or "genres" not in movies.columns:
            # Fallback: use empty string for features
            self.item_features = {}
            return

        # Create feature string from genres (replace "|" with space for TF-IDF)
        for _, row in movies.iterrows():
            movie_id = row["movieId"]
            genres = row.get("genres", "")
            # Replace separators with spaces for better tokenization
            feature_str = genres.replace("|", " ")
            self.item_features[movie_id] = feature_str

    def _compute_tfidf_matrix(self) -> None:
        """Compute TF-IDF matrix from item features."""
        if not self.item_features:
            # Empty matrix
            self.tfidf_matrix = np.zeros((0, 0))
            self.item_index = {}
            return

        # Create sorted list of item IDs
        item_ids = sorted(self.item_features.keys())
        self.item_index = {item_id: idx for idx, item_id in enumerate(item_ids)}

        # Get feature strings in order
        feature_strings = [self.item_features[item_id] for item_id in item_ids]

        # Fit TF-IDF vectorizer
        vectorizer = TfidfVectorizer(
            lowercase=True,
            stop_words=None,
            ngram_range=(1, 1),
            min_df=1,
        )
        self.tfidf_matrix = vectorizer.fit_transform(feature_strings).toarray()

    def _compute_popularity(self, ratings: pd.DataFrame) -> None:
        """Compute item popularity from rating counts."""
        # Count ratings per item
        rating_counts = ratings["movieId"].value_counts()
        self.item_popularity = dict(rating_counts)

    def recommend(
        self,
        user_id: int,
        k: int = 10,
        exclude_items: set[int] | None = None,
    ) -> list[int]:
        """Recommend items for a user based on their rating history.

        Args:
            user_id: User ID (not used in pure content model, kept for interface)
            k: Number of recommendations to return
            exclude_items: Items to exclude from recommendations

        Returns:
            List of recommended item IDs, sorted by similarity score

        Raises:
            ValueError: If model is not fitted
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before calling recommend")

        if exclude_items is None:
            exclude_items = set()

        # Get user's rated items
        user_ratings = self._ratings[self._ratings["userId"] == user_id]
        user_rated_items = set(user_ratings["movieId"].unique())

        # If user has no ratings, fall back to popularity
        if not user_rated_items:
            popular_items = sorted(
                self.item_popularity.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            recommendations: list[int] = []
            for item_id, _ in popular_items:
                if item_id not in exclude_items and len(recommendations) < k:
                    recommendations.append(item_id)
            return recommendations

        # Compute similarity scores for all items
        # For each candidate item, find max similarity to any of user's rated items
        candidate_scores: dict[int, float] = {}
        for candidate_id in self.item_index.keys():
            if candidate_id in user_rated_items or candidate_id in exclude_items:
                continue

            max_sim = 0.0
            for rated_id in user_rated_items:
                if rated_id not in self.item_index:
                    continue
                # Compute similarity between candidate and rated item
                if self.tfidf_matrix is None or self.tfidf_matrix.size == 0:
                    continue
                candidate_idx = self.item_index[candidate_id]
                rated_idx = self.item_index[rated_id]
                sim = cosine_similarity(
                    self.tfidf_matrix[candidate_idx:candidate_idx + 1],
                    self.tfidf_matrix[rated_idx:rated_idx + 1],
                )[0][0]
                max_sim = max(max_sim, sim)

            if max_sim > 0:
                candidate_scores[candidate_id] = max_sim

        # Sort by similarity score
        sorted_candidates = sorted(
            candidate_scores.items(),
            key=lambda x: x[1],
            reverse=True,
        )

        # Return top-k
        recommendations = [item_id for item_id, _ in sorted_candidates[:k]]

        # If not enough similar items, fill with popular items
        if len(recommendations) < k:
            popular_items = sorted(
                self.item_popularity.items(),
                key=lambda x: x[1],
                reverse=True,
            )
            for item_id, _ in popular_items:
                if (
                    item_id not in exclude_items
                    and item_id not in user_rated_items
                    and item_id not in recommendations
                    and len(recommendations) < k
                ):
                    recommendations.append(item_id)

        return recommendations

    def similar_items(
        self,
        item_id: int,
        k: int = 10,
    ) -> list[tuple[int, float]]:
        """Find items similar to a given item.

        Args:
            item_id: Item ID to find similar items for
            k: Number of similar items to return

        Returns:
            List of (item_id, similarity_score) tuples, sorted by similarity

        Raises:
            FeatureError: If item_id is not in the model
            ValueError: If model is not fitted
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before calling similar_items")

        if item_id not in self.item_index:
            raise FeatureError(f"Item {item_id} not found in model", movie_id=item_id)

        if self.tfidf_matrix is None or self.tfidf_matrix.size == 0:
            return []

        # Get index of query item
        query_idx = self.item_index[item_id]

        # Compute cosine similarity with all items
        query_vector = self.tfidf_matrix[query_idx:query_idx+1]
        similarities = cosine_similarity(query_vector, self.tfidf_matrix)[0]

        # Get top-k similar items (excluding the query item itself)
        similar_indices = np.argsort(similarities)[::-1][1:k+1]  # Skip first (self)

        results = []
        for idx in similar_indices:
            # Find item_id from index
            for item_i, item_idx in self.item_index.items():
                if item_idx == idx:
                    results.append((item_i, float(similarities[idx])))
                    break

        return results

    def recommend_cold_start(
        self,
        genres: list[str],
        liked_movie_ids: list[int],
        k: int,
    ) -> list[int]:
        """Recommend items for a cold-start user with no rating history.

        Args:
            genres: List of genre names the user likes
            liked_movie_ids: List of movie IDs the user has liked (to exclude)
            k: Number of recommendations to return

        Returns:
            List of recommended item IDs

        Raises:
            FeatureError: If both genres and liked_movie_ids are empty
        """
        if not self.fitted:
            raise ValueError("Model must be fitted before calling recommend_cold_start")

        # If no genres and no liked movies, raise error per protocol
        if not genres and not liked_movie_ids:
            raise FeatureError(
                "Cannot recommend without genre preferences or liked movies",
                movie_id=None,
            )

        # Filter items by preferred genres
        matching_items = []
        for item_id, feature_str in self.item_features.items():
            item_genres = feature_str.split()
            # Check if any preferred genre matches
            if any(genre in item_genres for genre in genres):
                matching_items.append(item_id)

        # Exclude liked movies
        exclude_set = set(liked_movie_ids)
        matching_items = [item for item in matching_items if item not in exclude_set]

        # Sort by popularity among matching items
        matching_items.sort(
            key=lambda x: self.item_popularity.get(x, 0),
            reverse=True,
        )

        return matching_items[:k]

    def get_explanation(
        self,
        user_id: int,
        item_id: int,
    ) -> str:
        """Generate explanation for why an item was recommended.

        Args:
            user_id: User ID (not used in content model)
            item_id: Item ID to explain

        Returns:
            Human-readable explanation string
        """
        if item_id not in self.item_features:
            return f"Item {item_id} not found in catalog"

        genres = self.item_features[item_id].replace(" ", "|")
        return f"Recommended because it matches your interest in {genres} movies"

    def to_bundle(self) -> dict[str, Any]:
        """Serialize model to a dictionary for persistence.

        Returns:
            Dictionary containing all model state
        """
        return {
            "item_features": self.item_features,
            "item_index": self.item_index,
            "tfidf_matrix": (
                self.tfidf_matrix.tolist() if self.tfidf_matrix is not None else None
            ),
            "item_popularity": self.item_popularity,
            "fitted": self.fitted,
            "ratings": self._ratings.to_dict() if self._ratings is not None else None,
        }

    @classmethod
    def from_bundle(cls, bundle: dict[str, Any]) -> ContentModel:
        """Deserialize model from a dictionary.

        Args:
            bundle: Dictionary containing model state

        Returns:
            ContentModel instance
        """
        model = cls(
            item_features=bundle.get("item_features", {}),
            item_index=bundle.get("item_index", {}),
            tfidf_matrix=(
                np.array(bundle["tfidf_matrix"]) if bundle.get("tfidf_matrix") else None
            ),
            item_popularity=bundle.get("item_popularity", {}),
            fitted=bundle.get("fitted", False),
        )
        # Restore ratings if present
        if bundle.get("ratings") is not None:
            model._ratings = pd.DataFrame.from_dict(bundle["ratings"])
        return model

    def save(self, path: str | Path) -> Path:
        """Save model to disk using pickle.

        Args:
            path: Path to save the model

        Returns:
            Resolved path where model was saved
        """
        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "wb") as f:
            pickle.dump(self.to_bundle(), f)

        return path.resolve()

    @classmethod
    def load(cls, path: str | Path) -> ContentModel:
        """Load model from disk.

        Args:
            path: Path to load the model from

        Returns:
            Loaded ContentModel instance
        """
        path = Path(path)
        if not path.exists():
            raise FileNotFoundError(f"Model file not found: {path}")

        with open(path, "rb") as f:
            bundle = pickle.load(f)

        return cls.from_bundle(bundle)
