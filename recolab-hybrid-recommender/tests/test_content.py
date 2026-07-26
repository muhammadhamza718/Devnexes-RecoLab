"""Tests for ContentModel (Phase 4a: init and fit)."""

from __future__ import annotations

import pandas as pd
import pytest

from recolab.content import ContentModel
from recolab.interfaces import ColdStartHandler, FeatureError, Recommender


@pytest.fixture
def sample_ratings() -> pd.DataFrame:
    """Sample ratings DataFrame for testing."""
    return pd.DataFrame({
        "userId": [1, 1, 2, 2, 3, 3, 4, 4],
        "movieId": [10, 20, 10, 30, 20, 40, 30, 50],
        "rating": [5.0, 4.0, 5.0, 3.0, 4.0, 2.0, 3.0, 5.0],
        "timestamp": pd.to_datetime([
            "2000-01-01", "2000-01-02", "2000-01-01",
            "2000-01-02", "2000-01-01", "2000-01-02",
            "2000-01-01", "2000-01-02"
        ]),
    })


@pytest.fixture
def sample_movies() -> pd.DataFrame:
    """Sample movies DataFrame with genres."""
    return pd.DataFrame({
        "movieId": [10, 20, 30, 40, 50],
        "title": ["Movie A", "Movie B", "Movie C", "Movie D", "Movie E"],
        "genres": ["Action", "Action|Sci-Fi", "Drama", "Comedy", "Action|Drama"],
    })


class TestContentModelInit:
    """Test ContentModel initialization."""
    
    def test_default_initialization(self):
        """Test model initializes with empty state."""
        model = ContentModel()
        assert model.item_features == {}
        assert model.item_index == {}
        assert model.tfidf_matrix is None
        assert model.item_popularity == {}
        assert model.fitted is False
    
    def test_initialization_with_params(self):
        """Test model initialization with parameters."""
        model = ContentModel(
            item_features={1: "Action", 2: "Drama"},
            item_popularity={1: 10.0, 2: 5.0},
        )
        assert model.item_features == {1: "Action", 2: "Drama"}
        assert model.item_popularity == {1: 10.0, 2: 5.0}
        assert model.fitted is False


class TestContentModelFit:
    """Test ContentModel.fit() method."""
    
    def test_fit_builds_item_features(self, sample_ratings, sample_movies):
        """Test fit() builds item_features from movies."""
        model = ContentModel()
        model.fit(sample_ratings, sample_movies)
        
        assert len(model.item_features) == 5
        assert 10 in model.item_features
        assert model.item_features[10] == "Action"
        assert model.item_features[20] == "Action Sci-Fi"
    
    def test_fit_without_movies(self, sample_ratings):
        """Test fit() works without movies DataFrame."""
        model = ContentModel()
        model.fit(sample_ratings)
        
        # Should not crash, just have empty features
        assert model.item_features == {}
    
    def test_fit_computes_tfidf_matrix(self, sample_ratings, sample_movies):
        """Test fit() computes TF-IDF matrix."""
        model = ContentModel()
        model.fit(sample_ratings, sample_movies)
        
        assert model.tfidf_matrix is not None
        assert model.tfidf_matrix.shape[0] == 5  # 5 items
        assert len(model.item_index) == 5
    
    def test_fit_computes_popularity(self, sample_ratings, sample_movies):
        """Test fit() computes item popularity."""
        model = ContentModel()
        model.fit(sample_ratings, sample_movies)
        
        assert len(model.item_popularity) > 0
        # Items 10 and 20 appear twice, others once
        assert model.item_popularity[10] == 2
        assert model.item_popularity[20] == 2
        assert model.item_popularity[30] == 2
        assert model.item_popularity[40] == 1
        assert model.item_popularity[50] == 1
    
    def test_fit_sets_fitted_flag(self, sample_ratings, sample_movies):
        """Test fit() sets fitted flag to True."""
        model = ContentModel()
        assert model.fitted is False
        
        model.fit(sample_ratings, sample_movies)
        assert model.fitted is True
    
    def test_fit_returns_self(self, sample_ratings, sample_movies):
        """Test fit() returns self for method chaining."""
        model = ContentModel()
        result = model.fit(sample_ratings, sample_movies)
        
        assert result is model
    
    def test_fit_missing_columns_raises(self, sample_movies):
        """Test fit() raises ValueError with missing columns."""
        bad_ratings = pd.DataFrame({
            "user": [1, 2],  # Wrong column name
            "movieId": [10, 20],
            "rating": [5.0, 4.0],
        })
        
        model = ContentModel()
        with pytest.raises(ValueError, match="Missing required columns"):
            model.fit(bad_ratings, sample_movies)
    
    def test_fit_empty_ratings(self, sample_movies):
        """Test fit() handles empty ratings DataFrame."""
        empty_ratings = pd.DataFrame(columns=["userId", "movieId", "rating", "timestamp"])
        
        model = ContentModel()
        model.fit(empty_ratings, sample_movies)
        
        assert model.fitted is True
        assert model.item_popularity == {}


class TestContentModelRecommenderProtocol:
    """Test ContentModel satisfies Recommender protocol."""
    
    def test_implements_recommender_protocol(self, sample_ratings, sample_movies):
        """Test ContentModel satisfies Recommender protocol."""
        from recolab.interfaces import Recommender
        from typing_extensions import runtime_checkable
        
        model = ContentModel().fit(sample_ratings, sample_movies)
        assert isinstance(model, runtime_checkable(Recommender))
    
    def test_recommend_requires_fit(self):
        """Test recommend() raises ValueError when not fitted."""
        model = ContentModel()
        
        with pytest.raises(ValueError, match="must be fitted"):
            model.recommend(user_id=1, k=5)
    
    def test_recommend_basic_call(self, sample_ratings, sample_movies):
        """Test recommend() basic functionality."""
        model = ContentModel().fit(sample_ratings, sample_movies)
        
        recs = model.recommend(user_id=1, k=3)
        
        assert isinstance(recs, list)
        assert len(recs) <= 3
        assert all(isinstance(item_id, int) for item_id in recs)


class TestContentModelColdStartHandlerProtocol:
    """Test ContentModel satisfies ColdStartHandler protocol."""
    
    def test_implements_cold_start_handler_protocol(self, sample_ratings, sample_movies):
        """Test ContentModel satisfies ColdStartHandler protocol."""
        from recolab.interfaces import ColdStartHandler
        from typing_extensions import runtime_checkable
        
        model = ContentModel().fit(sample_ratings, sample_movies)
        assert isinstance(model, runtime_checkable(ColdStartHandler))
    
    def test_recommend_cold_start_requires_fit(self):
        """Test recommend_cold_start() raises ValueError when not fitted."""
        model = ContentModel()

        with pytest.raises(ValueError, match="must be fitted"):
            model.recommend_cold_start(genres=["Action"], liked_movie_ids=[], k=5)
    
    def test_recommend_cold_start_basic_call(self, sample_ratings, sample_movies):
        """Test recommend_cold_start() basic functionality."""
        model = ContentModel().fit(sample_ratings, sample_movies)

        recs = model.recommend_cold_start(genres=["Action"], liked_movie_ids=[], k=3)

        assert isinstance(recs, list)
        assert len(recs) <= 3
        assert all(isinstance(item_id, int) for item_id in recs)

    def test_recommend_cold_start_raises_on_empty_query(self, sample_ratings, sample_movies):
        """Test recommend_cold_start() raises FeatureError when both args empty."""
        model = ContentModel().fit(sample_ratings, sample_movies)

        with pytest.raises(FeatureError, match="Cannot recommend without"):
            model.recommend_cold_start(genres=[], liked_movie_ids=[], k=3)


class TestContentModelSimilarItems:
    """Test ContentModel.similar_items() method."""
    
    def test_similar_items_requires_fit(self):
        """Test similar_items() raises ValueError when not fitted."""
        model = ContentModel()
        
        with pytest.raises(ValueError, match="must be fitted"):
            model.similar_items(item_id=10, k=5)
    
    def test_similar_items_unknown_item_raises(self, sample_ratings, sample_movies):
        """Test similar_items() raises FeatureError for unknown item."""
        model = ContentModel().fit(sample_ratings, sample_movies)
        
        with pytest.raises(FeatureError, match="not found in model"):
            model.similar_items(item_id=999, k=5)
    
    def test_similar_items_basic_call(self, sample_ratings, sample_movies):
        """Test similar_items() basic functionality."""
        model = ContentModel().fit(sample_ratings, sample_movies)
        
        similar = model.similar_items(item_id=10, k=3)
        
        assert isinstance(similar, list)
        assert len(similar) <= 3
        assert all(isinstance(item, tuple) and len(item) == 2 for item in similar)
        assert all(isinstance(item_id, int) and isinstance(score, float) 
                   for item_id, score in similar)
    
    def test_similar_items_returns_scores_descending(self, sample_ratings, sample_movies):
        """Test similar_items() returns items sorted by similarity score."""
        model = ContentModel().fit(sample_ratings, sample_movies)
        
        similar = model.similar_items(item_id=10, k=5)
        
        if len(similar) > 1:
            scores = [score for _, score in similar]
            assert scores == sorted(scores, reverse=True)