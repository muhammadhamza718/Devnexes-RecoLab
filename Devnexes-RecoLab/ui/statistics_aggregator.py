"""Statistics aggregator for user visualizations (Task-007).

Per the Day 3 Afternoon SDD this uses an Aggregator Pattern with lazy
computation: per-user aggregations are computed on first request and cached,
both in the instance cache and in session state (``rating_statistics``), so
charts render without recomputation on every Streamlit rerun.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from ui.data_provider import DataProvider
from ui.session_manager import SessionManager

#: Day-of-week labels in chronological order (used by the activity heatmap).
_DAY_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


class StatisticsAggregator:
    """Lazily computes and caches per-user rating statistics."""

    def __init__(self, data_provider: DataProvider) -> None:
        self.data_provider = data_provider
        self.cache: dict[str, Any] = dict(SessionManager.get_rating_statistics())

    def get_rating_timeline(self, user_id: int) -> pd.DataFrame:
        """Return the user's ratings as a ``[timestamp, rating]`` DataFrame."""
        cache_key = f"rating_timeline_{user_id}"
        if cache_key not in self.cache:
            ratings = self.data_provider.train
            user_ratings = ratings[ratings["userId"] == user_id].copy()
            if user_ratings.empty:
                self.cache[cache_key] = pd.DataFrame(columns=["timestamp", "rating"])
            else:
                self.cache[cache_key] = pd.DataFrame(
                    {
                        "timestamp": pd.to_datetime(
                            user_ratings["timestamp"], unit="s"
                        ),
                        "rating": user_ratings["rating"],
                    }
                ).sort_values("timestamp")
            SessionManager.set_rating_statistics(self.cache)
        return self.cache[cache_key]

    def get_rating_distribution(self, user_id: int) -> dict[float, int]:
        """Return a mapping of rating value -> number of ratings."""
        cache_key = f"rating_distribution_{user_id}"
        if cache_key not in self.cache:
            ratings = self.data_provider.train
            user_ratings = ratings[ratings["userId"] == user_id]
            self.cache[cache_key] = (
                user_ratings["rating"].value_counts().sort_index().to_dict()
            )
            SessionManager.set_rating_statistics(self.cache)
        return self.cache[cache_key]

    def get_genre_preferences(self, user_id: int) -> dict[str, float]:
        """Return normalized genre preferences for the user (fractions of 1.0)."""
        cache_key = f"genre_preferences_{user_id}"
        if cache_key not in self.cache:
            ratings = self.data_provider.train
            user_ratings = ratings[ratings["userId"] == user_id]
            genre_counts: dict[str, int] = {}
            for movie_id in user_ratings["movieId"].unique():
                movie = self.data_provider.get_movie(int(movie_id))
                if movie is None:
                    continue
                for genre in str(movie.get("genres") or "").split("|"):
                    if genre:
                        genre_counts[genre] = genre_counts.get(genre, 0) + 1
            total = sum(genre_counts.values())
            self.cache[cache_key] = (
                {g: c / total for g, c in genre_counts.items()} if total > 0 else {}
            )
            SessionManager.set_rating_statistics(self.cache)
        return self.cache[cache_key]

    def get_activity_heatmap(self, user_id: int) -> pd.DataFrame:
        """Return a day-of-week x hour-of-day rating-count matrix.

        The DataFrame is indexed by weekday name and has one column per hour
        (0-23), suitable for ``plotly.express.imshow``.
        """
        cache_key = f"activity_heatmap_{user_id}"
        if cache_key not in self.cache:
            ratings = self.data_provider.train
            user_ratings = ratings[ratings["userId"] == user_id].copy()
            matrix = pd.DataFrame(0, index=_DAY_ORDER, columns=list(range(24)))
            if not user_ratings.empty:
                hours = pd.to_datetime(user_ratings["timestamp"], unit="s").dt.hour
                days = (
                    pd.to_datetime(user_ratings["timestamp"], unit="s")
                    .dt.dayofweek.map({i: name for i, name in enumerate(_DAY_ORDER)})
                )
                counts = pd.DataFrame({"day": days, "hour": hours}).value_counts()
                for (day, hour), count in counts.items():
                    matrix.loc[day, hour] = count
            self.cache[cache_key] = matrix
            SessionManager.set_rating_statistics(self.cache)
        return self.cache[cache_key]
