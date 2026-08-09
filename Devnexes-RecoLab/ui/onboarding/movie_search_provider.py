"""Movie search provider with efficient lookup and preview capabilities (Task-003)."""

from __future__ import annotations

import re
import time
from typing import Any
import pandas as pd
import streamlit as st

from ui.data_provider import DataProvider, extract_year
from ui.session_manager import SessionManager


class MovieSearchProvider:
    """Provides movie search functionality for onboarding liked-movies input."""

    # Rate limiting: max 10 searches per minute per session
    MAX_SEARCHES_PER_MINUTE = 10
    RATE_LIMIT_WINDOW = 60  # seconds

    def __init__(self, data_provider: DataProvider | None = None) -> None:
        self._dp = data_provider or DataProvider()
        self._movies_df = self._dp.movies

    def _check_rate_limit(self) -> tuple[bool, str]:
        """Check if search rate limit has been exceeded.

        Returns:
            Tuple of (allowed: bool, message: str)
        """
        search_history = SessionManager.get_onboarding_search_history() or []
        current_time = time.time()

        # Filter searches within the rate limit window
        recent_searches = [t for t in search_history if current_time - t < self.RATE_LIMIT_WINDOW]

        if len(recent_searches) >= self.MAX_SEARCHES_PER_MINUTE:
            wait_time = int(self.RATE_LIMIT_WINDOW - (current_time - recent_searches[0]))
            return False, f"Rate limit exceeded. Please wait {wait_time} seconds before searching again."

        # Add current search to history
        recent_searches.append(current_time)
        SessionManager.set_onboarding_search_history(recent_searches)
        return True, ""

    def search_movies(self, query: str, limit: int = 10) -> list[dict[str, Any]]:
        """Search movies by title substring matching, returning top `limit` results.

        Sanitizes search query for XSS and regex safety.
        Enforces rate limiting (max 10 searches per minute).
        """
        # Check rate limit before processing
        allowed, message = self._check_rate_limit()
        if not allowed:
            st.warning(message)
            return []
        query_str = (query or "").strip()
        if not query_str:
            # Default to top popular movies if no search query provided
            popular_ids = [1, 2571, 296, 356, 318, 593, 480, 110, 589, 527]
            results = []
            for mid in popular_ids:
                m = self.get_movie_preview(mid)
                if m:
                    results.append(m)
            return results[:limit]

        # Sanitize query by removing dangerous characters
        clean_query = re.sub(r"[<>]", "", query_str)
        if not clean_query:
            return []

        # Case-insensitive substring search on title
        mask = self._movies_df["title"].str.contains(clean_query, case=False, na=False, regex=False)
        matches = self._movies_df[mask].head(limit)

        results = []
        for row in matches.itertuples():
            movie_id: int | None = None
            if hasattr(row, 'movieId'):
                try:
                    movie_id = int(row.movieId)  # type: ignore[arg-type]
                except (ValueError, TypeError):
                    continue
            if movie_id is None:
                continue
            stats = self._dp.get_movie_stats(movie_id)
            genres_list = [g.strip() for g in str(row.genres).split("|") if g.strip()]
            title_str = str(row.title) if hasattr(row, 'title') else f"Movie {movie_id}"
            results.append({
                "movieId": movie_id,
                "title": title_str,
                "genres": str(row.genres) if hasattr(row, 'genres') else "Unknown",
                "genres_list": genres_list,
                "year": extract_year(title_str),
                "popularity": stats.get("rating_count", 0),
                "mean_rating": stats.get("mean_rating"),
            })
        return results

    def get_movie_preview(self, movie_id: int) -> dict[str, Any] | None:
        """Get detailed preview info for a specific movie."""
        movie = self._dp.get_movie(movie_id)
        if not movie:
            return None

        stats = self._dp.get_movie_stats(movie_id)
        genres_list = [g.strip() for g in str(movie["genres"]).split("|") if g.strip()]
        return {
            "movieId": int(movie["movieId"]),
            "title": str(movie["title"]),
            "genres": str(movie["genres"]),
            "genres_list": genres_list,
            "year": movie.get("year"),
            "popularity": stats.get("rating_count", 0),
            "mean_rating": stats.get("mean_rating"),
        }
