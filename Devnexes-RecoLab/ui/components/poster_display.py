"""Poster display component (Task-002).

Renders movie posters as text-based placeholder cards (the movie title styled
as a poster, per the Day 3 Afternoon implementation prompt). The component
accepts a poster representation from :class:`ui.image_manager.ImageCacheManager`:
values prefixed with ``placeholder:`` render as a styled title card; real URLs
(once a TMDB-backed pipeline is added) render via ``st.image``. Titles are
HTML-escaped before embedding so user-influenced data cannot inject markup.
"""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

from ui.image_manager import PLACEHOLDER_PREFIX

#: Poster card background gradient (matches the app's dark Streamlit theme).
_CARD_STYLE = """
    aspect-ratio: 2 / 3;
    display: flex; flex-direction: column;
    align-items: center; justify-content: center;
    background: linear-gradient(160deg, #2e3348 0%, #1e2233 70%);
    border: 1px solid #4a4f6a; border-radius: 8px;
    padding: 8px 6px; text-align: center;
"""


def render_poster(
    movie: dict[str, Any],
    poster: str,
    key: str | None = None,
) -> None:
    """Render a single movie poster.

    Args:
        movie: Movie dict with at least ``{"movieId", "title"}``.
        poster: Poster representation from :meth:`ImageCacheManager.get_poster`.
        key: Optional unique widget key suffix for the placeholder card (use
            when the same movie appears multiple times on one page).
    """
    if not poster.startswith(PLACEHOLDER_PREFIX):
        # Real image URL path (reserved for a future TMDB-backed pipeline).
        st.image(poster, use_container_width=True)
        return

    title = movie.get("title") or poster[len(PLACEHOLDER_PREFIX):] or "Unknown title"
    year = movie.get("year")
    _render_text_card(title, year, key)


def _render_text_card(
    title: str,
    year: int | None = None,
    key: str | None = None,
) -> None:
    """Render the text-based placeholder poster card for a movie."""
    escaped_title = html.escape(str(title))
    year_html = (
        f'<span style="font-size:10px; color:#a6accd; margin-top:4px;">'
        f"{html.escape(str(year))}</span>"
        if year is not None
        else ""
    )
    aria_label = f"Poster for {escaped_title}"
    if year is not None:
        aria_label += f", {year}"
    st.markdown(
        f"""<div style="{_CARD_STYLE}" role="img" aria-label="{aria_label}">
            <span style="font-weight:600; color:#f2f3f7; font-size:12px;
                         line-height:1.35; word-break:break-word;">{escaped_title}</span>
            {year_html}
            <span style="font-size:9px; color:#6c7291; margin-top:6px;">POSTER</span>
        </div>""",
        unsafe_allow_html=True,
    )
