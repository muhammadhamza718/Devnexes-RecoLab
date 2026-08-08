# Day 5 Afternoon: Advanced Analysis - Data Model

**Feature ID:** 009-day5-evaluation-afternoon  
**Date:** 2026-08-08  
**Status:** Draft

---

## Overview

This document defines the data structures, schemas, and storage formats used for advanced analysis of model performance, error patterns, bias quantification, and limitations documentation. The data model focuses on structured analysis storage, pattern identification, and actionable insights generation.

---

## Core Data Structures

### 1. ErrorAnalysisResult

**Purpose**: Stores comprehensive error analysis results for a single model

**Schema**:
```python
class ErrorAnalysisResult:
    model_name: str                    # Model identifier (e.g., "hybrid")
    timestamp: str                     # ISO 8601 timestamp
    error_threshold: float            # Threshold for error classification (default: 3.0)
    
    # Error statistics
    total_errors: int                  # Total number of errors
    error_rate: float                  # Error rate (0-1)
    total_predictions: int            # Total number of predictions
    
    # User error patterns
    user_error_patterns: dict[int, dict]
    # Example: {user_id: {"error_count": 5, "error_type": "cold_start",
    #                   "precision": 0.08, "recall": 0.15}}
    
    # Item error patterns
    item_error_patterns: dict[int, dict]
    # Example: {item_id: {"error_count": 3, "error_type": "new_item",
    #                   "popularity_decile": 1}}
    
    # Activity level errors
    activity_level_errors: dict[str, dict]
    # Example: {"sparse_users": {"user_count": 10, "error_rate": 0.45},
    #           "active_users": {"user_count": 100, "error_rate": 0.12}}
    
    # Popularity level errors
    popularity_level_errors: dict[str, dict]
    # Example: {"new_items": {"item_count": 20, "error_rate": 0.38},
    #           "popular_items": {"item_count": 50, "error_rate": 0.08}}
    
    # Systematic bias detection
    systematic_bias: dict[str, any]
    # Example: {"has_bias": True, "bias_type": "popularity_bias",
    #           "bias_direction": "high_popularity", "confidence": 0.92}
    
    # Error distribution
    error_distribution: dict[str, int]  # Error type distribution
    # Example: {"cold_start_errors": 15, "new_item_errors": 8,
    #           "genre_mismatch": 5, "other": 12}
```

**Storage Format**: JSON file in `data/evaluation/advanced_analysis/error_analysis/{model_name}_error_analysis.json`

---

### 2. EdgeCaseAnalysisResult

**Purpose**: Stores edge case analysis results for a single model

**Schema**:
```python
class EdgeCaseAnalysisResult:
    model_name: str                    # Model identifier
    timestamp: str                     # ISO 8601 timestamp
    
    # Sparse user analysis (≤ 3 ratings)
    sparse_users: dict[str, any]
    # Example: {"user_count": 25, "avg_precision": 0.05, "avg_recall": 0.12,
    #           "comparison_to_overall": {"precision_diff": -0.10,
    #                                  "recall_diff": -0.15}}
    
    # Power user analysis (> 50 ratings)
    power_users: dict[str, any]
    # Example: {"user_count": 50, "avg_precision": 0.18, "avg_recall": 0.35,
    #           "comparison_to_overall": {"precision_diff": +0.05,
    #                                  "recall_diff": +0.08}}
    
    # New item analysis (≤ 5 ratings)
    new_items: dict[str, any]
    # Example: {"item_count": 30, "avg_precision": 0.08, "avg_recall": 0.10,
    #           "comparison_to_overall": {"precision_diff": -0.07,
    #                                  "recall_diff": -0.15}}
    
    # Popular item analysis (> 100 ratings)
    popular_items: dict[str, any]
    # Example: {"item_count": 45, "avg_precision": 0.16, "avg_recall": 0.32,
    #           "comparison_to_overall": {"precision_diff": +0.04,
    #                                  "recall_diff": +0.10}}
    
    # Genre-specific analysis
    genre_specific: dict[str, dict]
    # Example: {"Action": {"precision": 0.14, "recall": 0.28},
    #           "Comedy": {"precision": 0.12, "recall": 0.25},
    #           "Drama": {"precision": 0.16, "recall": 0.30}}
    
    # Temporal drift analysis
    temporal_drift: dict[str, any]
    # Example: {"has_drift": True, "drift_magnitude": 0.15,
    #           "early_period_precision": 0.18, "late_period_precision": 0.12}
    
    # Cross-validation summary
    cross_validation: dict[str, any]
    # Example: {"findings_consistent": True, "edge_cases_significant": True,
    #           "recommendation": "Improve cold-start handling"}
```

**Storage Format**: JSON file in `data/evaluation/advanced_analysis/edge_case_analysis/{model_name}_edge_case_analysis.json`

---

### 3. BiasAnalysisResult

**Purpose**: Stores bias quantification results for a single model

**Schema**:
```python
class BiasAnalysisResult:
    model_name: str                    # Model identifier
    timestamp: str                     # ISO 8601 timestamp
    
    # Popularity bias
    popularity_bias: dict[str, any]
    # Example: {"mean_popularity_decile": 7.2, "bias_level": "high",
    #           "distribution": {"decile_1": 0.05, "decile_10": 0.25}}
    
    # Catalog coverage
    catalog_coverage: dict[str, float]
    # Example: {"overall_coverage": 0.35, "unique_items": 450,
    #           "total_catalog": 1682, "coverage_percentage": 26.8}
    
    # Diversity metrics
    diversity_metrics: dict[str, float]
    # Example: {"intra_list_diversity": 0.45, "inter_list_diversity": 0.62,
    #           "overall_diversity_score": 0.54}
    
    # Novelty score
    novelty_score: float               # Novelty score (0-1)
    # Example: 0.38
    
    # Serendipity assessment
    serendipity: dict[str, any]
    # Example: {"serendipity_score": 0.42, "unexpectedness": 0.35,
    #           "relevance_maintained": True}
    
    # Fairness evaluation
    fairness: dict[str, any]
    # Example: {"user_group_fairness": {"active_users": 0.85,
    #                                   "cold_start_users": 0.62},
    #           "fairness_score": 0.74, "bias_detected": True}
    
    # Bias comparison across models
    bias_comparison: dict[str, dict]
    # Example: {"vs_content": {"popularity_bias_diff": -0.3,
    #                        "coverage_diff": +0.1},
    #           "vs_hybrid": {"popularity_bias_diff": +0.2,
    #                        "coverage_diff": -0.05}}
```

**Storage Format**: JSON file in `data/evaluation/advanced_analysis/bias_analysis/{model_name}_bias_analysis.json`

---

### 4. LimitationsDocumentation

**Purpose**: Stores comprehensive limitations documentation

**Schema**:
```python
class LimitationsDocumentation:
    timestamp: str                     # ISO 8601 timestamp
    
    # Model-specific limitations
    model_limitations: dict[str, dict]
    # Example: {"popularity": {"cold_start_performance": "poor",
    #                          "scalability": "excellent",
    #                          "robustness": "high",
    #                          "computational_requirements": "low"},
    #           "content": {"cold_start_performance": "good",
    #                      "scalability": "good",
    #                      "robustness": "medium",
    #                      "computational_requirements": "medium"},
    #           "hybrid": {"cold_start_performance": "good",
    #                     "scalability": "medium",
    #                     "robustness": "high",
    #                     "computational_requirements": "high"}}
    
    # Data limitations
    data_limitations: dict[str, any]
    # Example: {"dataset_size": 100004, "sparsity": 0.98,
    #           "temporal_coverage": "limited",
    #           "genre_balance": "moderate",
    #           "rating_distribution": "skewed"}
    
    # Evaluation limitations
    evaluation_limitations: dict[str, any]
    # Example: {"metrics": "limited to P@K, R@K, NDCG@K",
    #           "test_set_size": 20000,
    #           "statistical_significance": "moderate",
    #           "offline_evaluation": "no real-user feedback"}
    
    # Deployment limitations
    deployment_limitations: dict[str, any]
    # Example: {"computational_requirements": "medium",
    #           "latency": "acceptable for batch",
    #           "memory_usage": "4GB",
    #           "scalability": "horizontal scaling needed"}
    
    # Real-world applicability
    real_world_applicability: dict[str, any]
    # Example: {"cold_start_handling": "needs improvement",
    #           "new_item_handling": "content-based fallback",
    #           "user_preference_changes": "not addressed",
    #           "seasonal_trends": "not considered"}
    
    # Scalability considerations
    scalability: dict[str, any]
    # Example: {"user_scale": "up to 1M users",
    #           "item_scale": "up to 100K items",
    #           "latency_requirements": "batch processing acceptable",
    #           "memory_requirements": "4GB minimum"}
    
    # Known failure modes
    known_failure_modes: list[dict]
    # Example: [{"mode": "cold_start_users", "severity": "high",
    #            "mitigation": "content-based fallback"},
    #           {"mode": "new_items", "severity": "medium",
    #            "mitigation": "genre-based recommendations"},
    #           {"mode": "sparse_genre_data", "severity": "low",
    #            "mitigation": "popularity fallback"}]
```

**Storage Format**: JSON file in `data/evaluation/advanced_analysis/limitations/limitations_documentation.json`

---

### 5. AnalysisVisualizationMetadata

**Purpose**: Stores metadata for analysis-specific visualizations

**Schema**:
```python
class AnalysisVisualizationMetadata:
    chart_type: str                    # Type of chart (heatmap, scatter, radar, etc.)
    analysis_type: str                 # Type of analysis (error, edge_case, bias, etc.)
    title: str                         # Chart title
    description: str                   # Chart description
    timestamp: str                     # ISO 8601 timestamp
    
    # Data source
    data_source: str                   # Analysis result file used
    data_subset: dict[str, any]        # Data subset used
    
    # Chart configuration
    x_axis: str                        # X-axis label
    y_axis: str                        # Y-axis label
    color_scheme: str                  # Color scheme used
    colorblind_friendly: bool          # Whether color scheme is colorblind-friendly
    
    # File paths
    file_paths: dict[str, str]         # {format: file_path}
    # Example: {"png": "data/evaluation/advanced_analysis/visualizations/error_heatmap.png",
    #           "svg": "data/evaluation/advanced_analysis/visualizations/error_heatmap.svg"}
    
    # Dimensions
    width: int                         # Chart width in pixels
    height: int                        # Chart height in pixels
    dpi: int                           # Resolution
    
    # Insights
    key_insights: list[str]            # Key insights from the visualization
    # Example: ["High error rate for cold-start users",
    #           "Performance improves with user activity"]
```

**Storage Format**: JSON file in `data/evaluation/advanced_analysis/visualizations/{chart_name}_metadata.json`

---

## File Storage Structure

```
data/evaluation/advanced_analysis/
├── error_analysis/
│   ├── popularity_error_analysis.json
│   ├── content_error_analysis.json
│   ├── user_based_cf_error_analysis.json
│   ├── item_based_cf_error_analysis.json
│   └── hybrid_error_analysis.json
├── edge_case_analysis/
│   ├── popularity_edge_case_analysis.json
│   ├── content_edge_case_analysis.json
│   ├── user_based_cf_edge_case_analysis.json
│   ├── item_based_cf_edge_case_analysis.json
│   └── hybrid_edge_case_analysis.json
├── bias_analysis/
│   ├── popularity_bias_analysis.json
│   ├── content_bias_analysis.json
│   ├── user_based_cf_bias_analysis.json
│   ├── item_based_cf_bias_analysis.json
│   └── hybrid_bias_analysis.json
├── limitations/
│   └── limitations_documentation.json
├── visualizations/
│   ├── error_heatmap.png
│   ├── error_heatmap.svg
│   ├── error_heatmap_metadata.json
│   ├── user_activity_scatter.png
│   ├── user_activity_scatter.svg
│   ├── user_activity_scatter_metadata.json
│   ├── item_popularity_scatter.png
│   ├── item_popularity_scatter.svg
│   ├── item_popularity_scatter_metadata.json
│   ├── genre_radar.png
│   ├── genre_radar.svg
│   ├── genre_radar_metadata.json
│   ├── bias_comparison.png
│   ├── bias_comparison.svg
│   ├── bias_comparison_metadata.json
│   ├── limitations_matrix.png
│   ├── limitations_matrix.svg
│   └── limitations_matrix_metadata.json
└── analysis_summary.md
```

---

## Data Validation Rules

### ErrorAnalysisResult Validation
- `model_name` must be one of: ["popularity", "content", "user_based_cf", "item_based_cf", "hybrid"]
- `error_threshold` must be in range [0, 5] (rating scale)
- `error_rate` must be in range [0, 1]
- `total_errors` must be ≤ `total_predictions`
- User and item IDs must be valid
- `systematic_bias` confidence must be in range [0, 1]

### EdgeCaseAnalysisResult Validation
- `model_name` must be one of: ["popularity", "content", "user_based_cf", "item_based_cf", "hybrid"]
- Segment sizes must be positive integers
- Comparison differences can be negative or positive
- Genre-specific performance must be in range [0, 1]
- `temporal_drift` drift_magnitude must be in range [0, 1]

### BiasAnalysisResult Validation
- `model_name` must be one of: ["popularity", "content", "user_based_cf", "item_based_cf", "hybrid"]
- `mean_popularity_decile` must be in range [1, 10]
- `catalog_coverage` must be in range [0, 1]
- Diversity metrics must be in range [0, 1]
- `novelty_score` must be in range [0, 1]
- Fairness scores must be in range [0, 1]

### LimitationsDocumentation Validation
- All model names must be valid
- Performance assessments must be categorical (poor/good/excellent)
- Severity levels must be categorical (low/medium/high)
- Dataset metrics must be positive
- Failure modes must include severity and mitigation

---

## Data Relationships

### ErrorAnalysisResult → Day 5 Morning Results
- ErrorAnalysisResult references Day 5 Morning EvaluationResult via `model_name`
- Error analysis uses per-user metrics from EvaluationResult
- Error patterns derived from evaluation predictions

### EdgeCaseAnalysisResult → Day 5 Morning Results
- EdgeCaseAnalysisResult references Day 5 Morning SegmentedResult via `model_name`
- Edge case analysis uses segmented evaluation results
- Comparison to overall calculated from Day 5 Morning results

### BiasAnalysisResult → Day 5 Morning Results
- BiasAnalysisResult references Day 5 Morning EvaluationResult via `model_name`
- Bias analysis uses coverage and popularity metrics from evaluation
- Bias comparison uses multiple model results

### LimitationsDocumentation → All Analysis Results
- LimitationsDocumentation aggregates insights from all analysis types
- Model limitations derived from ErrorAnalysisResult and EdgeCaseAnalysisResult
- Data limitations derived from dataset analysis
- Deployment limitations derived from model performance analysis

### AnalysisVisualizationMetadata → Analysis Results
- AnalysisVisualizationMetadata references specific analysis result files
- Visualizations derived from analysis data
- Multiple visualizations can reference same analysis result

---

## Data Flow

```
┌─────────────────────────────────────────────────────────┐
│  Day 5 Morning Evaluation Results                         │
├─────────────────────────────────────────────────────────┤
│  ┌──────────────────┐                                   │
│  │ EvaluationResult │ ────── Load Results               │
│  └──────────────────┘                                   │
│  ┌──────────────────┐                                   │
│  │ SegmentedResult  │ ────── Load Segmented Results      │
│  └──────────────────┘                                   │
└────────────┬────────────────────────────────────────────┘
             │
             ├─────────────────────────────────────────────┐
             │                                             │
             ▼                                             ▼
┌──────────────────────────┐           ┌──────────────────────────┐
│  ErrorAnalyzer           │           │  EdgeCaseAnalyzer         │
│  (error patterns)        │           │  (edge cases)             │
└──────────────────────────┘           └──────────────────────────┘
             │                                             │
             ▼                                             ▼
┌──────────────────────────┐           ┌──────────────────────────┐
│  ErrorAnalysisResult     │           │  EdgeCaseAnalysisResult  │
└──────────────────────────┘           └──────────────────────────┘
             │                                             │
             └─────────────────────────────────────────────┐
                                                             │
                    ┌────────────────────────────────────────┘
                    │
                    ▼
          ┌──────────────────────────┐
          │  BiasAnalyzer            │
          │  (bias quantification)   │
          └──────────────────────────┘
                    │
                    ▼
          ┌──────────────────────────┐
          │  BiasAnalysisResult      │
          └──────────────────────────┘
                    │
                    ▼
          ┌──────────────────────────┐
          │  LimitationsAnalyzer     │
          │  (limitations doc)       │
          └──────────────────────────┘
                    │
                    ▼
          ┌──────────────────────────┐
          │  LimitationsDocumentation│
          └──────────────────────────┘
                    │
                    ▼
          ┌──────────────────────────┐
          │  AnalysisVisualization   │
          │  (charts & insights)      │
          └──────────────────────────┘
```

---

## Data Retention Policy

- **Error Analysis Results**: Keep all analyses (version-controlled by timestamp)
- **Edge Case Analysis Results**: Keep all analyses (version-controlled by timestamp)
- **Bias Analysis Results**: Keep all analyses (version-controlled by timestamp)
- **Limitations Documentation**: Keep latest documentation
- **Visualizations**: Keep latest visualizations
- **Analysis Summary**: Keep latest summary

---

## Data Backups

- Analysis results should be backed up to separate location
- Timestamp-based versioning enables rollback
- Day 5 Morning results should be preserved (read-only)
- Analysis scripts should be version-controlled
- Original evaluation metadata should be preserved
