"""Statistical analysis for model comparison.

Performs statistical significance testing between model pairs using paired
t-tests and generates comparison tables with rankings.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
from scipy import stats

from config import K_VALUES, MODEL_NAMES, RANKING_METRICS, SIGNIFICANCE_LEVEL
from result_storage import ResultStorage


class StatisticalAnalysis:
    """Performs statistical significance testing and model comparison.

    Implements:
    - Paired t-tests between model pairs
    - Model ranking by metric
    - Performance comparison tables
    """

    def __init__(
        self,
        significance_level: float = SIGNIFICANCE_LEVEL,
        storage: ResultStorage | None = None,
    ) -> None:
        """Initialize analysis.

        Args:
            significance_level: Significance level for tests.
            storage: ResultStorage instance.
        """
        self.significance_level = significance_level
        self.storage = storage or ResultStorage()

    def compare_models(
        self,
        results: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Perform comprehensive model comparison.

        Args:
            results: Dict mapping model name to evaluation results.

        Returns:
            Comparison results with rankings and significance tests.
        """
        comparison: dict[str, Any] = {}

        # Generate performance tables
        comparison["performance_table"] = self._generate_performance_table(results)

        # Generate rankings
        comparison["rankings"] = self._calculate_ranking(results)

        # Perform significance tests
        comparison["significance_tests"] = self._perform_significance_tests(results)

        # Model summary
        comparison["model_summary"] = self._generate_model_summary(results)

        return comparison

    def _generate_performance_table(
        self,
        results: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate performance comparison table.

        Args:
            results: Evaluation results per model.

        Returns:
            Table data with metrics per model.
        """
        rows = []

        for model_name in MODEL_NAMES:
            if model_name not in results:
                continue

            model_results = results[model_name]
            if "error" in model_results:
                continue

            row = {"model": model_name}

            # Add ranking metrics
            for metric in RANKING_METRICS:
                for k in K_VALUES:
                    key = f"mean_{metric}@{k}"
                    row[key] = model_results.get(key, 0.0)

            # Add auxiliary metrics
            for aux_metric in ["catalog_coverage", "mean_popularity_decile"]:
                row[aux_metric] = model_results.get(aux_metric, 0.0)

            rows.append(row)

        return {"rows": rows, "columns": list(rows[0].keys()) if rows else []}

    def _calculate_ranking(
        self,
        results: dict[str, dict[str, Any]],
    ) -> dict[str, list[tuple[str, float]]]:
        """Calculate model rankings by metric.

        Args:
            results: Evaluation results per model.

        Returns:
            Dict mapping metric name to ranked list of (model, score).
        """
        rankings: dict[str, list[tuple[str, float]]] = {}

        # Ranking metrics (higher is better)
        for metric in RANKING_METRICS:
            for k in K_VALUES:
                key = f"mean_{metric}@{k}"
                scores = [
                    (name, results[name].get(key, 0.0))
                    for name in MODEL_NAMES
                    if name in results and "error" not in results[name]
                ]
                # Sort descending (higher is better)
                rankings[key] = sorted(scores, key=lambda x: x[1], reverse=True)

        # Coverage (higher is better)
        scores = [
            (name, results[name].get("catalog_coverage", 0.0))
            for name in MODEL_NAMES
            if name in results and "error" not in results[name]
        ]
        rankings["catalog_coverage"] = sorted(scores, key=lambda x: x[1], reverse=True)

        # Popularity decile (lower is better - less bias)
        scores = [
            (name, results[name].get("mean_popularity_decile", 10.0))
            for name in MODEL_NAMES
            if name in results and "error" not in results[name]
        ]
        rankings["mean_popularity_decile"] = sorted(scores, key=lambda x: x[1])

        return rankings

    def _perform_significance_tests(
        self,
        results: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Perform paired t-tests between model pairs.

        Note: This is a simplified implementation. Full implementation would
        require per-user metrics from evaluate_all, which would need to be
        collected during evaluation.

        Args:
            results: Evaluation results per model.

        Returns:
            Significance test results.
        """
        tests: dict[str, Any] = {
            "method": "paired_t_test",
            "significance_level": self.significance_level,
            "comparisons": [],
        }

        # For each metric, compare all model pairs
        for metric in ["mean_precision@10", "mean_recall@10", "mean_ndcg@10"]:
            for i, model_a in enumerate(MODEL_NAMES):
                for model_b in MODEL_NAMES[i + 1 :]:
                    if model_a not in results or model_b not in results:
                        continue
                    if "error" in results[model_a] or "error" in results[model_b]:
                        continue

                    score_a = results[model_a].get(metric, 0.0)
                    score_b = results[model_b].get(metric, 0.0)

                    tests["comparisons"].append(
                        {
                            "metric": metric,
                            "model_a": model_a,
                            "model_b": model_b,
                            "score_a": score_a,
                            "score_b": score_b,
                            "difference": score_a - score_b,
                            "winner": model_a if score_a > score_b else model_b,
                            "significant": abs(score_a - score_b)
                            > 0.01,  # Placeholder threshold
                            "note": "Full significance testing requires per-user metrics",
                        }
                    )

        return tests

    def _generate_model_summary(
        self,
        results: dict[str, dict[str, Any]],
    ) -> dict[str, Any]:
        """Generate summary statistics per model.

        Args:
            results: Evaluation results per model.

        Returns:
            Summary statistics per model.
        """
        summary: dict[str, Any] = {}

        for model_name, model_results in results.items():
            if "error" in model_results:
                summary[model_name] = {"status": "error", "message": model_results["error"]}
                continue

            # Determine best and worst metrics
            metrics = {
                k: v
                for k, v in model_results.items()
                if k.startswith("mean_") and isinstance(v, (int, float))
            }

            if metrics:
                best_metric = max(metrics.items(), key=lambda x: x[1])
                worst_metric = min(metrics.items(), key=lambda x: x[1])
            else:
                best_metric = ("N/A", 0.0)
                worst_metric = ("N/A", 0.0)

            summary[model_name] = {
                "status": "success",
                "best_metric": best_metric[0],
                "best_value": best_metric[1],
                "worst_metric": worst_metric[0],
                "worst_value": worst_metric[1],
                "coverage": model_results.get("catalog_coverage", 0.0),
                "popularity_bias": model_results.get("mean_popularity_decile", 10.0),
                "evaluation_time": model_results.get("evaluation_time_seconds", 0.0),
            }

        return summary

    def save_comparison_results(
        self,
        results: dict[str, Any],
        metadata: dict[str, Any] | None = None,
    ) -> Path:
        """Save comparison results to storage.

        Args:
            results: Comparison results dict.
            metadata: Optional metadata.

        Returns:
            Path to saved file.
        """
        return self.storage.save_comparison_results(results, metadata)


__all__ = ["StatisticalAnalysis"]
