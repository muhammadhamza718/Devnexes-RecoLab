"""Visual confidence indicators for recommendation rows (Task-014).

Renders colour-coded confidence scores, uncertainty messages, reliability
badges and threshold controls.  Consumes the payload produced by
:class:`ConfidenceCalculator.calculate_confidence` and respects the
session-level confidence threshold and visibility toggle managed by
:class:`SessionManager`.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.session_manager import SessionManager

# Category → (badge colour, background colour, icon).
_CATEGORY_STYLES: dict[str, tuple[str, str, str]] = {
    "high": ("#27ae60", "#e8f5e9", "●"),
    "medium": ("#f39c12", "#fff8e1", "●"),
    "low": ("#e74c3c", "#fce4ec", "●"),
}

# Uncertainty message thresholds.
_UNCERTAINTY_HIGH = 0.60
_UNCERTAINTY_MEDIUM = 0.30


def render_confidence_panel(
    confidence: dict[str, Any],
    movie_id: int,
) -> None:
    """Render the full confidence panel for one recommendation row.

    Parameters
    ----------
    confidence : dict
        Output of ``ConfidenceCalculator.calculate_confidence()``.
    movie_id : int
        Movie identifier (used for unique widget keys).
    """
    if not SessionManager.should_show_confidence_indicators():
        return

    threshold = SessionManager.get_confidence_threshold()
    score = confidence.get("overall_score", 0.0)
    category = confidence.get("category", "low")
    factors = confidence.get("factors", {})
    uncertainty = confidence.get("uncertainty", 1.0 - score)
    reliability = confidence.get("reliability", 0.5)

    # Apply threshold filter.
    if score < threshold:
        _render_below_threshold(movie_id, score, threshold)
        return

    _render_score_badge(score, category, movie_id)
    _render_uncertainty_message(uncertainty, movie_id)
    _render_reliability_indicator(reliability, movie_id)

    if factors:
        with st.expander("Confidence breakdown", key=f"conf-expand-{movie_id}"):
            _render_factor_breakdown(factors, movie_id)


def render_confidence_sidebar_controls() -> None:
    """Render the confidence threshold and toggle controls in the sidebar.

    Called once from ``streamlit_app.py`` inside ``with st.sidebar:``.
    """
    st.markdown("---")
    st.subheader("Confidence Settings")

    show = st.checkbox(
        "Show confidence indicators",
        value=SessionManager.should_show_confidence_indicators(),
        key="sidebar_show_confidence",
        help="Toggle the visual confidence display on recommendation cards.",
    )
    SessionManager.set_show_confidence_indicators(show)

    threshold = st.slider(
        "Confidence threshold",
        min_value=0.0,
        max_value=1.0,
        step=0.05,
        value=SessionManager.get_confidence_threshold(),
        key="sidebar_confidence_threshold",
        help="Recommendations below this score are flagged as low-confidence.",
    )
    SessionManager.set_confidence_threshold(threshold)


# ------------------------------------------------------------------
# Private helpers
# ------------------------------------------------------------------


def _render_score_badge(score: float, category: str, movie_id: int) -> None:
    """Colour-coded confidence score badge."""
    text_colour, bg_colour, icon = _CATEGORY_STYLES.get(
        category, _CATEGORY_STYLES["low"]
    )
    aria = f"Confidence {category}, score {score:.2f}"
    st.markdown(
        f'<div style="display:inline-block; padding:4px 12px; border-radius:6px; '
        f"background:{bg_colour}; color:{text_colour}; font-weight:600; "
        f'font-size:13px; margin-bottom:4px;" '
        f'role="status" aria-label="{aria}">'
        f"{icon} Confidence: {category.upper()} ({score:.2f})"
        f"</div>",
        unsafe_allow_html=True,
        key=f"conf-badge-{movie_id}",
    )


def _render_uncertainty_message(uncertainty: float, movie_id: int) -> None:
    """Human-readable uncertainty message below the badge."""
    if uncertainty >= _UNCERTAINTY_HIGH:
        msg = "Low data coverage — take this with a grain of salt."
    elif uncertainty >= _UNCERTAINTY_MEDIUM:
        msg = "Moderate confidence — some signals were limited."
    else:
        msg = None

    if msg:
        st.caption(
            f"*{msg}*",
            key=f"conf-uncert-{movie_id}",
        )


def _render_reliability_indicator(reliability: float, movie_id: int) -> None:
    """Small progress-bar-style reliability indicator."""
    colour = "#27ae60" if reliability >= 0.66 else "#f39c12" if reliability >= 0.33 else "#e74c3c"
    st.markdown(
        f'<div style="font-size:11px; color:#888; margin-bottom:2px;">'
        f"Reliability: {reliability:.0%}</div>",
        unsafe_allow_html=True,
        key=f"conf-rel-label-{movie_id}",
    )
    st.progress(min(max(reliability, 0.0), 1.0), key=f"conf-rel-bar-{movie_id}")


def _render_factor_breakdown(factors: dict[str, float], movie_id: int) -> None:
    """Tabular breakdown of per-factor confidence scores."""
    labels = {
        "user_activity": "User activity",
        "item_popularity": "Item popularity",
        "model_specific": "Model-specific",
        "model_agreement": "Model agreement",
        "data_quality": "Data quality",
    }
    for key, label in labels.items():
        value = factors.get(key)
        if value is not None:
            bar_colour = "#27ae60" if value >= 0.66 else "#f39c12" if value >= 0.33 else "#e74c3c"
            st.markdown(
                f'<div style="display:flex; align-items:center; gap:8px; margin-bottom:4px;">'
                f'<span style="width:120px; font-size:12px; color:#555;">{label}</span>'
                f'<div style="flex:1; background:#eee; border-radius:4px; height:8px;">'
                f'<div style="width:{value * 100:.0f}%; background:{bar_colour}; '
                f'height:100%; border-radius:4px;"></div></div>'
                f'<span style="font-size:12px; color:#333; width:40px; text-align:right;">'
                f"{value:.2f}</span></div>",
                unsafe_allow_html=True,
                key=f"conf-factor-{movie_id}-{key}",
            )


def _render_below_threshold(movie_id: int, score: float, threshold: float) -> None:
    """Render a muted indicator when confidence is below the threshold."""
    st.caption(
        f"Confidence {score:.2f} is below threshold ({threshold:.2f})",
        key=f"conf-below-{movie_id}",
    )
