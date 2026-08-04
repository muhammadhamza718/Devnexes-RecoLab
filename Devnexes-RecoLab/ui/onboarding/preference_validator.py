"""Preference validation with rule-based checks (Task-004)."""

from __future__ import annotations

from typing import Any


class PreferenceValidator:
    """Validates user preferences during onboarding steps."""

    MAX_GENRES = 10
    MAX_LIKED_MOVIES = 20

    @classmethod
    def validate_genres(
        cls, genres: list[str], available_genres: list[str] | None = None
    ) -> tuple[bool, str | None]:
        """Validate selected genre list."""
        if not isinstance(genres, list):
            return False, "Selected genres must be a list."

        if len(genres) > cls.MAX_GENRES:
            return False, f"You can select up to {cls.MAX_GENRES} genres (selected {len(genres)})."

        if available_genres is not None:
            invalid_genres = [g for g in genres if g not in available_genres]
            if invalid_genres:
                return False, f"Invalid genre(s) selected: {', '.join(invalid_genres)}"

        return True, None

    @classmethod
    def validate_liked_movies(cls, liked_movies: list[Any]) -> tuple[bool, str | None]:
        """Validate liked movies list."""
        if not isinstance(liked_movies, list):
            return False, "Liked movies must be a list."

        if len(liked_movies) > cls.MAX_LIKED_MOVIES:
            return (
                False,
                f"You can select up to {cls.MAX_LIKED_MOVIES} liked movies (selected {len(liked_movies)}).",
            )

        return True, None

    @classmethod
    def validate_preferences(
        cls, preferences: dict[str, Any], available_genres: list[str] | None = None
    ) -> tuple[bool, str | None]:
        """Validate complete preference set before backend recommendation generation."""
        if not isinstance(preferences, dict):
            return False, "Preferences must be a dictionary."

        genres = preferences.get("genres", [])
        liked_movies = preferences.get("liked_movies", [])

        # Check genre validity
        valid_g, err_g = cls.validate_genres(genres, available_genres)
        if not valid_g:
            return False, err_g

        # Check liked movies validity
        valid_m, err_m = cls.validate_liked_movies(liked_movies)
        if not valid_m:
            return False, err_m

        # Ensure at least one preference signal exists if not explicitly skipping
        if not genres and not liked_movies and not preferences.get("is_skip"):
            return False, "Please select at least one genre or liked movie, or click Skip."

        return True, None
