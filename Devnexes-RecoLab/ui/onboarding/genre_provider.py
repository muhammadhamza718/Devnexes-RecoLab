"""Genre data provider with popularity metrics and combinations (Task-002)."""

from __future__ import annotations

from typing import Any
import pandas as pd
import streamlit as st

from ui.data_provider import DataProvider


@st.cache_data(show_spinner=False)
def _compute_genre_metrics() -> tuple[list[str], dict[str, int]]:
    """Extract sorted unique genres and genre popularity counts from movies catalog."""
    dp = DataProvider()
    movies_df = dp.movies

    genre_counts: dict[str, int] = {}
    for genres_str in movies_df["genres"].dropna():
        for genre in str(genres_str).split("|"):
            g = genre.strip()
            if g and g != "(no genres listed)":
                genre_counts[g] = genre_counts.get(g, 0) + 1

    sorted_genres = sorted(genre_counts.keys())
    return sorted_genres, genre_counts


class GenreProvider:
    """Provides cached access to dataset genres and metrics."""

    def __init__(self, data_provider: DataProvider | None = None) -> None:
        self._dp = data_provider or DataProvider()

    def get_all_genres(self) -> list[str]:
        """Return all unique genres available in the dataset."""
        genres, _ = _compute_genre_metrics()
        return genres

    def get_genre_popularity(self) -> dict[str, int]:
        """Return map of genre name to movie count in catalog."""
        _, popularity = _compute_genre_metrics()
        return popularity

    def get_suggested_combinations(self) -> list[dict[str, Any]]:
        """Return popular predefined genre combinations for quick selection."""
        return [
            {
                "id": "action_adventure",
                "name": "Action & Adventure",
                "description": "High-octane blockbusters & epic journeys",
                "genres": ["Action", "Adventure"],
            },
            {
                "id": "sci_fi_thriller",
                "name": "Sci-Fi & Thriller",
                "description": "Mind-bending futuristic thrillers",
                "genres": ["Sci-Fi", "Thriller"],
            },
            {
                "id": "comedy_romance",
                "name": "Comedy & Romance",
                "description": "Lighthearted laughs & romance",
                "genres": ["Comedy", "Romance"],
            },
            {
                "id": "drama_crime",
                "name": "Drama & Crime",
                "description": "Intense character studies & crime stories",
                "genres": ["Drama", "Crime"],
            },
            {
                "id": "family_animation",
                "name": "Family & Animation",
                "description": "Animated favorites for all ages",
                "genres": ["Animation", "Children"],
            },
        ]
