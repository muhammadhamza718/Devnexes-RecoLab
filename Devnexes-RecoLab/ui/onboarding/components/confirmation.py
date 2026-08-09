"""Confirmation and preview wizard step component (Task-007)."""

from __future__ import annotations

import html
from typing import Any
import streamlit as st

from ui.session_manager import SessionManager
from ui.onboarding.wizard_controller import OnboardingWizard


def render_confirmation(
    wizard: OnboardingWizard,
    onboarding_recommender: Any | None = None,
) -> None:
    """Render Step 3: Preference confirmation & recommendation preview."""
    st.subheader("Step 3 of 3: Confirm Preferences & Preview Recommendations 🎉")
    st.write("Review your selections below and fine-tune preference weights before completing onboarding.")

    preferences = wizard.get_preferences()
    genres = preferences.get("genres", [])
    liked_movies = preferences.get("liked_movies", [])

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### 🎬 Selected Genres")
        if genres:
            pills = " ".join(
                f'<span style="background-color:#1e3a8a; color:#ffffff; padding:4px 10px; '
                f'border-radius:12px; font-size:13px; font-weight:500; margin-right:6px; display:inline-block; margin-bottom:6px;">'
                f'{html.escape(g)}</span>'
                for g in genres
            )
            st.markdown(pills, unsafe_allow_html=True)
        else:
            st.info("No explicit genres selected.")

    with col2:
        st.markdown("### 🍿 Liked Movies")
        if liked_movies:
            for item in liked_movies:
                title = item.get("title", "Unknown") if isinstance(item, dict) else str(item)
                st.markdown(f"• **{html.escape(title)}**")
        else:
            st.info("No explicit liked movies selected.")

    st.markdown("---")

    # Optional Weight Adjustment Section
    st.markdown("### ⚖️ Fine-Tune Genre Weights (Optional)")
    if genres:
        st.caption("Adjust the weight/importance of each genre for your personalized recommendations (0.1 to 2.0):")
        current_weights = SessionManager.get_onboarding_preference_weights()
        updated_weights = {}
        weight_cols = st.columns(min(len(genres), 4))
        for idx, genre in enumerate(genres):
            with weight_cols[idx % 4]:
                w = st.slider(
                    f"{genre}",
                    min_value=0.1,
                    max_value=2.0,
                    value=float(current_weights.get(genre, 1.0)),
                    step=0.1,
                    key=f"weight_slider_{genre}",
                )
                updated_weights[genre] = w
        SessionManager.set_onboarding_preference_weights(updated_weights)
    else:
        st.write("Select genres in Step 1 to customize genre weights.")

    st.markdown("---")

    # Preview section
    st.markdown("### 🔮 Initial Recommendation Preview")
    preview_items = SessionManager.get_onboarding_recommendation_preview()

    if st.button("🔄 Generate Recommendation Preview", key="btn_gen_preview"):
        if onboarding_recommender is not None:
            with st.spinner("Calculating personalized cold-start recommendations..."):
                current_prefs = wizard.get_preferences()
                recs = onboarding_recommender.get_preview_recommendations(current_prefs, top_n=5)
                SessionManager.set_onboarding_recommendation_preview(recs)
                preview_items = recs
        else:
            st.info("Recommender integration pending.")

    if preview_items:
        st.markdown("**Top Recommended Movies for You:**")
        for idx, rec in enumerate(preview_items, 1):
            title = rec.get("title", f"Movie #{rec.get('movieId')}")
            score = rec.get("score")
            score_str = f" (Match Score: {score:.2f})" if score is not None else ""
            genres_str = rec.get("genres", "")
            st.markdown(f"**{idx}. {html.escape(title)}**{score_str} — `{html.escape(genres_str)}`")
    else:
        st.caption("Click 'Generate Recommendation Preview' above to see instant preview results.")

    st.markdown("---")

    # Final step navigation
    col_back, col_space, col_finish = st.columns([1, 1, 2])

    with col_back:
        if st.button("⬅️ Back: Liked Movies", key="btn_back_step3", width="stretch"):
            wizard.previous_step()
            st.rerun()

    with col_finish:
        if st.button("🚀 Complete Onboarding & See Full Recommendations", key="btn_complete_onboarding", width="stretch", type="primary"):
            wizard.complete_onboarding()
            st.success("Onboarding complete! Loading your personalized recommendations...")
            st.rerun()
