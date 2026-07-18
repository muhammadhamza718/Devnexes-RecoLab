"""Popularity baseline for RecoLab (Week 1, P3-T1 / REQ-009).

Computes item popularity from the *training* split only and recommends the
top-N most popular items to each user, excluding items the user already rated
in training. Excluding already-rated items is the CRITICAL EVAL RULE: without
it, ranking metrics are inflated because the test items are typically popular
and would be trivially "hit".
"""

from __future__ import annotations

import pandas as pd

ITEM_ID = "movieId"
RATING_COL = "rating"

# Deterministic tie-breaker seed (modern numpy API, not legacy seed()).
_TIE_RNG_SEED = 42


def compute_popularity(train_df: pd.DataFrame, weight_by_rating: bool = True) -> pd.DataFrame:
    """Compute per-item popularity from training data only.

    Args:
        train_df: Training ratings with ``movieId`` and ``rating`` columns.
        weight_by_rating: If True, popularity = sum of ratings (weighted);
            if False, popularity = count of ratings.

    Returns:
        DataFrame with columns ``movieId`` and ``popularity``, sorted by
        ``popularity`` descending. Ties broken deterministically.
    """
    agg = "sum" if weight_by_rating else "count"
    pop = (
        train_df.groupby(ITEM_ID, sort=False)[RATING_COL]
        .agg(agg)
        .rename("popularity")
        .reset_index()
    )
    pop = _stable_sort_descending(pop, "popularity")
    return pop


def _stable_sort_descending(df: pd.DataFrame, col: str) -> pd.DataFrame:
    """Sort ``df`` by ``col`` descending with a deterministic tie-break.

    Uses ``numpy.random.default_rng`` to assign a tiny jitter to equal values
    so identical-popularity items get a reproducible, stable order.
    """
    import numpy as np

    rng = np.random.default_rng(_TIE_RNG_SEED)
    jitter = rng.random(len(df)) * 1e-9
    order = (df[col].to_numpy() + jitter)
    return df.assign(_order=order).sort_values("_order", ascending=False, kind="mergesort").drop(columns="_order").reset_index(drop=True)


class PopularityModel:
    """Top-N popularity recommender fitted on training data.

    The fitted object is a plain, picklable container (no open file handles,
    no non-serializable state), so persistence agents can save/load it.
    """

    def __init__(self, weight_by_rating: bool = True) -> None:
        self.weight_by_rating = weight_by_rating
        self._popularity: pd.DataFrame | None = None
        self._global_top: list[int] = []

    def fit(self, train_df: pd.DataFrame) -> "PopularityModel":
        """Fit on training data; stores global popularity ranking."""
        self._popularity = compute_popularity(
            train_df, weight_by_rating=self.weight_by_rating
        )
        self._global_top = self._popularity[ITEM_ID].astype(int).tolist()
        return self

    @property
    def is_fitted(self) -> bool:
        return self._popularity is not None

    def recommend(
        self,
        user_id: int,
        k: int,
        exclude_items: set[int] | None = None,
    ) -> list[int]:
        """Return top-N most popular itemIds for ``user_id``.

        Items in ``exclude_items`` (typically the user's training-rated items)
        are removed first. This prevents metric inflation (REQ-009).

        Edge cases:
            - Cold-start user (``exclude_items`` is None/empty and the model
              has no per-user history) -> global top-N.
            - User who already rated >= available distinct items -> empty list.

        Args:
            user_id: Identifier for the user (kept for API symmetry; the
                popularity model is user-agnostic).
            k: Number of items to recommend.
            exclude_items: ItemIds to exclude (already-rated in training).

        Returns:
            List of recommended ``movieId`` integers, length <= k.
        """
        if not self.is_fitted:
            raise ValueError("PopularityModel must be fit() before recommend()")
        if k <= 0:
            return []

        exclude = set(exclude_items) if exclude_items else set()
        candidates = [mid for mid in self._global_top if mid not in exclude]
        return candidates[:k]

    def save(self, path) -> None:
        """Persist the fitted model via pickle.

        Provided as a hook for the persistence agent. Raises if not fitted.
        """
        import pickle

        if not self.is_fitted:
            raise ValueError("Cannot save an unfitted model")
        with open(path, "wb") as fh:
            pickle.dump(self, fh)

    @classmethod
    def load(cls, path) -> "PopularityModel":
        """Load a pickled ``PopularityModel`` (persistence hook)."""
        import pickle

        with open(path, "rb") as fh:
            model = pickle.load(fh)
        if not isinstance(model, cls):
            raise TypeError(f"Loaded object is not a {cls.__name__}")
        return model
