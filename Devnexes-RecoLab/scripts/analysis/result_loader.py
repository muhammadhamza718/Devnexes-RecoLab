"""Result loader for Day 5 Morning evaluation data.

Provides standard interface to load and validate evaluation artifacts
from data/evaluation/ for use by Day 5 Afternoon analysis engines.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

PROJECT_ROOT = Path(__file__).resolve().parents[2]
EVAL_DIR = PROJECT_ROOT / "data" / "evaluation"


class EvaluationResultLoader:
    """Loader for Day 5 Morning evaluation results."""

    MODEL_KEY_MAP = {
        "Popularity": "popularity",
        "Content": "content",
        "User-Based CF": "user_based_cf",
        "Item-Based CF": "item_based_cf",
        "Hybrid": "hybrid",
    }

    def __init__(self, eval_dir: Path | str | None = None) -> None:
        """Initialize loader with evaluation root directory."""
        self.eval_dir = Path(eval_dir) if eval_dir else EVAL_DIR
        self.results_dir = self.eval_dir / "results"
        self.comparison_dir = self.eval_dir / "comparison"
        self.segmented_dir = self.eval_dir / "segmented"

    def load_model_results(
        self, model_names: list[str] | None = None
    ) -> dict[str, dict[str, Any]]:
        """Load evaluation results for specified or all 5 models.

        Args:
            model_names: List of display model names (e.g. ['Popularity', 'Content']).
                        If None, loads all 5 standard models.

        Returns:
            Dictionary mapping display model name to evaluation metrics dictionary.
        """
        if model_names is None:
            model_names = list(self.MODEL_KEY_MAP.keys())

        results: dict[str, dict[str, Any]] = {}

        for display_name in model_names:
            file_key = self.MODEL_KEY_MAP.get(display_name, display_name.lower().replace(" ", "_").replace("-", "_"))
            matches = sorted(self.results_dir.glob(f"{file_key}_results_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)

            if not matches:
                # Try finding without timestamp
                direct = self.results_dir / f"{file_key}_results.json"
                if direct.exists():
                    matches = [direct]

            if not matches:
                print(f"Warning: No result file found for model '{display_name}' ({file_key}) in {self.results_dir}")
                continue

            latest_file = matches[0]
            with open(latest_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract metrics from storage wrapper if present
            if isinstance(data, dict) and "metrics" in data:
                res_data = data["metrics"]
            elif isinstance(data, dict) and "data" in data:
                res_data = data["data"]
            else:
                res_data = data

            # Validate result format
            self._validate_model_result(display_name, res_data)
            results[display_name] = res_data

        return results

    def load_comparison_results() -> dict[str, Any]:
        """Load statistical comparison results.

        Returns:
            Dictionary containing model rankings, p-values, and statistical tests.
        """
        matches = sorted(self.comparison_dir.glob("comparison_*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not matches:
            direct = self.comparison_dir / "comparison.json"
            if direct.exists():
                matches = [direct]

        if not matches:
            print(f"Warning: No comparison results found in {self.comparison_dir}")
            return {}

        latest_file = matches[0]
        with open(latest_file, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict) and "data" in data:
            return data["data"]
        return data

    def load_segmented_results(
        self, model_names: list[str] | None = None
    ) -> dict[str, dict[str, Any]]:
        """Load segmented subgroup results (cold-start, active users, new items, etc.).

        Returns:
            Dictionary mapping display model name to subgroup results dictionary.
        """
        if model_names is None:
            model_names = list(self.MODEL_KEY_MAP.keys())

        segmented_results: dict[str, dict[str, Any]] = {}

        segments = [
            "cold_start_users",
            "active_users",
            "new_items",
            "established_items",
        ]

        for display_name in model_names:
            file_key = self.MODEL_KEY_MAP.get(display_name, display_name.lower().replace(" ", "_").replace("-", "_"))
            model_segments: dict[str, Any] = {}

            for seg in segments:
                pattern = f"{file_key}_{seg}_*.json"
                matches = sorted(self.segmented_dir.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)

                if matches:
                    with open(matches[0], "r", encoding="utf-8") as f:
                        seg_data = json.load(f)
                    model_segments[seg] = seg_data.get("data", seg_data)

            if model_segments:
                segmented_results[display_name] = model_segments

        return segmented_results

    def _validate_model_result(self, model_name: str, data: dict[str, Any]) -> None:
        """Validate structure and metrics completeness of model result."""
        if not isinstance(data, dict):
            raise ValueError(f"Result for {model_name} must be a dict, got {type(data)}")

        # Check expected metric keys if present
        expected_metrics = ["precision", "recall", "ndcg"]
        found_metrics = [k for k in expected_metrics if any(k in key.lower() for key in data.keys())]

        if not found_metrics and "error" not in data:
            print(f"Notice: Model result for '{model_name}' has keys: {list(data.keys())}")
