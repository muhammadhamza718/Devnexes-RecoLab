"""Shared interfaces for all recommendation models.

Defines the protocol contracts that PopularityModel, ContentModel, CollaborativeModel,
and HybridModel must satisfy. This enables duck-typing and protocol conformance
testing without requiring existing models to inherit from a common base class.
"""

from __future__ import annotations

from typing import Protocol

from typing_extensions import runtime_checkable


@runtime_checkable
class Recommender(Protocol):
    """Protocol for all recommendation models.

    Any model that can provide personalized recommendations for existing users
    must implement this interface. The protocol is structural (duck-typing) rather
    than nominal (inheritance), so PopularityModel automatically satisfies it
    without requiring changes to Week 1 code.
    """

    def recommend(
        self,
        user_id: int,
        k: int,
        exclude_items: set[int] | None = None,
    ) -> list[int]:
        """Return top-K recommended item IDs for the given user.

        Args:
            user_id: Identifier for the user (kept for API symmetry).
            k: Number of items to recommend.
            exclude_items: Item IDs to exclude (typically the user's already-rated
                items). If None, no exclusion is applied.

        Returns:
            List of recommended item IDs, length <= k. May be empty if no
            suitable recommendations exist (e.g., all items excluded).
        """
        ...


@runtime_checkable
class ColdStartHandler(Protocol):
    """Protocol for models that handle new users with no interaction history.

    Models that can generate recommendations from genre preferences and/or
    liked movie IDs (without inventing fake history) must implement this
    interface. This is the core cold-start requirement for the project.
    """

    def recommend_cold_start(
        self,
        genres: list[str],
        liked_movie_ids: list[int],
        k: int,
    ) -> list[int]:
        """Return top-K recommendations for a new user with no history.

        Args:
            genres: List of genre names the user likes (e.g., ["Action", "Sci-Fi"]).
                Duplicates are deduplicated before use.
            liked_movie_ids: List of movie IDs the user has liked (e.g., from an
                onboarding flow). These are excluded from results to avoid
                redundancy.
            k: Number of items to recommend.

        Returns:
            List of recommended item IDs, length <= k. Must not include any
            IDs from liked_movie_ids. Raises FeatureError if both genres and
            liked_movie_ids are empty (no query basis).
        """
        ...


class FeatureError(ValueError):
    """Custom exception for feature-related errors.

    Raised when a recommendation query cannot be processed due to missing or
    invalid feature data (e.g., a movie with no genres, a zero-norm vector).
    This is preferred over returning NaN or crashing with a generic error.

    Attributes:
        movie_id: The movie ID that caused the error (if applicable).
    """

    def __init__(self, message: str, movie_id: int | None = None) -> None:
        super().__init__(message)
        self.movie_id = movie_id

    def __str__(self) -> str:
        if self.movie_id is not None:
            return f"movie_id={self.movie_id}: {super().__str__()}"
        return super().__str__()


__all__ = [
    "Recommender",
    "ColdStartHandler",
    "FeatureError",
]
