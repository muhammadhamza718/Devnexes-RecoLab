"""Tests for SimilarityProvider (Day 3 Afternoon, Task-004)."""

import pandas as pd
import pytest
from unittest.mock import Mock, MagicMock

from ui.similarity_provider import SimilarityProvider, CONTENT_MODEL, ITEM_CF_MODEL


class TestSimilarityProvider:
    """Test SimilarityProvider similarity computation and fallback logic."""

    def test_initialization(self):
        """Verify SimilarityProvider initializes correctly."""
        model_manager = Mock()
        data_provider = Mock()

        provider = SimilarityProvider(model_manager, data_provider)
        assert provider.model_manager is model_manager
        assert provider.data_provider is data_provider

    def test_initialization_without_data_provider(self):
        """Verify SimilarityProvider creates default DataProvider if none provided."""
        model_manager = Mock()
        provider = SimilarityProvider(model_manager)

        assert provider.model_manager is model_manager
        assert provider.data_provider is not None

    def test_model_name_constants(self):
        """Verify model name constants are defined correctly."""
        assert CONTENT_MODEL == "Content"
        assert ITEM_CF_MODEL == "Item-Based CF"

    def test_content_similar_empty_on_model_error(self):
        """Verify _content_similar returns empty list on model errors."""
        model_manager = Mock()
        model_manager.get_model.side_effect = KeyError("Model not found")
        data_provider = Mock()

        provider = SimilarityProvider(model_manager, data_provider)
        result = provider._content_similar(1, k=5)

        assert result == []

    def test_item_cf_similar_empty_on_model_error(self):
        """Verify _item_cf_similar returns empty list on model errors."""
        model_manager = Mock()
        model_manager.get_model.side_effect = KeyError("Model not found")
        data_provider = Mock()

        provider = SimilarityProvider(model_manager, data_provider)
        result = provider._item_cf_similar(1, k=5)

        assert result == []

    def test_popularity_fallback_structure(self):
        """Verify _popular_fallback returns properly structured results."""
        model_manager = Mock()
        data_provider = Mock()

        # Mock the _train attribute to return a real DataFrame
        train_df = pd.DataFrame({
            "movieId": [1, 2, 3, 4, 5, 1, 2, 3]  # Multiple ratings per movie
        })
        data_provider._train = train_df

        provider = SimilarityProvider(model_manager, data_provider)
        result = provider._popular_fallback(movie_id=1, k=3)

        assert isinstance(result, list)
        assert len(result) <= 3
        # All results should be tuples of (movie_id, score)
        assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
        # Should exclude the target movie_id
        assert all(item[0] != 1 for item in result)

    def test_enrich_method_structure(self):
        """Verify _enrich method adds metadata correctly."""
        model_manager = Mock()
        data_provider = Mock()
        # Mock get_movie to return a movie dict
        data_provider.get_movie.return_value = {
            "movieId": 1,
            "title": "Test Movie",
            "genres": "Action|Drama",
            "year": 2020
        }

        provider = SimilarityProvider(model_manager, data_provider)
        enriched = provider._enrich(1, 0.85)

        assert enriched["movie_id"] == 1
        assert enriched["similarity"] == 0.85
        assert enriched["title"] == "Test Movie"
        assert enriched["genres"] == "Action|Drama"
        assert enriched["year"] == 2020

    def test_enrich_method_unknown_movie(self):
        """Verify _enrich handles unknown movies gracefully."""
        model_manager = Mock()
        data_provider = Mock()
        data_provider.get_movie.return_value = None

        provider = SimilarityProvider(model_manager, data_provider)
        enriched = provider._enrich(999, 0.5)

        assert enriched["movie_id"] == 999
        assert enriched["similarity"] == 0.5
        assert enriched["title"] == "Movie 999"
        assert enriched["genres"] == ""
        assert enriched["year"] is None
