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
    "onboarding_selected_genres": [],  # Selected genre preferences
    "onboarding_liked_movies": [],  # Selected liked movie IDs or metadata dicts
    "onboarding_preference_weights": {},  # Genre preference weights
    "onboarding_preferences": {},  # Complete preference set
    "onboarding_recommendation_preview": [],  # Preview recommendations
    "onboarding_search_history": [],  # Search timestamps for rate limiting
    # Day 4 Afternoon: advanced dashboard & polish state (namespaced with dashboard_)
    "dashboard_active": False,  # Whether the metrics dashboard is active
    "show_model_comparison": False,  # Whether the side-by-side comparison view is active
    "selected_k_value": 10,  # Evaluation k (one of 5/10/20)
    "dashboard_metrics": {},  # Cached model metrics (ModelMetrics dicts by model)
    "comparison_data": {},  # Model comparison engine output
    "selected_models_for_comparison": [],  # Models selected for side-by-side comparison
    "show_agreement_analysis": True,  # Toggle Jaccard agreement analysis
    "explanation_detail_level": "detailed",  # "brief" | "detailed"
    "enhanced_explanations": {},  # movie_id -> enhanced explanation payload
    "confidence_threshold": 0.5,  # 0.0-1.0 confidence cutoff
    "show_confidence_indicators": True,  # Toggle confidence display
    "confidence_data": {},  # movie_id -> ConfidenceScore factors
    "accessibility_mode": False,  # WCAG-friendly high-contrast mode
    "performance_mode": "balanced",  # "fast" | "balanced" | "rich"
    # Day 6: deployment & production readiness state (namespaced with deployment_)
    "deployment_environment": "local",  # "local" | "production" | "streamlit_cloud"
    "deployment_health_status": "healthy",  # "healthy" | "degraded" | "unhealthy"
    "deployment_feedback_history": [],  # List of user feedback dicts
    "deployment_active_operations": {},  # operation_id -> status dict
    "deployment_error_count": 0,  # Count of logged user-facing errors
    "deployment_last_health_check": None,  # Timestamp of last health check
    # UI state keys
    "show_feedback_history": False,  # Whether to show feedback history view
    "last_health_check_result": None,  # Last health check result dict
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
    def get_onboarding_selected_genres() -> list[str]:
        return st.session_state.get("onboarding_selected_genres") or []

    @staticmethod
    def set_onboarding_selected_genres(genres: list[str]) -> None:
        st.session_state["onboarding_selected_genres"] = genres

    @staticmethod
    def get_onboarding_liked_movies() -> list[Any]:
        return st.session_state.get("onboarding_liked_movies") or []

    @staticmethod
    def set_onboarding_liked_movies(movies: list[Any]) -> None:
        st.session_state["onboarding_liked_movies"] = movies

    @staticmethod
    def get_onboarding_preference_weights() -> dict[str, float]:
        return st.session_state.get("onboarding_preference_weights") or {}

    @staticmethod
    def set_onboarding_preference_weights(weights: dict[str, float]) -> None:
        st.session_state["onboarding_preference_weights"] = weights

    @staticmethod
    def get_onboarding_recommendation_preview() -> list[dict[str, Any]]:
        return st.session_state.get("onboarding_recommendation_preview") or []

    @staticmethod
    def set_onboarding_recommendation_preview(preview: list[dict[str, Any]]) -> None:
        st.session_state["onboarding_recommendation_preview"] = preview

    @staticmethod
    def get_onboarding_search_history() -> list[float]:
        return st.session_state.get("onboarding_search_history") or []

    @staticmethod
    def set_onboarding_search_history(history: list[float]) -> None:
        st.session_state["onboarding_search_history"] = history

    @staticmethod
    def reset_onboarding_state() -> None:
        """Reset all onboarding-related session state keys to defaults."""
        st.session_state["onboarding_active"] = True
        st.session_state["onboarding_step"] = 0
        st.session_state["onboarding_complete"] = False
        st.session_state["onboarding_timestamp"] = None
        st.session_state["onboarding_selected_genres"] = []
        st.session_state["onboarding_liked_movies"] = []
        st.session_state["onboarding_preference_weights"] = {}
        st.session_state["onboarding_preferences"] = {}
        st.session_state["onboarding_recommendation_preview"] = []
        st.session_state["onboarding_search_history"] = []

    # --- Day 4 Afternoon: dashboard & polish accessors ---------------------

    @staticmethod
    def is_dashboard_active() -> bool:
        return bool(st.session_state.get("dashboard_active"))

    @staticmethod
    def set_dashboard_active(active: bool) -> None:
        st.session_state["dashboard_active"] = active

    @staticmethod
    def is_model_comparison_active() -> bool:
        return bool(st.session_state.get("show_model_comparison"))

    @staticmethod
    def set_model_comparison_active(active: bool) -> None:
        st.session_state["show_model_comparison"] = active

    @staticmethod
    def get_selected_k_value() -> int:
        return int(st.session_state.get("selected_k_value") or 10)

    @staticmethod
    def set_selected_k_value(k: int) -> None:
        st.session_state["selected_k_value"] = k

    @staticmethod
    def get_dashboard_metrics() -> dict[str, Any]:
        return st.session_state.get("dashboard_metrics") or {}

    @staticmethod
    def set_dashboard_metrics(metrics: dict[str, Any]) -> None:
        st.session_state["dashboard_metrics"] = metrics

    @staticmethod
    def get_comparison_data() -> dict[str, Any]:
        return st.session_state.get("comparison_data") or {}

    @staticmethod
    def set_comparison_data(data: dict[str, Any]) -> None:
        st.session_state["comparison_data"] = data

    @staticmethod
    def get_selected_models_for_comparison() -> list[str]:
        return list(st.session_state.get("selected_models_for_comparison") or [])

    @staticmethod
    def set_selected_models_for_comparison(models: list[str]) -> None:
        st.session_state["selected_models_for_comparison"] = models

    @staticmethod
    def should_show_agreement_analysis() -> bool:
        return bool(st.session_state.get("show_agreement_analysis", True))

    @staticmethod
    def set_show_agreement_analysis(show: bool) -> None:
        st.session_state["show_agreement_analysis"] = show

    @staticmethod
    def get_explanation_detail_level() -> str:
        return str(st.session_state.get("explanation_detail_level") or "detailed")

    @staticmethod
    def set_explanation_detail_level(level: str) -> None:
        st.session_state["explanation_detail_level"] = level

    @staticmethod
    def get_enhanced_explanations() -> dict[int, Any]:
        return st.session_state.get("enhanced_explanations") or {}

    @staticmethod
    def set_enhanced_explanation(movie_id: int, payload: Any) -> None:
        cache = SessionManager.get_enhanced_explanations()
        cache[movie_id] = payload
        st.session_state["enhanced_explanations"] = cache

    @staticmethod
    def clear_enhanced_explanations() -> None:
        st.session_state["enhanced_explanations"] = {}

    @staticmethod
    def get_confidence_threshold() -> float:
        return float(st.session_state.get("confidence_threshold") or 0.5)

    @staticmethod
    def set_confidence_threshold(threshold: float) -> None:
        st.session_state["confidence_threshold"] = threshold

    @staticmethod
    def should_show_confidence_indicators() -> bool:
        return bool(st.session_state.get("show_confidence_indicators", True))

    @staticmethod
    def set_show_confidence_indicators(show: bool) -> None:
        st.session_state["show_confidence_indicators"] = show

    @staticmethod
    def get_confidence_data() -> dict[int, Any]:
        return st.session_state.get("confidence_data") or {}

    @staticmethod
    def set_confidence_data(data: dict[int, Any]) -> None:
        st.session_state["confidence_data"] = data

    @staticmethod
    def is_accessibility_mode() -> bool:
        return bool(st.session_state.get("accessibility_mode"))

    @staticmethod
    def set_accessibility_mode(enabled: bool) -> None:
        st.session_state["accessibility_mode"] = enabled

    @staticmethod
    def get_performance_mode() -> str:
        return str(st.session_state.get("performance_mode") or "balanced")

    @staticmethod
    def set_performance_mode(mode: str) -> None:
        st.session_state["performance_mode"] = mode

    # --- Day 6: deployment & production accessors ------------------------

    @staticmethod
    def get_deployment_environment() -> str:
        return str(st.session_state.get("deployment_environment") or "local")

    @staticmethod
    def set_deployment_environment(env: str) -> None:
        st.session_state["deployment_environment"] = env

    @staticmethod
    def get_deployment_health_status() -> str:
        return str(st.session_state.get("deployment_health_status") or "healthy")

    @staticmethod
    def set_deployment_health_status(status: str) -> None:
        st.session_state["deployment_health_status"] = status

    @staticmethod
    def get_deployment_feedback_history() -> list[dict[str, Any]]:
        return st.session_state.get("deployment_feedback_history") or []

    @staticmethod
    def add_deployment_feedback(feedback: dict[str, Any]) -> None:
        history = SessionManager.get_deployment_feedback_history()
        history.append(feedback)
        st.session_state["deployment_feedback_history"] = history

    @staticmethod
    def get_deployment_active_operations() -> dict[str, dict[str, Any]]:
        return st.session_state.get("deployment_active_operations") or {}

    @staticmethod
    def set_deployment_operation_status(op_id: str, status: dict[str, Any]) -> None:
        ops = SessionManager.get_deployment_active_operations()
        ops[op_id] = status
        st.session_state["deployment_active_operations"] = ops

    @staticmethod
    def clear_deployment_operation(op_id: str) -> None:
        ops = SessionManager.get_deployment_active_operations()
        ops.pop(op_id, None)
        st.session_state["deployment_active_operations"] = ops

    @staticmethod
    def get_deployment_error_count() -> int:
        return int(st.session_state.get("deployment_error_count") or 0)

    @staticmethod
    def increment_deployment_error_count() -> int:
        count = SessionManager.get_deployment_error_count() + 1
        st.session_state["deployment_error_count"] = count
        return count

    @staticmethod
    def get_deployment_last_health_check() -> str | None:
        return st.session_state.get("deployment_last_health_check")

    @staticmethod
    def set_deployment_last_health_check(timestamp: str | None) -> None:
        st.session_state["deployment_last_health_check"] = timestamp

    # --- UI state accessors ------------------------------------------------

    @staticmethod
    def get_show_feedback_history() -> bool:
        return bool(st.session_state.get("show_feedback_history"))

    @staticmethod
    def set_show_feedback_history(show: bool) -> None:
        st.session_state["show_feedback_history"] = show

    @staticmethod
    def get_last_health_check_result() -> dict[str, Any] | None:
        return st.session_state.get("last_health_check_result")

    @staticmethod
    def set_last_health_check_result(result: dict[str, Any] | None) -> None:
        st.session_state["last_health_check_result"] = result

    @staticmethod
    def get_onboarding_preferences() -> dict[str, Any]:
        return st.session_state.get("onboarding_preferences") or {}

    @staticmethod
    def set_onboarding_preferences(prefs: dict[str, Any]) -> None:
        st.session_state["onboarding_preferences"] = prefs

