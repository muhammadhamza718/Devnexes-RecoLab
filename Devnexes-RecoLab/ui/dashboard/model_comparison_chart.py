"""Model comparison chart for the RecoLab dashboard (Feature 008, Task-003).

Renders an interactive grouped bar chart comparing all five models across the
three ranking metrics (Precision@K, Recall@K, NDCG@K) at a chosen cut-off K.
Every value comes from the :class:`MetricsProvider` — never hardcoded — and the
no-data case renders an ``st.info`` empty state instead of a blank chart.
"""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import streamlit as st

from ui.dashboard.metrics_provider import MODEL_NAMES, MetricsProvider

# metric key template -> display label (K is substituted at render time)
_METRIC_LABELS: dict[str, str] = {
    "mean_precision@{k}": "Precision@K",
    "mean_recall@{k}": "Recall@K",
    "mean_ndcg@{k}": "NDCG@K",
}


def render_model_comparison_chart(
    metrics_provider: MetricsProvider,
    k: int,
) -> None:
    """Render a grouped bar chart of P@K / R@K / NDCG@K across all models.

    The chart is only drawn when at least one model has real evaluation data
    (a non-zero value); otherwise a helpful empty-state message is shown.
    """
    comparison = metrics_provider.get_comparison_metrics(k)

    rows: list[dict[str, object]] = []
    for model_name in MODEL_NAMES:
        metrics = comparison.get(model_name, {})
        for key_template, label in _METRIC_LABELS.items():
            rows.append(
                {
                    "Model": model_name,
                    "Metric": label.format(k=k),
                    "Value": float(metrics.get(key_template.format(k=k), 0.0)),
                }
            )

    df = pd.DataFrame(rows)
    if df.empty or float(df["Value"].sum()) == 0:
        st.info(
            "No evaluation data available yet. Generate recommendations or drop "
            "pre-computed metric files under `data/evaluation/` to populate this chart."
        )
        return

    fig = px.bar(
        df,
        x="Model",
        y="Value",
        color="Metric",
        barmode="group",
        title=f"Model Comparison — P@{k} / R@{k} / NDCG@{k}",
        labels={"Model": "Model", "Value": "Score", "Metric": "Metric"},
    )
    fig.update_layout(legend_title_text="Metric", height=420)
    fig.update_yaxes(range=[0, 1])
    st.plotly_chart(fig, use_container_width=True)
