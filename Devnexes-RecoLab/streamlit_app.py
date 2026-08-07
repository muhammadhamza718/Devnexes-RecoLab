# Main Streamlit application for Devnexes RecoLab
#
# Day 3 Morning — Core UI Structure. Wires the sidebar (user + model
# selection) to the five recommendation models and renders results in the
# main area. Recommendations survive reruns via session state.

import sys
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import streamlit as st  # noqa: E402

st.set_page_config(
    page_title="Devnexes RecoLab",
    page_icon="🎬",
    layout="wide",
)

from ui.components.model_selection import render_model_selector  # noqa: E402
from ui.components.recommendation_display import render_recommendations  # noqa: E402
from ui.components.similar_items import render_similar_items  # noqa: E402
from ui.components.user_selection import render_user_selector  # noqa: E402
from ui.components.visualizations import render_visualizations_panel  # noqa: E402
from ui.data_provider import DataProvider  # noqa: E402
from ui.model_manager import ModelManager  # noqa: E402
from ui.session_manager import SessionManager  # noqa: E402
from ui.similarity_provider import SimilarityProvider  # noqa: E402
from ui.statistics_aggregator import StatisticsAggregator  # noqa: E402

from ui.onboarding.genre_provider import GenreProvider  # noqa: E402
from ui.onboarding.movie_search_provider import MovieSearchProvider  # noqa: E402
from ui.onboarding.wizard_controller import OnboardingWizard  # noqa: E402
from ui.onboarding.onboarding_recommender import OnboardingRecommender  # noqa: E402
from ui.onboarding.components.genre_selection import render_genre_selection  # noqa: E402
from ui.onboarding.components.liked_movies import render_liked_movies  # noqa: E402
from ui.onboarding.components.confirmation import render_confirmation  # noqa: E402

from ui.dashboard.explanation_enhancer import ExplanationEnhancer  # noqa: E402
from ui.dashboard.metrics_provider import MetricsProvider  # noqa: E402
from ui.dashboard.performance_dashboard import render_performance_dashboard  # noqa: E402
from ui.dashboard.confidence_calculator import ConfidenceCalculator  # noqa: E402
from ui.dashboard.accessibility import inject_accessibility_styles, render_accessibility_sidebar_controls  # noqa: E402
from ui.dashboard.confidence_indicators import render_confidence_sidebar_controls  # noqa: E402
from ui.dashboard.performance_controls import (  # noqa: E402
    render_performance_sidebar_controls,
    should_compute_confidence,
    should_compute_enhanced_explanations,
)
from ui.dashboard.model_comparison_engine import ModelComparisonEngine  # noqa: E402
from ui.dashboard.model_comparison_view import render_model_comparison_view  # noqa: E402

SessionManager.ensure_initialized()
inject_accessibility_styles()

st.title("Devnexes RecoLab — Movie Recommendation System")
st.caption(
    "Compare five recommendation models on the MovieLens small dataset: "
    "Popularity, Content, User-Based CF, Item-Based CF, and a Hybrid blend."
)


@st.cache_resource(show_spinner=False)
def _load_provider() -> DataProvider:
    """DataProvider is cached so the catalog loads once per server run."""
    return DataProvider()


def _build_rows(
    model: Any,
    model_name: str,
    rec_ids: list[int],
    user_id: int,
    provider: DataProvider,
    k: int,
) -> list[dict[str, Any]]:
    """Enrich raw movie ids into display rows (title, year, genres, scores)."""
    has_explain = callable(getattr(model, "explain", None))
    has_confidence = callable(getattr(model, "get_confidence", None))

    rows: list[dict[str, Any]] = []
    for rank, movie_id in enumerate(rec_ids, start=1):
        movie = provider.get_movie(movie_id) or {}
        row: dict[str, Any] = {
            "movie_id": movie_id,
            "title": movie.get("title") or f"Movie {movie_id}",
            "year": movie.get("year"),
            "genres": movie.get("genres") or "Unknown",
            # Rank-based relevance: 1.0 for the top pick, falling to 1/k.
            "score": round((k - rank + 1) / k, 3) if k else None,
            "confidence": None,
            "explanation": None,
        }

        if has_confidence:
            try:
                row["confidence"] = float(model.get_confidence(user_id, movie_id))
            except Exception:
                pass  # confidence is best-effort

        if has_explain:
            try:
                row["explanation"] = str(model.explain(user_id, movie_id))
            except Exception:
                pass  # explanation is best-effort
        else:
            row["explanation"] = "Popular among users in the training data."

        rows.append(row)
    return rows


def _generate(
    user_id: int,
    model_name: str,
    params: dict[str, Any],
    provider: DataProvider,
    model_manager: ModelManager,
) -> None:
    """Run the selected model and store the rendered rows in session state."""
    try:
        with st.spinner(f"Running the {model_name} model…"):
            model, provenance = model_manager.get_model(model_name)
            model_manager.apply_params(model, model_name, params)
            k = int(params.get("n", 10))
            rec_ids = list(model.recommend(user_id, k=k, exclude_items=None) or [])
            rows = _build_rows(model, model_name, rec_ids, user_id, provider, k)
            SessionManager.set_recommendations(rows)

            # Task-016: skip expensive post-processing based on performance mode
            if should_compute_enhanced_explanations():
                enhancer = ExplanationEnhancer(model_manager, provider)
                SessionManager.clear_enhanced_explanations()
                for row in rows:
                    movie_id = row.get("movie_id")
                    if movie_id is None:
                        continue
                    SessionManager.set_enhanced_explanation(
                        movie_id,
                        enhancer.enhance_explanation(
                            user_id,
                            movie_id,
                            model_name,
                            detail_level=SessionManager.get_explanation_detail_level(),
                        ),
                    )
            else:
                SessionManager.clear_enhanced_explanations()

            # Task-013/014/016: confidence scores (skipped in fast mode)
            if should_compute_confidence():
                conf_calc = ConfidenceCalculator(model_manager, provider)
                all_models_agreement: dict[str, list[int]] = {}
                from ui.model_manager import MODEL_NAMES
                for mname in MODEL_NAMES:
                    try:
                        mobj, _ = model_manager.get_model(mname)
                        all_models_agreement[mname] = list(mobj.recommend(user_id, k=k, exclude_items=None) or [])
                    except Exception:
                        pass
                SessionManager.set_confidence_data({})
                for row in rows:
                    movie_id = row.get("movie_id")
                    if movie_id is None:
                        continue
                    SessionManager.set_confidence_data(
                        {**SessionManager.get_confidence_data(), int(movie_id): conf_calc.calculate_confidence(
                            user_id, int(movie_id), model_name, all_models_agreement
                        )}
                    )
            else:
                SessionManager.set_confidence_data({})

        st.success(f"**{model_name}** — {provenance}.")
        if not rows:
            st.warning("No recommendations could be generated for this user.")
    except Exception as err:
        SessionManager.clear_recommendations()
        st.error(f"Could not generate recommendations: {err}")
        st.caption("Tip: try another user or model.")


def _render_similar_items_view(
    provider: DataProvider,
    similarity_provider: SimilarityProvider,
) -> None:
    """Render the similar-items view with back navigation (Tasks 005/006).

    Shown when ``current_view`` is "similar_items": a back button returns to
    the recommendations view, then the cached similar items are rendered as a
    poster grid with the source movie's title as context.
    """
    if st.button("← Back to recommendations"):
        SessionManager.set_current_view("recommendations")
        st.rerun()

    render_similar_items(
        similarity_provider,
        SessionManager.get_similar_items(),
        source_title=SessionManager.get_similar_source_title(),
    )


def main() -> None:
    with st.spinner("Loading data…"):
        provider = _load_provider()
    model_manager = ModelManager()
    similarity_provider = SimilarityProvider(model_manager, provider)
    stats_aggregator = StatisticsAggregator(provider)
    metrics_provider = MetricsProvider()
    comparison_engine = ModelComparisonEngine(model_manager, metrics_provider)

    genre_provider = GenreProvider(provider)
    search_provider = MovieSearchProvider(provider)
    wizard = OnboardingWizard()
    onboarding_recommender = OnboardingRecommender(provider)

    with st.sidebar:
        st.header("Configuration")
        user_id = render_user_selector(provider)
        model_name, params = render_model_selector()

        st.markdown("---")
        st.subheader("Cold-Start Onboarding")
        if st.button("✨ Start New User Onboarding", key="btn_start_onboarding_sidebar", use_container_width=True):
            SessionManager.reset_onboarding_state()
            st.rerun()

        st.markdown("---")
        st.subheader("Advanced Features")
        show_dashboard = st.checkbox(
            "Show Performance Dashboard",
            value=SessionManager.is_dashboard_active(),
            key="sidebar_show_dashboard",
        )
        SessionManager.set_dashboard_active(show_dashboard)

        show_comparison = st.checkbox(
            "Show Model Comparison",
            value=SessionManager.is_model_comparison_active(),
            key="sidebar_show_comparison",
        )
        SessionManager.set_model_comparison_active(show_comparison)

        render_confidence_sidebar_controls()
        render_accessibility_sidebar_controls()
        render_performance_sidebar_controls()

    # If onboarding wizard is active, render the wizard instead of main recommendations dashboard
    if SessionManager.is_onboarding_active():
        current_step = wizard.get_current_step()
        progress_val = int((current_step + 1) / wizard.TOTAL_STEPS * 100)

        col_head, col_exit = st.columns([4, 1])
        with col_head:
            st.markdown(f"### 🚀 New User Onboarding Wizard — Step {current_step + 1} of {wizard.TOTAL_STEPS}")
        with col_exit:
            if st.button("✖️ Cancel Wizard", key="btn_cancel_wizard"):
                SessionManager.set_onboarding_active(False)
                st.rerun()

        st.progress(progress_val)

        if current_step == 0:
            render_genre_selection(genre_provider, wizard)
        elif current_step == 1:
            render_liked_movies(search_provider, wizard)
        elif current_step == 2:
            render_confirmation(wizard, onboarding_recommender)

        return

    if SessionManager.is_dashboard_active():
        render_performance_dashboard(metrics_provider)
        return

    if SessionManager.is_model_comparison_active():
        if user_id is None:
            st.info("Select a user from the sidebar to compare model outputs side-by-side.")
            return
        render_model_comparison_view(
            comparison_engine, metrics_provider, provider, user_id
        )
        return

    if user_id is None:
        st.info("Select a user from the sidebar or click '✨ Start New User Onboarding' to get started.")
        return

    # Display active onboarding preferences banner if user completed onboarding
    if SessionManager.is_onboarding_complete():
        prefs = SessionManager.get_onboarding_preferences()
        if prefs:
            g_count = len(prefs.get("genres", []))
            m_count = len(prefs.get("liked_movies", []))
            st.success(
                f"✨ Cold-Start Profile Active! Preferences: {g_count} genres, {m_count} liked movies. "
                f"Showing cold-start recommendations."
            )

    profile = SessionManager.get_user_profile()
    cols = st.columns(3)
    cols[0].metric("User ID", profile.get("user_id", user_id))
    cols[1].metric("Ratings", profile.get("rating_count", 0))
    activity = str(profile.get("activity_level", "unknown")).replace("-", " ").title()
    cols[2].metric("Activity", activity)

    if SessionManager.get_current_view() == "similar_items":
        _render_similar_items_view(provider, similarity_provider)
        return

    if st.button("Generate Recommendations", type="primary"):
        _generate(user_id, model_name, params, provider, model_manager)

    render_recommendations(
        provider,
        SessionManager.get_recommendations(),
        model_name,
        params,
        similarity_provider=similarity_provider,
    )

    render_visualizations_panel(user_id, stats_aggregator)


if __name__ == "__main__":
    main()
