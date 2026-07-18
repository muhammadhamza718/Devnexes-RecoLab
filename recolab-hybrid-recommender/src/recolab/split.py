"""Chronological per-user train/test split for MovieLens.

Splits each user's ratings by time: the earliest ``train_ratio`` of a user's
ratings go to training, the remainder to test. This prevents temporal leakage
(a model must not be evaluated on ratings it could only learn from after the
fact).
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

RATINGS_COLUMNS = ["userId", "movieId", "rating", "timestamp"]


def load_ratings(data_path: Path) -> pd.DataFrame:
    """Load ``ml-latest-small/ratings.csv`` with datetime parsing.

    Raises:
        FileNotFoundError: if the ratings CSV does not exist.
        ValueError: if required columns are missing.
    """
    ratings_path = Path(data_path) / "ml-latest-small" / "ratings.csv"
    if not ratings_path.exists():
        raise FileNotFoundError(f"Ratings file not found: {ratings_path}")

    ratings = pd.read_csv(ratings_path)
    # MovieLens timestamps are Unix epoch seconds; convert explicitly.
    ratings["timestamp"] = pd.to_datetime(ratings["timestamp"], unit="s")
    missing = set(RATINGS_COLUMNS) - set(ratings.columns)
    if missing:
        raise ValueError(f"Ratings file missing columns: {sorted(missing)}")
    return ratings


def chronological_split(
    ratings: pd.DataFrame,
    train_ratio: float = 0.8,
    seed: int = 42,
    min_ratings_per_user: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split ``ratings`` chronologically per user.

    Each user's rows are sorted by ``timestamp`` ascending. The first
    ``train_ratio`` fraction (rounded down, minimum 1) become training rows;
    the rest become test rows. ``numpy.random.default_rng(seed)`` breaks ties
    deterministically.

    Returns:
        ``(train, test)`` dataframes with the same columns as the input.

    Raises:
        ValueError: if ``train_ratio`` not in (0, 1].
    """
    if not 0.0 < train_ratio <= 1.0:
        raise ValueError(f"train_ratio must be in (0, 1], got {train_ratio}")
    if "timestamp" not in ratings.columns:
        raise ValueError("ratings must contain a 'timestamp' column")

    rng = np.random.default_rng(seed)
    train_parts: list[pd.DataFrame] = []
    test_parts: list[pd.DataFrame] = []

    for _, user_ratings in ratings.groupby("userId", sort=False):
        if len(user_ratings) < min_ratings_per_user:
            continue
        # Break timestamp ties deterministically before sorting.
        jitter = rng.random(len(user_ratings)) * 1e-6
        ordered = user_ratings.assign(
            _sort=user_ratings["timestamp"].astype("int64").to_numpy() + jitter
        ).sort_values("_sort", kind="mergesort").drop(columns="_sort")

        n_train = max(1, int(np.floor(len(ordered) * train_ratio)))
        train_parts.append(ordered.iloc[:n_train])
        test_parts.append(ordered.iloc[n_train:])

    if train_parts:
        train = pd.concat(train_parts).reset_index(drop=True)
        test = pd.concat(test_parts).reset_index(drop=True)
    else:
        train = ratings.iloc[0:0]
        test = ratings.iloc[0:0]
    return train, test


def validate_no_leakage(train: pd.DataFrame, test: pd.DataFrame) -> None:
    """Raise ``AssertionError`` if any (userId, movieId) pair appears in both."""
    shared = set(zip(train["userId"], train["movieId"])) & set(
        zip(test["userId"], test["movieId"])
    )
    if shared:
        raise AssertionError(f"Data leakage detected: {len(shared)} shared pairs")


def save_split(
    train: pd.DataFrame, test: pd.DataFrame, output_dir: Path
) -> tuple[Path, Path]:
    """Persist train/test splits to ``train.csv`` / ``test.csv``."""
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    train_path = out / "train.csv"
    test_path = out / "test.csv"
    train.to_csv(train_path, index=False)
    test.to_csv(test_path, index=False)
    return train_path, test_path
