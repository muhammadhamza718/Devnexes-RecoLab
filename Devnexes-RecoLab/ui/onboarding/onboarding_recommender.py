"""Onboarding recommender bridging onboarding preferences with backend ColdStartHandler (Task-008)."""

from __future__ import annotations

from typing import Any
import streamlit as st

from ui.data_provider import DataProvider, extract_year
from ui.model_manager import ModelManager


class OnboardingRecommender:
    """Generates recommendations for new cold-start users based on onboarding preferences."""

    def __init__(
        self,
        data_provider: DataProvider | None = None,
        model: Any | None = None,
        model_manager: ModelManager | None = None,
    ) -> None:
        self._dp = data_provider or DataProvider()
        self._model = model
        self._model_mgr = model_manager or ModelManager()

    def _get_cold_start_model(self) -> Any:
        """Fetch pre-loaded Content or Hybrid model capable of handling cold-start."""
        if self._model is not None:
            return self._model

        # Prefer Content model for pure metadata/genre cold start, fallback to Hybrid
        try:
            model, _ = self._model_mgr.get_model("Content")
            if hasattr(model, "recommend_cold_start"):
                return model
        except Exception:
            pass

        try:
            model, _ = self._model_mgr.get_model("Hybrid")
            if hasattr(model, "recommend_cold_start"):
                return model
        except Exception:
            pass

        return None

    def get_preview_recommendations(
        self, preferences: dict[str, Any], top_n: int = 10
    ) -> list[dict[str, Any]]:
        """Generate formatted movie recommendations from cold-start preferences."""
        genres = preferences.get("genres", [])
        if not isinstance(genres, list):
            genres = []

        raw_liked = preferences.get("liked_movies", [])
        liked_ids: list[int] = []
        for item in raw_liked:
            if isinstance(item, dict) and "movieId" in item:
                liked_ids.append(int(item["movieId"]))
            elif isinstance(item, (int, str)) and str(item).isdigit():
                liked_ids.append(int(item))

        model = self._get_cold_start_model()

        rec_movie_ids: list[int] = []

        if model is not None and (genres or liked_ids):
            try:
                rec_movie_ids = model.recommend_cold_start(
                    genres=genres,
                    liked_movie_ids=liked_ids,
                    k=top_n,
                )
            except Exception as err:
                st.warning(f"Backend cold-start model notice: {err}")

        # Fallback heuristic if backend model returned empty or unavailable
        if not rec_movie_ids:
            rec_movie_ids = self._fallback_cold_start(genres, liked_ids, top_n)

        # Enrich movie metadata for UI display
        results = []
        for rank, mid in enumerate(rec_movie_ids, 1):
            movie = self._dp.get_movie(mid)
            if not movie:
                continue
            stats = self._dp.get_movie_stats(mid)
            results.append({
                "rank": rank,
                "movieId": mid,
                "title": str(movie["title"]),
                "genres": str(movie["genres"]),
                "year": extract_year(str(movie["title"])),
                "mean_rating": stats.get("mean_rating"),
                "rating_count": stats.get("rating_count", 0),
                "score": max(0.95 - (rank * 0.05), 0.50),  # UI confidence score
            })

        return results[:top_n]

    def _fallback_cold_start(
        self, genres: list[str], liked_ids: list[int], top_n: int
    ) -> list[int]:
        """Fallback recommendation when model fails or yields no items."""
        movies_df = self._dp.movies
        liked_set = set(liked_ids)

        if genres:
            # Match movies containing any of the selected genres
            pattern = "|".join([g for g in genres if g])
            mask = movies_df["genres"].str.contains(pattern, case=False, na=False, regex=True)
            candidate_df = movies_df[mask]
        else:
            candidate_df = movies_df

        # Exclude already liked movies
        candidate_ids = []
        for row in candidate_df.itertuples():
            movie_id = None
            if hasattr(row, 'movieId'):
                try:
                    movie_id = int(row.movieId)  # type: ignore[arg-type]
                except (ValueError, TypeError):
                    continue
            if movie_id is not None and movie_id not in liked_set:
                candidate_ids.append(movie_id)

        # Top popular from candidates
        stats = [
            (mid, self._dp.get_movie_stats(mid).get("rating_count", 0))
            for mid in candidate_ids
        ]
        stats.sort(key=lambda x: x[1], reverse=True)

        return [mid for mid, _ in stats[:top_n]]
