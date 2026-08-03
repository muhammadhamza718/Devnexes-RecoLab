"""Recommendation display component (Task-007).

Renders the recommendation rows with visual separation: rank, title, release
year, genres, a relevance score, confidence (hybrid model), and a plain-text
explanation of why each item was recommended.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.data_provider import DataProvider


def render_recommendations(
    provider: DataProvider,
    rows: list[dict[str, Any]],
    model_name: str,
    params: dict[str, Any],
) -> None:
    """Render stored recommendation rows, or a hint when none exist."""
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
        _render_row(rank, row)

    st.divider()
    st.caption("Explanations describe why each item was recommended by the selected model.")


def _render_row(rank: int, row: dict[str, Any]) -> None:
    """Render a single bordered recommendation card."""
    title = row.get("title") or "Unknown title"
    year = row.get("year")
    header = f"**{rank}. {title}**" if year is None else f"**{rank}. {title}** ({year})"

    with st.container(border=True):
        title_col, score_col = st.columns([4, 1])

        with title_col:
            st.markdown(header)
            genres = row.get("genres")
            if genres:
                st.caption(f"Genres: {genres}")

        with score_col:
            score = row.get("score")
            if score is not None:
                st.metric("Relevance", f"{score:.2f}")
            confidence = row.get("confidence")
            if confidence is not None:
                st.caption(f"Confidence: {confidence:.2f}")

        explanation = row.get("explanation")
        if explanation:
            st.markdown(f"*{explanation}*")
