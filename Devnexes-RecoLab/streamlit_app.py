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

SessionManager.ensure_initialized()

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

    with st.sidebar:
        st.header("Configuration")
        user_id = render_user_selector(provider)
        model_name, params = render_model_selector()

    if user_id is None:
        st.info("Select a user from the sidebar to get started.")
        return

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
