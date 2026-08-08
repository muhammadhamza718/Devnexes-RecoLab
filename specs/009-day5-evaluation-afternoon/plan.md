# Day 5 Afternoon: Advanced Analysis - Implementation Plan

**Feature ID:** 009-day5-evaluation-afternoon  
**Date:** 2026-08-08  
**Status:** Draft  
**Effort:** 4 hours (Day 5 Afternoon)

---

## Architecture Overview

The advanced analysis framework leverages Day 5 Morning evaluation results to perform deep analysis of model performance, error patterns, bias quantification, and limitations documentation. The architecture follows a script-based analysis pattern that doesn't interfere with the Streamlit UI and produces actionable insights for documentation and improvement.

### System Architecture Extension

```
┌─────────────────────────────────────────────────────────────┐
│                    Advanced Analysis Framework                 │
├─────────────────────────────────────────────────────────────┤
│  Analysis Scripts                                             │
│  ├── error_analysis.py (error pattern analysis)               │
│  ├── edge_case_analysis.py (edge case identification)          │
│  ├── bias_analysis.py (bias quantification)                    │
│  ├── limitations_analysis.py (limitations documentation)       │
│  └── visualization_generator.py (analysis charts)              │
├─────────────────────────────────────────────────────────────┤
│  Analysis Integration Layer                                   │
│  ├── EvaluationResultLoader (loads Day 5 Morning results from 009-day5-evaluation)      │
│  ├── ErrorAnalyzer (error pattern analysis)                    │
│  ├── EdgeCaseAnalyzer (edge case identification)               │
│  ├── BiasAnalyzer (bias quantification)                        │
│  ├── LimitationsAnalyzer (limitations documentation)            │
│  └── AnalysisStorage (structured result storage)               │
├─────────────────────────────────────────────────────────────┤
│  Result Storage Layer                                           │
│  ├── data/evaluation/advanced_analysis/error_analysis/         │
│  ├── data/evaluation/advanced_analysis/edge_case_analysis/     │
│  ├── data/evaluation/advanced_analysis/bias_analysis/          │
│  ├── data/evaluation/advanced_analysis/limitations/            │
│  └── data/evaluation/advanced_analysis/visualizations/         │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Error Analysis Engine

**Purpose**: Analyze error patterns in model predictions

**Design Pattern**: Error Classification Pattern with Pattern Recognition

**Interface**:
```python
class ErrorAnalyzer:
    def __init__(self, evaluation_results: dict, test_data: pd.DataFrame):
        self.evaluation_results = evaluation_results
        self.test_data = test_data
        self.error_threshold = 3.0  # Ratings below 3.0 considered errors
    
    def analyze_errors(self, model_name: str) -> dict:
        """Perform comprehensive error analysis for a model."""
        model_results = self.evaluation_results[model_name]
        
        errors = {
            'total_errors': self._count_errors(model_results),
            'error_rate': self._calculate_error_rate(model_results),
            'user_error_patterns': self._analyze_user_error_patterns(model_results),
            'item_error_patterns': self._analyze_item_error_patterns(model_results),
            'activity_level_errors': self._analyze_activity_level_errors(model_results),
            'popularity_level_errors': self._analyze_popularity_level_errors(model_results),
            'systematic_bias': self._detect_systematic_bias(model_results)
        }
        
        return errors
    
    def _count_errors(self, model_results: dict) -> int:
        """Count total errors in model predictions."""
        error_count = 0
        for user_id, user_metrics in model_results['per_user_metrics'].items():
            # Identify errors based on predicted rating vs actual
            # This is a simplified example
            if user_metrics.get('precision_at_10', 0) < 0.1:
                error_count += 1
        return error_count
    
    def _analyze_user_error_patterns(self, model_results: dict) -> dict:
        """Analyze error patterns per user."""
        user_errors = {}
        for user_id, user_metrics in model_results['per_user_metrics'].items():
            user_errors[user_id] = {
                'error_count': self._count_user_errors(user_id, user_metrics),
                'error_type': self._classify_user_error(user_id, user_metrics)
            }
        return user_errors
```

---

### 2. Edge Case Analysis Engine

**Purpose**: Identify and analyze edge cases (sparse users, power users, new items, etc.)

**Design Pattern**: Segmentation Pattern with Edge Case Detection

**Interface**:
```python
class EdgeCaseAnalyzer:
    def __init__(self, evaluation_results: dict, test_data: pd.DataFrame):
        self.evaluation_results = evaluation_results
        self.test_data = test_data
    
    def analyze_edge_cases(self, model_name: str) -> dict:
        """Perform edge case analysis for a model."""
        edge_cases = {
            'sparse_users': self._analyze_sparse_users(model_name),
            'power_users': self._analyze_power_users(model_name),
            'new_items': self._analyze_new_items(model_name),
            'popular_items': self._analyze_popular_items(model_name),
            'genre_specific': self._analyze_genre_specific(model_name),
            'temporal_drift': self._analyze_temporal_drift(model_name)
        }
        
        return edge_cases
    
    def _analyze_sparse_users(self, model_name: str) -> dict:
        """Analyze performance for sparse users (≤ 3 ratings)."""
        model_results = self.evaluation_results[model_name]
        sparse_users = self._identify_sparse_users()
        
        sparse_metrics = {
            'user_count': len(sparse_users),
            'avg_precision': self._calculate_avg_precision(model_results, sparse_users),
            'avg_recall': self._calculate_avg_recall(model_results, sparse_users),
            'comparison_to_overall': self._compare_to_overall(model_results, sparse_users)
        }
        
        return sparse_metrics
    
    def _identify_sparse_users(self) -> list[int]:
        """Identify users with ≤ 3 ratings."""
        user_counts = self.test_data.groupby('userId').size()
        sparse_users = user_counts[user_counts <= 3].index.tolist()
        return sparse_users
```

---

### 3. Bias Analysis Framework

**Purpose**: Quantify model bias using measurable metrics

**Design Pattern**: Bias Quantification Pattern with Metric Calculation

**Interface**:
```python
class BiasAnalyzer:
    def __init__(self, evaluation_results: dict, test_data: pd.DataFrame):
        self.evaluation_results = evaluation_results
        self.test_data = test_data
    
    def analyze_bias(self, model_name: str) -> dict:
        """Perform comprehensive bias analysis for a model."""
        bias_analysis = {
            'popularity_bias': self._calculate_popularity_bias(model_name),
            'catalog_coverage': self._calculate_catalog_coverage(model_name),
            'diversity_metrics': self._calculate_diversity_metrics(model_name),
            'novelty_score': self._calculate_novelty_score(model_name),
            'serendipity': self._calculate_serendipity(model_name),
            'fairness': self._evaluate_fairness(model_name),
            'bias_comparison': self._compare_bias_across_models(model_name)
        }
        
        return bias_analysis
    
    def _calculate_popularity_bias(self, model_name: str) -> dict:
        """Calculate popularity bias metrics."""
        model_results = self.evaluation_results[model_name]
        
        # Extract popularity decile from evaluation results
        mean_popularity_decile = model_results.get('mean_popularity_decile', 5.0)
        
        popularity_bias = {
            'mean_popularity_decile': mean_popularity_decile,
            'bias_level': self._classify_popularity_bias(mean_popularity_decile),
            'distribution': self._calculate_popularity_distribution(model_results)
        }
        
        return popularity_bias
    
    def _calculate_diversity_metrics(self, model_name: str) -> dict:
        """Calculate diversity metrics (intra-list, inter-list)."""
        model_results = self.evaluation_results[model_name]
        
        diversity = {
            'intra_list_diversity': self._calculate_intra_list_diversity(model_results),
            'inter_list_diversity': self._calculate_inter_list_diversity(model_results),
            'overall_diversity_score': 0.0  # Calculated from above
        }
        
        return diversity
```

---

### 4. Limitations Documentation Engine

**Purpose**: Document comprehensive limitations across models, data, evaluation, and deployment

**Design Pattern**: Documentation Pattern with Impact Assessment

**Interface**:
```python
class LimitationsAnalyzer:
    def __init__(self, evaluation_results: dict, test_data: pd.DataFrame):
        self.evaluation_results = evaluation_results
        self.test_data = test_data
    
    def document_limitations(self) -> dict:
        """Document comprehensive limitations."""
        limitations = {
            'model_limitations': self._analyze_model_limitations(),
            'data_limitations': self._analyze_data_limitations(),
            'evaluation_limitations': self._analyze_evaluation_limitations(),
            'deployment_limitations': self._analyze_deployment_limitations(),
            'real_world_applicability': self._analyze_real_world_applicability(),
            'scalability': self._analyze_scalability(),
            'known_failure_modes': self._identify_failure_modes()
        }
        
        return limitations
    
    def _analyze_model_limitations(self) -> dict:
        """Analyze model-specific limitations."""
        model_limitations = {}
        
        for model_name in self.evaluation_results.keys():
            model_results = self.evaluation_results[model_name]
            
            model_limitations[model_name] = {
                'cold_start_performance': self._assess_cold_start_performance(model_results),
                'scalability': self._assess_model_scalability(model_results),
                'robustness': self._assess_model_robustness(model_results),
                'computational_requirements': self._assess_computational_requirements(model_name)
            }
        
        return model_limitations
    
    def _analyze_data_limitations(self) -> dict:
        """Analyze data-related limitations."""
        data_limitations = {
            'dataset_size': len(self.test_data),
            'sparsity': self._calculate_sparsity(),
            'temporal_coverage': self._assess_temporal_coverage(),
            'genre_balance': self._assess_genre_balance(),
            'rating_distribution': self._assess_rating_distribution()
        }
        
        return data_limitations
```

---

### 5. Advanced Visualization Generator

**Purpose**: Generate analysis-specific visualizations

**Design Pattern**: Visualization Factory with Analysis-Specific Charts

**Interface**:
```python
class AdvancedVisualizationGenerator:
    def __init__(self, analysis_results: dict, output_dir: str):
        self.analysis_results = analysis_results
        self.output_dir = output_dir
    
    def generate_analysis_charts(self) -> dict:
        """Generate all analysis-specific visualizations."""
        charts = {}
        
        charts['error_heatmap'] = self._generate_error_heatmap()
        charts['user_activity_scatter'] = self._generate_user_activity_scatter()
        charts['item_popularity_scatter'] = self._generate_item_popularity_scatter()
        charts['genre_radar'] = self._generate_genre_radar()
        charts['bias_comparison'] = self._generate_bias_comparison()
        charts['limitations_matrix'] = self._generate_limitations_matrix()
        
        return charts
    
    def _generate_error_heatmap(self) -> str:
        """Generate error distribution heatmap."""
        # Extract error patterns from analysis results
        error_patterns = self.analysis_results['error_analysis']['user_error_patterns']
        
        # Create heatmap data
        # This is a simplified example
        plt.figure(figsize=(12, 8))
        # Create heatmap visualization
        # ... (visualization code)
        
        output_path = os.path.join(self.output_dir, 'error_heatmap.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def _generate_user_activity_scatter(self) -> str:
        """Generate user activity vs. performance scatter plot."""
        # Extract user activity and performance data
        # This is a simplified example
        plt.figure(figsize=(10, 6))
        # Create scatter plot
        # ... (visualization code)
        
        output_path = os.path.join(self.output_dir, 'user_activity_scatter.png')
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return output_path
```

---

## Data Model

### Error Analysis Result Structure
```python
class ErrorAnalysisResult:
    model_name: str
    timestamp: str
    total_errors: int
    error_rate: float
    user_error_patterns: dict[int, dict]  # user_id -> error analysis
    item_error_patterns: dict[int, dict]  # item_id -> error analysis
    activity_level_errors: dict[str, float]  # activity_level -> error_rate
    popularity_level_errors: dict[str, float]  # popularity_level -> error_rate
    systematic_bias: dict[str, any]  # detected systematic bias
```

### Edge Case Analysis Result Structure
```python
class EdgeCaseAnalysisResult:
    model_name: str
    timestamp: str
    sparse_users: dict[str, any]  # sparse user performance
    power_users: dict[str, any]  # power user performance
    new_items: dict[str, any]  # new item performance
    popular_items: dict[str, any]  # popular item performance
    genre_specific: dict[str, dict]  # genre-specific performance
    temporal_drift: dict[str, any]  # temporal performance drift
```

### Bias Analysis Result Structure
```python
class BiasAnalysisResult:
    model_name: str
    timestamp: str
    popularity_bias: dict[str, any]  # popularity bias metrics
    catalog_coverage: dict[str, float]  # coverage metrics
    diversity_metrics: dict[str, float]  # diversity metrics
    novelty_score: float  # novelty score
    serendipity: dict[str, any]  # serendipity metrics
    fairness: dict[str, any]  # fairness evaluation
    bias_comparison: dict[str, dict]  # comparison to other models
```

### Limitations Documentation Structure
```python
class LimitationsDocumentation:
    timestamp: str
    model_limitations: dict[str, dict]  # per-model limitations
    data_limitations: dict[str, any]  # data-related limitations
    evaluation_limitations: dict[str, any]  # evaluation limitations
    deployment_limitations: dict[str, any]  # deployment limitations
    real_world_applicability: dict[str, any]  # real-world constraints
    scalability: dict[str, any]  # scalability considerations
    known_failure_modes: list[dict]  # known failure modes
```

---

## Integration Points

### Day 5 Morning Results Integration
- Load evaluation results from data/evaluation/ directory
- Use EvaluationResultLoader for structured loading
- Validate result format before analysis
- Handle missing results gracefully

### Test Data Integration
- Load test data for additional analysis
- Use existing DataProvider if available
- Calculate additional metrics if needed
- Maintain data consistency with Day 5 Morning

### Model Metadata Integration
- Use model metadata from Day 5 Morning
- Include model parameters in limitations analysis
- Reference model training dates
- Document model-specific characteristics

---

## Error Handling Strategy

### Analysis Data Loading Failures
- Log error and skip analysis if data unavailable
- Document missing data in analysis results
- Continue with available analyses
- Provide clear error messages

### Visualization Failures
- Log matplotlib errors
- Fallback to text output if charts fail
- Continue with remaining visualization generation
- Document visualization failures

### Statistical Analysis Failures
- Use safe defaults for failed calculations
- Handle small sample sizes appropriately
- Document statistical assumptions violations
- Provide alternative non-parametric tests if needed

---

## Performance Considerations

### Memory Management
- Process analysis in batches if memory constrained
- Use efficient data structures for large datasets
- Clear intermediate data structures after use
- Monitor memory usage during analysis

### Computation Time
- Estimated analysis time: 10-15 minutes for all models
- Progress indicators for long-running operations
- Early stopping on critical failures
- Parallel processing where possible

### File I/O
- Batch file writes to reduce I/O overhead
- Compress analysis results if large
- Ensure atomic file writes where possible
- Organize results by analysis type

---

## Testing Strategy

### Unit Tests
- Test error classification logic
- Test bias metric calculations
- Test edge case identification
- Test visualization generation

### Integration Tests
- Test end-to-end analysis pipeline
- Test Day 5 Morning results integration
- Test analysis result storage
- Test visualization integration

### Validation Tests
- Validate analysis results against expectations
- Validate statistical test correctness
- Validate visualization quality
- Validate documentation completeness
