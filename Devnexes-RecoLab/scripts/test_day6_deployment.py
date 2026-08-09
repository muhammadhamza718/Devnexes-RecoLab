"""Comprehensive Unit & End-to-End Tests for Day 6 Deployment & Production Readiness.

Tests:
1. Environment Configuration and Health Diagnostics (env_utils.py)
2. Production Error Handling & Logging Safeguards (logging_config.py)
3. Loading State & Timeout Management (loading_state.py)
4. Deployment Session State Schema (session_manager.py)
5. Feedback System & History Storage (feedback.py)
6. App UI End-to-End Test (streamlit.testing.v1.AppTest)

Run from project root:
    python scripts/test_day6_deployment.py
"""

import os
import sys
import time
from pathlib import Path

# Add project root and src directory to sys.path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from scripts.env_utils import (
    DEFAULT_ENVIRONMENT,
    _detect_deployment_environment,
    perform_health_check,
    validate_environment,
)
from scripts.logging_config import UserFacingError, production_error_handler
from ui.empty_states import (
    render_empty_dashboard_metrics,
    render_empty_feedback,
    render_empty_recommendations,
    render_empty_search_results,
    render_empty_similar_items,
    render_empty_user_selection,
)
from ui.feedback import render_feedback_history_view, render_feedback_sidebar_widget
from ui.loading_state import (
    OperationTimeoutError,
    render_operation_tracker,
    with_loading_state,
)
from ui.session_manager import SessionManager

RESULTS = []


def check(name: str, condition: bool) -> None:
    RESULTS.append((name, condition))
    status = "PASS" if condition else "FAIL"
    print(f"[{status}] {name}")


def test_environment_utilities() -> None:
    print("\n--- 1. Testing Environment Utilities ---")
    config = validate_environment()
    check("validate_environment returns dict", isinstance(config, dict))
    check("RECOLAB_CACHE_TTL is int", isinstance(config["RECOLAB_CACHE_TTL"], int))
    check("STREAMLIT_RUNTIME is bool", isinstance(config["STREAMLIT_RUNTIME"], bool))

    env_type = _detect_deployment_environment()
    check("environment detection returns valid string", env_type in ("streamlit_cloud", "production", "local"))

    health = perform_health_check()
    check("perform_health_check returns dictionary", isinstance(health, dict))
    check("health status in allowed values", health["status"] in ("healthy", "degraded", "unhealthy"))
    check("health checks include data & model dirs", "data_directory" in health["checks"] and "model_directory" in health["checks"])


def test_production_error_handling() -> None:
    print("\n--- 2. Testing Production Error Handling ---")

    @production_error_handler(context_message="Test context error message")
    def succeeding_fn(a: int, b: int) -> int:
        return a + b

    @production_error_handler(context_message="Test failure context")
    def failing_fn() -> None:
        raise ValueError("Simulated backend internal error")

    check("production_error_handler passes through successful return", succeeding_fn(3, 5) == 8)

    caught_exception = False
    try:
        failing_fn()
    except UserFacingError as err:
        caught_exception = True
        check("UserFacingError wraps internal message safely", "Simulated backend internal error" in str(err))

    check("failing_fn raises UserFacingError", caught_exception)


def test_loading_state_management() -> None:
    print("\n--- 3. Testing Loading State & Timeout Management ---")

    @with_loading_state(message="Running fast operation", timeout_seconds=10.0, show_progress=False)
    def fast_op() -> str:
        return "completed"

    @with_loading_state(message="Running slow operation", timeout_seconds=0.1, show_progress=False)
    def slow_op() -> None:
        time.sleep(0.2)

    check("fast operation completes successfully", fast_op() == "completed")

    timeout_caught = False
    try:
        slow_op()
    except OperationTimeoutError:
        timeout_caught = True

    check("slow operation raises OperationTimeoutError on breach", timeout_caught)


def test_deployment_session_state() -> None:
    print("\n--- 4. Testing Deployment Session State & Feedback Schema ---")
    SessionManager.ensure_initialized()

    check("deployment_environment default state initialized", SessionManager.get_deployment_environment() == "local")

    SessionManager.set_deployment_health_status("degraded")
    check("set_deployment_health_status updates value", SessionManager.get_deployment_health_status() == "degraded")

    feedback_sample = {
        "id": 1,
        "category": "Recommendation Quality",
        "rating": 5,
        "comment": "Great recommendations!",
    }
    SessionManager.add_deployment_feedback(feedback_sample)
    history = SessionManager.get_deployment_feedback_history()
    check("add_deployment_feedback stores entry", len(history) > 0 and history[-1]["comment"] == "Great recommendations!")

    SessionManager.increment_deployment_error_count()
    check("increment_deployment_error_count increments state", SessionManager.get_deployment_error_count() > 0)


def test_app_ui_integration() -> None:
    print("\n--- 5. Testing Streamlit App UI Integration (AppTest) ---")
    from streamlit.testing.v1 import AppTest

    app_path = PROJECT_ROOT / "streamlit_app.py"
    at = AppTest.from_file(str(app_path), default_timeout=300)
    at.run()

    check("Streamlit app launches without exception", not at.exception)
    check("RecoLab title renders", any("RecoLab" in str(el.value) for el in at.title))
    check("Deployment components loaded in session state", "deployment_environment" in at.session_state)


def main() -> None:
    print("==========================================================")
    print("Devnexes RecoLab — Day 6 Deployment & Production Test Suite")
    print("==========================================================")

    test_environment_utilities()
    test_production_error_handling()
    test_loading_state_management()
    test_deployment_session_state()
    test_app_ui_integration()

    print("\n==========================================================")
    passed = sum(1 for _, cond in RESULTS if cond)
    total = len(RESULTS)
    print(f"SUMMARY: {passed}/{total} checks passed.")
    print("==========================================================")

    if passed != total:
        sys.exit(1)


if __name__ == "__main__":
    main()
