"""Tests for :mod:`recolab.metrics` — hand-implemented top-N ranking metrics.

Each known-case test asserts an exact analytic result so we prove correctness
without relying on scikit-learn (which has no NDCG@K and whose
``top_k_accuracy_score`` is NOT a Precision/Recall/NDCG substitute).
"""

from __future__ import annotations

import math

import pandas as pd
import pytest

from recolab.metrics import (
    evaluate_all,
    evaluate_user,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)

# ---------------------------------------------------------------------------
# 1. Precision@K known cases
# ---------------------------------------------------------------------------


def test_precision_at_k_exact():
    # recommended=[A,B,C], relevant={A,C}, k=2 -> hits={A}=1 / 2 = 0.5
    assert precision_at_k(["A", "B", "C"], {"A", "C"}, 2) == pytest.approx(0.5)


def test_precision_at_k_no_relevant_in_topk():
    assert precision_at_k(["A", "B"], {"C"}, 2) == 0.0


def test_precision_at_k_zero_k():
    assert precision_at_k(["A", "B"], {"A"}, 0) == 0.0


# ---------------------------------------------------------------------------
# 2. Recall@K known cases
# ---------------------------------------------------------------------------


def test_recall_at_k_exact():
    # recommended=[A,B,C], relevant={A,C,D}, k=3 -> hits={A,C}=2 / 3
    assert recall_at_k(["A", "B", "C"], {"A", "C", "D"}, 3) == pytest.approx(2 / 3)


def test_recall_at_k_all_relevant_covered():
    # relevant smaller than k, all at top -> recall = 1.0
    assert recall_at_k(["A", "B", "C"], {"A", "B"}, 3) == pytest.approx(1.0)


def test_recall_at_k_empty_relevant():
    assert recall_at_k(["A", "B"], set(), 3) == 0.0


# ---------------------------------------------------------------------------
# 3. NDCG@K known cases
# ---------------------------------------------------------------------------


def test_ndcg_at_k_relevant_at_top_is_one():
    # relevant={A} at position 0 -> ideal, NDCG = 1.0
    assert ndcg_at_k(["A", "B", "C"], {"A"}, 3) == pytest.approx(1.0)


def test_ndcg_at_k_relevant_at_second_position():
    # relevant={A} at position 1 -> 1/log2(3) ~ 0.6309
    expected = 1.0 / math.log2(3.0)
    assert ndcg_at_k(["B", "A", "C"], {"A"}, 3) == pytest.approx(expected)


def test_ndcg_at_k_relevant_set_smaller_than_k():
    # Only one relevant item; k=10. Graceful: ideal DCG uses the single gain.
    assert ndcg_at_k(["A", "B", "C"], {"A"}, 10) == pytest.approx(1.0)
    # None relevant -> 0.0
    assert ndcg_at_k(["B", "C"], {"A"}, 10) == 0.0


# ---------------------------------------------------------------------------
# 4. REQ-009 exclude-known-items guard in evaluate_user
# ---------------------------------------------------------------------------


def test_evaluate_user_raises_on_train_leakage():
    with pytest.raises(AssertionError):
        evaluate_user(
            user_id=1,
            recommended=["A", "B"],  # "A" is a training item -> leakage
            test_items={"C"},
            train_items={"A"},
            ks=[5],
        )


def test_evaluate_user_clean_pass():
    m = evaluate_user(
        user_id=1,
        recommended=["A", "B"],
        test_items={"A"},
        train_items={"Z"},
        ks=[2],
    )
    assert m["precision@2"] == pytest.approx(0.5)
    assert m["recall@2"] == pytest.approx(1.0)
    assert m["ndcg@2"] == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# 5. evaluate_all: mean metrics + coverage + decile, deterministic
# ---------------------------------------------------------------------------


def _recommend(user_id: int, train_items: set) -> list:
    # Deterministic toy recommender over a fixed candidate pool.
    pool = [101, 102, 103, 104, 105]
    return [i for i in pool if i not in train_items][:5]


@pytest.fixture
def frames() -> tuple[pd.DataFrame, pd.DataFrame]:
    train = pd.DataFrame(
        {
            "userId": [1, 1, 2, 2, 3, 3],
            "movieId": [101, 102, 103, 104, 101, 105],
            "rating": [4.0, 3.0, 5.0, 4.0, 3.0, 2.0],
        }
    )
    test = pd.DataFrame(
        {
            "userId": [1, 2, 3],
            "movieId": [103, 101, 102],
            "rating": [5.0, 4.0, 3.0],
        }
    )
    return train, test


def test_evaluate_all_keys_and_coverage(frames):
    train, test = frames
    result = evaluate_all(test, _recommend, train, ks=[3, 5])

    for name in ("precision", "recall", "ndcg"):
        for k in (3, 5):
            assert f"mean_{name}@{k}" in result
    assert "catalog_coverage" in result
    assert "mean_popularity_decile" in result
    assert 0.0 <= result["catalog_coverage"] <= 1.0
    assert 1 <= result["mean_popularity_decile"] <= 10


def test_evaluate_all_deterministic(frames):
    train, test = frames
    r1 = evaluate_all(test, _recommend, train, ks=[5])
    r2 = evaluate_all(test, _recommend, train, ks=[5])
    assert r1 == r2


# ---------------------------------------------------------------------------
# Documentation: performance floor for baselines (not asserted as a hard test).
# ---------------------------------------------------------------------------
# MovieLens ml-latest-small has 9742 movies (9724 in the candidate catalog used
# for coverage). A random baseline achieves Precision@K ~= K / 9724 (each
# recommendation has a 1/9724 chance of being relevant), so:
#     P@5_random  ~ 5  / 9724 ~ 0.000514
#     P@10_random ~ 10 / 9724 ~ 0.001028
#     P@20_random ~ 20 / 9724 ~ 0.002057
# Any credible model (and the popularity baseline in baseline.py) must exceed
# these floors. We merely record the floor here for documentation/reference.
def test_random_baseline_floor_constant():
    n_movies = 9724
    assert 5 / n_movies < 5 / 1000  # sanity: P@5 floor is tiny, easy to beat
