"""Data access layer for the RecoLab Streamlit app (Task-002).

Loads the MovieLens catalog and the chronological train split once per server
run (cached), then exposes derived views: the user index, per-user rating
counts and activity levels, and movie metadata with the release year parsed
from the title (e.g. "Toy Story (1995)" -> 1995).

Activity thresholds mirror ``HybridRecommender`` (cold_start_threshold=5,
active_threshold=20) so the badges shown in the UI match the behaviour of the
hybrid model's adaptive selection.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]

MOVIES_CSV = PROJECT_ROOT / "data" / "ml-latest-small" / "movies.csv"
RATINGS_CSV = PROJECT_ROOT / "data" / "ml-latest-small" / "ratings.csv"
TRAIN_CSV = PROJECT_ROOT / "data" / "split_datasets" / "train.csv"

# Activity thresholds (mirror HybridRecommender).
COLD_START_MAX_RATINGS = 5
ACTIVE_MIN_RATINGS = 20

_YEAR_RE = re.compile(r"\((\d{4})\)\s*$")


@st.cache_data(show_spinner=False)
def load_movies() -> pd.DataFrame:
    """Load the movie catalog (movieId, title, genres) with int movie ids."""
    if not MOVIES_CSV.exists():
        raise FileNotFoundError(f"Movies file not found: {MOVIES_CSV}")
    df = pd.read_csv(MOVIES_CSV)
    df = df.dropna(subset=["movieId"])
    df["movieId"] = df["movieId"].astype(int)
    return df


@st.cache_data(show_spinner=False)
def load_ratings() -> pd.DataFrame:
    """Load the full ratings table (userId, movieId, rating, timestamp)."""
    if not RATINGS_CSV.exists():
        raise FileNotFoundError(f"Ratings file not found: {RATINGS_CSV}")
    return pd.read_csv(RATINGS_CSV)


@st.cache_data(show_spinner=False)
def load_train() -> pd.DataFrame:
    """Load the chronological train split used to fit the models."""
    if not TRAIN_CSV.exists():
        raise FileNotFoundError(f"Train split not found: {TRAIN_CSV}")
    return pd.read_csv(TRAIN_CSV)


def extract_year(title: str) -> int | None:
    """Parse the release year from a title like 'Toy Story (1995)'."""
    match = _YEAR_RE.search(str(title))
    return int(match.group(1)) if match else None


def activity_level(rating_count: int) -> str:
    """Map a rating count to 'cold-start', 'intermediate' or 'active'."""
    if rating_count <= COLD_START_MAX_RATINGS:
        return "cold-start"
    if rating_count >= ACTIVE_MIN_RATINGS:
        return "active"
    return "intermediate"


class DataProvider:
    """Cached facade over the MovieLens catalog and the train split."""

    def __init__(self) -> None:
        self._movies = load_movies()
        self._train = load_train()
        # Per-user rating counts come from the train split (what the models see).
        self._counts = self._train["userId"].value_counts().sort_index()
        self._movie_index: dict[int, dict[str, Any]] = {
            int(row.movieId): {
                "movieId": int(row.movieId),
                "title": str(row.title),
                "genres": str(row.genres),
                "year": extract_year(row.title),
            }
            for row in self._movies.itertuples()
        }

    # --- raw data --------------------------------------------------------

    @property
    def movies(self) -> pd.DataFrame:
        return self._movies

    @property
    def train(self) -> pd.DataFrame:
        return self._train

    # --- users -----------------------------------------------------------

    def user_ids(self) -> list[int]:
        """All user ids present in the train split, ascending."""
        return [int(uid) for uid in self._counts.index]

    def search_users(self, query: str, limit: int = 50) -> list[int]:
        """Filter users by exact numeric id match, falling back to a prefix scan."""
        query = (query or "").strip()
        if not query:
            return self.user_ids()[:limit]
        try:
            target = int(query)
            return [target] if target in self._counts.index else []
        except ValueError:
            return [uid for uid in self.user_ids() if str(uid).startswith(query)][:limit]

    def get_user_rating_count(self, user_id: int) -> int:
        """Number of ratings the user has in the train split (0 if unknown)."""
        return int(self._counts.get(user_id, 0))

    def get_user_profile(self, user_id: int) -> dict[str, Any]:
        """Build the profile dict shown in the UI for a user."""
        count = self.get_user_rating_count(user_id)
        return {
            "user_id": user_id,
            "rating_count": count,
            "activity_level": activity_level(count),
        }

    # --- movies ----------------------------------------------------------

    def get_movie(self, movie_id: int) -> dict[str, Any] | None:
        """Movie metadata for a given id, or None when unknown."""
        return self._movie_index.get(int(movie_id))

    def get_movie_title(self, movie_id: int) -> str:
        movie = self.get_movie(movie_id)
        return movie["title"] if movie else f"Movie {movie_id}"

    def get_movie_year(self, movie_id: int) -> int | None:
        movie = self.get_movie(movie_id)
        return movie["year"] if movie else None

    def get_movie_stats(self, movie_id: int) -> dict[str, Any]:
        """Rating statistics for a movie from the train split.

        Returns ``{"rating_count": int, "mean_rating": float | None}``. The
        rating count doubles as the popularity metric (mirrors the Popularity
        model's ranking signal). Unknown movies return a zero count.
        """
        rows = self._train[self._train["movieId"] == int(movie_id)]
        if rows.empty:
            return {"rating_count": 0, "mean_rating": None}
        return {
            "rating_count": int(len(rows)),
            "mean_rating": float(rows["rating"].mean()),
        }
