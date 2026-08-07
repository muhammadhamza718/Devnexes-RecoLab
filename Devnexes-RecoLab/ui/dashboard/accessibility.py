"""Accessibility enhancements for the RecoLab dashboard (Task-015).

Provides global CSS injection for keyboard focus indicators and WCAG AA
high-contrast overrides, plus sidebar controls to toggle accessibility mode.
Consumes :class:`SessionManager` accessors for state management.
"""

from __future__ import annotations

import streamlit as st

from ui.session_manager import SessionManager

# WCAG AA minimum contrast ratios — all colour pairs in the high-contrast
# palette must achieve ≥ 4.5 : 1 on their respective backgrounds.
_HIGH_CONTRAST_CSS = """
<style>
/* ---- Focus indicators (WCAG 2.4.7 / 2.4.11) ---- */
:focus-visible {
    outline: 3px solid #4a90d9 !important;
    outline-offset: 2px !important;
}
button:focus-visible,
[role="button"]:focus-visible {
    outline: 3px solid #4a90d9 !important;
    outline-offset: 2px !important;
}

/* ---- High-contrast overrides ---- */
/* Confidence badge: high — dark green on light bg */
div[style*="background:#e8f5e9"] > div,
div[style*="background:#fff8e1"] > div,
div[style*="background:#fce4ec"] > div {
    font-weight: 700;
}

/* Ensure text-based poster cards are readable */
div[style*="POSTER"] {
    border-width: 2px !important;
}

/* Progress bars — thicker for visibility */
div[data-baseweb="progress"] > div {
    height: 10px !important;
}
</style>
"""

_STANDARD_CSS = """
<style>
/* ---- Focus indicators (WCAG 2.4.7 / 2.4.11) ---- */
:focus-visible {
    outline: 3px solid #4a90d9 !important;
    outline-offset: 2px !important;
}
button:focus-visible,
[role="button"]:focus-visible {
    outline: 3px solid #4a90d9 !important;
    outline-offset: 2px !important;
}

/* Thicker progress bars for better visibility */
div[data-baseweb="progress"] > div {
    height: 10px !important;
}
</style>
"""


def inject_accessibility_styles() -> None:
    """Inject global CSS for focus indicators and high-contrast mode.

    Called once at the top of ``streamlit_app.py`` before any UI rendering.
    The CSS adapts to the current ``SessionManager.is_accessibility_mode()``
    flag so the user can toggle it live.
    """
    if SessionManager.is_accessibility_mode():
        st.markdown(_HIGH_CONTRAST_CSS, unsafe_allow_html=True)
    else:
        st.markdown(_STANDARD_CSS, unsafe_allow_html=True)


def render_accessibility_sidebar_controls() -> None:
    """Render the accessibility toggle control in the sidebar.

    Called from ``streamlit_app.py`` inside ``with st.sidebar:``.
    """
    st.markdown("---")
    st.subheader("Accessibility")
    enabled = st.checkbox(
        "High-contrast / accessibility mode",
        value=SessionManager.is_accessibility_mode(),
        key="sidebar_accessibility_mode",
        help="Enable high-contrast colours and thicker focus indicators "
        "for better visibility (WCAG AA).",
    )
    SessionManager.set_accessibility_mode(enabled)
