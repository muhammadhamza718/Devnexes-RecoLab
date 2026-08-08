# Day 5 Morning: Full Model Evaluation - Implementation Plan

**Feature ID:** 009-day5-evaluation  
**Date:** 2026-08-08  
**Status:** Draft  
**Effort:** 4 hours (Day 5 Morning)

---

## Architecture Overview

The comprehensive evaluation framework leverages the existing metrics.py framework and ModelManager to perform offline evaluation of all 5 models. The architecture follows a script-based evaluation pattern that doesn't interfere with the Streamlit UI and produces structured results for analysis and documentation.

### System Architecture Extension

```
┌─────────────────────────────────────────────────────────────┐
│                    Evaluation Framework                          │
├─────────────────────────────────────────────────────────────┤
│  Evaluation Scripts                                           │
│  ├── main_evaluation.py (orchestrates full evaluation)      │
│  ├── segmented_evaluation.py (segmented analysis)            │
│  ├── statistical_analysis.py (significance testing)           │
│  └── visualization_generator.py (chart generation)          │
├─────────────────────────────────────────────────────────────┤
│  Extended Backend Integration                                │
│  ├── ModelManager (model loading)                             │
│  ├── metrics.py (metrics calculation)                        │
│  ├── DataProvider (test data loading)                         │
│  └── ResultStorage (structured result storage)               │
├─────────────────────────────────────────────────────────────┤
│  Result Storage Layer                                           │
│  ├── data/evaluation/results/ (per-model JSON results)         │
│  ├── data/evaluation/comparison/ (comparison results)          │
│  ├── data/evaluation/segmented/ (segmented analysis)           │
│  └── data/evaluation/visualizations/ (generated charts)       │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Main Evaluation Orchestrator

**Purpose**: Coordinate comprehensive evaluation of all models

**Design Pattern**: Orchestrator Pattern with Result Aggregation

**Interface**:
```python
class EvaluationOrchestrator:
    def __init__(self, model_manager: ModelManager, data_provider: DataProvider):
        self.model_manager = model_manager
        self.data_provider = data_provider
        self.result_storage = ResultStorage()
    
    def run_full_evaluation(self, k_values: list[int] = [5, 10, 20]) -> dict:
        """Run comprehensive evaluation of all models."""
        models = ['popularity', 'content', 'user_based_cf', 'item_based_cf', 'hybrid']
        results = {}
        
        for model_name in models:
            print(f"Evaluating {model_name}...")
            model_results = self._evaluate_model(model_name, k_values)
            results[model_name] = model_results
            self.result_storage.save_model_results(model_name, model_results)
        
        comparison = self._generate_comparison(results)
        self.result_storage.save_comparison_results(comparison)
        
        return results
    
    def _evaluate_model(self, model_name: str, k_values: list[int]) -> dict:
        """Evaluate a single model on all metrics."""
        model, _ = self.model_manager.get_model(model_name)
        test_data = self.data_provider.get_test_data()
        
        results = {}
        for k in k_values:
            results[f'precision_at_{k}'] = self._calculate_precision(model, test_data, k)
            results[f'recall_at_{k}'] = self._calculate_recall(model, test_data, k)
            results[f'ndcg_at_{k}'] = self._calculate_ndcg(model, test_data, k)
        
        results['catalog_coverage'] = self._calculate_coverage(model, test_data)
        results['mean_popularity_decile'] = self._calculate_popularity_decile(model, test_data)
        
        return results
```

---

### 2. Segmented Evaluation Engine

**Purpose**: Perform segmented analysis by user activity, item popularity, genre

**Design Pattern**: Segmentation Pattern with Result Partitioning

**Interface**:
```python
class SegmentedEvaluation:
    def __init__(self, model_manager: ModelManager, data_provider: DataProvider):
        self.model_manager = model_manager
        self.data_provider = data_provider
    
    def run_segmented_evaluation(self, model_name: str) -> dict:
        """Run segmented evaluation for a model."""
        test_data = self.data_provider.get_test_data()
        
        segments = {
            'cold_start_users': self._segment_cold_start_users(test_data),
            'active_users': self._segment_active_users(test_data),
            'new_items': self._segment_new_items(test_data),
            'genre_based': self._segment_by_genre(test_data)
        }
        
        results = {}
        for segment_name, segment_data in segments.items():
            results[segment_name] = self._evaluate_on_segment(model_name, segment_data)
        
        return results
    
    def _segment_cold_start_users(self, test_data) -> pd.DataFrame:
        """Identify users with ≤ 5 ratings."""
        user_counts = test_data.groupby('userId').size()
        cold_start_users = user_counts[user_counts <= 5].index
        return test_data[test_data['userId'].isin(cold_start_users)]
    
    def _segment_active_users(self, test_data) -> pd.DataFrame:
        """Identify users with > 20 ratings."""
        user_counts = test_data.groupby('userId').size()
        active_users = user_counts[user_counts > 20].index
        return test_data[test_data['userId'].isin(active_users)]
```

---

### 3. Statistical Analysis Engine

**Purpose**: Perform statistical significance testing between models

**Design Pattern**: Statistical Testing with Hypothesis Validation

**Interface**:
```python
class StatisticalAnalysis:
    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level
    
    def compare_models(self, results: dict) -> dict:
        """Perform statistical significance tests between models."""
        model_names = list(results.keys())
        pairwise_tests = {}
        
        for i, model1 in enumerate(model_names):
            for model2 in model_names[i+1:]:
                test_result = self._paired_t_test(
                    results[model1], 
                    results[model2]
                )
                pairwise_tests[f"{model1}_vs_{model2}"] = test_result
        
        return pairwise_tests
    
    def _paired_t_test(self, results1: dict, results2: dict) -> dict:
        """Perform paired t-test between two models."""
        # Extract per-user precision@10 values for comparison
        scores1 = self._extract_per_user_scores(results1, 'precision_at_10')
        scores2 = self._extract_per_user_scores(results2, 'precision_at_10')
        
        t_stat, p_value = scipy.stats.ttest_rel(scores1, scores2)
        
        return {
            't_statistic': t_stat,
            'p_value': p_value,
            'significant': p_value < self.significance_level,
            'mean_diff': np.mean(scores1) - np.mean(scores2)
        }
```

---

### 4. Visualization Generator

**Purpose**: Generate performance comparison charts and visualizations

**Design Pattern**: Visualization Factory with Chart Generation

**Interface**:
```python
class VisualizationGenerator:
    def __init__(self, results: dict, output_dir: str):
        self.results = results
        self.output_dir = output_dir
    
    def generate_all_charts(self) -> dict:
        """Generate all visualization charts."""
        charts = {}
        
        charts['comparison_bar'] = self._generate_comparison_bar_chart()
        charts['metric_trends'] = self._generate_metric_trends()
        charts['coverage_pie'] = self._generate_coverage_pie()
        charts['statistical_tests'] = self._generate_statistical_tests_chart()
        
        return charts
    
    def _generate_comparison_bar_chart(self) -> str:
        """Generate model comparison bar chart."""
        # Extract precision@10 for all models
        models = list(self.results.keys())
        precisions = [self.results[m]['precision_at_10'] for m in models]
        
        plt.figure(figsize=(10, 6))
        plt.bar(models, precisions, color=['red', 'blue', 'green', 'orange', 'purple'])
        plt.title('Model Comparison: Precision@10')
        plt.ylabel('Precision')
        plt.xlabel('Model')
        plt.ylim(0, 1.0)
        
        output_path = os.path.join(self.output_dir, 'comparison_bar.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
```

---

## Data Model

### Evaluation Result Structure
```python
class EvaluationResult:
    model_name: str
    timestamp: str
    k_values: list[int]
    metrics: dict[str, float]  # precision_at_5, recall_at_5, ndcg_at_5, etc.
    catalog_coverage: float
    mean_popularity_decile: float
    per_user_metrics: dict[int, dict]  # user_id -> {metric: value}
    statistical_tests: dict[str, dict]  # if applicable
```

### Segmented Result Structure
```python
class SegmentedResult:
    model_name: str
    segment_name: str
    timestamp: str
    metrics: dict[str, float]
    segment_size: int
    comparison_to_overall: dict[str, float]
```

### Comparison Result Structure
```python
class ComparisonResult:
    timestamp: str
    model_results: dict[str, EvaluationResult]
    ranking: list[str]  # ordered by performance
    statistical_tests: dict[str, dict]
    performance_table: pd.DataFrame
```

---

## Integration Points

### ModelManager Integration
- Load models via `model_manager.get_model(model_name)`
- Handle model loading failures gracefully
- Use existing model caching

### Metrics Framework Integration
- Extend existing metrics.py if needed
- Use metrics.precision_at_k, metrics.recall_at_k, metrics.ndcg_at_k
- Ensure consistency with existing evaluation framework

### DataProvider Integration
- Load test data via `data_provider.get_test_data()`
- Validate test data structure
- Handle missing data gracefully

### Result Storage Integration
- Write to data/evaluation/ directory
- Use JSON format for structured results
- Include metadata for reproducibility

---

## Error Handling Strategy

### Model Loading Failures
- Log error and skip model if loading fails
- Document missing models in results
- Continue evaluation with available models

### Data Loading Failures
- Validate test data structure before processing
- Handle missing columns gracefully
- Document data quality issues

### Metric Calculation Failures
- Use safe division with small epsilon
- Handle edge cases (empty data, division by zero)
- Return default values for failed calculations

### Visualization Failures
- Log matplotlib errors
- Fallback to simple text output if charts fail
- Continue with remaining visualization generation

---

## Performance Considerations

### Memory Management
- Process evaluation in batches if memory constrained
- Use sparse matrix operations for efficiency
- Clear intermediate data structures after use
- Monitor memory usage during evaluation

### Computation Time
- Estimated evaluation time: 5-10 minutes for all models
- Progress indicators for long-running operations
- Early stopping on critical failures

### File I/O
- Batch file writes to reduce I/O overhead
- Compress result files if large
- Ensure atomic file writes where possible

---

## Testing Strategy

### Unit Tests
- Test metric calculation accuracy
- Test result storage functionality
- Test statistical test calculations
- Test segmentation logic

### Integration Tests
- Test end-to-end evaluation pipeline
- Test model integration
- Test data loading and validation
- Test visualization generation

### Validation Tests
- Validate results against known benchmarks
- Validate statistical test correctness
- Validate chart generation quality
- Validate result format and structure
