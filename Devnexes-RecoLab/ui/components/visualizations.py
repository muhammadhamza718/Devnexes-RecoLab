"""Visualization panel component (Task-012).

Combines the four chart renderers from
:mod:`ui.visualization_components` into one collapsible panel. Charts are
computed lazily: the aggregator methods only run when the panel toggle is on,
satisfying the "lazy render charts when panel is expanded" performance
requirement from the plan. The toggle state persists through the
``visualization_panel_open`` session key.
"""

from __future__ import annotations

import streamlit as st

from ui.session_manager import SessionManager
from ui.statistics_aggregator import StatisticsAggregator
from ui.visualization_components import (
    render_activity_heatmap,
    render_genre_preferences,
    render_rating_distribution,
    render_rating_timeline,
)


def render_visualizations_panel(
    user_id: int,
    stats_aggregator: StatisticsAggregator,
) -> None:
    """Render the toggle and, when enabled, the user-statistics charts.

    Args:
        user_id: Selected user ID.
        stats_aggregator: Aggregator providing the chart data.
    """
    panel_open = st.checkbox(
        "Show visualizations",
        value=SessionManager.is_visualization_panel_open(),
        key="widget_visualization_panel_open",
        help="Compute and display charts for the selected user",
    )
    if not panel_open:
        return

    with st.expander("User Statistics & Activity", expanded=True):
        st.caption(
            "Aggregated from the selected user's ratings — timeline, "
            "distribution, genre preferences and activity heatmap."
        )
        col1, col2 = st.columns(2)
        with col1:
            render_rating_timeline(user_id, stats_aggregator)
            render_rating_distribution(user_id, stats_aggregator)
        with col2:
            render_genre_preferences(user_id, stats_aggregator)
        render_activity_heatmap(user_id, stats_aggregator)
