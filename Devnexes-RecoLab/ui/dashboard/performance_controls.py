"""Performance mode controls for the RecoLab dashboard (Task-016).

Provides a sidebar control to select the performance mode (``fast``,
``balanced``, ``rich``) and helper predicates so the main render loop can
skip expensive computations (confidence scores, enhanced explanations) when
the user prefers speed over detail.

Performance modes
-----------------
* **fast** — Skips confidence computation and enhanced explanations. The
  ``_generate()`` loop only builds rank-based rows and basic explanations.
* **balanced** (default) — Computes enhanced explanations but skips the
  per-rec confidence pipeline (the most expensive step, which runs all five
  models for each recommendation).
* **rich** — Full fidelity: confidence scores, enhanced explanations, and
  all dashboard detail panels.
"""

from __future__ import annotations

import streamlit as st

from ui.session_manager import SessionManager

#: Allowed performance mode values (matches ``DEFAULT_SESSION_STATE``).
ALLOWED_MODES: tuple[str, ...] = ("fast", "balanced", "rich")

#: Human-readable labels shown in the sidebar segmented control.
_MODE_LABELS: dict[str, str] = {
    "fast": "Fast",
    "balanced": "Balanced",
    "rich": "Rich",
}


def render_performance_sidebar_controls() -> None:
    """Render the performance mode selector inside ``with st.sidebar:``."""
    st.markdown("---")
    st.subheader("Performance Mode")

    current = SessionManager.get_performance_mode()
    if current not in ALLOWED_MODES:
        current = "balanced"

    selected = st.segmented_control(
        "Mode",
        options=ALLOWED_MODES,
        default=current,
        format_func=lambda m: _MODE_LABELS.get(m, m),
        key="sidebar_performance_mode",
        help=(
            "Fast: skip heavy computations for quicker response. "
            "Balanced: enhanced explanations but no confidence scores. "
            "Rich: full detail including confidence and explanations."
        ),
    )
    SessionManager.set_performance_mode(selected)


# ------------------------------------------------------------------
# Predicates consumed by the render loop
# ------------------------------------------------------------------


def should_compute_confidence() -> bool:
    """Return True when the current mode includes confidence computation."""
    return SessionManager.get_performance_mode() in ("balanced", "rich")


def should_compute_enhanced_explanations() -> bool:
    """Return True when the current mode includes enhanced explanations."""
    return SessionManager.get_performance_mode() in ("balanced", "rich")


def should_render_detail_panels() -> bool:
    """Return True when the current mode includes detail/expanders."""
    return SessionManager.get_performance_mode() == "rich"
