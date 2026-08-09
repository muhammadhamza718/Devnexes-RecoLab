"""Liked movies wizard step component (Task-006)."""

from __future__ import annotations

import html
from typing import Any
import streamlit as st

from ui.session_manager import SessionManager
from ui.onboarding.movie_search_provider import MovieSearchProvider
from ui.onboarding.wizard_controller import OnboardingWizard


def render_liked_movies(
    search_provider: MovieSearchProvider,
    wizard: OnboardingWizard,
) -> None:
    """Render Step 2: Liked movies search & selection."""
    st.subheader("Step 2 of 3: Select Movies You Love 🍿")
    st.write("Search for movies you have enjoyed in the past. This helps us match your specific taste profile.")

    current_liked: list[dict[str, Any]] = SessionManager.get_onboarding_liked_movies()
    current_liked_ids = {m.get("movieId") for m in current_liked if isinstance(m, dict)}

    # Search bar
    search_query = st.text_input(
        "Search by movie title:",
        value="",
        placeholder="e.g. Inception, The Dark Knight, Toy Story...",
        key="movie_search_query_input",
    )

    results = search_provider.search_movies(search_query, limit=10)

    if search_query.strip():
        st.markdown(f"**Search Results ({len(results)} matches):**")
    else:
        st.markdown("**Popular Recommendations to get started:**")

    if not results:
        st.warning("No movies found matching your query. Try a different title.")
    else:
        # Render candidate movies in a grid/list
        for movie in results:
            mid = movie["movieId"]
            title = movie["title"]
            year = movie.get("year")
            year_str = f" ({year})" if year else ""
            genres_str = movie.get("genres", "")
            pop = movie.get("popularity", 0)
            mean_r = movie.get("mean_rating")
            rating_str = f"⭐ {mean_r:.1f}" if mean_r else "No rating"

            col_info, col_btn = st.columns([4, 1])

            with col_info:
                st.markdown(
                    f"**{html.escape(title)}**{year_str} &nbsp;|&nbsp; `{html.escape(genres_str)}` &nbsp;|&nbsp; {rating_str} ({pop:,} ratings)"
                )

            with col_btn:
                is_selected = mid in current_liked_ids
                if is_selected:
                    if st.button("Remove ❌", key=f"btn_rem_movie_{mid}", width="stretch"):
                        updated = [m for m in current_liked if m.get("movieId") != mid]
                        SessionManager.set_onboarding_liked_movies(updated)
                        st.rerun()
                else:
                    can_add = len(current_liked) < 20
                    if st.button("Add ➕", key=f"btn_add_movie_{mid}", width="stretch", disabled=not can_add):
                        current_liked.append(movie)
                        SessionManager.set_onboarding_liked_movies(current_liked)
                        st.rerun()

    st.markdown("---")

    # Display selected movies summary
    st.markdown(f"**Your Liked Movies ({len(current_liked)}/20):**")

    if current_liked:
        for idx, item in enumerate(current_liked):
            col_txt, col_del = st.columns([5, 1])
            with col_txt:
                st.markdown(f"• **{html.escape(item.get('title', 'Unknown'))}** (`{html.escape(item.get('genres', ''))}`)")
            with col_del:
                if st.button("❌", key=f"btn_del_sel_{item.get('movieId')}_{idx}"):
                    updated = [m for i, m in enumerate(current_liked) if i != idx]
                    SessionManager.set_onboarding_liked_movies(updated)
                    st.rerun()
    else:
        st.info("No movies added yet. Use the search bar above or pick from suggestions.")

    st.markdown("---")

    # Navigation buttons
    col_back, col_skip, col_next = st.columns([1, 1, 1])

    with col_back:
        if st.button("⬅️ Back: Genres", key="btn_back_step2", width="stretch"):
            wizard.previous_step()
            st.rerun()

    with col_skip:
        if st.button("⏭️ Skip with Defaults", key="btn_skip_step2", width="stretch"):
            wizard.skip_onboarding()
            st.rerun()

    with col_next:
        if st.button("Next: Confirmation ➡️", key="btn_next_step2", width="stretch"):
            wizard.next_step()
            st.rerun()
