"""Main entry point for Day 5 Morning evaluation.

Runs the complete evaluation pipeline:
1. Full evaluation of all 5 models
2. Segmented evaluation by user/item subgroups
3. Statistical comparison
4. Visualization generation
5. Summary report
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import pandas as pd

# Add project to path with validation
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from path_utils import get_validated_project_root

PROJECT_ROOT = get_validated_project_root()
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from evaluation_orchestrator import EvaluationOrchestrator
from segmented_evaluation import SegmentedEvaluation
from statistical_analysis import StatisticalAnalysis
from visualization_generator import VisualizationGenerator
from result_storage import ResultStorage

# Import existing ModelManager from UI
import sys
sys.path.insert(0, str(PROJECT_ROOT / "ui"))
from model_manager import ModelManager, _fit_model, _discover_bundle_files, _try_load_bundle


class OfflineModelManager:
    """Wrapper around existing ModelManager for offline evaluation.
    
    Uses the same model loading logic as the UI ModelManager but 
    without Streamlit dependencies.
    """

    MODEL_NAMES = [
        "Popularity",
        "Content",
        "User-Based CF",
        "Item-Based CF",
        "Hybrid",
    ]

    def __init__(self) -> None:
        """Initialize with train data and movies catalog."""
        from ui.data_provider import load_train, load_movies
        
        self.train_df = load_train()
        self.movies_df = load_movies()
        self._models: dict[str, Any] = {}
        self._bundle_files = _discover_bundle_files()

    def get_model(self, name: str) -> tuple[Any, str]:
        """Get or fit a model, returning (model, provenance)."""
        if name not in self.MODEL_NAMES:
            raise ValueError(f"Unknown model name: {name}")

        if name in self._models:
            return self._models[name], "Cached instance"

        # Try to load from bundle first
        if name in self._bundle_files:
            model = _try_load_bundle(self._bundle_files[name])
            if model is not None:
                self._models[name] = model
                return model, f"Loaded from {self._bundle_files[name].name}"

        # Fallback to fitting
        model = _fit_model(name, self.train_df, self.movies_df)
        self._models[name] = model
        return model, "Fitted at evaluation time on the train split"

    def get_available_models(self) -> list[str]:
        """Return list of available model names."""
        return list(self.MODEL_NAMES)


def run_evaluation(
    run_segmented: bool = True,
    run_visualizations: bool = True,
    run_comparison: bool = True,
    model_names: list[str] | None = None,
) -> dict:
    """Run the complete evaluation pipeline.

    Args:
        run_segmented: Whether to run segmented evaluation.
        run_visualizations: Whether to generate visualizations.
        run_comparison: Whether to run statistical comparison.
        model_names: Specific models to evaluate (None = all).

    Returns:
        Dict with all evaluation results.
    """
    print("\n" + "=" * 70)
    print("  RECOLAB DAY 5 MORNING — COMPREHENSIVE EVALUATION")
    print("=" * 70)

    # Initialize components
    storage = ResultStorage()
    model_manager = OfflineModelManager()

    all_results: dict = {
        "full_evaluation": {},
        "segmented_evaluation": {},
        "statistical_comparison": {},
        "visualizations": [],
    }

    # Phase 1: Full Evaluation
    print("\n" + "=" * 70)
    print("  PHASE 1: FULL EVALUATION")
    print("=" * 70)

    orchestrator = EvaluationOrchestrator(
        model_manager=model_manager,
        storage=storage,
    )

    full_results = orchestrator.run_full_evaluation(model_names=model_names)
    all_results["full_evaluation"] = full_results

    # Phase 2: Segmented Evaluation
    if run_segmented:
        print("\n" + "=" * 70)
        print("  PHASE 2: SEGMENTED EVALUATION")
        print("=" * 70)

        segmented = SegmentedEvaluation(
            model_manager=model_manager,
            storage=storage,
        )

        segmented_results = segmented.run_segmented_evaluation(model_names=model_names)
        all_results["segmented_evaluation"] = segmented_results

    # Phase 3: Statistical Comparison
    if run_comparison:
        print("\n" + "=" * 70)
        print("  PHASE 3: STATISTICAL COMPARISON")
        print("=" * 70)

        analysis = StatisticalAnalysis(storage=storage)
        comparison = analysis.compare_models(full_results)
        all_results["statistical_comparison"] = comparison

        # Save comparison
        comparison_path = analysis.save_comparison_results(comparison)
        print(f"\nComparison results saved to: {comparison_path}")

    # Phase 4: Visualizations
    if run_visualizations:
        print("\n" + "=" * 70)
        print("  PHASE 4: VISUALIZATION GENERATION")
        print("=" * 70)

        viz_generator = VisualizationGenerator(results=full_results)
        viz_paths = viz_generator.generate_all_charts()
        all_results["visualizations"] = [str(p) for p in viz_paths]

    # Summary
    print("\n" + "=" * 70)
    print("  EVALUATION COMPLETE")
    print("=" * 70)

    successful = sum(1 for r in full_results.values() if "error" not in r)
    total = len(full_results)
    print(f"Models evaluated: {successful}/{total}")

    if all_results["visualizations"]:
        print(f"Visualizations generated: {len(all_results['visualizations'])}")

    print(f"\nResults stored in: {storage.results_dir}")

    return all_results


def main() -> int:
    """Main entry point.

    Returns:
        Exit code (0 for success).
    """
    try:
        results = run_evaluation()

        # Check for errors
        errors = []
        for model, result in results["full_evaluation"].items():
            if "error" in result:
                errors.append(f"{model}: {result['error']}")

        if errors:
            print("\nErrors encountered:")
            for err in errors:
                print(f"  - {err}")
            return 1

        return 0

    except Exception as e:
        print(f"\nFATAL ERROR: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit(main())
