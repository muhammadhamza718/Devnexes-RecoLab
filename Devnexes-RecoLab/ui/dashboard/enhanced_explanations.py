"""Enhanced explanation panels for the RecoLab dashboard (Feature 008, Tasks 010-012).

Renders the payload from :class:`ExplanationEnhancer` inside a collapsible
expander per recommendation row. The payload is detail-level agnostic — it
always carries the base explanation, feature importance, contribution
breakdown and confidence score — and this panel decides how much to reveal
based on the selected detail level:

    brief    -> base explanation only
    detailed -> + feature-importance bar chart (Task-011)
    expert   -> + contribution-breakdown pie chart with percentages (Task-012)

Every section degrades to a readable empty state when the enhancer had no
data to work with (Task-009: "Fallbacks work for missing data").
"""

from __future__ import annotations

from typing import Any

import pandas as pd
import plotly.express as px
import streamlit as st

from ui.session_manager import SessionManager

_DETAIL_LEVELS: tuple[str, ...] = ("brief", "detailed", "expert")

#: Contribution-breakdown key -> human label + slice colour (Task-012).
_BREAKDOWN_SLICES: dict[str, str] = {
    "content_contribution": "Content",
    "collaborative_contribution": "Collaborative",
    "popularity_contribution": "Popularity",
    "confidence_contribution": "Confidence",
}

_PIE_COLORS = {
    "Content": "#1f77b4",
    "Collaborative": "#ff7f0e",
    "Popularity": "#2ca02c",
    "Confidence": "#9467bd",
}


def render_enhanced_explanation(enhanced: dict[str, Any], movie_id: int) -> None:
    """Render the collapsible "why this recommendation?" panel for one row."""
    if not enhanced:
        return
    with st.expander("Why this recommendation?", key=f"rec-enhanced-{movie_id}"):
        _render_detail_control(movie_id)

        base = enhanced.get("base_explanation")
        if base:
            st.markdown(f"*{base}*")

        level = SessionManager.get_explanation_detail_level()
        if level in ("detailed", "expert"):
            _render_feature_importance(enhanced.get("feature_importance") or {}, movie_id)

        if level == "expert":
            _render_contribution_breakdown(enhanced.get("contribution_breakdown") or {}, movie_id)
            confidence = enhanced.get("confidence_score")
            if confidence is not None:
                st.caption(f"Confidence score: **{float(confidence):.2f}**")


def _render_detail_control(movie_id: int) -> None:
    """Segmented control choosing how much of the explanation to reveal."""
    current = SessionManager.get_explanation_detail_level()
    if current not in _DETAIL_LEVELS:
        current = "detailed"
    level = st.segmented_control(
        "Detail level",
        options=list(_DETAIL_LEVELS),
        default=current,
        key=f"enhanced_detail_level_{movie_id}",
        help="How much of the explanation to reveal: base text, feature "
        "importance, or the full contribution breakdown.",
    )
    SessionManager.set_explanation_detail_level(level)


def _render_feature_importance(importance: dict[str, float], movie_id: int) -> None:
    """Horizontal bar chart of per-feature weights (Task-011)."""
    st.markdown("##### Feature importance")
    if not importance:
        st.caption("No feature-importance data is available for this model.")
        return

    df = pd.DataFrame(
        [{"Feature": label, "Weight": float(value)} for label, value in importance.items()]
    )
    df = df.sort_values("Weight", ascending=True)
    fig = px.bar(
        df,
        x="Weight",
        y="Feature",
        orientation="h",
        labels={"Weight": "Relative weight", "Feature": ""},
        height=max(180, 34 * len(df)),
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), showlegend=False)
    st.plotly_chart(fig, use_container_width=True, key=f"feature_importance_{movie_id}")
    st.caption("Weights are normalised to sum to 1: genres are IDF-weighted, "
               "CF contributions combine similarity and rating strength.")


def _render_contribution_breakdown(breakdown: dict[str, float], movie_id: int) -> None:
    """Pie chart of content / collaborative / popularity contributions (Task-012)."""
    st.markdown("##### Contribution breakdown")
    slices = [
        (_BREAKDOWN_SLICES[key], round(float(breakdown.get(key, 0.0)), 4))
        for key in _BREAKDOWN_SLICES
    ]
    df = pd.DataFrame(slices, columns=["Source", "Share"])
    df = df[df["Share"] > 0]
    if df.empty:
        st.caption("No contribution data is available for this model.")
        return

    fig = px.pie(
        df,
        names="Source",
        values="Share",
        color="Source",
        color_discrete_map=_PIE_COLORS,
        hole=0.35,
    )
    fig.update_traces(
        textposition="inside",
        textinfo="percent+label",
        hovertemplate="%{label}: %{value:.2f} (%{percent})",
    )
    fig.update_layout(margin=dict(l=0, r=0, t=10, b=0), legend_title_text="Signal")
    st.plotly_chart(fig, use_container_width=True, key=f"contribution_breakdown_{movie_id}")
    st.caption("How much each signal contributed to this recommendation. "
               "Click legend entries to toggle slices.")
