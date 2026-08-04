"""Session state manager for the RecoLab Streamlit app (Task-001).

Centralizes access to ``st.session_state`` behind a small, extensible schema so
UI components never talk to the Streamlit runtime directly. New state keys are
declared in :data:`DEFAULT_SESSION_STATE` and are lazily initialised on first
access, which keeps the app working across Streamlit reruns and refreshes.

Schema (per the Day 3 Morning + Day 3 Afternoon implementation prompts):

    selected_user_id:        int | None   currently selected user
    selected_model:          str          one of the five model display names
    model_params:            dict         {"alpha": 0.0-1.0, "k": 5-50, "n": 5/10/20}
    recommendations:         list[dict]   rendered recommendation rows
    user_profile:            dict         {"user_id", "rating_count", "activity_level"}
    poster_cache:            dict         movie_id -> poster_url (placeholder)
    similar_items:           list[dict]   similar items for the selected movie
    similar_source_title:    str|None     title of the movie the items are similar to
    current_view:            str          "recommendations" or "similar_items"
    visualization_panel_open: bool        expandable panel state
    rating_statistics:       dict         cached per-user rating statistics
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
    # Day 3 Afternoon: rich UI state
    "poster_cache": {},  # movie_id -> poster_url
    "similar_items": [],  # Similar items for selected movie
    "similar_source_title": None,  # Title of the movie the items are similar to
    "current_view": "recommendations",  # "recommendations" or "similar_items"
    "visualization_panel_open": False,  # Expandable panel state
    "rating_statistics": {},  # Cached user statistics
    # Day 4 Morning: onboarding state (namespaced with onboarding_)
    "onboarding_active": False,  # Whether onboarding is currently active
    "onboarding_step": 0,  # Current wizard step (0, 1, 2)
    "onboarding_complete": False,  # Whether onboarding is completed
    "onboarding_timestamp": None,  # ISO timestamp of onboarding completion
    "selected_genres": [],  # Selected genre preferences
    "liked_movies": [],  # Selected liked movie IDs or metadata dicts
    "preference_weights": {},  # Genre preference weights
    "onboarding_preferences": {},  # Complete preference set
    "recommendation_preview": [],  # Preview recommendations
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

    # --- Day 3 Afternoon: rich UI accessors ------------------------------

    @staticmethod
    def get_poster_cache() -> dict[int, str]:
        return st.session_state.get("poster_cache") or {}

    @staticmethod
    def set_poster_for(movie_id: int, poster_url: str) -> None:
        cache = SessionManager.get_poster_cache()
        cache[movie_id] = poster_url
        st.session_state["poster_cache"] = cache

    @staticmethod
    def get_poster_for(movie_id: int) -> str | None:
        return SessionManager.get_poster_cache().get(movie_id)

    @staticmethod
    def get_similar_items() -> list[dict[str, Any]]:
        return st.session_state.get("similar_items") or []

    @staticmethod
    def set_similar_items(items: list[dict[str, Any]]) -> None:
        st.session_state["similar_items"] = items

    @staticmethod
    def clear_similar_items() -> None:
        st.session_state["similar_items"] = []

    @staticmethod
    def get_similar_source_title() -> str | None:
        return st.session_state.get("similar_source_title")

    @staticmethod
    def set_similar_source_title(title: str | None) -> None:
        st.session_state["similar_source_title"] = title

    @staticmethod
    def get_current_view() -> str:
        return st.session_state.get("current_view") or "recommendations"

    @staticmethod
    def set_current_view(view: str) -> None:
        st.session_state["current_view"] = view

    @staticmethod
    def is_visualization_panel_open() -> bool:
        return bool(st.session_state.get("visualization_panel_open"))

    @staticmethod
    def set_visualization_panel_open(open_: bool) -> None:
        st.session_state["visualization_panel_open"] = open_

    @staticmethod
    def get_rating_statistics() -> dict[str, Any]:
        return st.session_state.get("rating_statistics") or {}

    @staticmethod
    def set_rating_statistics(stats: dict[str, Any]) -> None:
        st.session_state["rating_statistics"] = stats

    # --- Day 4 Morning: onboarding accessors ------------------------------

    @staticmethod
    def is_onboarding_active() -> bool:
        return bool(st.session_state.get("onboarding_active"))

    @staticmethod
    def set_onboarding_active(active: bool) -> None:
        st.session_state["onboarding_active"] = active

    @staticmethod
    def get_onboarding_step() -> int:
        return st.session_state.get("onboarding_step") or 0

    @staticmethod
    def set_onboarding_step(step: int) -> None:
        st.session_state["onboarding_step"] = step

    @staticmethod
    def is_onboarding_complete() -> bool:
        return bool(st.session_state.get("onboarding_complete"))

    @staticmethod
    def set_onboarding_complete(complete: bool) -> None:
        st.session_state["onboarding_complete"] = complete

    @staticmethod
    def get_onboarding_timestamp() -> str | None:
        return st.session_state.get("onboarding_timestamp")

    @staticmethod
    def set_onboarding_timestamp(timestamp: str | None) -> None:
        st.session_state["onboarding_timestamp"] = timestamp

    @staticmethod
    def get_selected_genres() -> list[str]:
        return st.session_state.get("selected_genres") or []

    @staticmethod
    def set_selected_genres(genres: list[str]) -> None:
        st.session_state["selected_genres"] = genres

    @staticmethod
    def get_liked_movies() -> list[Any]:
        return st.session_state.get("liked_movies") or []

    @staticmethod
    def set_liked_movies(movies: list[Any]) -> None:
        st.session_state["liked_movies"] = movies

    @staticmethod
    def get_preference_weights() -> dict[str, float]:
        return st.session_state.get("preference_weights") or {}

    @staticmethod
    def set_preference_weights(weights: dict[str, float]) -> None:
        st.session_state["preference_weights"] = weights

    @staticmethod
    def get_onboarding_preferences() -> dict[str, Any]:
        return st.session_state.get("onboarding_preferences") or {}

    @staticmethod
    def set_onboarding_preferences(prefs: dict[str, Any]) -> None:
        st.session_state["onboarding_preferences"] = prefs

    @staticmethod
    def get_recommendation_preview() -> list[dict[str, Any]]:
        return st.session_state.get("recommendation_preview") or []

    @staticmethod
    def set_recommendation_preview(preview: list[dict[str, Any]]) -> None:
        st.session_state["recommendation_preview"] = preview

    @staticmethod
    def reset_onboarding_state() -> None:
        """Reset all onboarding-related session state keys to defaults."""
        st.session_state["onboarding_active"] = True
        st.session_state["onboarding_step"] = 0
        st.session_state["onboarding_complete"] = False
        st.session_state["onboarding_timestamp"] = None
        st.session_state["selected_genres"] = []
        st.session_state["liked_movies"] = []
        st.session_state["preference_weights"] = {}
        st.session_state["onboarding_preferences"] = {}
        st.session_state["recommendation_preview"] = []

