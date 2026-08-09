"""User feedback collection and feedback history UI component for RecoLab (Day 6).

Provides a non-intrusive feedback widget for user rating, issue reporting,
and feature suggestions, stored in session state.
"""

from __future__ import annotations

from datetime import datetime, timezone
import streamlit as st

from ui.session_manager import SessionManager


def render_feedback_sidebar_widget() -> None:
    """Render non-intrusive feedback form in sidebar expander."""
    with st.sidebar.expander("💬 Give Feedback / Report Issue", expanded=False):
        with st.form(key="recolab_user_feedback_form", clear_on_submit=True):
            category = st.selectbox(
                "Category",
                options=[
                    "Recommendation Quality",
                    "UI / UX Ergonomics",
                    "Bug / Technical Issue",
                    "Feature Request",
                    "Other",
                ],
                key="feedback_category_select",
            )

            rating = st.slider(
                "Satisfaction Rating",
                min_value=1,
                max_value=5,
                value=5,
                help="1 = Poor, 5 = Excellent",
                key="feedback_rating_slider",
            )

            comment = st.text_area(
                "Comments / Details",
                placeholder="Share your thoughts or describe what happened...",
                max_chars=500,
                key="feedback_comment_area",
            )

            submitted = st.form_submit_button("Submit Feedback", type="primary")

            if submitted:
                if not comment.strip():
                    st.error("Please include a comment before submitting.")
                else:
                    feedback_entry = {
                        "id": len(SessionManager.get_deployment_feedback_history()) + 1,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "category": category,
                        "rating": rating,
                        "comment": comment.strip(),
                        "user_id": SessionManager.get_selected_user_id(),
                        "model": SessionManager.get_selected_model(),
                        "view": SessionManager.get_current_view(),
                    }
                    SessionManager.add_deployment_feedback(feedback_entry)
                    st.success("Thank you! Your feedback has been recorded.")


def render_feedback_history_view() -> None:
    """Render admin/dev view of submitted user feedback."""
    st.subheader("💬 Submitted User Feedback")
    history = SessionManager.get_deployment_feedback_history()

    if not history:
        st.info("No feedback entries submitted in this session.")
        return

    col1, col2 = st.columns(2)
    avg_rating = sum(item["rating"] for item in history) / len(history)
    with col1:
        st.metric("Total Submissions", len(history))
    with col2:
        st.metric("Average Rating", f"{avg_rating:.1f} / 5.0")

    st.markdown("---")
    for item in reversed(history):
        with st.container():
            c1, c2, c3 = st.columns([2, 2, 1])
            with c1:
                st.markdown(f"**Category:** {item['category']}")
            with c2:
                st.markdown(f"**Rating:** {'⭐' * item['rating']}")
            with c3:
                st.caption(f"{item['timestamp'][:19]}")

            st.write(f"\"{item['comment']}\"")
            st.caption(f"Context: User ID {item.get('user_id') or 'N/A'} | Model: {item.get('model')} | View: {item.get('view')}")
            st.markdown("---")
