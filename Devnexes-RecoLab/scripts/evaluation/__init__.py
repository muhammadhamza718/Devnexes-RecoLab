"""Day 5 Morning - Comprehensive Evaluation Framework.

This module provides tools for evaluating recommendation models:
- Full evaluation on complete test set
- Segmented evaluation by user/item subgroups
- Statistical significance testing
- Visualization generation
- Summary report generation
"""

from __future__ import annotations

from .config import (
    ACTIVE_MIN_RATINGS,
    COLD_START_MAX_RATINGS,
    K_VALUES,
    MODEL_NAMES,
    NEW_ITEM_MAX_RATINGS,
    RANDOM_SEED,
    RANKING_METRICS,
    SIGNIFICANCE_LEVEL,
)
from .evaluation_orchestrator import EvaluationOrchestrator
from .generate_summary import SummaryReportGenerator, generate_summary_report
from .result_storage import ResultStorage
from .segmented_evaluation import SegmentedEvaluation
from .statistical_analysis import StatisticalAnalysis
from .validation import (
    ValidationError,
    validate_model_availability,
    validate_test_data,
    validate_train_data,
)
from .visualization_generator import VisualizationGenerator

__all__ = [
    # Config
    "ACTIVE_MIN_RATINGS",
    "COLD_START_MAX_RATINGS",
    "K_VALUES",
    "MODEL_NAMES",
    "NEW_ITEM_MAX_RATINGS",
    "RANDOM_SEED",
    "RANKING_METRICS",
    "SIGNIFICANCE_LEVEL",
    # Core classes
    "EvaluationOrchestrator",
    "ResultStorage",
    "SegmentedEvaluation",
    "StatisticalAnalysis",
    "VisualizationGenerator",
    "SummaryReportGenerator",
    # Validation
    "ValidationError",
    "validate_model_availability",
    "validate_test_data",
    "validate_train_data",
    # Convenience functions
    "generate_summary_report",
]
