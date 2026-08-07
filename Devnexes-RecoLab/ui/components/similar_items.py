"""Similar items ("More Like This") component (Task-005).

Computes similar items through :class:`ui.similarity_provider.SimilarityProvider`
and renders them as a responsive grid of text-based poster cards with the
similarity score attached. View state (``similar_items`` / ``current_view``)
is managed through the session manager so navigation between the
recommendations view and the similar-items view survives reruns.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.poster_display import render_poster
from ui.image_manager import ImageCacheManager
from ui.session_manager import SessionManager
from ui.similarity_provider import SimilarityProvider

#: Number of poster columns in the similar-items grid.
_GRID_COLUMNS = 4

_image_manager = ImageCacheManager()


def compute_similar_items(
    provider: SimilarityProvider,
    movie_id: int,
    k: int = 8,
    source_title: str | None = None,
) -> list[dict[str, Any]]:
    """Compute similar items, cache them in session state, and switch the view.

    Args:
        provider: Similarity provider to query.
        movie_id: Target movie ID.
        k: Number of similar items to request.
        source_title: Title of the movie the items are similar to, kept in
            session state so the "Because you liked X" caption survives reruns.

    Returns:
        The computed list of similar-item dicts.
    """
    items = provider.get_similar_items(movie_id, k=k)
    SessionManager.set_similar_items(items)
    SessionManager.set_similar_source_title(source_title)
    SessionManager.set_current_view("similar_items")
    return items


def render_similar_items(
    provider: SimilarityProvider,
    items: list[dict[str, Any]],
    source_title: str | None = None,
) -> None:
    """Render the similar-items grid, or an empty-state hint.

    Args:
        provider: Similarity provider (kept for a symmetric component API).
        items: Similar-item dicts from :func:`compute_similar_items`.
        source_title: Title of the movie the items are similar to.
    """
    heading = "More Like This"
    if source_title:
        heading += f" — because you liked {source_title}"
    st.subheader(heading, anchor=f"similar-items-{source_title or 'grid'}")

    if not items:
        st.info("No similar items found for this movie.")
        return

    st.markdown(
        f'<div role="region" aria-label="Similar movies to {source_title or "selected movie"}">',
        unsafe_allow_html=True,
    )
    cols = st.columns(_GRID_COLUMNS)
    for idx, item in enumerate(items):
        with cols[idx % _GRID_COLUMNS]:
            _render_item_card(item)

    st.markdown("</div>", unsafe_allow_html=True)


def _render_item_card(item: dict[str, Any]) -> None:
    """Render a single similar-item card (poster placeholder + score + label)."""
    movie_id = item.get("movie_id")
    if movie_id is None:
        return
    title = item.get("title") or f"Movie {movie_id}"
    poster = _image_manager.get_poster(int(movie_id), title=str(title))
    render_poster(item, poster, key=f"similar-poster-{movie_id}")

    similarity = item.get("similarity")
    if similarity is not None:
        st.caption(f"Similarity: {similarity:.2f}")

    year = item.get("year")
    label = f"{title} ({year})" if year else title
    st.markdown(f"**{label}**")
