"""Model selection component (Task-006).

Renders the radio buttons for the five models plus the live-adjustable
parameters: an alpha slider (0.0-1.0) for the hybrid model, a neighbourhood
size slider (k, 5-50) for the collaborative models, and an N picker
(5 / 10 / 20) that applies to every model.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.model_manager import ModelManager, MODEL_NAMES
from ui.session_manager import SessionManager

_N_OPTIONS = [5, 10, 20]


def render_model_selector() -> tuple[str, dict[str, Any]]:
    """Render the model picker and parameters; returns (model_name, params)."""
    st.sidebar.subheader("2. Select Model")

    previous = SessionManager.get_selected_model()
    index = MODEL_NAMES.index(previous) if previous in MODEL_NAMES else 0

    model_name = st.sidebar.radio(
        "Recommendation model",
        MODEL_NAMES,
        index=index,
        help="Popularity is the baseline; Hybrid blends content + collaborative.",
    )

    # Clear stale recommendations when the model changes.
    if model_name != previous:
        SessionManager.set_selected_model(model_name)
        SessionManager.clear_recommendations()

    params = dict(SessionManager.get_model_params())

    st.sidebar.caption("Model parameters")
    if model_name == "Hybrid":
        params["alpha"] = st.sidebar.slider(
            "Content weight (α)",
            min_value=0.0,
            max_value=1.0,
            value=float(params.get("alpha", 0.5)),
            step=0.05,
            help="α=1.0 → content only; α=0.0 → collaborative only.",
        )
    elif model_name in ("User-Based CF", "Item-Based CF"):
        params["k"] = st.sidebar.slider(
            "Neighbourhood size (k)",
            min_value=5,
            max_value=50,
            value=int(params.get("k", 10)),
            step=1,
            help="Number of similar users/items used per prediction.",
        )

    params["n"] = st.sidebar.selectbox(
        "Number of recommendations (N)",
        _N_OPTIONS,
        index=_N_OPTIONS.index(params.get("n", 10))
        if params.get("n", 10) in _N_OPTIONS
        else 1,
        help="How many recommendations to generate.",
    )

    SessionManager.set_model_params(params)
    return model_name, params
