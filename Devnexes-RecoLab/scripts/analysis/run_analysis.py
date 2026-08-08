"""Main entry point for Day 5 Afternoon Advanced Analysis.

Runs the complete advanced analysis pipeline:
1. Error Analysis Engine
2. Edge Case Analysis Engine
3. Bias Analysis Framework
4. Limitations Documentation Engine
5. Advanced Visualization Generation
6. Executive Summary Report Generation
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

# Add project to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
EVAL_SCRIPTS = PROJECT_ROOT / "scripts" / "evaluation"
ANALYSIS_SCRIPTS = PROJECT_ROOT / "scripts" / "analysis"
# Eval scripts first so run_evaluation.py's own imports resolve correctly,
# then analysis scripts, then src.
for path_item in [SRC_DIR, EVAL_SCRIPTS, ANALYSIS_SCRIPTS]:
    if str(path_item) not in sys.path:
        sys.path.insert(0, str(path_item))

import importlib.util

from analysis_storage import AnalysisStorage
from bias_analysis import BiasAnalyzer
from edge_case_analysis import EdgeCaseAnalyzer
from error_analysis import ErrorAnalyzer
from generate_analysis_summary import AnalysisSummaryReportGenerator
from limitations_analysis import LimitationsAnalyzer
from result_loader import EvaluationResultLoader

# Explicit load of the *analysis* visualization_generator to avoid
# collision with scripts/evaluation/visualization_generator.py
_viz_spec = importlib.util.spec_from_file_location(
    "analysis_visualization_generator",
    ANALYSIS_SCRIPTS / "visualization_generator.py",
)
_viz_mod = importlib.util.module_from_spec(_viz_spec)
_viz_spec.loader.exec_module(_viz_mod)
AdvancedVisualizationGenerator = _viz_mod.AdvancedVisualizationGenerator


def run_advanced_analysis(
    model_names: list[str] | None = None,
    run_visualizations: bool = True,
) -> dict:
    """Run the complete Day 5 Afternoon analysis pipeline.

    Args:
        model_names: Specific models to analyze (None = all 5 models).
        run_visualizations: Whether to generate analysis visualizations.

    Returns:
        Dict with all aggregated analysis results.
    """
    start_time = time.time()

    print("\n" + "=" * 70)
    print("  RECOLAB DAY 5 AFTERNOON — ADVANCED ANALYSIS PIPELINE")
    print("=" * 70)

    # Initialize components
    storage = AnalysisStorage()
    loader = EvaluationResultLoader()

    analysis_results: dict = {
        "error_analysis": {},
        "edge_case_analysis": {},
        "bias_analysis": {},
        "limitations": {},
        "visualizations": [],
    }

    # 1. Error Analysis
    print("\n" + "=" * 70)
    print("  PHASE 1: ERROR ANALYSIS ENGINE")
    print("=" * 70)
    error_analyzer = ErrorAnalyzer(loader=loader, storage=storage)
    analysis_results["error_analysis"] = error_analyzer.analyze_errors(model_names)

    # 2. Edge Case Analysis
    print("\n" + "=" * 70)
    print("  PHASE 2: EDGE CASE ANALYSIS ENGINE")
    print("=" * 70)
    edge_analyzer = EdgeCaseAnalyzer(loader=loader, storage=storage)
    analysis_results["edge_case_analysis"] = edge_analyzer.analyze_edge_cases(model_names)

    # 3. Bias Analysis Framework
    print("\n" + "=" * 70)
    print("  PHASE 3: BIAS QUANTIFICATION FRAMEWORK")
    print("=" * 70)
    bias_analyzer = BiasAnalyzer(loader=loader, storage=storage)
    analysis_results["bias_analysis"] = bias_analyzer.analyze_bias(model_names)

    # 4. Limitations Documentation Engine
    print("\n" + "=" * 70)
    print("  PHASE 4: LIMITATIONS DOCUMENTATION ENGINE")
    print("=" * 70)
    limitations_analyzer = LimitationsAnalyzer(loader=loader, storage=storage)
    analysis_results["limitations"] = limitations_analyzer.document_limitations(model_names)

    # 5. Advanced Visualizations
    if run_visualizations:
        print("\n" + "=" * 70)
        print("  PHASE 5: ADVANCED VISUALIZATION GENERATION")
        print("=" * 70)
        viz_generator = AdvancedVisualizationGenerator(
            analysis_data=analysis_results,
            storage=storage,
        )
        viz_paths = viz_generator.generate_analysis_charts()
        analysis_results["visualizations"] = [str(p) for p in viz_paths]

    # 6. Executive Summary Report
    print("\n" + "=" * 70)
    print("  PHASE 6: EXECUTIVE SUMMARY REPORT GENERATION")
    print("=" * 70)
    report_gen = AnalysisSummaryReportGenerator(analysis_results)
    json_p, md_p = report_gen.generate_report()

    elapsed = time.time() - start_time
    print("\n" + "=" * 70)
    print("  DAY 5 AFTERNOON ADVANCED ANALYSIS COMPLETE")
    print(f"  Execution time: {elapsed:.2f} seconds")
    print(f"  Results stored in: {storage.base_dir}")
    print("=" * 70)

    return analysis_results


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success).
    """
    try:
        results = run_advanced_analysis()
        return 0
    except Exception as e:
        print(f"\nFATAL ERROR in analysis pipeline: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
