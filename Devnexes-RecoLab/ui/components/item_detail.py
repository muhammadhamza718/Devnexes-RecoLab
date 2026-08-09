"""Item detail component (Task-014).

Renders a context panel for a single movie: metadata (title, year, genres),
color-coded genre tags, rating statistics and popularity metrics drawn from
the train split via :meth:`DataProvider.get_movie_stats`. Genre tags are
HTML-escaped before embedding so movie titles/genres cannot inject markup.
"""

from __future__ import annotations

import html
from typing import Any

import streamlit as st

try:
    import bleach
    BLEACH_AVAILABLE = True
except ImportError:
    BLEACH_AVAILABLE = False

from ui.data_provider import DataProvider

#: Deterministic genre -> color palette (falls back to a hash-based pick).
_GENRE_COLORS: dict[str, str] = {
    "Action": "#e74c3c",
    "Adventure": "#e67e22",
    "Animation": "#f1c40f",
    "Children": "#2ecc71",
    "Comedy": "#27ae60",
    "Crime": "#8e44ad",
    "Documentary": "#16a085",
    "Drama": "#3498db",
    "Fantasy": "#9b59b6",
    "Film-Noir": "#34495e",
    "Horror": "#c0392b",
    "IMAX": "#7f8c8d",
    "Musical": "#d35400",
    "Mystery": "#5b2c6f",
    "Romance": "#e84393",
    "Sci-Fi": "#2980b9",
    "Thriller": "#f39c12",
    "War": "#6c3483",
    "Western": "#a04000",
}
_FALLBACK_COLORS = ["#607d8b", "#795548", "#00897b", "#5e35b1", "#ef6c00"]


def render_genre_tags(genres: str) -> str:
    """Return HTML for color-coded genre tags, safe to embed in markdown.

    Args:
        genres: Pipe-separated genre string from the movie catalog.
    """
    tags = [g for g in (genres or "").split("|") if g]
    if not tags:
        return ""
    spans: list[str] = []
    for genre in tags:
        color = _GENRE_COLORS.get(
            genre,
            _FALLBACK_COLORS[hash(genre) % len(_FALLBACK_COLORS)]
        )
        # CRITICAL-4: Use bleach for stricter HTML sanitization if available
        if BLEACH_AVAILABLE:
            clean_genre = bleach.clean(
                genre, tags=[], attributes={}, strip=True
            )
        else:
            clean_genre = html.escape(genre)
        
        spans.append(
            f'<span style="background:{color}; color:#fff; font-size:10px; '
            f'padding:2px 8px; border-radius:10px; margin-right:4px;">'
            f"{clean_genre}</span>"
        )
    return " ".join(spans)


def render_item_detail(provider: DataProvider, movie_id: int) -> None:
    """Render the detail panel for a movie inside a bordered container.

    Args:
        provider: Data provider for metadata and rating statistics.
        movie_id: Target movie ID.
    """
    movie = provider.get_movie(movie_id)
    if movie is None:
        st.info(f"No catalog entry for movie {movie_id}.")
        return

    stats = provider.get_movie_stats(movie_id)
    title = str(movie.get("title") or f"Movie {movie_id}")
    year = movie.get("year")
    header = f"**{title}**" if year is None else f"**{title}** ({year})"

    with st.container():
        st.markdown(header)
        tags_html = render_genre_tags(str(movie.get("genres") or ""))
        if tags_html:
            st.markdown(tags_html, unsafe_allow_html=True)

        rating_count = int(stats.get("rating_count") or 0)
        mean_rating = stats.get("mean_rating")

        cols = st.columns(3)
        cols[0].metric("Ratings", rating_count)
        cols[1].metric(
            "Avg Rating", f"{mean_rating:.2f}" if mean_rating is not None else "—"
        )
        cols[2].metric(
            "Popularity",
            f"{rating_count:,}" if rating_count else "—",
            help="Number of ratings in the train split (higher = more popular)",
        )
