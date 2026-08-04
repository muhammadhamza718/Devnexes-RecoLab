"""Genre selection wizard step component (Task-005)."""

from __future__ import annotations

import html
from typing import Any
import streamlit as st

from ui.session_manager import SessionManager
from ui.onboarding.genre_provider import GenreProvider
from ui.onboarding.wizard_controller import OnboardingWizard


def render_genre_selection(
    genre_provider: GenreProvider,
    wizard: OnboardingWizard,
) -> None:
    """Render Step 1: Genre preference selection with popularity badges and presets."""
    st.subheader("Step 1 of 3: Select Your Favorite Genres 🎬")
    st.write("Tell us what genres you enjoy so we can personalize your movie recommendations right away.")

    all_genres = genre_provider.get_all_genres()
    popularity = genre_provider.get_genre_popularity()
    current_selected = SessionManager.get_selected_genres()

    # Quick preset selection section
    st.markdown("**Quick Presets:**")
    preset_cols = st.columns(5)
    combinations = genre_provider.get_suggested_combinations()
    for idx, combo in enumerate(combinations):
        with preset_cols[idx % 5]:
            if st.button(combo["name"], key=f"preset_btn_{combo['id']}", use_container_width=True):
                # Apply preset genres
                SessionManager.set_selected_genres(list(combo["genres"]))
                st.rerun()

    st.markdown("---")

    # Multi-select list with popularity indicator context
    st.markdown("**Select Genres (Up to 10):**")

    # Custom multiselect with formatted display labels including movie counts
    formatted_options = {
        f"{g} ({popularity.get(g, 0):,} movies)": g
        for g in all_genres
    }

    # Reverse lookup for initial values
    default_formatted = [
        fmt for fmt, raw in formatted_options.items() if raw in current_selected
    ]

    selected_formatted = st.multiselect(
        "Choose genres:",
        options=list(formatted_options.keys()),
        default=default_formatted,
        max_selections=10,
        key="genre_multiselect_input",
    )

    # Convert back to raw genre strings
    selected_raw = [formatted_options[fmt] for fmt in selected_formatted if fmt in formatted_options]
    SessionManager.set_selected_genres(selected_raw)

    # Display selected genre pills
    if selected_raw:
        st.markdown("**Selected Genres:**")
        pills_html = " ".join(
            f'<span style="background-color:#1e3a8a; color:#ffffff; padding:4px 10px; '
            f'border-radius:12px; font-size:13px; font-weight:500; margin-right:6px; display:inline-block; margin-bottom:6px;">'
            f'{html.escape(g)}</span>'
            for g in selected_raw
        )
        st.markdown(pills_html, unsafe_allow_html=True)
    else:
        st.info("No genres selected yet. Select genres above or click 'Skip' to use default genres.")

    st.markdown("---")

    # Step navigation buttons
    col_skip, col_space, col_next = st.columns([1, 2, 1])

    with col_skip:
        if st.button("⏭️ Skip with Defaults", key="btn_skip_step1", use_container_width=True):
            wizard.skip_onboarding()
            st.rerun()

    with col_next:
        next_disabled = False
        if st.button("Next: Liked Movies ➡️", key="btn_next_step1", use_container_width=True, disabled=next_disabled):
            wizard.next_step()
            st.rerun()
