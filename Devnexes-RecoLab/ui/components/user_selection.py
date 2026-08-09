"""User selection component (Task-005).

Renders a searchable user dropdown in the sidebar, keeps the selection in
session state, and shows the user profile (id, rating count, activity level)
using activity thresholds that mirror the hybrid model.
"""

from __future__ import annotations

from typing import Any

import streamlit as st

from ui.data_provider import DataProvider
from ui.session_manager import SessionManager

# Visual badges for each activity level.
ACTIVITY_BADGES: dict[str, str] = {
    "cold-start": ":blue[❄ cold-start]",
    "intermediate": ":orange[⚙ intermediate]",
    "active": ":green[⚡ active]",
}

_SEARCH_HELP = "Search by full user id, or leave empty to browse."
_PROFILE_HELP = (
    "Activity = ratings in the train split. "
    "cold-start ≤ 5, active ≥ 20 (matches the hybrid model's thresholds)."
)


def render_user_selector(provider: DataProvider) -> int | None:
    """Render the user picker; returns the selected user id (or None)."""
    st.sidebar.subheader("1. Select User")

    query = st.sidebar.text_input(
        "Search user ID",
        placeholder="e.g. 1",
        help=_SEARCH_HELP,
        key="widget_user_search",
    )
    user_ids = provider.search_users(query, limit=100)

    if not user_ids:
        st.sidebar.warning("No users match your search.")
        return None

    options = [str(uid) for uid in user_ids]
    previous = SessionManager.get_selected_user_id()
    previous_str = str(previous) if previous is not None and str(previous) in options else options[0]

    selected_str = st.sidebar.selectbox(
        "User ID",
        options,
        index=options.index(previous_str),
        help="Choose the user to generate recommendations for.",
    )
    user_id = int(selected_str)

    # Persist the selection; clear stale recommendations on user change.
    if user_id != previous:
        SessionManager.set_selected_user_id(user_id)
        SessionManager.clear_recommendations()

    profile = provider.get_user_profile(user_id)
    SessionManager.set_user_profile(profile)
    _render_profile(profile)

    return user_id


def _render_profile(profile: dict[str, Any]) -> None:
    """Show the selected user's profile card in the sidebar."""
    badge = ACTIVITY_BADGES.get(profile.get("activity_level", ""), "")
    with st.sidebar.expander("User profile", expanded=True):
        st.write(f"**ID:** {profile.get('user_id')}")
        st.write(f"**Ratings:** {profile.get('rating_count')}")
        st.write(f"**Activity:** {badge}")
        st.caption(_PROFILE_HELP)
