"""Performance dashboard component for the RecoLab app (Feature 008, Task-002).

Renders the evaluation dashboard in the main area: a K cut-off selector
(persisted via ``SessionManager``), headline KPI metric cards, and chart
sections backed by :class:`MetricsProvider`. Every displayed number comes from
the provider — never hardcoded — and missing evaluation data degrades to an
informative empty state.
"""

from __future__ import annotations

import streamlit as st

from ui.dashboard.metrics_provider import ALLOWED_K, MODEL_NAMES, MetricsProvider
from ui.dashboard.model_comparison_chart import render_model_comparison_chart
from ui.session_manager import SessionManager


def _render_kpi_cards(metrics_provider: MetricsProvider, k: int) -> None:
    """Show headline KPIs: best model by NDCG@K, coverage, and user count."""
    comparison = metrics_provider.get_comparison_metrics(k)

    best_model, best_ndcg = "—", 0.0
    coverage, n_users = 0.0, 0
    for name in MODEL_NAMES:
        metrics = comparison.get(name, {})
        ndcg = float(metrics.get(f"mean_ndcg@{k}", 0.0))
        if ndcg > best_ndcg:
            best_model, best_ndcg = name, ndcg
        coverage = max(coverage, float(metrics.get("catalog_coverage", 0.0)))
        n_users = max(n_users, int(metrics.get("n_users", 0)))

    col1, col2, col3 = st.columns(3)
    col1.metric("Best Model (NDCG)", best_model, help=f"Highest mean NDCG@{k} across all models")
    col2.metric(f"NDCG@{k}", f"{best_ndcg:.3f}")
    col3.metric("Catalog Coverage", f"{coverage:.1%}")

    st.caption(f"Evaluated over {n_users} held-out test users at cut-off K={k}.")


def render_performance_dashboard(metrics_provider: MetricsProvider) -> None:
    """Render the full performance dashboard for the current session."""
    st.markdown("### 📊 Performance Dashboard")
    st.caption(
        "Offline evaluation of the five recommendation models on the held-out "
        "test split. Metrics come from the evaluation framework, not hardcoded values."
    )

    # K selector, persisted through the session-managed dashboard state.
    current_k = SessionManager.get_selected_k_value()
    if current_k not in ALLOWED_K:
        current_k = ALLOWED_K[1]
    k = st.selectbox(
        "Evaluation Cut-Off (K)",
        options=list(ALLOWED_K),
        index=ALLOWED_K.index(current_k),
        key="dashboard_k_selector",
    )
    SessionManager.set_selected_k_value(int(k))

    st.markdown("---")
    st.markdown("#### Key Performance Indicators")
    _render_kpi_cards(metrics_provider, k)

    st.markdown("#### Model Comparison")
    render_model_comparison_chart(metrics_provider, k)

    st.markdown("#### Metric Breakdown")
    _render_metric_breakdown(metrics_provider, k)


def _render_metric_breakdown(metrics_provider: MetricsProvider, k: int) -> None:
    """Table of every model's P@K / R@K / NDCG@K at the chosen cut-off."""
    comparison = metrics_provider.get_comparison_metrics(k)

    rows = [
        {
            "Model": name,
            f"Precision@{k}": round(float(m.get(f"mean_precision@{k}", 0.0)), 4),
            f"Recall@{k}": round(float(m.get(f"mean_recall@{k}", 0.0)), 4),
            f"NDCG@{k}": round(float(m.get(f"mean_ndcg@{k}", 0.0)), 4),
        }
        for name, m in comparison.items()
    ]
    if not rows or all(
        row[f"NDCG@{k}"] == 0.0 for row in rows
    ):
        st.info("No evaluation data available to tabulate yet.")
        return

    st.dataframe(
        rows,
        use_container_width=True,
        hide_index=True,
    )
