# Day 5 Morning: Full Model Evaluation - Data Model

**Feature ID:** 009-day5-evaluation  
**Date:** 2026-08-08  
**Status:** Draft

---

## Overview

This document defines the data structures, schemas, and storage formats used for comprehensive model evaluation. The data model focuses on structured result storage, segmentation analysis, and visualization generation.

---

## Core Data Structures

### 1. EvaluationResult

**Purpose**: Stores comprehensive evaluation results for a single model

**Schema**:
```python
class EvaluationResult:
    model_name: str                    # Model identifier (e.g., "hybrid")
    timestamp: str                     # ISO 8601 timestamp
    k_values: list[int]                # K values used (e.g., [5, 10, 20])
    test_dataset_size: int             # Number of test users
    test_item_count: int               # Number of unique test items
    
    # Core metrics (nested by K value)
    metrics: dict[str, dict[str, float]]  # {k: {metric: value}}
    # Example: {"5": {"precision": 0.15, "recall": 0.23, "ndcg": 0.18},
    #           "10": {"precision": 0.12, "recall": 0.31, "ndcg": 0.16},
    #           "20": {"precision": 0.10, "recall": 0.42, "ndcg": 0.15}}
    
    # Coverage and bias metrics
    catalog_coverage: float            # Percentage of catalog covered (0-1)
    mean_popularity_decile: float      # Mean popularity decile (1-10)
    catalog_coverage_count: int       # Number of unique items recommended
    
    # Per-user metrics (for statistical analysis)
    per_user_metrics: dict[int, dict[str, float]]
    # Example: {user_id: {"precision_at_10": 0.25, "recall_at_10": 0.40}}
    
    # Statistical measures
    metric_std_dev: dict[str, float]   # Standard deviation across users
    metric_confidence_interval: dict[str, tuple[float, float]]  # 95% CI
    
    # Metadata
    evaluation_time_seconds: float     # Time taken for evaluation
    error_count: int                   # Number of evaluation errors
    warnings: list[str]                # Evaluation warnings
```

**Storage Format**: JSON file in `data/evaluation/results/{model_name}_results.json`

---

### 2. SegmentedResult

**Purpose**: Stores evaluation results for specific user/item segments

**Schema**:
```python
class SegmentedResult:
    model_name: str                    # Model identifier
    segment_name: str                  # Segment identifier (e.g., "cold_start_users")
    segment_description: str           # Human-readable description
    timestamp: str                     # ISO 8601 timestamp
    
    # Segment characteristics
    segment_size: int                  # Number of users/items in segment
    segment_percentage: float          # Percentage of total (0-1)
    segment_criteria: dict[str, any]   # Criteria used for segmentation
    # Example: {"min_ratings": 0, "max_ratings": 5}
    
    # Metrics for this segment
    metrics: dict[str, dict[str, float]]  # Same structure as EvaluationResult
    coverage: float                    # Catalog coverage for this segment
    popularity_decile: float           # Mean popularity decile
    
    # Comparison to overall performance
    performance_delta: dict[str, float]  # Difference from overall
    # Example: {"precision_at_10": -0.05, "recall_at_10": -0.08}
    performance_relative: dict[str, float]  # Percentage difference
    # Example: {"precision_at_10": -25.0, "recall_at_10": -20.0}
    
    # Statistical significance
    statistical_test: dict[str, any]  # If applicable
    # Example: {"test_type": "t_test", "p_value": 0.023, "significant": True}
```

**Storage Format**: JSON file in `data/evaluation/segmented/{model_name}_{segment_name}_results.json`

---

### 3. ComparisonResult

**Purpose**: Stores model comparison and statistical analysis results

**Schema**:
```python
class ComparisonResult:
    timestamp: str                     # ISO 8601 timestamp
    evaluated_models: list[str]        # Model names evaluated
    k_values: list[int]                # K values used
    
    # Model results reference
    model_results: dict[str, EvaluationResult]  # {model_name: EvaluationResult}
    
    # Performance ranking
    ranking: dict[str, list[str]]      # Ranked models by metric
    # Example: {"precision_at_10": ["hybrid", "content", "user_based_cf", 
    #                               "item_based_cf", "popularity"]}
    
    # Statistical significance tests
    pairwise_tests: dict[str, dict[str, any]]
    # Example: {"hybrid_vs_content": {"metric": "precision_at_10",
    #                               "test": "paired_t_test",
    #                               "t_statistic": 2.45,
    #                               "p_value": 0.015,
    #                               "significant": True,
    #                               "mean_diff": 0.025}}
    
    # Performance difference matrix
    performance_matrix: dict[str, dict[str, dict[str, float]]]
    # Example: {"hybrid": {"content": {"precision_at_10": 0.025}}}
    
    # Best performing model per metric
    best_model: dict[str, str]         # {metric: model_name}
    
    # Summary statistics
    summary: dict[str, any]
    # Example: {"avg_precision": 0.135, "std_precision": 0.045,
    #           "avg_recall": 0.285, "std_recall": 0.082}
```

**Storage Format**: JSON file in `data/evaluation/comparison/model_comparison.json`

---

### 4. VisualizationMetadata

**Purpose**: Stores metadata for generated visualizations

**Schema**:
```python
class VisualizationMetadata:
    chart_type: str                    # Type of chart (bar, line, pie, etc.)
    title: str                         # Chart title
    description: str                   # Chart description
    timestamp: str                     # ISO 8601 timestamp
    
    # Data source
    data_source: str                   # Result file used
    data_subset: dict[str, any]        # Data subset used
    
    # Chart configuration
    x_axis: str                        # X-axis label
    y_axis: str                        # Y-axis label
    legend: bool                       # Whether legend is present
    color_scheme: str                  # Color scheme used
    
    # File paths
    file_paths: dict[str, str]         # {format: file_path}
    # Example: {"png": "data/evaluation/visualizations/comparison_bar.png",
    #           "svg": "data/evaluation/visualizations/comparison_bar.svg"}
    
    # Dimensions
    width: int                         # Chart width in pixels
    height: int                        # Chart height in pixels
    dpi: int                           # Resolution
```

**Storage Format**: JSON file in `data/evaluation/visualizations/{chart_name}_metadata.json`

---

## File Storage Structure

```
data/evaluation/
├── results/
│   ├── popularity_results.json
│   ├── content_results.json
│   ├── user_based_cf_results.json
│   ├── item_based_cf_results.json
│   └── hybrid_results.json
├── comparison/
│   ├── model_comparison.json
│   └── performance_matrix.json
├── segmented/
│   ├── popularity_cold_start_users.json
│   ├── popularity_active_users.json
│   ├── content_cold_start_users.json
│   ├── content_active_users.json
│   └── ... (for all models and segments)
├── visualizations/
│   ├── comparison_bar.png
│   ├── comparison_bar.svg
│   ├── comparison_bar_metadata.json
│   ├── metric_trends.png
│   ├── metric_trends.svg
│   ├── metric_trends_metadata.json
│   ├── coverage_pie.png
│   ├── coverage_pie.svg
│   ├── coverage_pie_metadata.json
│   └── ... (for all visualizations)
└── evaluation_summary.json
```

---

## Data Validation Rules

### Input Validation Rules (Evaluation Parameters)
- `k_values` must be subset of [5, 10, 20] (must be validated before evaluation)
- `metrics` must be from allowed set: ["precision", "recall", "ndcg", "coverage", "popularity_decile"]
- `random_seed` must be integer in range [0, 2^32-1]
- `model_names` must be subset of: ["popularity", "content", "user_based_cf", "item_based_cf", "hybrid"]
- All parameters must be validated before evaluation execution to prevent DoS via extreme values

### EvaluationResult Validation
- `model_name` must be one of: ["popularity", "content", "user_based_cf", "item_based_cf", "hybrid"]
- `k_values` must be subset of [5, 10, 20]
- `metrics` values must be in range [0, 1] for precision, recall, ndcg
- `catalog_coverage` must be in range [0, 1]
- `mean_popularity_decile` must be in range [1, 10]
- `per_user_metrics` keys must be valid user IDs
- Timestamp must be valid ISO 8601 format

### SegmentedResult Validation
- `segment_name` must be one of: ["cold_start_users", "active_users", "new_items", "genre_based"]
- `segment_size` must be positive integer
- `segment_percentage` must be in range [0, 1]
- `performance_delta` values can be negative or positive
- `performance_relative` values represent percentage change

### ComparisonResult Validation
- `evaluated_models` must include all 5 models
- `ranking` must include all 5 models in each list
- `pairwise_tests` must include all model pairs
- `p_value` must be in range [0, 1]
- `significant` must be boolean based on p_value < 0.05

---

## Data Relationships

### EvaluationResult → SegmentedResult
- SegmentedResult references EvaluationResult via `model_name`
- SegmentedResult metrics are subset of EvaluationResult metrics
- Performance deltas calculated against EvaluationResult

### EvaluationResult → ComparisonResult
- ComparisonResult aggregates multiple EvaluationResult objects
- ComparisonResult performs statistical tests on EvaluationResult data
- ComparisonResult ranks models based on EvaluationResult metrics

### EvaluationResult → VisualizationMetadata
- VisualizationMetadata references EvaluationResult via `data_source`
- Visualizations derived from EvaluationResult metrics
- Multiple visualizations can reference same EvaluationResult

---

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│  EvaluationOrchestrator                                  │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────┐                                   │
│  │ Model Manager    │ ────── Load Models               │
│  └──────────────────┘                                   │
│  ┌──────────────────┐                                   │
│  │ Data Provider    │ ────── Load Test Data             │
│  └──────────────────┘                                   │
│  ┌──────────────────┐                                   │
│  │ Metrics Engine   │ ────── Calculate Metrics          │
│  └──────────────────┘                                   │
└────────────┬────────────────────────────────────────────┘
             │
             ├─────────────────────────────────────────────┐
             │                                             │
             ▼                                             ▼
┌──────────────────────────┐           ┌──────────────────────────┐
│  EvaluationResult        │           │  SegmentedResult         │
│  (per model)             │           │  (per segment)           │
└──────────────────────────┘           └──────────────────────────┘
             │                                             │
             └─────────────────────────────────────────────┐
                                                             │
                    ┌────────────────────────────────────────┘
                    │
                    ▼
          ┌──────────────────────────┐
          │  ComparisonResult        │
          │  (model comparison)      │
          └──────────────────────────┘
                    │
                    ▼
          ┌──────────────────────────┐
          │  VisualizationMetadata   │
          │  (charts & plots)        │
          └──────────────────────────┘
```

---

## Data Retention Policy

- **Evaluation Results**: Keep all runs (version-controlled by timestamp)
- **Comparison Results**: Keep latest comparison
- **Segmented Results**: Keep all segment analyses
- **Visualizations**: Keep latest visualizations
- **Evaluation Summary**: Keep latest summary

---

## Data Backups

- Evaluation results should be backed up to separate location
- Timestamp-based versioning enables rollback
- Original test dataset should be preserved
- Model artifacts should not be modified during evaluation
