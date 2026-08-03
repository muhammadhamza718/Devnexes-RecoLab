"""Session state manager for the RecoLab Streamlit app (Task-001).

Centralizes access to ``st.session_state`` behind a small, extensible schema so
UI components never talk to the Streamlit runtime directly. New state keys are
declared in :data:`DEFAULT_SESSION_STATE` and are lazily initialised on first
access, which keeps the app working across Streamlit reruns and refreshes.

Schema (per the Day 3 Morning implementation prompt):

    selected_user_id: int | None   currently selected user
    selected_model:    str          one of the five model display names
    model_params:      dict         {"alpha": 0.0-1.0, "k": 5-50, "n": 5/10/20}
    recommendations:   list[dict]   rendered recommendation rows
    user_profile:      dict         {"user_id", "rating_count", "activity_level"}
"""

from __future__ import annotations

from typing import Any

import streamlit as st

# Extensible session-state schema. Any new key added here is guaranteed to
# exist (with a sane default) after SessionManager.ensure_initialized().
DEFAULT_SESSION_STATE: dict[str, Any] = {
    "selected_user_id": None,
    "selected_model": "Hybrid",
    "model_params": {"alpha": 0.5, "k": 10, "n": 10},
    "recommendations": [],
    "user_profile": {},
}


class SessionManager:
    """Thin facade over ``st.session_state`` with a fixed, extensible schema."""

    @staticmethod
    def ensure_initialized() -> None:
        """Populate any missing session keys with their defaults."""
        for key, default in DEFAULT_SESSION_STATE.items():
            if key not in st.session_state:
                st.session_state[key] = default

    @staticmethod
    def get(key: str, default: Any = None) -> Any:
        """Read a session value, initialising the schema first."""
        SessionManager.ensure_initialized()
        return st.session_state.get(key, default)

    @staticmethod
    def set(key: str, value: Any) -> None:
        """Write a session value, initialising the schema first."""
        SessionManager.ensure_initialized()
        st.session_state[key] = value

    # --- typed accessors -------------------------------------------------

    @staticmethod
    def get_selected_user_id() -> int | None:
        return st.session_state.get("selected_user_id")

    @staticmethod
    def set_selected_user_id(user_id: int | None) -> None:
        st.session_state["selected_user_id"] = user_id

    @staticmethod
    def get_selected_model() -> str:
        return st.session_state.get("selected_model")

    @staticmethod
    def set_selected_model(name: str) -> None:
        st.session_state["selected_model"] = name

    @staticmethod
    def get_model_params() -> dict[str, Any]:
        return st.session_state.get("model_params") or {}

    @staticmethod
    def set_model_params(params: dict[str, Any]) -> None:
        st.session_state["model_params"] = params

    @staticmethod
    def get_recommendations() -> list[dict[str, Any]]:
        return st.session_state.get("recommendations") or []

    @staticmethod
    def set_recommendations(rows: list[dict[str, Any]]) -> None:
        st.session_state["recommendations"] = rows

    @staticmethod
    def clear_recommendations() -> None:
        st.session_state["recommendations"] = []

    @staticmethod
    def get_user_profile() -> dict[str, Any]:
        return st.session_state.get("user_profile") or {}

    @staticmethod
    def set_user_profile(profile: dict[str, Any]) -> None:
        st.session_state["user_profile"] = profile
