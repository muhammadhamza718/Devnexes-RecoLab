"""User-Based and Item-Based Collaborative Filtering Recommender Engines.

Implements personalized movie recommendations based on user-user and item-item
cosine similarity over sparse rating matrices, with consumed-item filtering and
cold-start fallback.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Set, Tuple

import numpy as np
import pandas as pd
from scipy.sparse import csr_matrix
from sklearn.metrics.pairwise import cosine_similarity

from recolab.content import ContentModel
from recolab.interfaces import Recommender
from recolab.persistence import load_artifact, save_artifact


def _build_user_item_matrix_and_mappings(
    ratings_df: pd.DataFrame,
) -> Tuple[csr_matrix, Dict[int, int], Dict[int, int], Dict[int, int], Dict[int, int]]:
    """Build index mappings and CSR sparse user-item matrix from ratings DataFrame."""
    unique_users: List[int] = sorted(ratings_df["userId"].unique())
    unique_movies: List[int] = sorted(ratings_df["movieId"].unique())

    user_mapping = {uid: idx for idx, uid in enumerate(unique_users)}
    reverse_user_mapping = {idx: uid for idx, uid in enumerate(unique_users)}
    movie_mapping = {mid: idx for idx, mid in enumerate(unique_movies)}
    reverse_movie_mapping = {idx: mid for idx, mid in enumerate(unique_movies)}

    rows = ratings_df["userId"].map(user_mapping).values
    cols = ratings_df["movieId"].map(movie_mapping).values
    data = ratings_df["rating"].values.astype(np.float32)

    n_users = len(unique_users)
    n_movies = len(unique_movies)

    user_item_matrix = csr_matrix(
        (data, (rows, cols)), shape=(n_users, n_movies), dtype=np.float32
    )

    return (
        user_item_matrix,
        user_mapping,
        reverse_user_mapping,
        movie_mapping,
        reverse_movie_mapping,
    )


class UserBasedCF:
    """User-based collaborative filtering recommender.

    Computes user-user cosine similarity from a user-item rating matrix stored in
    scipy CSR sparse format, and aggregates ratings of nearest neighbors to predict
    unrated movie preferences.

    Attributes:
        k_similar_users: Number of top similar users to consider (default: 50).
        min_similarity: Threshold for user similarity (default: 0.1).
        cold_start_threshold: Max ratings count to treat user as cold-start (default: 5).
        user_item_matrix: Sparse CSR matrix of shape (n_users, n_items).
        similarity_matrix: Dense matrix of user-user cosine similarities.
        user_mapping: Map from raw user_id to row index.
        movie_mapping: Map from raw movie_id to column index.
        reverse_user_mapping: Map from row index to raw user_id.
        reverse_movie_mapping: Map from column index to raw movie_id.
        content_model: Optional ContentModel instance for cold-start fallback.
        is_fitted: Boolean flag indicating if fit() has been executed.
    """

    def __init__(
        self,
        k_similar_users: int = 50,
        min_similarity: float = 0.1,
        cold_start_threshold: int = 5,
        content_model: Optional[ContentModel] = None,
    ) -> None:
        """Initialize UserBasedCF model with hyper-parameters.

        Args:
            k_similar_users: Maximum number of similar users for rating aggregation.
            min_similarity: Minimum cosine similarity score threshold.
            cold_start_threshold: Rating threshold for cold-start fallback.
            content_model: ContentModel instance used for cold-start user recommendations.

        Raises:
            ValueError: If hyper-parameters are invalid.
        """
        if k_similar_users <= 0:
            raise ValueError("k_similar_users must be a positive integer.")
        if min_similarity < 0.0 or min_similarity > 1.0:
            raise ValueError("min_similarity must be between 0.0 and 1.0.")

        self.k_similar_users: int = k_similar_users
        self.min_similarity: float = min_similarity
        self.cold_start_threshold: int = cold_start_threshold
        self.content_model: Optional[ContentModel] = content_model

        self.user_item_matrix: Optional[csr_matrix] = None
        self.similarity_matrix: Optional[np.ndarray] = None
        self.user_mapping: Dict[int, int] = {}
        self.movie_mapping: Dict[int, int] = {}
        self.reverse_user_mapping: Dict[int, int] = {}
        self.reverse_movie_mapping: Dict[int, int] = {}
        self.is_fitted: bool = False

    def fit(self, ratings_df: pd.DataFrame) -> None:
        """Train model on user-item ratings data.

        Args:
            ratings_df: DataFrame containing 'userId', 'movieId', and 'rating' columns.

        Raises:
            ValueError: If required columns are missing or DataFrame is empty.
        """
        if not isinstance(ratings_df, pd.DataFrame):
            raise ValueError("ratings_df must be a pandas DataFrame.")

        required_cols = {"userId", "movieId", "rating"}
        if not required_cols.issubset(set(ratings_df.columns)):
            raise ValueError(
                f"ratings_df missing required columns: {required_cols - set(ratings_df.columns)}"
            )

        if ratings_df.empty:
            raise ValueError("ratings_df cannot be empty.")

        try:
            self._build_user_item_matrix(ratings_df)
            self._compute_similarity()
            self.is_fitted = True
        except Exception as err:
            self.is_fitted = False
            raise RuntimeError(f"Failed to fit UserBasedCF model: {str(err)}") from err

    def _build_user_item_matrix(self, ratings_df: pd.DataFrame) -> None:
        """Build index mappings and CSR sparse user-item matrix from ratings DataFrame."""
        (
            self.user_item_matrix,
            self.user_mapping,
            self.reverse_user_mapping,
            self.movie_mapping,
            self.reverse_movie_mapping,
        ) = _build_user_item_matrix_and_mappings(ratings_df)

    def _compute_similarity(self) -> None:
        """Compute pairwise user-user cosine similarity matrix using sklearn."""
        if self.user_item_matrix is None:
            raise ValueError("user_item_matrix is not built.")

        # pyrefly: ignore [bad-argument-type]
        self.similarity_matrix = np.asarray(cosine_similarity(self.user_item_matrix))

    def _find_similar_users(self, user_id: int) -> List[Tuple[int, float]]:
        """Find up to k_similar_users exceeding min_similarity threshold for target user.

        Args:
            user_id: Raw target user ID.

        Returns:
            List of (user_id, similarity_score) tuples sorted by similarity descending.
        """
        if self.similarity_matrix is None or user_id not in self.user_mapping:
            return []

        user_idx = self.user_mapping[user_id]
        sim_scores = self.similarity_matrix[user_idx]

        # Candidate user indices (excluding target user self-similarity)
        candidate_indices_array = np.where(sim_scores >= self.min_similarity)[0]
        candidate_indices: list[int] = candidate_indices_array.tolist()
        candidate_indices = [idx for idx in candidate_indices if idx != user_idx]

        if not candidate_indices:
            return []

        # Sort candidate indices by similarity descending
        sorted_indices = sorted(
            candidate_indices, key=lambda idx: sim_scores[idx], reverse=True
        )
        top_k_indices = sorted_indices[: self.k_similar_users]

        return [
            (self.reverse_user_mapping[idx], float(sim_scores[idx]))
            for idx in top_k_indices
        ]

    def _aggregate_predictions(
        self, similar_users: List[Tuple[int, float]], target_user_id: int
    ) -> Dict[int, float]:
        """Aggregate predicted ratings for unconsumed movies using weighted similarity sum.

        Args:
            similar_users: List of (similar_user_id, similarity_score) tuples.
            target_user_id: Target user ID.

        Returns:
            Dict mapping raw movie_id -> predicted rating score.
        """
        if not similar_users or self.user_item_matrix is None:
            return {}

        target_row_idx = self.user_mapping[target_user_id]
        target_consumed = set(self.user_item_matrix[target_row_idx].indices)

        weighted_sums: Dict[int, float] = {}
        sim_sums: Dict[int, float] = {}

        for sim_uid, sim_score in similar_users:
            sim_row_idx = self.user_mapping[sim_uid]
            sim_row = self.user_item_matrix[sim_row_idx]
            movie_indices = sim_row.indices
            ratings = sim_row.data

            for col_idx, rating in zip(movie_indices, ratings):
                if col_idx not in target_consumed:
                    weighted_sums[col_idx] = weighted_sums.get(col_idx, 0.0) + (
                        sim_score * rating
                    )
                    sim_sums[col_idx] = sim_sums.get(col_idx, 0.0) + sim_score

        predictions: Dict[int, float] = {}
        for col_idx, w_sum in weighted_sums.items():
            s_sum = sim_sums[col_idx]
            if s_sum > 0.0:
                raw_mid = self.reverse_movie_mapping[col_idx]
                predictions[raw_mid] = w_sum / s_sum

        return predictions

    def _is_cold_start(self, user_id: int) -> bool:
        """Check if user has <= cold_start_threshold ratings or is unknown."""
        if self.user_item_matrix is None or user_id not in self.user_mapping:
            return True

        user_idx = self.user_mapping[user_id]
        num_ratings = self.user_item_matrix[user_idx].nnz
        return bool(num_ratings <= self.cold_start_threshold)

    def recommend(
        self,
        user_id: int,
        k: int,
        exclude_items: Optional[Set[int] | List[int]] = None,
    ) -> List[int]:
        """Generate top-K recommended movie IDs for given user.

        Args:
            user_id: Target user ID.
            k: Number of recommendations to return.
            exclude_items: Set or List of movie IDs to explicitly exclude.

        Returns:
            List of recommended movie IDs of length <= k.

        Raises:
            ValueError: If model is not fitted or k <= 0.
        """
        if not self.is_fitted:
            raise ValueError("Model is not fitted. Call fit() before recommend().")
        if k <= 0:
            raise ValueError("k must be a positive integer.")

        exclude_set: Set[int] = (
            set(exclude_items) if exclude_items is not None else set()
        )

        # Handle cold-start fallback if user has <= cold_start_threshold ratings or is unknown
        if self._is_cold_start(user_id):
            if self.content_model is not None and getattr(
                self.content_model, "fitted", False
            ):
                return self.content_model.recommend(
                    user_id=user_id, k=k, exclude_items=exclude_set
                )
            return []

        # Find similar users
        similar_users = self._find_similar_users(user_id)
        if not similar_users:
            if self.content_model is not None and getattr(
                self.content_model, "fitted", False
            ):
                return self.content_model.recommend(
                    user_id=user_id, k=k, exclude_items=exclude_set
                )
            return []

        # Aggregate predictions for candidate movies
        predictions = self._aggregate_predictions(similar_users, target_user_id=user_id)
        if not predictions:
            if self.content_model is not None and getattr(
                self.content_model, "fitted", False
            ):
                return self.content_model.recommend(
                    user_id=user_id, k=k, exclude_items=exclude_set
                )
            return []

        # Exclude items explicitly specified in exclude_items
        candidate_items = [
            (mid, score) for mid, score in predictions.items() if mid not in exclude_set
        ]

        # Sort candidate items by predicted rating descending, then movie_id ascending
        candidate_items.sort(key=lambda item: (-item[1], item[0]))

        return [mid for mid, _ in candidate_items[:k]]

    def explain(self, user_id: int, movie_id: int) -> str:
        """Provide a human-readable explanation for recommending movie_id to user_id (REQ-004).

        Args:
            user_id: Target user ID.
            movie_id: Target movie ID.

        Returns:
            Grounded, truthful explanation string.
        """
        if not self.is_fitted:
            return "Model is not fitted."
        if self._is_cold_start(user_id):
            if self.content_model is not None and getattr(
                self.content_model, "fitted", False
            ):
                if hasattr(self.content_model, "explain"):
                    return str(self.content_model.explain(user_id, movie_id))
            return "Recommended based on overall popular choices (cold-start fallback)."
        return "Recommended based on ratings from users with similar taste to you."

    def to_bundle(self) -> Dict[str, Any]:
        """Serialize model state to a dictionary for persistence (REQ-012).

        Returns:
            Dict containing all model parameters, mappings, matrices, and state.
        """
        cm_bundle = None
        if self.content_model is not None and hasattr(self.content_model, "to_bundle"):
            cm_bundle = self.content_model.to_bundle()

        return {
            "k_similar_users": self.k_similar_users,
            "min_similarity": self.min_similarity,
            "cold_start_threshold": self.cold_start_threshold,
            "user_mapping": self.user_mapping,
            "movie_mapping": self.movie_mapping,
            "reverse_user_mapping": self.reverse_user_mapping,
            "reverse_movie_mapping": self.reverse_movie_mapping,
            "user_item_matrix": self.user_item_matrix,
            "similarity_matrix": self.similarity_matrix,
            "is_fitted": self.is_fitted,
            "content_model": cm_bundle,
        }

    @classmethod
    def from_bundle(
        cls, bundle: Dict[str, Any], content_model: Optional[ContentModel] = None
    ) -> UserBasedCF:
        """Deserialize model instance from a bundle dictionary (REQ-012).

        Args:
            bundle: Dict containing model state.
            content_model: Optional ContentModel instance override.

        Returns:
            Reconstructed UserBasedCF model instance.
        """
        cm = content_model
        if cm is None and bundle.get("content_model") is not None:
            cm = ContentModel.from_bundle(bundle["content_model"])

        model = cls(
            k_similar_users=bundle.get("k_similar_users", 50),
            min_similarity=bundle.get("min_similarity", 0.1),
            cold_start_threshold=bundle.get("cold_start_threshold", 5),
            content_model=cm,
        )
        model.user_mapping = bundle.get("user_mapping", {})
        model.movie_mapping = bundle.get("movie_mapping", {})
        model.reverse_user_mapping = bundle.get("reverse_user_mapping", {})
        model.reverse_movie_mapping = bundle.get("reverse_movie_mapping", {})
        model.user_item_matrix = bundle.get("user_item_matrix")
        model.similarity_matrix = bundle.get("similarity_matrix")
        model.is_fitted = bundle.get("is_fitted", False)
        return model

    def save(self, path: str | Path) -> Path:
        """Save fitted model artifact to disk.

        Args:
            path: Destination file path.

        Returns:
            Resolved Path object where artifact was written.
        """
        return save_artifact(self.to_bundle(), path)

    @classmethod
    def load(
        cls, path: str | Path, content_model: Optional[ContentModel] = None
    ) -> UserBasedCF:
        """Load model artifact from disk.

        Args:
            path: File path of saved artifact.
            content_model: Optional ContentModel fallback override.

        Returns:
            Reconstructed UserBasedCF model.
        """
        bundle = load_artifact(path)
        return cls.from_bundle(bundle, content_model=content_model)


class ItemBasedCF:
    """Item-based collaborative filtering recommender.

    Computes item-item cosine similarity from the user-item rating matrix stored in
    scipy CSR sparse format, and aggregates ratings of items similar to a user's
    previously rated items to predict unrated movie preferences.

    Attributes:
        k_similar_items: Maximum number of similar items per rated item (default: 50).
        min_similarity: Threshold for item similarity (default: 0.1).
        user_item_matrix: Sparse CSR matrix of shape (n_users, n_items).
        item_item_matrix: Dense matrix of shape (n_items, n_items) storing item-item cosine similarities.
        user_mapping: Map from raw user_id to row index.
        movie_mapping: Map from raw movie_id to column index.
        reverse_user_mapping: Map from row index to raw user_id.
        reverse_movie_mapping: Map from column index to raw movie_id.
        content_model: Optional ContentModel instance for new-item cold-start fallback.
        is_fitted: Boolean flag indicating if fit() has been executed.
    """

    def __init__(
        self,
        k_similar_items: int = 50,
        min_similarity: float = 0.1,
        content_model: Optional[ContentModel] = None,
    ) -> None:
        """Initialize ItemBasedCF model with hyper-parameters.

        Args:
            k_similar_items: Maximum number of similar items per rated item.
            min_similarity: Minimum cosine similarity score threshold.
            content_model: ContentModel instance used for new-item cold-start fallback.

        Raises:
            ValueError: If hyper-parameters are invalid.
        """
        if k_similar_items <= 0:
            raise ValueError("k_similar_items must be a positive integer.")
        if min_similarity < 0.0 or min_similarity > 1.0:
            raise ValueError("min_similarity must be between 0.0 and 1.0.")

        self.k_similar_items: int = k_similar_items
        self.min_similarity: float = min_similarity
        self.content_model: Optional[ContentModel] = content_model

        self.user_item_matrix: Optional[csr_matrix] = None
        self.item_item_matrix: Optional[np.ndarray] = None
        self.user_mapping: Dict[int, int] = {}
        self.movie_mapping: Dict[int, int] = {}
        self.reverse_user_mapping: Dict[int, int] = {}
        self.reverse_movie_mapping: Dict[int, int] = {}
        self.is_fitted: bool = False

    def fit(self, ratings_df: pd.DataFrame) -> None:
        """Train model on user-item ratings data.

        Args:
            ratings_df: DataFrame containing 'userId', 'movieId', and 'rating' columns.

        Raises:
            ValueError: If required columns are missing or DataFrame is empty.
        """
        if not isinstance(ratings_df, pd.DataFrame):
            raise ValueError("ratings_df must be a pandas DataFrame.")

        required_cols = {"userId", "movieId", "rating"}
        if not required_cols.issubset(set(ratings_df.columns)):
            raise ValueError(
                f"ratings_df missing required columns: {required_cols - set(ratings_df.columns)}"
            )

        if ratings_df.empty:
            raise ValueError("ratings_df cannot be empty.")

        try:
            self._build_user_item_matrix(ratings_df)
            self._compute_item_similarity()
            self.is_fitted = True
        except Exception as err:
            self.is_fitted = False
            raise RuntimeError(f"Failed to fit ItemBasedCF model: {str(err)}") from err

    def _build_user_item_matrix(self, ratings_df: pd.DataFrame) -> None:
        """Build index mappings and CSR sparse user-item matrix from ratings DataFrame."""
        (
            self.user_item_matrix,
            self.user_mapping,
            self.reverse_user_mapping,
            self.movie_mapping,
            self.reverse_movie_mapping,
        ) = _build_user_item_matrix_and_mappings(ratings_df)

    def _compute_item_similarity(self) -> None:
        """Compute pairwise item-item cosine similarity matrix using sklearn."""
        if self.user_item_matrix is None:
            raise ValueError("user_item_matrix is not built.")

        # Transpose user_item_matrix to (n_items, n_users) for item-item similarity
        item_user_matrix = self.user_item_matrix.T.tocsr()
        self.item_item_matrix = np.asarray(cosine_similarity(item_user_matrix))

    def _find_similar_items(self, movie_id: int) -> List[Tuple[int, float]]:
        """Find up to k_similar_items exceeding min_similarity threshold for target movie.

        Args:
            movie_id: Raw target movie ID.

        Returns:
            List of (movie_id, similarity_score) tuples sorted by similarity descending.
        """
        if self.item_item_matrix is None or movie_id not in self.movie_mapping:
            return []

        item_idx = self.movie_mapping[movie_id]
        sim_scores = self.item_item_matrix[item_idx]

        # Candidate item indices (excluding target item self-similarity)
        candidate_indices_array = np.where(sim_scores >= self.min_similarity)[0]
        candidate_indices: list[int] = candidate_indices_array.tolist()
        candidate_indices = [idx for idx in candidate_indices if idx != item_idx]

        if not candidate_indices:
            return []

        sorted_indices = sorted(
            candidate_indices, key=lambda idx: sim_scores[idx], reverse=True
        )
        top_k_indices = sorted_indices[: self.k_similar_items]

        return [
            (self.reverse_movie_mapping[idx], float(sim_scores[idx]))
            for idx in top_k_indices
        ]

    def _aggregate_predictions(
        self,
        user_rated_items: List[Tuple[int, float]],
        user_id: Optional[int] = None,
    ) -> Dict[int, float]:
        """Aggregate item-based predicted ratings for candidate items.

        For each movie the user has rated (rated_mid, user_rating), look up similar items
        (cand_mid, sim_score). Weighted prediction = sum(sim * user_rating) / sum(sim).
        """
        if not user_rated_items or self.item_item_matrix is None:
            return {}

        consumed_movie_ids = {mid for mid, _ in user_rated_items}

        weighted_sums: Dict[int, float] = {}
        sim_sums: Dict[int, float] = {}

        for rated_mid, user_rating in user_rated_items:
            similar_items = self._find_similar_items(rated_mid)
            for cand_mid, sim_score in similar_items:
                if cand_mid not in consumed_movie_ids:
                    weighted_sums[cand_mid] = weighted_sums.get(cand_mid, 0.0) + (
                        sim_score * user_rating
                    )
                    sim_sums[cand_mid] = sim_sums.get(cand_mid, 0.0) + sim_score

        predictions: Dict[int, float] = {}
        for cand_mid, w_sum in weighted_sums.items():
            s_sum = sim_sums[cand_mid]
            if s_sum > 0.0:
                predictions[cand_mid] = w_sum / s_sum

        return predictions

    def _is_new_item(self, movie_id: int) -> bool:
        """Check if movie_id is a new item with 0 training ratings."""
        return movie_id not in self.movie_mapping

    def recommend(
        self,
        user_id: int,
        k: int,
        exclude_items: Optional[Set[int] | List[int]] = None,
    ) -> List[int]:
        """Generate top-K recommended movie IDs for given user using item-based CF.

        Args:
            user_id: Target user ID.
            k: Number of recommendations to return.
            exclude_items: Set or List of movie IDs to explicitly exclude.

        Returns:
            List of recommended movie IDs of length <= k.

        Raises:
            ValueError: If model is not fitted or k <= 0.
        """
        if not self.is_fitted:
            raise ValueError("Model is not fitted. Call fit() before recommend().")
        if k <= 0:
            raise ValueError("k must be a positive integer.")

        exclude_set: Set[int] = (
            set(exclude_items) if exclude_items is not None else set()
        )

        if user_id not in self.user_mapping or self.user_item_matrix is None:
            # Fallback to ContentModel for unknown user
            if self.content_model is not None and getattr(
                self.content_model, "fitted", False
            ):
                return self.content_model.recommend(
                    user_id=user_id, k=k, exclude_items=exclude_set
                )
            return []

        # Extract user's rated items
        user_idx = self.user_mapping[user_id]
        user_row = self.user_item_matrix[user_idx]
        movie_indices = user_row.indices
        ratings = user_row.data

        if len(movie_indices) == 0:
            if self.content_model is not None and getattr(
                self.content_model, "fitted", False
            ):
                return self.content_model.recommend(
                    user_id=user_id, k=k, exclude_items=exclude_set
                )
            return []

        user_rated_items = [
            (self.reverse_movie_mapping[col_idx], float(rating))
            for col_idx, rating in zip(movie_indices, ratings)
        ]

        predictions = self._aggregate_predictions(user_rated_items)
        if not predictions:
            if self.content_model is not None and getattr(
                self.content_model, "fitted", False
            ):
                return self.content_model.recommend(
                    user_id=user_id, k=k, exclude_items=exclude_set
                )
            return []

        candidate_items = [
            (mid, score) for mid, score in predictions.items() if mid not in exclude_set
        ]

        candidate_items.sort(key=lambda item: (-item[1], item[0]))

        return [mid for mid, _ in candidate_items[:k]]

    def explain(self, user_id: int, movie_id: int) -> str:
        """Provide a human-readable explanation for recommending movie_id to user_id (REQ-004).

        Args:
            user_id: Target user ID.
            movie_id: Target movie ID.

        Returns:
            Grounded, truthful explanation string.
        """
        if not self.is_fitted:
            return "Model is not fitted."
        if self._is_new_item(movie_id):
            if self.content_model is not None and getattr(
                self.content_model, "fitted", False
            ):
                if hasattr(self.content_model, "explain"):
                    return str(self.content_model.explain(user_id, movie_id))
            return "Recommended based on content metadata features (new-item fallback)."
        return "Recommended because you rated similar movies highly."

    def to_bundle(self) -> Dict[str, Any]:
        """Serialize model state to a dictionary for persistence (REQ-012).

        Returns:
            Dict containing all model parameters, mappings, matrices, and state.
        """
        cm_bundle = None
        if self.content_model is not None and hasattr(self.content_model, "to_bundle"):
            cm_bundle = self.content_model.to_bundle()

        return {
            "k_similar_items": self.k_similar_items,
            "min_similarity": self.min_similarity,
            "user_mapping": self.user_mapping,
            "movie_mapping": self.movie_mapping,
            "reverse_user_mapping": self.reverse_user_mapping,
            "reverse_movie_mapping": self.reverse_movie_mapping,
            "user_item_matrix": self.user_item_matrix,
            "item_item_matrix": self.item_item_matrix,
            "is_fitted": self.is_fitted,
            "content_model": cm_bundle,
        }

    @classmethod
    def from_bundle(
        cls, bundle: Dict[str, Any], content_model: Optional[ContentModel] = None
    ) -> ItemBasedCF:
        """Deserialize model instance from a bundle dictionary (REQ-012).

        Args:
            bundle: Dict containing model state.
            content_model: Optional ContentModel instance override.

        Returns:
            Reconstructed ItemBasedCF model instance.
        """
        cm = content_model
        if cm is None and bundle.get("content_model") is not None:
            cm = ContentModel.from_bundle(bundle["content_model"])

        model = cls(
            k_similar_items=bundle.get("k_similar_items", 50),
            min_similarity=bundle.get("min_similarity", 0.1),
            content_model=cm,
        )
        model.user_mapping = bundle.get("user_mapping", {})
        model.movie_mapping = bundle.get("movie_mapping", {})
        model.reverse_user_mapping = bundle.get("reverse_user_mapping", {})
        model.reverse_movie_mapping = bundle.get("reverse_movie_mapping", {})
        model.user_item_matrix = bundle.get("user_item_matrix")
        model.item_item_matrix = bundle.get("item_item_matrix")
        model.is_fitted = bundle.get("is_fitted", False)
        return model

    def save(self, path: str | Path) -> Path:
        """Save fitted model artifact to disk.

        Args:
            path: Destination file path.

        Returns:
            Resolved Path object where artifact was written.
        """
        return save_artifact(self.to_bundle(), path)

    @classmethod
    def load(
        cls, path: str | Path, content_model: Optional[ContentModel] = None
    ) -> ItemBasedCF:
        """Load model artifact from disk.

        Args:
            path: File path of saved artifact.
            content_model: Optional ContentModel fallback override.

        Returns:
            Reconstructed ItemBasedCF model.
        """
        bundle = load_artifact(path)
        return cls.from_bundle(bundle, content_model=content_model)
