"""Metrics provider for the RecoLab dashboard (Feature 008, Task-001).

Loads model evaluation metrics for the performance dashboard and model
comparison. Pre-computed evaluation results are read from JSON files under
``data/evaluation/`` when present; otherwise metrics are computed in real time
from the held-out test split using the existing ``recolab.metrics`` framework
(``evaluate_all``). Both paths are cached so reruns stay fast.

Metric values are never hardcoded: they always come from ``metrics.py`` or a
pre-computed file, per the Feature 008 spec (MUST NOT hardcode evaluation
metrics).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Callable

import pandas as pd
import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

TEST_CSV = PROJECT_ROOT / "data" / "split_datasets" / "test.csv"
EVALUATION_DIR = PROJECT_ROOT / "data" / "evaluation"

from recolab.metrics import evaluate_all  # noqa: E402  (after sys.path bootstrap)

# Canonical model names (mirrors ui.model_manager.MODEL_NAMES).
MODEL_NAMES: list[str] = [
    "Popularity",
    "Content",
    "User-Based CF",
    "Item-Based CF",
    "Hybrid",
]

# Canonical name -> slug used for pre-computed metric file names.
_MODEL_SLUGS: dict[str, str] = {
    "Popularity": "popularity",
    "Content": "content",
    "User-Based CF": "user_based_cf",
    "Item-Based CF": "item_based_cf",
    "Hybrid": "hybrid",
}

# Allowed K cut-offs for the dashboard (Feature 008 FR-006).
ALLOWED_K: tuple[int, ...] = (5, 10, 20)

# Cap on test users evaluated in real time (bounds dashboard load time).
MAX_REALTIME_USERS = 200


@st.cache_data(show_spinner=False)
def _load_test_split() -> pd.DataFrame:
    """Load the held-out test split (deterministic; cached per run)."""
    if not TEST_CSV.exists():
        return pd.DataFrame()
    return pd.read_csv(TEST_CSV)


@st.cache_data(show_spinner=False)
def _load_train_split() -> pd.DataFrame:
    """Load the training split used for the popularity decile map."""
    from ui.data_provider import load_train

    return load_train()


@st.cache_resource(show_spinner=False)
def _evaluate_model_realtime(model_name: str, k: int) -> dict[str, float]:
    """Compute mean P@K / R@K / NDCG@K over the test split for one model.

    Uses ``recolab.metrics.evaluate_all`` on a capped, deterministic sample of
    test users so the dashboard stays responsive (Feature 008 NFR-001). The
    caller-supplied recommendation function excludes each user's training
    items, satisfying the REQ-009 eval rule.
    """
    from ui.model_manager import ModelManager

    test_df = _load_test_split()
    train_df = _load_train_split()
    if test_df.empty or train_df.empty:
        return _empty_metrics()

    model_manager = ModelManager()
    model, _ = model_manager.get_model(model_name)

    # Deterministic sample of test users (first N by userId) for speed.
    users = sorted(test_df["userId"].astype(int).unique())[:MAX_REALTIME_USERS]
    test_sample = test_df[test_df["userId"].astype(int).isin(users)]

    recommend_k = max(k, 20)  # generate enough for any allowed cut-off

    def _recommend_fn(user_id: int, train_items: set[int]) -> list[int]:
        try:
            return list(
                model.recommend(user_id=user_id, k=recommend_k, exclude_items=train_items)
                or []
            )
        except Exception:
            return []

    try:
        result = evaluate_all(
            test_df=test_sample,
            recommendations_fn=_recommend_fn,
            train_df=train_df,
            ks=(k,),
        )
    except Exception:
        return _empty_metrics()

    return {
        f"mean_precision@{k}": float(result.get(f"mean_precision@{k}", 0.0)),
        f"mean_recall@{k}": float(result.get(f"mean_recall@{k}", 0.0)),
        f"mean_ndcg@{k}": float(result.get(f"mean_ndcg@{k}", 0.0)),
        "catalog_coverage": float(result.get("catalog_coverage", 0.0)),
        "mean_popularity_decile": float(result.get("mean_popularity_decile", 0.0)),
        "n_users": float(result.get("n_users", 0.0)),
    }


def _empty_metrics() -> dict[str, float]:
    """Zero-filled metrics used when no evaluation data is available."""
    return {
        "mean_precision@5": 0.0,
        "mean_recall@5": 0.0,
        "mean_ndcg@5": 0.0,
        "mean_precision@10": 0.0,
        "mean_recall@10": 0.0,
        "mean_ndcg@10": 0.0,
        "mean_precision@20": 0.0,
        "mean_recall@20": 0.0,
        "mean_ndcg@20": 0.0,
        "catalog_coverage": 0.0,
        "mean_popularity_decile": 0.0,
        "n_users": 0.0,
    }


class MetricsProvider:
    """Provides per-model evaluation metrics with caching and fallbacks.

    Resolution order for ``get_model_metrics``:
        1. In-memory cache (this instance).
        2. Pre-computed JSON file under ``data/evaluation/``.
        3. Real-time evaluation via ``recolab.metrics.evaluate_all``.
    """

    def __init__(
        self,
        evaluation_dir: Path | None = None,
        model_manager: Any | None = None,
    ) -> None:
        self._evaluation_dir = evaluation_dir or EVALUATION_DIR
        self._model_manager = model_manager
        self._cache: dict[str, dict[str, float]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def get_model_metrics(self, model_name: str, k: int = 10) -> dict[str, float]:
        """Return metrics for one model at cut-off ``k`` (allowed: 5/10/20)."""
        if k not in ALLOWED_K:
            raise ValueError(f"k must be one of {ALLOWED_K}, got {k}")
        cache_key = f"{model_name}:{k}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        metrics = self._load_precomputed_metrics(model_name, k)
        if not metrics:
            metrics = _evaluate_model_realtime(model_name, k)

        self._cache[cache_key] = metrics
        return metrics

    def get_comparison_metrics(self, k: int = 10) -> dict[str, dict[str, float]]:
        """Return metrics for every model at cut-off ``k``."""
        return {
            name: self.get_model_metrics(name, k)
            for name in MODEL_NAMES
        }

    def get_metric_summary(
        self, k: int = 10, metric: str = "ndcg"
    ) -> list[dict[str, Any]]:
        """Rows [{model, metric value}] sorted best-first for a summary table."""
        if metric not in {"precision", "recall", "ndcg"}:
            raise ValueError(f"Unsupported metric: {metric}")
        key = f"mean_{metric}@{k}"
        rows = [
            {"model": name, "value": self.get_model_metrics(name, k).get(key, 0.0)}
            for name in MODEL_NAMES
        ]
        rows.sort(key=lambda row: row["value"], reverse=True)
        return rows

    # ------------------------------------------------------------------
    # Pre-computed file support
    # ------------------------------------------------------------------

    def _load_precomputed_metrics(
        self, model_name: str, k: int
    ) -> dict[str, float]:
        """Read ``data/evaluation/metrics_<slug>_k<k>.json`` when present."""
        slug = _MODEL_SLUGS.get(model_name, model_name.lower().replace(" ", "_"))
        path = self._evaluation_dir / f"metrics_{slug}_k{k}.json"
        if not path.exists():
            return {}
        try:
            with open(path, "r", encoding="utf-8") as fh:
                data = json.load(fh)
            return {str(key): float(value) for key, value in data.items()}
        except (OSError, ValueError, TypeError):
            return {}
