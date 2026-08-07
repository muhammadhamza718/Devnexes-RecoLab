"""Tests for StatisticsAggregator (Day 3 Afternoon, Task-007)."""

import pandas as pd
import pytest
from unittest.mock import Mock, MagicMock

from ui.statistics_aggregator import StatisticsAggregator


class TestStatisticsAggregator:
    """Test StatisticsAggregator statistics computation and caching."""

    def test_initialization(self):
        """Verify StatisticsAggregator initializes correctly."""
        data_provider = Mock()
        aggregator = StatisticsAggregator(data_provider)

        assert aggregator.data_provider is data_provider
        assert isinstance(aggregator.cache, dict)

    def test_get_rating_timeline_empty_user(self):
        """Verify get_rating_timeline handles users with no ratings."""
        data_provider = Mock()
        # Mock train data with no ratings for user 999
        data_provider.train = pd.DataFrame({
            "userId": [1, 2],
            "movieId": [10, 20],
            "rating": [4.0, 5.0],
            "timestamp": [1000000, 2000000]
        })

        aggregator = StatisticsAggregator(data_provider)
        timeline = aggregator.get_rating_timeline(999)

        assert isinstance(timeline, pd.DataFrame)
        assert timeline.empty
        assert list(timeline.columns) == ["timestamp", "rating"]

    def test_get_rating_timeline_with_data(self):
        """Verify get_rating_timeline returns correct timeline data."""
        data_provider = Mock()
        # Mock train data with ratings for user 1
        data_provider.train = pd.DataFrame({
            "userId": [1, 1, 1],
            "movieId": [10, 20, 30],
            "rating": [4.0, 5.0, 3.0],
            "timestamp": [1000000, 2000000, 3000000]
        })

        aggregator = StatisticsAggregator(data_provider)
        timeline = aggregator.get_rating_timeline(1)

        assert isinstance(timeline, pd.DataFrame)
        assert len(timeline) == 3
        assert "timestamp" in timeline.columns
        assert "rating" in timeline.columns
        # Verify sorted by timestamp
        assert timeline["timestamp"].is_monotonic_increasing

    def test_get_rating_timeline_caching(self):
        """Verify get_rating_timeline caches results."""
        data_provider = Mock()
        data_provider.train = pd.DataFrame({
            "userId": [1],
            "movieId": [10],
            "rating": [4.0],
            "timestamp": [1000000]
        })

        aggregator = StatisticsAggregator(data_provider)

        # First call
        timeline1 = aggregator.get_rating_timeline(1)
        # Second call should use cache
        timeline2 = aggregator.get_rating_timeline(1)

        assert timeline1.equals(timeline2)
        # Verify cache was populated
        cache_key = f"rating_timeline_1"
        assert cache_key in aggregator.cache

    def test_get_rating_distribution_empty_user(self):
        """Verify get_rating_distribution handles users with no ratings."""
        data_provider = Mock()
        data_provider.train = pd.DataFrame({
            "userId": [1, 2],
            "movieId": [10, 20],
            "rating": [4.0, 5.0]
        })

        aggregator = StatisticsAggregator(data_provider)
        distribution = aggregator.get_rating_distribution(999)

        assert isinstance(distribution, dict)
        assert len(distribution) == 0

    def test_get_rating_distribution_with_data(self):
        """Verify get_rating_distribution returns correct distribution."""
        data_provider = Mock()
        data_provider.train = pd.DataFrame({
            "userId": [1, 1, 1, 1],
            "movieId": [10, 20, 30, 40],
            "rating": [4.0, 5.0, 4.0, 3.0]
        })

        aggregator = StatisticsAggregator(data_provider)
        distribution = aggregator.get_rating_distribution(1)

        assert isinstance(distribution, dict)
        assert distribution[4.0] == 2  # Two 4.0 ratings
        assert distribution[5.0] == 1  # One 5.0 rating
        assert distribution[3.0] == 1  # One 3.0 rating

    def test_get_rating_distribution_caching(self):
        """Verify get_rating_distribution caches results."""
        data_provider = Mock()
        data_provider.train = pd.DataFrame({
            "userId": [1],
            "movieId": [10],
            "rating": [4.0]
        })

        aggregator = StatisticsAggregator(data_provider)

        # First call
        dist1 = aggregator.get_rating_distribution(1)
        # Second call should use cache
        dist2 = aggregator.get_rating_distribution(1)

        assert dist1 == dist2
        cache_key = f"rating_distribution_1"
        assert cache_key in aggregator.cache

    def test_get_genre_preferences_empty_user(self):
        """Verify get_genre_preferences handles users with no ratings."""
        data_provider = Mock()
        data_provider.train = pd.DataFrame({
            "userId": [1, 2],
            "movieId": [10, 20],
            "rating": [4.0, 5.0]
        })
        data_provider.get_movie.return_value = None

        aggregator = StatisticsAggregator(data_provider)
        preferences = aggregator.get_genre_preferences(999)

        assert isinstance(preferences, dict)
        assert len(preferences) == 0

    def test_get_genre_preferences_with_data(self):
        """Verify get_genre_preferences returns normalized preferences."""
        data_provider = Mock()
        data_provider.train = pd.DataFrame({
            "userId": [1, 1, 1],
            "movieId": [10, 20, 30],
            "rating": [4.0, 5.0, 3.0]
        })
        # Mock movie genres
        data_provider.get_movie.side_effect = [
            {"movieId": 10, "genres": "Action|Drama"},
            {"movieId": 20, "genres": "Action"},
            {"movieId": 30, "genres": "Drama|Comedy"}
        ]

        aggregator = StatisticsAggregator(data_provider)
        preferences = aggregator.get_genre_preferences(1)

        assert isinstance(preferences, dict)
        # Action appears in 2 movies, Drama in 2, Comedy in 1
        # Total genre occurrences: 5
        # Action: 2/5 = 0.4, Drama: 2/5 = 0.4, Comedy: 1/5 = 0.2
        assert abs(preferences.get("Action", 0) - 0.4) < 0.01
        assert abs(preferences.get("Drama", 0) - 0.4) < 0.01
        assert abs(preferences.get("Comedy", 0) - 0.2) < 0.01

    def test_get_genre_preferences_normalization(self):
        """Verify genre preferences sum to 1.0."""
        data_provider = Mock()
        data_provider.train = pd.DataFrame({
            "userId": [1, 1],
            "movieId": [10, 20],
            "rating": [4.0, 5.0]
        })
        data_provider.get_movie.side_effect = [
            {"movieId": 10, "genres": "Action|Drama"},
            {"movieId": 20, "genres": "Comedy"}
        ]

        aggregator = StatisticsAggregator(data_provider)
        preferences = aggregator.get_genre_preferences(1)

        total = sum(preferences.values())
        assert abs(total - 1.0) < 0.01

    def test_get_activity_heatmap_empty_user(self):
        """Verify get_activity_heatmap handles users with no ratings."""
        data_provider = Mock()
        data_provider.train = pd.DataFrame({
            "userId": [1, 2],
            "movieId": [10, 20],
            "rating": [4.0, 5.0],
            "timestamp": [1000000, 2000000]
        })

        aggregator = StatisticsAggregator(data_provider)
        heatmap = aggregator.get_activity_heatmap(999)

        assert isinstance(heatmap, pd.DataFrame)
        # Should return 7x24 matrix (days x hours)
        assert heatmap.shape == (7, 24)
        # All values should be 0
        assert (heatmap.values == 0).all()

    def test_get_activity_heatmap_structure(self):
        """Verify get_activity_heatmap returns correct structure."""
        data_provider = Mock()
        data_provider.train = pd.DataFrame({
            "userId": [1, 2],
            "movieId": [10, 20],
            "rating": [4.0, 5.0],
            "timestamp": [1000000, 2000000]
        })

        aggregator = StatisticsAggregator(data_provider)
        heatmap = aggregator.get_activity_heatmap(1)

        assert isinstance(heatmap, pd.DataFrame)
        # Should be 7 days x 24 hours
        assert heatmap.shape == (7, 24)
        # Index should be day names
        expected_days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        assert list(heatmap.index) == expected_days
        # Columns should be hours 0-23
        assert list(heatmap.columns) == list(range(24))

    def test_get_activity_heatmap_caching(self):
        """Verify get_activity_heatmap caches results."""
        data_provider = Mock()
        data_provider.train = pd.DataFrame({
            "userId": [1],
            "movieId": [10],
            "rating": [4.0],
            "timestamp": [1000000]
        })

        aggregator = StatisticsAggregator(data_provider)

        # First call
        heatmap1 = aggregator.get_activity_heatmap(1)
        # Second call should use cache
        heatmap2 = aggregator.get_activity_heatmap(1)

        assert heatmap1.equals(heatmap2)
        cache_key = f"activity_heatmap_1"
        assert cache_key in aggregator.cache

    def test_cache_persistence_across_methods(self):
        """Verify cache persists across different method calls."""
        data_provider = Mock()
        data_provider.train = pd.DataFrame({
            "userId": [1],
            "movieId": [10],
            "rating": [4.0],
            "timestamp": [1000000]
        })

        aggregator = StatisticsAggregator(data_provider)

        # Call multiple methods
        aggregator.get_rating_timeline(1)
        aggregator.get_rating_distribution(1)
        aggregator.get_genre_preferences(1)
        aggregator.get_activity_heatmap(1)

        # All should be in cache
        assert "rating_timeline_1" in aggregator.cache
        assert "rating_distribution_1" in aggregator.cache
        assert "genre_preferences_1" in aggregator.cache
        assert "activity_heatmap_1" in aggregator.cache
