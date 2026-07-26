"""Day 1 — chronological per-user train/test split.

Run from the repository root with the activated venv:
    python notebooks/data_split.py
"""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

from recolab.split import (  # noqa: E402
    chronological_split,
    load_ratings,
    save_split,
    validate_no_leakage,
)

DATA_DIR = ROOT / "data"
SPLIT_DIR = ROOT / "data" / "split_datasets"


def main() -> None:
    print("=== RecoLab Day 1: Chronological Split ===\n")
    ratings = load_ratings(DATA_DIR)
    print(f"Loaded {len(ratings):,} ratings from {ratings['userId'].nunique()} users")

    train, test = chronological_split(ratings, train_ratio=0.8, seed=42)
    validate_no_leakage(train, test)
    print(f"Train: {len(train):,} rows | Test: {len(test):,} rows")
    print(f"Leakage check: PASS (no shared user-item pairs)")

    train_path, test_path = save_split(train, test, SPLIT_DIR)
    print(f"Saved -> {train_path}")
    print(f"Saved -> {test_path}")
    print("\nDone.")


if __name__ == "__main__":
    main()
