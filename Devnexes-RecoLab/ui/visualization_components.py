"""Visualization components for user statistics (Tasks 008-011).

Renders Plotly charts from :class:`ui.statistics_aggregator.StatisticsAggregator`
data: a rating history timeline, a rating distribution histogram, a genre
preference bar chart, and a day-of-week x hour-of-day activity heatmap. Each
renderer handles the empty-data case with an ``st.info`` message so charts
never render without content.
"""

from __future__ import annotations

import plotly.express as px
import streamlit as st

from ui.statistics_aggregator import StatisticsAggregator


def render_rating_timeline(
    user_id: int,
    stats_aggregator: StatisticsAggregator,
) -> None:
    """Render the user's rating history as an interactive line chart."""
    timeline = stats_aggregator.get_rating_timeline(user_id)
    if timeline.empty:
        st.info("No rating history available for this user.")
        return
    fig = px.line(
        timeline,
        x="timestamp",
        y="rating",
        title="Rating History Timeline",
        labels={"timestamp": "Date", "rating": "Rating"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_rating_distribution(
    user_id: int,
    stats_aggregator: StatisticsAggregator,
) -> None:
    """Render the user's rating values as a histogram-style bar chart."""
    distribution = stats_aggregator.get_rating_distribution(user_id)
    if not distribution:
        st.info("No rating distribution available for this user.")
        return
    fig = px.bar(
        x=list(distribution.keys()),
        y=list(distribution.values()),
        title="Rating Distribution",
        labels={"x": "Rating", "y": "Count"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_genre_preferences(
    user_id: int,
    stats_aggregator: StatisticsAggregator,
) -> None:
    """Render the user's normalized genre preferences as percentages."""
    preferences = stats_aggregator.get_genre_preferences(user_id)
    if not preferences:
        st.info("No genre preferences available for this user.")
        return
    sorted_genres = sorted(preferences.items(), key=lambda item: item[1], reverse=True)
    fig = px.bar(
        x=[genre for genre, _ in sorted_genres],
        y=[share * 100 for _, share in sorted_genres],
        title="Genre Preferences",
        labels={"x": "Genre", "y": "Preference %"},
    )
    st.plotly_chart(fig, use_container_width=True)


def render_activity_heatmap(
    user_id: int,
    stats_aggregator: StatisticsAggregator,
) -> None:
    """Render the user's rating activity as a day-of-week x hour heatmap.

    The aggregator always returns a full 7x24 matrix, so an all-zero matrix is
    treated as "no activity" to show the empty state instead of a blank chart.
    """
    heatmap = stats_aggregator.get_activity_heatmap(user_id)
    if heatmap.empty or float(heatmap.to_numpy().sum()) == 0:
        st.info("No activity data available for this user.")
        return
    fig = px.imshow(
        heatmap,
        title="Activity Heatmap (Day vs Hour)",
        labels=dict(x="Hour of Day", y="Day of Week", color="Rating Count"),
        color_continuous_scale="Viridis",
    )
    st.plotly_chart(fig, use_container_width=True)
