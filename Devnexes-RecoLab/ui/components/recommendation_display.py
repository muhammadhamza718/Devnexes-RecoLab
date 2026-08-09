"""Recommendation display component (Task-007).

Renders the recommendation rows with visual separation: a poster thumbnail
(Day 3 Afternoon, Task-003), rank, title, release year, genres, a relevance
score, confidence (hybrid model), and a plain-text explanation of why each
item was recommended.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.components.item_detail import render_item_detail
from ui.dashboard.confidence_indicators import render_confidence_panel
from ui.dashboard.enhanced_explanations import render_enhanced_explanation
from ui.components.poster_display import render_poster
from ui.components.similar_items import compute_similar_items
from ui.data_provider import DataProvider
from ui.image_manager import ImageCacheManager
from ui.session_manager import SessionManager
from ui.similarity_provider import SimilarityProvider

#: Module-level manager so poster lookups hit the session-state cache.
_image_manager = ImageCacheManager()


def render_recommendations(
    provider: DataProvider,
    rows: list[dict[str, Any]],
    model_name: str,
    params: dict[str, Any],
    similarity_provider: SimilarityProvider | None = None,
) -> None:
    """Render stored recommendation rows, or a hint when none exist.

    Args:
        provider: Data provider for movie metadata.
        rows: Stored recommendation rows from session state.
        model_name: Display name of the active model.
        params: Active model parameters (``n`` etc.).
        similarity_provider: When given, each row gets a "More like this"
            button that switches to the similar-items view (Task-006).
    """
    st.subheader("Recommendations")

    if not rows:
        st.info("Select a user and a model, then click **Generate Recommendations**.")
        return

    n = params.get("n", 10)
    st.caption(
        f"Showing {len(rows)} recommendation(s) · model: **{model_name}** · "
        f"relevance is rank-based (1.0 = top pick)"
    )

    for rank, row in enumerate(rows, start=1):
        _render_row(rank, row, provider, similarity_provider)

    st.divider()
    st.caption("Explanations describe why each item was recommended by the selected model.")


def _render_row(
    rank: int,
    row: dict[str, Any],
    provider: DataProvider,
    similarity_provider: SimilarityProvider | None = None,
) -> None:
    """Render a single bordered recommendation card with a poster thumbnail."""
    title = row.get("title") or "Unknown title"
    year = row.get("year")
    header = f"**{rank}. {title}**" if year is None else f"**{rank}. {title}** ({year})"

    poster_col, title_col, score_col = st.columns([1, 4, 1])

    with poster_col:
        _render_poster_thumbnail(row)

    with title_col:
        st.markdown(header)
        genres = row.get("genres")
        if genres:
            st.caption(f"Genres: {genres}")
        _render_more_like_this(rank, row, similarity_provider)

    with score_col:
        score = row.get("score")
        if score is not None:
            _render_relevance(score)
        confidence = row.get("confidence")
        if confidence is not None:
            st.caption(f"Confidence: {confidence:.2f}")

        explanation = row.get("explanation")
        if explanation:
            st.markdown(f"*{explanation}*")

        movie_id = row.get("movie_id")

        # Task-014: confidence indicators panel
        confidence_data = SessionManager.get_confidence_data()
        if movie_id is not None:
            confidence = confidence_data.get(int(movie_id))
            if confidence is not None:
                render_confidence_panel(confidence, int(movie_id))
            enhanced = SessionManager.get_enhanced_explanations().get(int(movie_id))
            if enhanced:
                render_enhanced_explanation(enhanced, int(movie_id))

        _render_row_detail(provider, row)


def _render_relevance(score: float) -> None:
    """Render the relevance score with color coding and a progress bar.

    Score tiers: high (>= 0.66) green, mid (>= 0.33) amber, low red. The
    progress bar doubles as the "progress indicator" called for by Task-013.
    """
    color = "#27ae60" if score >= 0.66 else "#f39c12" if score >= 0.33 else "#e74c3c"
    st.markdown(
        f'<div style="font-weight:600; color:{color}; font-size:14px;">'
        f"Relevance {score:.2f}</div>",
        unsafe_allow_html=True,
    )
    st.progress(min(max(score, 0.0), 1.0))


def _render_more_like_this(
    rank: int,
    row: dict[str, Any],
    similarity_provider: SimilarityProvider | None,
) -> None:
    """Render the "More like this" action for a recommendation row."""
    if similarity_provider is None:
        return
    movie_id = row.get("movie_id")
    if movie_id is None:
        return
    if st.button(
        "More like this",
        key=f"widget_similar_btn_{rank}",
        type="tertiary",
        help="Show similar movies for this title",
    ):
        compute_similar_items(
            similarity_provider,
            int(movie_id),
            k=8,
            source_title=str(row.get("title") or ""),
        )
        st.rerun()


def _render_poster_thumbnail(row: dict[str, Any]) -> None:
    """Render the poster thumbnail column for a recommendation row."""
    movie_id = row.get("movie_id")
    if movie_id is None:
        return
    poster = _image_manager.get_poster(
        int(movie_id),
        title=str(row.get("title") or ""),
    )
    # Convert row to movie dict format expected by render_poster
    movie_dict = {
        "movieId": movie_id,
        "title": row.get("title", ""),
        "year": row.get("year")
    }
    render_poster(movie_dict, poster, key=f"widget_rec_poster_{movie_id}")


def _render_row_detail(provider: DataProvider, row: dict[str, Any]) -> None:
    """Render the collapsible item-detail panel for a recommendation row.

    The detail panel (Task-014) lives in a collapsed expander so it does not
    dominate the recommendation list; opening it shows the movie metadata,
    color-coded genre tags and train-split rating statistics.
    """
    movie_id = row.get("movie_id")
    if movie_id is None:
        return
    with st.expander("Movie details", key=f"widget_rec_detail_{movie_id}"):
        render_item_detail(provider, int(movie_id))
