"""Generate comprehensive Markdown summary report from evaluation results.

Creates a publication-ready report with:
- Executive summary
- Model comparison tables
- Segmented analysis findings
- Key insights and recommendations
"""

from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any

# Add scripts directory to path for path_utils import
sys.path.insert(0, str(Path(__file__).resolve().parent))
from path_utils import get_validated_project_root

# Add project to path with validation
PROJECT_ROOT = get_validated_project_root()
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from config import K_VALUES, MODEL_NAMES, RANKING_METRICS, SEGMENTED_DIR
from result_storage import ResultStorage


class SummaryReportGenerator:
    """Generates Markdown summary reports from evaluation results."""

    def __init__(self, storage: ResultStorage | None = None) -> None:
        """Initialize generator.

        Args:
            storage: ResultStorage instance.
        """
        self.storage = storage or ResultStorage()
        self.output_dir = self.storage.results_dir

    def generate_report(
        self,
        full_results: dict[str, dict[str, Any]] | None = None,
        segmented_results: dict[str, dict[str, dict[str, Any]]] | None = None,
        comparison_results: dict[str, Any] | None = None,
    ) -> Path:
        """Generate comprehensive summary report.

        Args:
            full_results: Full evaluation results per model.
            segmented_results: Segmented evaluation results.
            comparison_results: Statistical comparison results.

        Returns:
            Path to generated report.
        """
        # Load results from storage if not provided
        if full_results is None:
            full_results = self._load_full_results()

        if segmented_results is None:
            segmented_results = self._load_segmented_results()

        if comparison_results is None:
            comparison_results = self._load_comparison_results()

        # Build report
        report_lines: list[str] = []
        report_lines.append("# RecoLab Evaluation Report — Day 5 Morning\n")
        report_lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        report_lines.append("---\n")

        # Executive Summary
        report_lines.extend(self._generate_executive_summary(full_results))

        # Model Performance Tables
        report_lines.extend(self._generate_performance_tables(full_results))

        # Segmented Analysis
        if segmented_results:
            report_lines.extend(self._generate_segmented_section(segmented_results))

        # Statistical Comparison
        if comparison_results:
            report_lines.extend(self._generate_comparison_section(comparison_results))

        # Key Findings
        report_lines.extend(self._generate_key_findings(full_results, segmented_results))

        # Recommendations
        report_lines.extend(self._generate_recommendations(full_results))

        # Appendix
        report_lines.extend(self._generate_appendix())

        # Write report
        report_path = self.output_dir / "evaluation_summary.md"
        report_path.write_text("\n".join(report_lines), encoding="utf-8")
        print(f"\nSummary report generated: {report_path}")

        return report_path

    def _load_full_results(self) -> dict[str, dict[str, Any]]:
        """Load full evaluation results from storage."""
        results: dict[str, dict[str, Any]] = {}
        for model_name in MODEL_NAMES:
            key = model_name.lower().replace('-', '_').replace(' ', '_')
            matching = list(self.output_dir.glob(f"{key}_results*.json"))
            if matching:
                latest = max(matching, key=lambda p: p.stat().st_mtime)
                with open(latest, encoding="utf-8") as f:
                    data = json.load(f)
                    results[model_name] = data.get("results", data)
        return results

    def _load_segmented_results(self) -> dict[str, dict[str, dict[str, Any]]]:
        """Load segmented evaluation results from storage."""
        results: dict[str, dict[str, dict[str, Any]]] = {}
        segments = ["cold_start_users", "active_users", "new_items", "established_items"]
        segmented_dir = SEGMENTED_DIR

        for model_name in MODEL_NAMES:
            results[model_name] = {}
            key = model_name.lower().replace('-', '_').replace(' ', '_')
            for segment in segments:
                matching = list(segmented_dir.glob(f"{key}_{segment}*.json")) if segmented_dir.exists() else []
                if matching:
                    latest = max(matching, key=lambda p: p.stat().st_mtime)
                    with open(latest, encoding="utf-8") as f:
                        data = json.load(f)
                        results[model_name][segment] = data.get("results", data)

        return results

    def _load_comparison_results(self) -> dict[str, Any]:
        """Load comparison results from storage."""
        result_file = self.output_dir / "model_comparison.json"
        if result_file.exists():
            with open(result_file, encoding="utf-8") as f:
                return json.load(f)
        return {}

    def _generate_executive_summary(self, results: dict[str, dict[str, Any]]) -> list[str]:
        """Generate executive summary section."""
        lines: list[str] = []
        lines.append("## Executive Summary\n")

        successful_models = [name for name, r in results.items() if "error" not in r]
        lines.append(f"**Models Evaluated:** {len(successful_models)}/{len(MODEL_NAMES)}\n")

        if successful_models:
            # Find best model by P@10
            best_model = max(
                successful_models,
                key=lambda m: results[m].get("mean_precision@10", 0)
            )
            best_p10 = results[best_model].get("mean_precision@10", 0)

            lines.append(f"**Best Performer (P@10):** {best_model} ({best_p10:.4f})\n")

            # Coverage leader
            coverage_leader = max(
                successful_models,
                key=lambda m: results[m].get("catalog_coverage", 0)
            )
            best_coverage = results[coverage_leader].get("catalog_coverage", 0)

            lines.append(f"**Highest Coverage:** {coverage_leader} ({best_coverage:.2%})\n")

        lines.append("\n")
        return lines

    def _generate_performance_tables(self, results: dict[str, dict[str, Any]]) -> list[str]:
        """Generate performance comparison tables."""
        lines: list[str] = []
        lines.append("## Model Performance\n")

        # Main metrics table at K=10
        lines.append("### Ranking Metrics @ K=10\n")
        lines.append("| Model | Precision@10 | Recall@10 | NDCG@10 |")
        lines.append("|-------|-------------|-----------|---------|")

        for model_name in MODEL_NAMES:
            if model_name in results and "error" not in results[model_name]:
                r = results[model_name]
                p10 = r.get("mean_precision@10", 0)
                r10 = r.get("mean_recall@10", 0)
                ndcg10 = r.get("mean_ndcg@10", 0)
                lines.append(f"| {model_name} | {p10:.4f} | {r10:.4f} | {ndcg10:.4f} |")

        lines.append("\n")

        # Auxiliary metrics table
        lines.append("### System Metrics\n")
        lines.append("| Model | Catalog Coverage | Popularity Bias (Decile) |")
        lines.append("|-------|-----------------|-------------------------|")

        for model_name in MODEL_NAMES:
            if model_name in results and "error" not in results[model_name]:
                r = results[model_name]
                coverage = r.get("catalog_coverage", 0)
                pop_decile = r.get("mean_popularity_decile", 0)
                lines.append(f"| {model_name} | {coverage:.2%} | {pop_decile:.2f} |")

        lines.append("\n")

        # Metrics across all K values
        lines.append("### Metrics Across K Values\n")
        lines.append("| Model | " + " | ".join([f"P@{k}" for k in K_VALUES]) + " |")
        lines.append("|-------" + "|------" * len(K_VALUES) + "|")

        for model_name in MODEL_NAMES:
            if model_name in results and "error" not in results[model_name]:
                r = results[model_name]
                values = [f"{r.get(f'mean_precision@{k}', 0):.4f}" for k in K_VALUES]
                lines.append(f"| {model_name} | " + " | ".join(values) + " |")

        lines.append("\n")
        return lines

    def _generate_segmented_section(self, results: dict[str, dict[str, dict[str, Any]]]) -> list[str]:
        """Generate segmented analysis section."""
        lines: list[str] = []
        lines.append("## Segmented Analysis\n")

        # Cold-start vs Active users
        lines.append("### User Segments: Cold-Start vs Active\n")
        lines.append("| Model | P@10 (Cold-Start) | P@10 (Active) | Gap |")
        lines.append("|-------|------------------|---------------|-----|")

        for model_name in MODEL_NAMES:
            if model_name in results:
                cold = results[model_name].get("cold_start_users", {})
                active = results[model_name].get("active_users", {})

                if "error" not in cold and "error" not in active:
                    p10_cold = cold.get("mean_precision@10", 0)
                    p10_active = active.get("mean_precision@10", 0)
                    gap = p10_active - p10_cold
                    lines.append(f"| {model_name} | {p10_cold:.4f} | {p10_active:.4f} | {gap:+.4f} |")

        lines.append("\n")

        # New vs Established items
        lines.append("### Item Segments: New vs Established\n")
        lines.append("| Model | P@10 (New Items) | P@10 (Established) | Gap |")
        lines.append("|-------|-----------------|-------------------|-----|")

        for model_name in MODEL_NAMES:
            if model_name in results:
                new = results[model_name].get("new_items", {})
                est = results[model_name].get("established_items", {})

                if "error" not in new and "error" not in est:
                    p10_new = new.get("mean_precision@10", 0)
                    p10_est = est.get("mean_precision@10", 0)
                    gap = p10_est - p10_new
                    lines.append(f"| {model_name} | {p10_new:.4f} | {p10_est:.4f} | {gap:+.4f} |")

        lines.append("\n")
        return lines

    def _generate_comparison_section(self, comparison: dict[str, Any]) -> list[str]:
        """Generate statistical comparison section."""
        lines: list[str] = []
        lines.append("## Statistical Comparison\n")

        # Rankings
        rankings = comparison.get("rankings", {})
        if rankings:
            lines.append("### Model Rankings by Precision@10\n")
            lines.append("| Rank | Model | Score |")
            lines.append("|------|-------|-------|")

            p10_ranking = rankings.get("mean_precision@10", [])
            for i, (model, score) in enumerate(p10_ranking, 1):
                lines.append(f"| {i} | {model} | {score:.4f} |")

            lines.append("\n")

        # Significance tests summary
        tests = comparison.get("significance_tests", {}).get("comparisons", [])
        if tests:
            lines.append("### Key Pairwise Comparisons\n")

            # Find most significant differences
            significant = [t for t in tests if t.get("significant", False)]
            for test in significant[:5]:  # Top 5
                metric = test.get("metric", "")
                a = test.get("model_a", "")
                b = test.get("model_b", "")
                diff = test.get("difference", 0)
                winner = test.get("winner", "")
                lines.append(f"- **{metric}:** {winner} wins ({a} vs {b}, Δ={diff:+.4f})\n")

            lines.append("\n")

        return lines

    def _generate_key_findings(
        self,
        full_results: dict[str, dict[str, Any]],
        segmented_results: dict[str, dict[str, dict[str, Any]]] | None,
    ) -> list[str]:
        """Generate key findings section."""
        lines: list[str] = []
        lines.append("## Key Findings\n")

        successful = [name for name, r in full_results.items() if "error" not in r]
        if not successful:
            lines.append("No successful evaluations to analyze.\n")
            return lines

        # Performance spread
        p10_scores = [full_results[m].get("mean_precision@10", 0) for m in successful]
        p10_range = max(p10_scores) - min(p10_scores)
        lines.append(f"1. **Performance Spread:** P@10 ranges from {min(p10_scores):.4f} to {max(p10_scores):.4f} (Δ={p10_range:.4f})\n")

        # Coverage diversity
        coverage_scores = [full_results[m].get("catalog_coverage", 0) for m in successful]
        coverage_range = max(coverage_scores) - min(coverage_scores)
        lines.append(f"2. **Coverage Diversity:** Catalog coverage varies from {min(coverage_scores):.2%} to {max(coverage_scores):.2%}\n")

        # Popularity bias
        pop_scores = [full_results[m].get("mean_popularity_decile", 5) for m in successful]
        lines.append(f"3. **Popularity Bias:** Mean decile ranges from {min(pop_scores):.1f} to {max(pop_scores):.1f} (lower=more popular items)\n")

        # Segmented insights
        if segmented_results:
            # Check cold-start gap
            gaps = []
            for model_name in successful:
                cold = segmented_results.get(model_name, {}).get("cold_start_users", {})
                active = segmented_results.get(model_name, {}).get("active_users", {})
                if "error" not in cold and "error" not in active:
                    gap = active.get("mean_precision@10", 0) - cold.get("mean_precision@10", 0)
                    gaps.append(gap)

            if gaps:
                avg_gap = sum(gaps) / len(gaps)
                lines.append(f"4. **Cold-Start Penalty:** Average P@10 gap between active and cold-start users is {avg_gap:.4f}\n")

        lines.append("\n")
        return lines

    def _generate_recommendations(self, results: dict[str, dict[str, Any]]) -> list[str]:
        """Generate recommendations section."""
        lines: list[str] = []
        lines.append("## Recommendations\n")

        successful = [name for name, r in results.items() if "error" not in r]
        if not successful:
            lines.append("Unable to generate recommendations without evaluation results.\n")
            return lines

        # Best overall
        best_overall = max(successful, key=lambda m: results[m].get("mean_precision@10", 0))
        lines.append(f"1. **Best Overall:** Use `{best_overall}` for highest precision when user history is available.\n")

        # Best coverage
        best_coverage = max(successful, key=lambda m: results[m].get("catalog_coverage", 0))
        if best_coverage != best_overall:
            lines.append(f"2. **Best Coverage:** Use `{best_coverage}` when catalog diversity is important.\n")

        # Cold-start handling
        lines.append("3. **Cold-Start Strategy:** Implement hybrid approach with content-based for new users.\n")

        # Production notes
        lines.append("4. **Production Deployment:** Consider A/B testing top performers before full rollout.\n")

        lines.append("\n")
        return lines

    def _generate_appendix(self) -> list[str]:
        """Generate appendix section."""
        lines: list[str] = []
        lines.append("## Appendix\n")
        lines.append("### Evaluation Configuration\n")
        lines.append(f"- **K Values:** {K_VALUES}\n")
        lines.append(f"- **Metrics:** {', '.join(m.upper() for m in RANKING_METRICS)}\n")
        lines.append(f"- **Models:** {', '.join(MODEL_NAMES)}\n")
        lines.append("\n")
        lines.append("### Generated Artifacts\n")
        lines.append("- `evaluation_summary.md` — This report\n")
        lines.append("- `model_comparison.json` — Full comparison data\n")
        lines.append("- `visualizations/` — Charts and plots\n")
        lines.append("\n")
        lines.append("---\n")
        lines.append("*Generated by RecoLab Day 5 Evaluation Framework*\n")

        return lines


def generate_summary_report(
    full_results: dict[str, dict[str, Any]] | None = None,
    segmented_results: dict[str, dict[str, dict[str, Any]]] | None = None,
    comparison_results: dict[str, Any] | None = None,
) -> Path:
    """Convenience function to generate summary report.

    Args:
        full_results: Full evaluation results.
        segmented_results: Segmented evaluation results.
        comparison_results: Statistical comparison results.

    Returns:
        Path to generated report.
    """
    generator = SummaryReportGenerator()
    return generator.generate_report(full_results, segmented_results, comparison_results)


if __name__ == "__main__":
    report_path = generate_summary_report()
    print(f"\nReport generated: {report_path}")
