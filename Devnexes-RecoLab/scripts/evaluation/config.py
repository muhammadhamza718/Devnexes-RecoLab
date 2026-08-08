"""Configuration for Day 5 Morning evaluation framework.

Defines evaluation parameters, model names, and directory paths for the
comprehensive model comparison pipeline.
"""

from __future__ import annotations

from pathlib import Path
from typing import Final

# Project root (2 levels up from this file: config.py -> evaluation -> Devnexes-RecoLab)
PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[2]

# Evaluation parameters
K_VALUES: Final[list[int]] = [5, 10, 20]
RANDOM_SEED: Final[int] = 42

# Significance level for statistical tests
SIGNIFICANCE_LEVEL: Final[float] = 0.05

# Model names (must match MODEL_NAMES in ui/model_manager.py)
MODEL_NAMES: Final[list[str]] = [
    "Popularity",
    "Content",
    "User-Based CF",
    "Item-Based CF",
    "Hybrid",
]

# Directory paths
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
EVALUATION_DIR: Final[Path] = DATA_DIR / "evaluation"
RESULTS_DIR: Final[Path] = EVALUATION_DIR / "results"
COMPARISON_DIR: Final[Path] = EVALUATION_DIR / "comparison"
SEGMENTED_DIR: Final[Path] = EVALUATION_DIR / "segmented"
VISUALIZATIONS_DIR: Final[Path] = EVALUATION_DIR / "visualizations"

# Data paths
TRAIN_CSV: Final[Path] = DATA_DIR / "split_datasets" / "train.csv"
TEST_CSV: Final[Path] = DATA_DIR / "split_datasets" / "test.csv"
MOVIES_CSV: Final[Path] = DATA_DIR / "ml-latest-small" / "movies.csv"

# Metric names for results
RANKING_METRICS: Final[list[str]] = ["precision", "recall", "ndcg"]
AUXILIARY_METRICS: Final[list[str]] = ["catalog_coverage", "mean_popularity_decile"]

# Segmentation thresholds (mirror HybridRecommender)
COLD_START_MAX_RATINGS: Final[int] = 5
ACTIVE_MIN_RATINGS: Final[int] = 20
NEW_ITEM_MAX_RATINGS: Final[int] = 10


def ensure_directories() -> None:
    """Create all evaluation directories if they don't exist."""
    for directory in [RESULTS_DIR, COMPARISON_DIR, SEGMENTED_DIR, VISUALIZATIONS_DIR]:
        directory.mkdir(parents=True, exist_ok=True)


__all__ = [
    "PROJECT_ROOT",
    "K_VALUES",
    "RANDOM_SEED",
    "SIGNIFICANCE_LEVEL",
    "MODEL_NAMES",
    "DATA_DIR",
    "EVALUATION_DIR",
    "RESULTS_DIR",
    "COMPARISON_DIR",
    "SEGMENTED_DIR",
    "VISUALIZATIONS_DIR",
    "TRAIN_CSV",
    "TEST_CSV",
    "MOVIES_CSV",
    "RANKING_METRICS",
    "AUXILIARY_METRICS",
    "COLD_START_MAX_RATINGS",
    "ACTIVE_MIN_RATINGS",
    "NEW_ITEM_MAX_RATINGS",
    "ensure_directories",
]
