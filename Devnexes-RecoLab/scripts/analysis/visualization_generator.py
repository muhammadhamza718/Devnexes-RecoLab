"""Advanced Visualization Generator for Day 5 Afternoon Analysis.

Generates high-resolution publication-quality PNG and SVG charts:
1. Error distribution heatmap (User Activity vs Item Popularity)
2. User activity level vs performance scatter plot
3. Item popularity vs recommendation frequency scatter plot
4. Genre-specific precision radar / grouped bar chart
5. Multi-dimensional bias comparison bar chart
6. Model limitations impact matrix
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import matplotlib
matplotlib.use("Agg")  # Non-interactive backend
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from analysis_storage import AnalysisStorage


class AdvancedVisualizationGenerator:
    """Visualization generator for Day 5 Afternoon advanced analysis."""

    def __init__(
        self,
        analysis_data: dict[str, Any],
        storage: AnalysisStorage | None = None,
    ) -> None:
        """Initialize with loaded analysis results."""
        self.analysis_data = analysis_data
        self.storage = storage or AnalysisStorage()
        self.output_dir = self.storage.get_category_dir("visualizations")

        # Colorblind friendly palette
        plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
        self.colors = ["#377eb8", "#ff7f00", "#4daf4a", "#f781bf", "#a65628"]

    def generate_analysis_charts(self) -> list[Path]:
        """Generate all required analysis visualizations in PNG and SVG formats."""
        generated_paths: list[Path] = []

        print("Generating advanced analysis visualizations...")

        # 1. Error Distribution Heatmap
        p1 = self._generate_error_heatmap()
        if p1:
            generated_paths.extend(p1)

        # 2. User Activity Scatter Plot
        p2 = self._generate_user_activity_scatter()
        if p2:
            generated_paths.extend(p2)

        # 3. Item Popularity Scatter Plot
        p3 = self._generate_item_popularity_scatter()
        if p3:
            generated_paths.extend(p3)

        # 4. Genre Radar / Bar Chart
        p4 = self._generate_genre_radar()
        if p4:
            generated_paths.extend(p4)

        # 5. Bias Comparison Chart
        p5 = self._generate_bias_comparison()
        if p5:
            generated_paths.extend(p5)

        # 6. Limitations Matrix
        p6 = self._generate_limitations_matrix()
        if p6:
            generated_paths.extend(p6)

        print(f"Generated {len(generated_paths)} visualization files in {self.output_dir}")
        return generated_paths

    def _save_figure(self, fig: plt.Figure, base_name: str) -> list[Path]:
        """Save figure in both PNG and SVG formats."""
        paths = []
        for ext in ["png", "svg"]:
            p = self.output_dir / f"{base_name}.{ext}"
            fig.savefig(p, dpi=300, bbox_inches="tight")
            paths.append(p)
        plt.close(fig)
        return paths

    def _generate_error_heatmap(self) -> list[Path] | None:
        """Generate User Activity vs Item Popularity Error Rate Heatmap."""
        error_data = self.analysis_data.get("error_analysis", {})
        if not error_data:
            return None

        models = [m for m in error_data.keys() if not m.startswith("_")]
        if not models:
            return None

        # Build matrix: User Activity (Sparse, Medium, Active) x Item Popularity (Obscure, Medium, Popular)
        act_levels = ["sparse", "medium", "active"]
        pop_levels = ["obscure", "medium", "popular"]

        # Average error rate matrix across models
        matrix = np.zeros((len(act_levels), len(pop_levels)))

        for i, act in enumerate(act_levels):
            for j, pop in enumerate(pop_levels):
                vals = []
                for m in models:
                    m_data = error_data[m]
                    a_err = m_data.get("activity_level_error_rates", {}).get(act, 0.5)
                    p_err = m_data.get("popularity_level_error_rates", {}).get(pop, 0.5)
                    vals.append((a_err + p_err) / 2.0)
                matrix[i, j] = np.mean(vals) if vals else 0.5

        fig, ax = plt.subplots(figsize=(8, 6))
        sns.heatmap(
            matrix,
            annot=True,
            fmt=".3f",
            cmap="YlOrRd",
            xticklabels=[p.capitalize() for p in pop_levels],
            yticklabels=[a.capitalize() for a in act_levels],
            ax=ax,
            cbar_kws={"label": "Mean Error Rate (1 - Precision@10)"},
        )
        ax.set_title("Error Rate Distribution: User Activity vs Item Popularity", fontsize=14, pad=15)
        ax.set_xlabel("Item Popularity Level", fontsize=12)
        ax.set_ylabel("User Activity Level", fontsize=12)

        return self._save_figure(fig, "error_distribution_heatmap")

    def _generate_user_activity_scatter(self) -> list[Path] | None:
        """Generate User Activity vs NDCG@10 Scatter Plot."""
        edge_data = self.analysis_data.get("edge_case_analysis", {})
        if not edge_data:
            return None

        models = [m for m in edge_data.keys() if not m.startswith("_")]
        if not models:
            return None

        fig, ax = plt.subplots(figsize=(9, 6))

        for idx, m in enumerate(models):
            m_res = edge_data[m]
            sparse_ndcg = m_res.get("sparse_users", {}).get("ndcg@10", 0.0)
            power_ndcg = m_res.get("power_users", {}).get("ndcg@10", 0.0)
            overall_ndcg = m_res.get("baseline_comparison", {}).get("overall_ndcg10", 0.0)

            x = [1, 2, 3]  # Sparse, Overall, Power
            y = [sparse_ndcg, overall_ndcg, power_ndcg]

            ax.plot(x, y, marker="o", linewidth=2.5, label=m, color=self.colors[idx % len(self.colors)])

        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(["Sparse (<=3 ratings)", "Overall Average", "Power (>50 ratings)"])
        ax.set_ylabel("NDCG@10 Score", fontsize=12)
        ax.set_title("Recommendation Performance Across User Activity Subgroups", fontsize=14, pad=15)
        ax.legend(title="Model", frameon=True)
        ax.set_ylim(bottom=0.0)

        return self._save_figure(fig, "user_activity_vs_performance")

    def _generate_item_popularity_scatter(self) -> list[Path] | None:
        """Generate Item Popularity vs Recommendation Frequency Scatter Plot."""
        bias_data = self.analysis_data.get("bias_analysis", {})
        if not bias_data:
            return None

        models = [m for m in bias_data.keys() if not m.startswith("_")]
        if not models:
            return None

        deciles = [bias_data[m].get("popularity_bias", {}).get("mean_popularity_decile", 5.0) for m in models]
        coverages = [bias_data[m].get("catalog_coverage", {}).get("catalog_coverage_pct", 0.0) * 100 for m in models]

        fig, ax = plt.subplots(figsize=(9, 6))

        for idx, m in enumerate(models):
            ax.scatter(
                deciles[idx],
                coverages[idx],
                s=200,
                color=self.colors[idx % len(self.colors)],
                label=m,
                edgecolor="black",
                zorder=3,
            )

        ax.set_xlabel("Mean Recommended Item Popularity Decile (1=Niche, 10=Popular)", fontsize=12)
        ax.set_ylabel("Catalog Coverage (%)", fontsize=12)
        ax.set_title("Tradeoff: Popularity Bias vs Catalog Coverage", fontsize=14, pad=15)
        ax.grid(True, linestyle="--", alpha=0.6)
        ax.legend(title="Model", frameon=True)

        return self._save_figure(fig, "popularity_vs_coverage_scatter")

    def _generate_genre_radar(self) -> list[Path] | None:
        """Generate Genre-Specific Performance Grouped Bar Chart."""
        edge_data = self.analysis_data.get("edge_case_analysis", {})
        if not edge_data:
            return None

        models = [m for m in edge_data.keys() if not m.startswith("_")]
        if not models:
            return None

        genres = ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller", "Romance"]
        df_list = []

        for m in models:
            g_perf = edge_data[m].get("genre_performance", {})
            for g in genres:
                df_list.append({"Model": m, "Genre": g, "Hit Rate": g_perf.get(g, 0.0)})

        df = pd.DataFrame(df_list)

        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=df, x="Genre", y="Hit Rate", hue="Model", palette=self.colors[:len(models)], ax=ax)

        ax.set_title("Genre-Specific Recommendation Hit Rate Across Models", fontsize=14, pad=15)
        ax.set_ylabel("Precision / Hit Rate", fontsize=12)
        ax.set_xlabel("Movie Genre", fontsize=12)
        ax.legend(title="Model", frameon=True)

        return self._save_figure(fig, "genre_performance_comparison")

    def _generate_bias_comparison(self) -> list[Path] | None:
        """Generate Multi-Metric Bias Comparison Chart."""
        bias_data = self.analysis_data.get("bias_analysis", {})
        if not bias_data:
            return None

        matrix = bias_data.get("_bias_comparison_matrix", {})
        if not matrix:
            return None

        df = pd.DataFrame(matrix).T

        fig, axes = plt.subplots(2, 2, figsize=(12, 10))

        metrics = [
            ("popularity_decile", "Mean Popularity Decile (Lower=Less Bias)", axes[0, 0]),
            ("catalog_coverage_pct", "Catalog Coverage (%)", axes[0, 1]),
            ("intra_list_diversity", "Intra-List Genre Diversity", axes[1, 0]),
            ("novelty_score", "Novelty Score (-log2 p_i)", axes[1, 1]),
        ]

        for col, title, ax in metrics:
            if col in df.columns:
                vals = df[col] if col != "catalog_coverage_pct" else df[col] * 100
                sns.barplot(x=vals.index, y=vals.values, ax=ax, palette=self.colors[:len(df)])
                ax.set_title(title, fontsize=12)
                ax.set_xticklabels(vals.index, rotation=25, ha="right")
                ax.set_ylabel("Score")

        plt.suptitle("Model Bias & Diversity Comparison Dashboard", fontsize=16, y=0.98)
        plt.tight_layout()

        return self._save_figure(fig, "bias_comparison_dashboard")

    def _generate_limitations_matrix(self) -> list[Path] | None:
        """Generate Model Limitations Impact Visualization Matrix."""
        limitations_data = self.analysis_data.get("limitations", {})
        if not limitations_data:
            return None

        model_lims = limitations_data.get("model_specific_limitations", {})
        if not model_lims:
            return None

        models = list(model_lims.keys())
        impact_map = {"Low": 1, "Medium": 2, "High": 3}

        impact_scores = [impact_map.get(model_lims[m].get("impact", "Medium"), 2) for m in models]

        fig, ax = plt.subplots(figsize=(9, 5))
        colors = ["#2ca02c" if s == 1 else ("#ff7f0e" if s == 2 else "#d62728") for s in impact_scores]

        bars = ax.barh(models, impact_scores, color=colors, height=0.55)
        ax.set_xlim(0, 4)
        ax.set_xticks([1, 2, 3])
        ax.set_xticklabels(["Low Impact", "Medium Impact", "High Impact"])
        ax.set_title("Overall Operational Risk & Limitation Impact per Model", fontsize=14, pad=15)
        ax.grid(True, axis="x", linestyle="--", alpha=0.6)

        for bar, score in zip(bars, impact_scores):
            label = "Low Risk" if score == 1 else ("Moderate" if score == 2 else "High Risk")
            ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2, label, va="center", fontweight="bold")

        return self._save_figure(fig, "limitations_impact_matrix")
