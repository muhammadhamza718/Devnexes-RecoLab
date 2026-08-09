"""Empty state component library for RecoLab (Day 6).

Provides context-aware UI empty state displays with icons, explanations,
and actionable next steps across recommendations, item similarity, search,
dashboard metrics, and user feedback views.
"""

from __future__ import annotations

from typing import Callable
import streamlit as st


def render_empty_user_selection(on_action: Callable[[], None] | None = None) -> None:
    """Render empty state when no user is selected."""
    st.info("👈 **Select a user from the sidebar to begin.**\n\nChoose any User ID to view personalized movie recommendations, user profile statistics, and model explanations.")
    if on_action and st.button("🚀 Start Onboarding Wizard"):
        on_action()


def render_empty_recommendations(user_id: int | None = None) -> None:
    """Render empty state when recommendations list is empty."""
    st.warning("🎬 **No recommendations available.**")
    st.write(
        f"We couldn't generate recommendations for User {user_id or 'selected'} with the current settings."
    )
    st.markdown(
        """
        **Suggested Actions:**
        - Try switching to a different recommender model (e.g. Content-Based or Hybrid).
        - Adjust model hyperparameters in the sidebar (e.g. increase $K$ or lower rating threshold).
        - If this is a new user, complete the Cold-Start Onboarding workflow.
        """
    )


def render_empty_similar_items(movie_title: str | None = None) -> None:
    """Render empty state when no similar items are found."""
    st.info(f"🔍 **No similar items found for '{movie_title or 'selected item'}'.**")
    st.write(
        "Item-based similarity could not identify related movies with sufficient confidence."
    )
    st.markdown(
        """
        **Suggestions:**
        - Check if the item has sufficient rating history.
        - Try searching for another movie title.
        """
    )


def render_empty_search_results(query: str = "") -> None:
    """Render empty state when movie search returns zero results."""
    st.info(f"🔎 **No movies found matching '{query}'.**")
    st.write(
        "Try searching with a broader title keyword, partial genre name, or release year."
    )


def render_empty_dashboard_metrics() -> None:
    """Render empty state when metrics evaluation data is missing."""
    st.warning("📊 **Evaluation metrics unavailable.**")
    st.write(
        "Day 5 evaluation summary files were not found or could not be loaded."
    )
    st.markdown(
        """
        **To populate metrics:**
        - Run the offline evaluation pipeline: `python scripts/evaluation/run_evaluation.py`
        - Or run the comprehensive analysis pipeline: `python scripts/analysis/run_analysis.py`
        """
    )


def render_empty_feedback() -> None:
    """Render empty state when no user feedback has been recorded."""
    st.info("💬 **No user feedback submitted yet.**")
    st.caption("Use the Feedback form in the sidebar to report issues or leave feedback.")
