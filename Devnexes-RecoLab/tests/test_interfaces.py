"""Tests for shared recommendation model interfaces.

Verifies that:
1. PopularityModel (Week 1) satisfies the Recommender protocol
2. FeatureError carries movie_id attribute correctly
3. FeatureError message format is as expected
4. ContentModel (Week 2) will satisfy both protocols (placeholder)
"""

from __future__ import annotations

import pandas as pd
import pytest

from recolab.baseline import PopularityModel
from recolab.interfaces import FeatureError, Recommender


@pytest.fixture
def train_df() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "userId": [1, 1, 1, 2, 2, 3],
            "movieId": [10, 20, 30, 10, 20, 40],
            "rating": [5.0, 4.0, 3.0, 5.0, 4.0, 2.0],
            "timestamp": pd.to_datetime(
                ["2000-01-01", "2000-01-02", "2000-01-03",
                 "2000-01-01", "2000-01-02", "2000-01-01"]
            ),
        }
    )


def test_popularity_satisfies_recommender_protocol(train_df: pd.DataFrame) -> None:
    """Verify PopularityModel (Week 1) satisfies Recommender protocol (AC-007)."""
    model = PopularityModel().fit(train_df)
    assert isinstance(model, Recommender)
    # Verify the method signature is correct
    recs = model.recommend(user_id=1, k=3, exclude_items={10, 20})
    assert isinstance(recs, list)
    assert all(isinstance(item, int) for item in recs)


def test_feature_error_carries_movie_id() -> None:
    """Verify FeatureError carries movie_id attribute correctly."""
    error = FeatureError("No genres found", movie_id=123)
    assert error.movie_id == 123
    assert str(error) == "movie_id=123: No genres found"


def test_feature_error_message_format() -> None:
    """Verify FeatureError message format when movie_id is None."""
    error = FeatureError("Generic error")
    assert error.movie_id is None
    assert str(error) == "Generic error"


def test_feature_error_inheritance() -> None:
    """Verify FeatureError inherits from ValueError."""
    error = FeatureError("Test error")
    assert isinstance(error, ValueError)
    assert isinstance(error, Exception)


@pytest.mark.skip(
    reason="ContentModel not yet implemented - will be unskipped in Phase 4"
)
def test_content_satisfies_protocols() -> None:
    """Placeholder: ContentModel must satisfy both Recommender and ColdStartHandler."""
    # This test will be unskipped in Phase 4 after ContentModel implementation
    # from recolab.content import ContentModel
    # model = ContentModel().fit(movies_df)
    # assert isinstance(model, Recommender)
    # assert isinstance(model, ColdStartHandler)
    pass
