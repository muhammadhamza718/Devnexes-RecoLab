"""Top-N ranking evaluation metrics for RecoLab (Week 1, P4-T1 / P4-T2 / REQ-009).

All three core metrics (Precision@K, Recall@K, NDCG@K) are hand-implemented for
TOP-N RANKING. scikit-learn's ``top_k_accuracy_score`` is a multiclass label
ranking metric and is NOT a substitute; sklearn ships no NDCG@K. We therefore
implement everything from scratch with ``numpy`` for the math.

CRITICAL EVAL RULE (REQ-009): a user's already-rated training items MUST be
excluded from ``recommended`` before scoring, otherwise metrics are inflated
because the test items are typically the most popular and would be trivially
"hit". ``evaluate_user`` enforces this with an assertion guard.
"""

from __future__ import annotations

from collections.abc import Collection, Mapping, Sequence
from typing import TypeVar, cast

import numpy as np
import pandas as pd

USER_ID = "userId"
ITEM_ID = "movieId"

K = TypeVar("K", int, str)

# Number of popularity deciles (1 = most popular, 10 = least popular).
N_DECILES = 10


def _as_set(relevant: Collection) -> set:
    """Coerce an iterable collection of relevant item ids to a frozenset-like set."""
    return set(relevant)


def precision_at_k(recommended: Sequence, relevant: Collection, k: int) -> float:
    """Precision@K: fraction of the top-K recommended items that are relevant.

    Args:
        recommended: Ordered list of recommended item ids (rank 0 = top).
        relevant: Set/collection of relevant item ids.
        k: Cut-off rank (number of recommendations to score).

    Returns:
        Precision in [0, 1]. Returns 0.0 when ``k <= 0``.
    """
    if k <= 0:
        return 0.0
    rel = _as_set(relevant)
    top_k = list(recommended)[:k]
    if not top_k:
        return 0.0
    hits = sum(1 for item in top_k if item in rel)
    return hits / len(top_k)


def recall_at_k(recommended: Sequence, relevant: Collection, k: int) -> float:
    """Recall@K: fraction of relevant items captured in the top-K.

    Args:
        recommended: Ordered list of recommended item ids (rank 0 = top).
        relevant: Set/collection of relevant item ids.
        k: Cut-off rank (number of recommendations to score).

    Returns:
        Recall in [0, 1]. Returns 0.0 when there are no relevant items.
    """
    rel = _as_set(relevant)
    if not rel:
        return 0.0
    top_k = list(recommended)[:k]
    hits = sum(1 for item in top_k if item in rel)
    return hits / len(rel)


def _dcg_at_k(gains: Sequence[float], k: int) -> float:
    """Discounted Cumulative Gain for a rank-ordered list of per-position gains.

    Uses log2 position discount (position is 1-indexed): discount = 1/log2(i+1).
    """
    if k <= 0:
        return 0.0
    gains_k = np.asarray(list(gains)[:k], dtype=float)
    if gains_k.size == 0:
        return 0.0
    discounts = np.log2(np.arange(1, gains_k.size + 1) + 1)
    return float(np.sum(gains_k / discounts))


def ndcg_at_k(recommended: Sequence, relevant: Collection, k: int) -> float:
    """NDCG@K: normalized DCG of the top-K recommendations.

    The ideal DCG is computed from the relevant set alone (gains of 1.0), so a
    relevant item placed at the top scores 1.0. When the relevant set is
    smaller than ``k`` the ideal DCG still uses only the available relevant
    items, so NDCG remains in [0, 1] and is well defined (graceful handling).

    Args:
        recommended: Ordered list of recommended item ids (rank 0 = top).
        relevant: Set/collection of relevant item ids.
        k: Cut-off rank (number of recommendations to score).

    Returns:
        NDCG in [0, 1]. Returns 0.0 when there are no relevant items.
    """
    rel = _as_set(relevant)
    if not rel:
        return 0.0
    top_k = list(recommended)[:k]
    # Gains: 1.0 if the recommended item is relevant, else 0.0.
    gains = [1.0 if item in rel else 0.0 for item in top_k]
    dcg = _dcg_at_k(gains, k)

    # Ideal DCG: all relevant items at the top, capped at k positions.
    ideal_gains = [1.0 for _ in rel]
    idcg = _dcg_at_k(ideal_gains, k)
    if idcg == 0.0:
        return 0.0
    return dcg / idcg


def evaluate_user(
    user_id: int,
    recommended: Sequence,
    test_items: Collection,
    train_items: Collection,
    ks: Sequence[int] = (5, 10, 20),
) -> dict[str, float]:
    """Compute Precision/Recall/NDCG@K for a SINGLE user.

    REQ-009 guard: ``recommended`` must have already excluded the user's
    training items. We assert ``recommended ∩ train_items == ∅``; if the caller
    failed to exclude known items this raises ``AssertionError`` instead of
    silently inflating the score.

    Args:
        user_id: Identifier for the user (included in the result for traceability).
        recommended: Ordered list of recommended item ids, already excluding
            ``train_items``.
        test_items: Set of relevant (held-out) item ids for this user.
        train_items: Set of items the user rated in training (must be excluded).
        ks: Cut-off ranks to compute.

    Returns:
        Dict with keys ``precision@{k}``, ``recall@{k}``, ``ndcg@{k}`` plus
        ``user_id``.
    """
    rec = list(recommended)
    train = _as_set(train_items)

    # CRITICAL EVAL RULE (REQ-009): no training item may appear in recommended.
    leakage = set(rec) & train
    assert not leakage, (
        f"User {user_id}: recommended contains {len(leakage)} training item(s); "
        f"exclude known items before scoring (REQ-009)."
    )

    relevant = _as_set(test_items)
    result: dict[str, float] = {"user_id": float(user_id)}
    for k in ks:
        result[f"precision@{k}"] = precision_at_k(rec, relevant, k)
        result[f"recall@{k}"] = recall_at_k(rec, relevant, k)
        result[f"ndcg@{k}"] = ndcg_at_k(rec, relevant, k)
    return result


def _build_popularity_decile_map(train_df: pd.DataFrame) -> Mapping[int, int]:
    """Map each item id to a popularity decile (1 = most popular ... 10 = least).

    Deciles are computed from TRAINING data only, deterministically. Items are
    ranked by descending rating count; ties broken by ascending movieId for a
    stable, reproducible ordering. This is used to evidence popularity bias.
    """
    counts = train_df.groupby(ITEM_ID, sort=False).size().reset_index(name="n")
    # Stable descending sort by count, then ascending movieId.
    counts = counts.sort_values(
        by=["n", ITEM_ID], ascending=[False, True], kind="mergesort"
    ).reset_index(drop=True)

    n_items = len(counts)
    if n_items == 0:
        return {}
    # Decile 1 = most popular. Partition into N_DECILES equal-ish bands.
    deciles = np.ceil((np.arange(n_items) + 1) / (n_items / N_DECILES)).astype(int)
    deciles = np.clip(deciles, 1, N_DECILES)
    return dict(zip(counts[ITEM_ID].astype(int).tolist(), deciles.tolist()))


def evaluate_all(
    test_df: pd.DataFrame,
    recommendations_fn,
    train_df: pd.DataFrame,
    ks: Sequence[int] = (5, 10, 20),
) -> dict[str, float]:
    """Aggregate ranking metrics over ALL test users (+ coverage & popularity).

    For each test user, ``recommendations_fn(user_id, train_items_for_user)`` is
    called and must return an ORDERED list of recommended item ids that ALREADY
    excludes the user's training items (the exclude-known-items rule is the
    caller's responsibility; ``evaluate_user`` also asserts it).

    In addition to mean P@K / R@K / NDCG@K, this reports:
        - ``catalog_coverage``: fraction of all items ever recommended (out of
          the distinct item catalog seen in training) — measures diversity.
        - ``mean_popularity_decile``: average popularity decile of recommended
          items (1 = very popular). Low values evidence popularity bias.

    Results are deterministic given fixed inputs (no randomness is used here).

    Args:
        test_df: Test ratings with ``userId`` and ``movieId`` columns.
        recommendations_fn: Callable ``(user_id, train_items) -> list[int]``.
        train_df: Training ratings used to build the popularity decile map.
        ks: Cut-off ranks to compute.

    Returns:
        Dict with mean metrics, ``catalog_coverage`` and
        ``mean_popularity_decile``.
    """
    # Distinct items ever rated in training -> the candidate catalog.
    catalog = set(train_df[ITEM_ID].astype(int).tolist())
    decile_map = _build_popularity_decile_map(train_df)

    # Group test items and training items per user. Keys are cast to int.
    test_by_user: dict[int, set[int]] = {
        cast(int, uid): set(items.astype(int).tolist())
        for uid, items in test_df.groupby(USER_ID)[ITEM_ID]
    }
    train_by_user: dict[int, set[int]] = {
        cast(int, uid): set(items.astype(int).tolist())
        for uid, items in train_df.groupby(USER_ID)[ITEM_ID]
    }

    ks = list(ks)
    sum_metrics: dict[str, float] = {
        f"{name}@{k}": 0.0 for name in ("precision", "recall", "ndcg") for k in ks
    }
    n_users = 0

    recommended_all: set[int] = set()
    decile_values: list[int] = []

    for user_id, test_items in test_by_user.items():
        train_items = set(train_by_user.get(user_id, set()))
        # The caller is responsible for excluding known items; we also assert.
        recommended = list(recommendations_fn(user_id, set(train_items)))

        user_metrics = evaluate_user(
            user_id,
            recommended,
            test_items,
            train_items,
            ks=ks,
        )

        for name in ("precision", "recall", "ndcg"):
            for k in ks:
                sum_metrics[f"{name}@{k}"] += user_metrics[f"{name}@{k}"]

        recommended_all.update(recommended)
        for item in recommended:
            decile_values.append(decile_map.get(item, N_DECILES))
        n_users += 1

    if n_users == 0:
        result: dict[str, float] = {
            f"mean_{name}@{k}": 0.0
            for name in ("precision", "recall", "ndcg")
            for k in ks
        }
        result["catalog_coverage"] = 0.0
        result["mean_popularity_decile"] = 0.0
        result["n_users"] = 0.0
        return result

    result = {
        f"mean_{name}@{k}": sum_metrics[f"{name}@{k}"] / n_users
        for name in ("precision", "recall", "ndcg")
        for k in ks
    }
    result["catalog_coverage"] = (
        len(recommended_all & catalog) / len(catalog) if catalog else 0.0
    )
    result["mean_popularity_decile"] = (
        float(np.mean(decile_values)) if decile_values else float(N_DECILES)
    )
    result["n_users"] = float(n_users)
    return result
