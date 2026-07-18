"""Tests for the RecoLab popularity baseline (Week 1, REQ-009)."""

from __future__ import annotations

import pandas as pd
import pytest

from recolab.baseline import PopularityModel, compute_popularity
from recolab.split import validate_no_leakage

ITEM_ID = "movieId"
RATING_COL = "rating"


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


def test_ranking_is_descending(train_df: pd.DataFrame) -> None:
    pop = compute_popularity(train_df, weight_by_rating=True)
    values = pop["popularity"].to_numpy()
    assert (values[:-1] >= values[1:]).all(), "popularity must be descending"
    # movieId 10 (5+5=10) and 20 (4+4=8) lead.
    assert pop[ITEM_ID].iloc[0] == 10


def test_exclude_items_removes_training_rated(train_df: pd.DataFrame) -> None:
    model = PopularityModel().fit(train_df)
    user1_train = {10, 20, 30}  # user 1's rated items
    recs = model.recommend(user_id=1, k=5, exclude_items=user1_train)
    assert set(recs).isdisjoint(user1_train)
    # Only item not rated by user 1 is movie 40.
    assert recs == [40]


def test_cold_start_user_gets_global_top_n(train_df: pd.DataFrame) -> None:
    model = PopularityModel().fit(train_df)
    # Cold-start: no training history -> global top-N regardless of user_id.
    recs = model.recommend(user_id=999, k=3, exclude_items=None)
    expected_global = model._global_top[:3]
    assert recs == expected_global
    assert len(recs) == 3


def test_user_with_all_items_rated_returns_empty(train_df: pd.DataFrame) -> None:
    model = PopularityModel().fit(train_df)
    all_items = set(train_df[ITEM_ID].unique())
    recs = model.recommend(user_id=1, k=5, exclude_items=all_items)
    assert recs == []


def test_reproducibility_same_input_same_output(train_df: pd.DataFrame) -> None:
    m1 = PopularityModel().fit(train_df)
    m2 = PopularityModel().fit(train_df)
    assert m1.recommend(1, k=5, exclude_items={10, 20, 30}) == m2.recommend(
        1, k=5, exclude_items={10, 20, 30}
    )


def test_save_and_load_roundtrip(train_df: pd.DataFrame, tmp_path) -> None:
    model = PopularityModel().fit(train_df)
    path = tmp_path / "model.pkl"
    model.save(path)
    loaded = PopularityModel.load(path)
    assert loaded._global_top == model._global_top
    assert loaded.recommend(1, k=3, exclude_items={10}) == model.recommend(
        1, k=3, exclude_items={10}
    )


def test_k_zero_returns_empty(train_df: pd.DataFrame) -> None:
    model = PopularityModel().fit(train_df)
    assert model.recommend(1, k=0, exclude_items={10}) == []


def test_unfitted_model_raises() -> None:
    model = PopularityModel()
    with pytest.raises(ValueError):
        model.recommend(1, k=3)
