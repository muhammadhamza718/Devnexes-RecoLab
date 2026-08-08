"""Result storage and validation for evaluation framework.

Provides structured JSON persistence for evaluation results with validation
and type safety.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import COMPARISON_DIR, RESULTS_DIR, SEGMENTED_DIR


class ResultStorage:
    """Manages persistent storage of evaluation results in JSON format.

    All results are stored with metadata including timestamps, model names,
    and evaluation parameters for reproducibility.
    """

    def __init__(self, results_dir: Path | None = None) -> None:
        """Initialize storage with optional custom directory.

        Args:
            results_dir: Custom directory for results (defaults to RESULTS_DIR).
        """
        self.results_dir = results_dir or RESULTS_DIR
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def save_model_results(
        self,
        model_name: str,
        results: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        """Save model evaluation results to JSON file.

        Args:
            model_name: Canonical model name.
            results: Evaluation metrics dict.
            metadata: Optional metadata (seed, timestamp, etc.).

        Returns:
            Path to saved file.
        """
        safe_name = model_name.lower().replace("-", "_").replace(" ", "_")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_name}_results_{timestamp}.json"
        filepath = self.results_dir / filename

        payload = {
            "model_name": model_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results,
            "metadata": metadata or {},
        }

        self._write_json(filepath, payload)
        return filepath

    def load_model_results(self, model_name: str) -> dict[str, Any] | None:
        """Load most recent results for a model.

        Args:
            model_name: Canonical model name.

        Returns:
            Results dict or None if not found.
        """
        safe_name = model_name.lower().replace("-", "_").replace(" ", "_")
        pattern = f"{safe_name}_results_*.json"
        matches = sorted(self.results_dir.glob(pattern), reverse=True)
        if not matches:
            return None
        return self._read_json(matches[0])

    def save_comparison_results(
        self,
        results: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        """Save model comparison results.

        Args:
            results: Comparison results dict.
            metadata: Optional metadata.

        Returns:
            Path to saved file.
        """
        COMPARISON_DIR.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"comparison_{timestamp}.json"
        filepath = COMPARISON_DIR / filename

        payload = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results,
            "metadata": metadata or {},
        }

        self._write_json(filepath, payload)
        return filepath

    def save_segmented_results(
        self,
        model_name: str,
        segment_name: str,
        results: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        """Save segmented evaluation results.

        Args:
            model_name: Canonical model name.
            segment_name: Segment identifier (e.g., 'cold_start_users').
            results: Segmented metrics dict.
            metadata: Optional metadata.

        Returns:
            Path to saved file.
        """
        SEGMENTED_DIR.mkdir(parents=True, exist_ok=True)
        safe_model = model_name.lower().replace("-", "_").replace(" ", "_")
        safe_segment = segment_name.lower().replace("-", "_").replace(" ", "_")
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        filename = f"{safe_model}_{safe_segment}_{timestamp}.json"
        filepath = SEGMENTED_DIR / filename

        payload = {
            "model_name": model_name,
            "segment_name": segment_name,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "results": results,
            "metadata": metadata or {},
        }

        self._write_json(filepath, payload)
        return filepath

    def validate_results(self, results: dict[str, Any]) -> list[str]:
        """Validate result format and ranges.

        Args:
            results: Evaluation results dict.

        Returns:
            List of validation error messages (empty if valid).
        """
        errors: list[str] = []

        # Check required metric keys
        for metric in ["precision", "recall", "ndcg"]:
            for k in [5, 10, 20]:
                key = f"mean_{metric}@{k}"
                if key not in results:
                    errors.append(f"Missing metric: {key}")
                elif not isinstance(results[key], (int, float)):
                    errors.append(f"Invalid type for {key}: {type(results[key])}")
                elif not (0.0 <= results[key] <= 1.0):
                    errors.append(f"Out of range for {key}: {results[key]}")

        # Check auxiliary metrics
        if "catalog_coverage" in results:
            if not (0.0 <= results["catalog_coverage"] <= 1.0):
                errors.append(f"Invalid catalog_coverage: {results['catalog_coverage']}")

        if "mean_popularity_decile" in results:
            if not (1.0 <= results["mean_popularity_decile"] <= 10.0):
                errors.append(
                    f"Invalid mean_popularity_decile: {results['mean_popularity_decile']}"
                )

        return errors

    def _write_json(self, filepath: Path, data: dict[str, Any]) -> None:
        """Write JSON data to file atomically."""
        temp_path = filepath.with_suffix(".tmp")
        try:
            with temp_path.open("w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False, default=str)
            temp_path.rename(filepath)
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise RuntimeError(f"Failed to write JSON to {filepath}: {e}") from e

    def _read_json(self, filepath: Path) -> dict[str, Any]:
        """Read JSON data from file."""
        try:
            with filepath.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Failed to read JSON from {filepath}: {e}") from e


__all__ = ["ResultStorage"]
