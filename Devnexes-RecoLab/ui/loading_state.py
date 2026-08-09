"""Loading state management component and decorator for RecoLab (Day 6).

Provides visual progress feedback, timeout management, operation cancellation,
and operation status tracking in session state.
"""

from __future__ import annotations

import functools
import time
import uuid
from typing import Any, Callable, TypeVar

import streamlit as st

from ui.session_manager import SessionManager

F = TypeVar("F", bound=Callable[..., Any])


class OperationTimeoutError(Exception):
    """Raised when an operation exceeds its configured timeout threshold."""
    pass


def with_loading_state(
    message: str = "Processing request...",
    timeout_seconds: float = 300.0,
    show_progress: bool = True,
) -> Callable[[F], F]:
    """Decorator to wrap operations with UI loading indicators and timeout handling.

    Args:
        message: Loading message to display in UI.
        timeout_seconds: Maximum allowed duration in seconds.
        show_progress: Whether to display Streamlit spinner/status widget.

    Returns:
        Decorated function.
    """
    def decorator(func: F) -> F:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            op_id = str(uuid.uuid4())
            start_time = time.time()

            # Record operation start
            op_status = {
                "operation_id": op_id,
                "function_name": func.__name__,
                "message": message,
                "start_time": start_time,
                "status": "running",
                "cancelled": False,
            }
            SessionManager.set_deployment_operation_status(op_id, op_status)

            try:
                if show_progress:
                    with st.spinner(message):
                        result = func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                elapsed = time.time() - start_time
                if elapsed > timeout_seconds:
                    raise OperationTimeoutError(
                        f"Operation '{func.__name__}' timed out after {elapsed:.1f}s (max: {timeout_seconds}s)"
                    )

                op_status["status"] = "completed"
                op_status["elapsed_seconds"] = elapsed
                SessionManager.set_deployment_operation_status(op_id, op_status)
                return result

            except Exception as e:
                op_status["status"] = "failed"
                op_status["error"] = str(e)
                SessionManager.set_deployment_operation_status(op_id, op_status)
                raise
            finally:
                SessionManager.clear_deployment_operation(op_id)

        return wrapper  # type: ignore[return-value]

    return decorator


def render_operation_tracker() -> None:
    """Render an operation tracking status indicator in the UI sidebar if operations are active."""
    active_ops = SessionManager.get_deployment_active_operations()
    if not active_ops:
        return

    with st.expander("⏳ Active Operations", expanded=False):
        for op_id, op_info in active_ops.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.caption(f"**{op_info.get('function_name', 'Op')}**: {op_info.get('message', '')}")
            with col2:
                if st.button("Cancel", key=f"cancel_op_{op_id}"):
                    op_info["cancelled"] = True
                    SessionManager.set_deployment_operation_status(op_id, op_info)
                    st.toast(f"Cancelled {op_info.get('function_name')}")
