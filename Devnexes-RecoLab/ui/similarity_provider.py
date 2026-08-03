"""Similarity provider for the "More like this" feature (Task-004).

Per the Day 3 Afternoon SDD, this uses a Provider Pattern with multiple
backends: content similarity is tried first (``ContentModel.similar_items``),
item-item collaborative similarity (``ItemBasedCF._find_similar_items``) fills
any remaining slots, and a popularity-based fill is the last resort when the
model backends have no data for the target movie.
"""

from __future__ import annotations

from typing import Any

from recolab.interfaces import FeatureError

from ui.data_provider import DataProvider
from ui.model_manager import ModelManager

#: Canonical model names (see ui/model_manager.py).
CONTENT_MODEL = "Content"
ITEM_CF_MODEL = "Item-Based CF"


class SimilarityProvider:
    """Provides "more like this" items using the best available backend."""

    def __init__(
        self,
        model_manager: ModelManager,
        data_provider: DataProvider | None = None,
    ) -> None:
        self.model_manager = model_manager
        self.data_provider = data_provider or DataProvider()

    def get_similar_items(self, movie_id: int, k: int = 10) -> list[dict[str, Any]]:
        """Return up to ``k`` similar movies, enriched with metadata.

        Args:
            movie_id: Target movie ID.
            k: Maximum number of similar items to return.

        Returns:
            List of dicts with keys ``movie_id``, ``title``, ``year``,
            ``genres`` and ``similarity``, sorted by similarity descending.
        """
        results = self._content_similar(movie_id, k)
        results.extend(
            pair
            for pair in self._item_cf_similar(movie_id, k)
            if pair[0] not in {mid for mid, _ in results}
        )
        if not results:
            results = self._popular_fallback(movie_id, k)

        return [self._enrich(movie_id, score) for movie_id, score in results[:k]]

    # --- backends --------------------------------------------------------

    def _content_similar(self, movie_id: int, k: int) -> list[tuple[int, float]]:
        """Content-based similar items via ContentModel.similar_items."""
        try:
            model, _ = self.model_manager.get_model(CONTENT_MODEL)
        except (KeyError, ValueError):
            return []
        similar = getattr(model, "similar_items", None)
        if similar is None:
            return []
        try:
            pairs = similar(movie_id, k=k)
        except (FeatureError, KeyError, ValueError):
            return []
        return [(int(mid), float(score)) for mid, score in pairs]

    def _item_cf_similar(self, movie_id: int, k: int) -> list[tuple[int, float]]:
        """Item-item collaborative similar items via ItemBasedCF internals.

        ``_find_similar_items`` is not part of the public Recommender protocol,
        so it is guarded by hasattr; the SDD explicitly designates it as the
        CF backend for this provider.
        """
        try:
            model, _ = self.model_manager.get_model(ITEM_CF_MODEL)
        except (KeyError, ValueError):
            return []
        finder = getattr(model, "_find_similar_items", None)
        if finder is None:
            return []
        try:
            pairs = finder(movie_id)
        except (KeyError, ValueError, TypeError):
            return []
        return [(int(mid), float(score)) for mid, score in pairs[:k]]

    def _popular_fallback(self, movie_id: int, k: int) -> list[tuple[int, float]]:
        """Popularity-based fill when no similarity backend can serve the movie."""
        popularity = self.data_provider._train["movieId"].value_counts()
        exclude = {movie_id}
        return [
            (int(mid), float(score))
            for mid, score in popularity.items()
            if int(mid) not in exclude
        ][:k]

    # --- enrichment ------------------------------------------------------

    def _enrich(self, movie_id: int, similarity: float) -> dict[str, Any]:
        """Attach catalog metadata to a (movie_id, similarity) pair."""
        movie = self.data_provider.get_movie(movie_id) or {
            "movieId": movie_id,
            "title": f"Movie {movie_id}",
            "genres": "",
            "year": None,
        }
        return {
            "movie_id": int(movie["movieId"]),
            "title": str(movie.get("title") or f"Movie {movie_id}"),
            "year": movie.get("year"),
            "genres": str(movie.get("genres") or ""),
            "similarity": similarity,
        }
