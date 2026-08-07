"""Side-by-side model comparison view (Feature 008, Tasks 006-008).

Renders the comparison payload from :class:`ModelComparisonEngine`: a
rank-aligned table of each model's recommendations with cross-model agreement
highlighting, a Jaccard agreement analysis, a performance comparison table with
best-per-metric highlighting, and a model-selection recommendation callout.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

import pandas as pd
import streamlit as st

from ui.dashboard.metrics_provider import MODEL_NAMES, MetricsProvider
from ui.dashboard.model_comparison_engine import ModelComparisonEngine
from ui.data_provider import DataProvider
from ui.session_manager import SessionManager

# Cross-model agreement colouring (row backgrounds in the side-by-side table).
_SHARED_STYLE = "background-color: #d4edda;"  # movie appears in 2+ models
_UNIQUE_STYLE = "background-color: #f5f5f5;"  # movie unique to one model


def _degree_label(percentage: float) -> str:
    """Human label for a Jaccard agreement percentage."""
    if percentage >= 50:
        return "High agreement"
    if percentage >= 20:
        return "Moderate"
    return "Low / none"


def render_model_comparison_view(
    comparison_engine: ModelComparisonEngine,
    metrics_provider: MetricsProvider,
    provider: DataProvider,
    user_id: int,
) -> None:
    """Render the full side-by-side comparison view for ``user_id``."""
    st.markdown("### 🤝 Model Comparison")
    st.caption(
        "Compare what each model recommends for this user, how much they "
        "agree, and how they perform offline on the held-out test split."
    )

    current_k = SessionManager.get_selected_k_value()
    if current_k not in (5, 10, 20):
        current_k = 10
    k = st.selectbox(
        "Evaluation Cut-Off (K)",
        options=[5, 10, 20],
        index=[5, 10, 20].index(current_k),
        key="comparison_k_selector",
    )
    SessionManager.set_selected_k_value(int(k))

    selected = st.multiselect(
        "Models to compare",
        options=MODEL_NAMES,
        default=SessionManager.get_selected_models_for_comparison() or MODEL_NAMES,
        key="comparison_models_multiselect",
    )
    SessionManager.set_selected_models_for_comparison(selected)

    if not selected:
        st.info("Select at least one model to compare.")
        return

    with st.spinner("Generating model outputs for comparison..."):
        comparison = comparison_engine.compare_models(user_id, k=k, models=selected)

    _render_selection_recommendation(comparison_engine, k)

    st.markdown("#### Side-by-Side Outputs")
    _render_side_by_side(comparison, provider)

    if SessionManager.should_show_agreement_analysis():
        st.markdown("#### Model Agreement (Jaccard)")
        _render_agreement_table(comparison["agreement_analysis"])

    st.markdown("#### Performance Comparison")
    _render_performance_table(comparison["performance_comparison"], k)


def _render_selection_recommendation(
    comparison_engine: ModelComparisonEngine,
    k: int,
) -> None:
    """Callout recommending a primary model with a metrics-based rationale."""
    profile = SessionManager.get_user_profile()
    rec = comparison_engine.recommend_models(
        k=k,
        rating_count=profile.get("rating_count"),
    )
    st.success(
        f"**Recommended model:** {rec['primary_model']} — {rec['rationale']}"
    )


def _render_side_by_side(
    comparison: dict[str, Any],
    provider: DataProvider,
) -> None:
    """Rank-aligned table of each model's recommendations with highlighting."""
    outputs: dict[str, list[int]] = comparison["model_outputs"]
    names = list(outputs)
    max_len = max((len(v) for v in outputs.values()), default=0)
    if max_len == 0:
        st.info("No recommendations were generated for any model.")
        return

    # Count how many models recommend each movie id (for highlighting).
    id_counts: Counter[int] = Counter(
        mid for recs in outputs.values() for mid in recs
    )
    cell_ids: dict[tuple[str, int], int | None] = {}
    rows: list[dict[str, Any]] = []
    for i in range(max_len):
        row: dict[str, Any] = {"Rank": i + 1}
        for name in names:
            recs = outputs[name]
            mid = recs[i] if i < len(recs) else None
            cell_ids[(name, i)] = mid
            movie = provider.get_movie(mid) if mid is not None else {}
            row[name] = (movie or {}).get("title") or f"Movie {mid}" if mid else "—"
        rows.append(row)

    df = pd.DataFrame(rows, columns=["Rank"] + names)

    def _style_rows(_: pd.DataFrame) -> pd.DataFrame:
        styled = pd.DataFrame("", index=df.index, columns=df.columns)
        for (col, i), mid in cell_ids.items():
            if mid is None:
                continue
            styled.at[i, col] = _SHARED_STYLE if id_counts[mid] > 1 else _UNIQUE_STYLE
        return styled

    st.dataframe(
        df.style.apply(_style_rows, axis=None),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(
        "Green cells are movies recommended by more than one model; grey cells "
        "are unique to a single model."
    )


def _render_agreement_table(
    agreements: dict[str, dict[str, Any]],
) -> None:
    """Table of pair-wise Jaccard similarity between model outputs."""
    if not agreements:
        st.info("Agreement analysis requires at least two models.")
        return
    rows = [
        {
            "Model A": pair["model_a"],
            "Model B": pair["model_b"],
            "Overlap": pair["overlap_count"],
            "Jaccard": pair["jaccard_similarity"],
            "Agreement %": pair["agreement_percentage"],
            "Degree": _degree_label(pair["agreement_percentage"]),
        }
        for pair in agreements.values()
    ]
    rows.sort(key=lambda r: r["Jaccard"], reverse=True)
    st.dataframe(rows, use_container_width=True, hide_index=True)


def _render_performance_table(
    performance: dict[str, dict[str, float]],
    k: int,
) -> None:
    """P@K / R@K / NDCG@K table with the best value per metric highlighted."""
    if not performance:
        st.info("No performance data available.")
        return
    metric_cols = [f"mean_precision@{k}", f"mean_recall@{k}", f"mean_ndcg@{k}"]
    rows = [
        {
            "Model": name,
            "Precision": metrics.get(f"mean_precision@{k}", 0.0),
            "Recall": metrics.get(f"mean_recall@{k}", 0.0),
            "NDCG": metrics.get(f"mean_ndcg@{k}", 0.0),
            "Coverage": metrics.get("catalog_coverage", 0.0),
        }
        for name, metrics in performance.items()
    ]
    df = pd.DataFrame(rows)
    if float(df["NDCG"].sum()) == 0:
        st.info("No evaluation data available to tabulate yet.")
        return

    def _style_perf(_: pd.DataFrame) -> pd.DataFrame:
        styled = pd.DataFrame("", index=df.index, columns=df.columns)
        for col in ("Precision", "Recall", "NDCG"):
            best_idx = df[col].idxmax()
            styled.at[best_idx, col] = "font-weight: bold; color: #1e3a8a;"
        return styled

    st.dataframe(
        df.style.apply(_style_perf, axis=None).format(
            {"Precision": "{:.3f}", "Recall": "{:.3f}", "NDCG": "{:.3f}", "Coverage": "{:.1%}"}
        ),
        use_container_width=True,
        hide_index=True,
    )
    st.caption(f"Bold blue values mark the best model for each metric at K={k}.")
