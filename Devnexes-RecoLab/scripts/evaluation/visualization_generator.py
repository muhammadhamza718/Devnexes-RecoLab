"""Visualization generation for evaluation results.

Creates charts and plots for:
- Model comparison bar charts
- Metric trends across K values
- Catalog coverage visualization
- Statistical test comparisons
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import numpy as np

from config import K_VALUES, MODEL_NAMES, RANKING_METRICS, VISUALIZATIONS_DIR


class VisualizationGenerator:
    """Generates visualizations for evaluation results.

    Creates publication-quality charts for model comparison and analysis.
    """

    def __init__(
        self,
        results: dict[str, dict[str, Any]],
        output_dir: Path | None = None,
    ) -> None:
        """Initialize generator.

        Args:
            results: Evaluation results per model.
            output_dir: Output directory for charts.
        """
        self.results = results
        self.output_dir = output_dir or VISUALIZATIONS_DIR
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Color palette for models
        self.colors = {
            "Popularity": "#4E79A7",
            "Content": "#F28E2B",
            "User-Based CF": "#E15759",
            "Item-Based CF": "#76B7B2",
            "Hybrid": "#59A14F",
        }

    def generate_all_charts(self) -> list[Path]:
        """Generate all visualization charts.

        Returns:
            List of paths to generated charts.
        """
        print("\nGenerating visualizations...")
        paths = []

        # Generate each chart type
        try:
            path = self._generate_comparison_bar_chart()
            paths.append(path)
            print(f"  [OK] Comparison bar chart: {path.name}")
        except Exception as e:
            print(f"  [FAIL] Comparison bar chart: {e}")

        try:
            path = self._generate_metric_trends()
            paths.append(path)
            print(f"  [OK] Metric trends: {path.name}")
        except Exception as e:
            print(f"  [FAIL] Metric trends: {e}")

        try:
            path = self._generate_coverage_chart()
            paths.append(path)
            print(f"  [OK] Coverage chart: {path.name}")
        except Exception as e:
            print(f"  [FAIL] Coverage chart: {e}")

        try:
            path = self._generate_radar_chart()
            paths.append(path)
            print(f"  [OK] Radar chart: {path.name}")
        except Exception as e:
            print(f"  [FAIL] Radar chart: {e}")

        return paths

    def _generate_comparison_bar_chart(self) -> Path:
        """Generate bar chart comparing models on key metrics.

        Returns:
            Path to saved chart.
        """
        fig, ax = plt.subplots(figsize=(12, 6))

        # Extract P@10 for each model
        models = []
        scores = []
        colors = []

        for model_name in MODEL_NAMES:
            if model_name in self.results and "error" not in self.results[model_name]:
                models.append(model_name)
                scores.append(self.results[model_name].get("mean_precision@10", 0))
                colors.append(self.colors.get(model_name, "#888888"))

        x = np.arange(len(models))
        bars = ax.bar(x, scores, color=colors, edgecolor="black", linewidth=1.2)

        # Add value labels on bars
        for bar, score in zip(bars, scores):
            height = bar.get_height()
            ax.annotate(
                f"{score:.4f}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

        ax.set_xlabel("Model", fontsize=12, fontweight="bold")
        ax.set_ylabel("Precision@10", fontsize=12, fontweight="bold")
        ax.set_title("Model Comparison — Precision@10", fontsize=14, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=15, ha="right")
        ax.set_ylim(0, max(scores) * 1.15 if scores else 1)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        path_png = self.output_dir / "comparison_precision_at_10.png"
        path_svg = self.output_dir / "comparison_precision_at_10.svg"
        plt.savefig(path_png, dpi=150, bbox_inches="tight")
        plt.savefig(path_svg, format='svg', bbox_inches='tight')
        plt.close()

        return path_png

    def _generate_metric_trends(self) -> Path:
        """Generate line chart showing metrics across K values.

        Returns:
            Path to saved chart.
        """
        fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True)

        for idx, metric in enumerate(RANKING_METRICS):
            ax = axes[idx]

            for model_name in MODEL_NAMES:
                if model_name not in self.results or "error" in self.results[model_name]:
                    continue

                scores = [
                    self.results[model_name].get(f"mean_{metric}@{k}", 0)
                    for k in K_VALUES
                ]

                ax.plot(
                    K_VALUES,
                    scores,
                    marker="o",
                    linewidth=2,
                    markersize=8,
                    label=model_name,
                    color=self.colors.get(model_name, "#888888"),
                )

            ax.set_xlabel("K", fontsize=11, fontweight="bold")
            ax.set_title(f"{metric.upper()}@K", fontsize=12, fontweight="bold")
            ax.grid(alpha=0.3)
            ax.set_xticks(K_VALUES)

        axes[0].set_ylabel("Score", fontsize=11, fontweight="bold")
        axes[-1].legend(loc="upper right", fontsize=9)
        fig.suptitle("Metric Trends Across K Values", fontsize=14, fontweight="bold", y=1.02)

        plt.tight_layout()
        path_png = self.output_dir / "metric_trends.png"
        path_svg = self.output_dir / "metric_trends.svg"
        plt.savefig(path_png, dpi=150, bbox_inches="tight")
        plt.savefig(path_svg, format='svg', bbox_inches='tight')
        plt.close()

        return path_png

    def _generate_coverage_chart(self) -> Path:
        """Generate bar chart for catalog coverage.

        Returns:
            Path to saved chart.
        """
        fig, ax = plt.subplots(figsize=(10, 5))

        models = []
        coverage = []
        colors = []

        for model_name in MODEL_NAMES:
            if model_name in self.results and "error" not in self.results[model_name]:
                models.append(model_name)
                coverage.append(self.results[model_name].get("catalog_coverage", 0))
                colors.append(self.colors.get(model_name, "#888888"))

        x = np.arange(len(models))
        bars = ax.bar(x, coverage, color=colors, edgecolor="black", linewidth=1.2)

        # Add value labels
        for bar, cov in zip(bars, coverage):
            height = bar.get_height()
            ax.annotate(
                f"{cov:.2%}",
                xy=(bar.get_x() + bar.get_width() / 2, height),
                xytext=(0, 3),
                textcoords="offset points",
                ha="center",
                va="bottom",
                fontsize=10,
                fontweight="bold",
            )

        ax.set_xlabel("Model", fontsize=12, fontweight="bold")
        ax.set_ylabel("Catalog Coverage", fontsize=12, fontweight="bold")
        ax.set_title("Catalog Coverage by Model", fontsize=14, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(models, rotation=15, ha="right")
        ax.set_ylim(0, 1.0)
        ax.grid(axis="y", alpha=0.3)

        plt.tight_layout()
        path_png = self.output_dir / "catalog_coverage.png"
        path_svg = self.output_dir / "catalog_coverage.svg"
        plt.savefig(path_png, dpi=150, bbox_inches="tight")
        plt.savefig(path_svg, format='svg', bbox_inches='tight')
        plt.close()

        return path_png

    def _generate_radar_chart(self) -> Path:
        """Generate radar chart for multi-metric comparison.

        Returns:
            Path to saved chart.
        """
        fig, ax = plt.subplots(figsize=(10, 10), subplot_kw=dict(polar=True))

        # Metrics for radar
        metrics = ["P@10", "R@10", "NDCG@10", "Coverage", "Novelty"]
        angles = np.linspace(0, 2 * np.pi, len(metrics), endpoint=False).tolist()
        angles += angles[:1]  # Complete the circle

        for model_name in MODEL_NAMES:
            if model_name not in self.results or "error" in self.results[model_name]:
                continue

            model_results = self.results[model_name]

            # Normalize values to [0, 1]
            p10 = model_results.get("mean_precision@10", 0)
            r10 = model_results.get("mean_recall@10", 0)
            ndcg10 = model_results.get("mean_ndcg@10", 0)
            coverage = model_results.get("catalog_coverage", 0)
            # Novelty: inverse of popularity decile (lower decile = more popular = less novel)
            novelty = 1 - (model_results.get("mean_popularity_decile", 5) - 1) / 9

            values = [p10, r10, ndcg10, coverage, novelty]
            values += values[:1]  # Complete the circle

            ax.plot(
                angles,
                values,
                linewidth=2,
                linestyle="solid",
                label=model_name,
                color=self.colors.get(model_name, "#888888"),
            )
            ax.fill(angles, values, alpha=0.1, color=self.colors.get(model_name, "#888888"))

        ax.set_xticks(angles[:-1])
        ax.set_xticklabels(metrics, fontsize=11, fontweight="bold")
        ax.set_ylim(0, 1)
        ax.legend(loc="upper right", bbox_to_anchor=(1.3, 1.1), fontsize=10)
        plt.title("Multi-Metric Model Comparison", fontsize=14, fontweight="bold", y=1.08)

        plt.tight_layout()
        path_png = self.output_dir / "radar_comparison.png"
        path_svg = self.output_dir / "radar_comparison.svg"
        plt.savefig(path_png, dpi=150, bbox_inches="tight")
        plt.savefig(path_svg, format='svg', bbox_inches='tight')
        plt.close()

        return path_png


__all__ = ["VisualizationGenerator"]
