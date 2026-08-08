# Day 5 Morning: Full Model Evaluation - Research

**Feature ID:** 009-day5-evaluation  
**Date:** 2026-08-08  
**Status:** Draft

---

## Research Context

This document captures research findings, best practices, and technical decisions for implementing comprehensive model evaluation. The evaluation framework must leverage existing infrastructure while providing rigorous statistical analysis and visualization capabilities.

---

## Existing Infrastructure Analysis

### Current Evaluation Framework (metrics.py)

**Capabilities Identified:**
- Precision@K calculation: `metrics.precision_at_k(recommendations, ground_truth, k)`
- Recall@K calculation: `metrics.recall_at_k(recommendations, ground_truth, k)`
- NDCG@K calculation: `metrics.ndcg_at_k(recommendations, ground_truth, k)`
- Basic model comparison utilities
- Catalog coverage calculation

**Integration Strategy:**
- Use existing metric calculation functions as building blocks
- Extend framework if additional metrics needed (e.g., statistical analysis)
- Maintain consistency with existing evaluation methodology
- Leverage existing test data loading mechanisms

### ModelManager Integration

**Current Capabilities:**
- `model_manager.get_model(model_name)` returns (model, metadata)
- Model caching via `@st.cache_resource` decorator
- Support for 5 models: popularity, content, user_based_cf, item_based_cf, hybrid
- Model artifact persistence

**Evaluation Integration:**
- Load models via ModelManager (no direct loading)
- Handle model loading failures gracefully
- Use model metadata for evaluation documentation
- Ensure model availability before evaluation

---

## Evaluation Best Practices

### Statistical Significance Testing

**Best Practice:** Use paired t-tests for model comparison

**Implementation Approach:**
```python
from scipy import stats

def paired_t_test(model1_scores, model2_scores):
    """Perform paired t-test between two models."""
    t_stat, p_value = stats.ttest_rel(model1_scores, model2_scores)
    return {
        't_statistic': t_stat,
        'p_value': p_value,
        'significant': p_value < 0.05
    }
```

**Key Considerations:**
- Use paired tests (same users tested on both models)
- Set significance level at 0.05 (standard practice)
- Report both p-value and effect size
- Handle non-normal distributions with Wilcoxon signed-rank test if needed

### Catalog Coverage Calculation

**Best Practice:** Measure coverage across full catalog

**Implementation Approach:**
```python
def calculate_coverage(all_recommendations, catalog_size):
    """Calculate catalog coverage percentage."""
    unique_items = set()
    for recs in all_recommendations:
        unique_items.update(recs)
    return len(unique_items) / catalog_size
```

**Key Considerations:**
- Track unique items recommended across all users
- Compare against total catalog size
- Report as percentage (0-1)
- Consider coverage at different K values

### Popularity Bias Analysis

**Best Practice:** Measure popularity of recommended items

**Implementation Approach:**
```python
def calculate_popularity_bias(recommendations, item_popularity):
    """Calculate mean popularity decile of recommendations."""
    deciles = []
    for recs in recommendations:
        mean_pop = np.mean([item_popularity.get(item, 0) for item in recs])
        deciles.append(mean_pop)
    return np.mean(deciles)
```

**Key Considerations:**
- Use popularity scores from dataset
- Calculate mean popularity across recommendations
- Compare across models to identify bias
- Higher mean popularity indicates more bias

---

## Segmentation Analysis

### Cold-Start User Segmentation

**Definition:** Users with ≤ 5 ratings in training data

**Implementation:**
```python
def segment_cold_start_users(ratings_df):
    """Identify cold-start users."""
    user_counts = ratings_df.groupby('userId').size()
    cold_start_users = user_counts[user_counts <= 5].index
    return cold_start_users
```

**Rationale:** Cold-start users benefit from content-based recommendations, so analyzing their performance separately is important.

### Active User Segmentation

**Definition:** Users with > 20 ratings in training data

**Implementation:**
```python
def segment_active_users(ratings_df):
    """Identify active users."""
    user_counts = ratings_df.groupby('userId').size()
    active_users = user_counts[user_counts > 20].index
    return active_users
```

**Rationale:** Active users benefit from collaborative filtering, so analyzing their performance separately is important.

### New-Item Segmentation

**Definition:** Items with few ratings (≤ 10) in training data

**Implementation:**
```python
def segment_new_items(ratings_df):
    """Identify new items."""
    item_counts = ratings_df.groupby('movieId').size()
    new_items = item_counts[item_counts <= 10].index
    return new_items
```

**Rationale:** New items lack collaborative signals, so content-based performance is critical.

---

## Visualization Best Practices

### Model Comparison Charts

**Best Practice:** Use grouped bar charts for comparison

**Implementation:**
```python
import matplotlib.pyplot as plt

def create_comparison_chart(model_results, metric='precision_at_10'):
    """Create model comparison bar chart."""
    models = list(model_results.keys())
    values = [model_results[m][metric] for m in models]
    
    plt.figure(figsize=(10, 6))
    plt.bar(models, values, color=['red', 'blue', 'green', 'orange', 'purple'])
    plt.title(f'Model Comparison: {metric}')
    plt.ylabel(metric)
    plt.xlabel('Model')
    plt.ylim(0, 1.0)
    plt.xticks(rotation=45)
    plt.tight_layout()
```

**Key Considerations:**
- Use distinct colors for each model
- Include error bars if statistical variability available
- Label axes clearly
- Rotate x-axis labels if needed
- Use high DPI for publication quality

### Metric Trends Visualization

**Best Practice:** Use line charts for K-value trends

**Implementation:**
```python
def create_metric_trends(model_results):
    """Create metric trends across K values."""
    k_values = [5, 10, 20]
    for model_name, results in model_results.items():
        precisions = [results[f'precision_at_{k}'] for k in k_values]
        plt.plot(k_values, precisions, marker='o', label=model_name)
    
    plt.xlabel('K')
    plt.ylabel('Precision')
    plt.title('Precision@K Trends')
    plt.legend()
    plt.grid(True)
```

**Key Considerations:**
- Show trends across K values (5, 10, 20)
- Use different line styles/markers for each model
- Include legend for model identification
- Add grid for readability

---

## Error Handling Strategies

### Model Loading Failures

**Strategy:** Graceful degradation with error logging

**Implementation:**
```python
def safe_load_model(model_manager, model_name):
    """Safely load model with error handling."""
    try:
        model, metadata = model_manager.get_model(model_name)
        return model, metadata
    except Exception as e:
        print(f"Warning: Failed to load {model_name}: {e}")
        return None, None
```

**Rationale:** Continue evaluation with available models rather than failing completely.

### Data Validation Failures

**Strategy:** Pre-evaluation validation with early failure

**Implementation:**
```python
def validate_test_data(test_data):
    """Validate test data structure."""
    required_columns = ['userId', 'movieId', 'rating']
    if not all(col in test_data.columns for col in required_columns):
        raise ValueError(f"Test data missing required columns: {required_columns}")
    if len(test_data) == 0:
        raise ValueError("Test data is empty")
    return True
```

**Rationale:** Fail fast on data issues rather than proceeding with invalid data.

---

## Performance Optimization

### Memory-Efficient Evaluation

**Strategy:** Process users in batches

**Implementation:**
```python
def evaluate_in_batches(model, test_data, batch_size=100):
    """Evaluate users in batches to manage memory."""
    users = test_data['userId'].unique()
    results = {}
    
    for i in range(0, len(users), batch_size):
        batch_users = users[i:i+batch_size]
        batch_data = test_data[test_data['userId'].isin(batch_users)]
        batch_results = evaluate_batch(model, batch_data)
        results.update(batch_results)
    
    return results
```

**Rationale:** Reduce memory usage for large test sets.

### Progressive Result Storage

**Strategy:** Store results as they're generated

**Implementation:**
```python
def store_results_incrementally(results, output_path):
    """Store results incrementally to avoid memory overflow."""
    with open(output_path, 'a') as f:
        for user_id, user_results in results.items():
            f.write(json.dumps({user_id: user_results}) + '\n')
```

**Rationale:** Avoid losing all results if evaluation fails partway through.

---

## Reproducibility Considerations

### Random Seed Control

**Strategy:** Fixed random seed for reproducibility

**Implementation:**
```python
import random
import numpy as np

def set_random_seed(seed=42):
    """Set random seed for reproducibility."""
    random.seed(seed)
    np.random.seed(seed)
```

**Rationale:** Ensure consistent results across evaluation runs.

### Metadata Documentation

**Strategy:** Include evaluation metadata in results

**Implementation:**
```python
def create_evaluation_metadata():
    """Create evaluation metadata."""
    return {
        'timestamp': datetime.now().isoformat(),
        'random_seed': 42,
        'k_values': [5, 10, 20],
        'test_dataset_size': len(test_data),
        'python_version': sys.version,
        'library_versions': {
            'pandas': pd.__version__,
            'numpy': np.__version__,
            'scipy': scipy.__version__
        }
    }
```

**Rationale:** Enable reproduction of evaluation conditions.

---

## Technology Stack Research

### Required Libraries

**Core Libraries:**
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `scipy` - Statistical analysis and testing
- `matplotlib` - Chart generation
- `seaborn` - Enhanced visualizations (optional)

**Model Integration:**
- Existing `ModelManager` - Model loading
- Existing `metrics.py` - Metric calculation
- Existing `DataProvider` - Data loading

**File I/O:**
- `json` - Result storage
- `os` - File system operations
- `pathlib` - Path handling

### Optional Libraries

**Enhanced Visualizations:**
- `seaborn` - Statistical visualizations
- `plotly` - Interactive charts (optional)

**Advanced Analysis:**
- `scikit-learn` - Additional statistical tests (optional)

---

## Key Decisions Documented

### Decision 1: Script-Based Evaluation

**Decision:** Run evaluation as separate Python scripts, not within Streamlit app

**Rationale:**
- Avoid memory conflicts with Streamlit
- Enable offline evaluation without UI
- Ensure evaluation performance doesn't impact UI
- Easier to automate and schedule

### Decision 2: Structured Result Storage

**Decision:** Store results in JSON format with standardized schema

**Rationale:**
- Human-readable and machine-parseable
- Supports version control and comparison
- Easy to import into analysis tools
- Standard format across all evaluation runs

### Decision 3: Segmented Analysis

**Decision:** Perform segmented evaluation by user activity and item characteristics

**Rationale:**
- Reveals model strengths/weaknesses for different user types
- Important for cold-start performance analysis
- Provides insights for model selection strategies
- Required for comprehensive evaluation

### Decision 4: Statistical Significance Testing

**Decision:** Include statistical significance tests between models

**Rationale:**
- Provides rigorous comparison beyond raw metrics
- Identifies statistically significant performance differences
- Enables confident model selection decisions
- Standard practice in research and industry

---

## Open Questions & Risks

### Question 1: Model Availability
**Risk:** Some models may not be available or may fail to load
**Mitigation:** Implement graceful degradation and continue with available models

### Question 2: Test Data Size
**Risk:** Test set may be too large for efficient evaluation
**Mitigation:** Implement batch processing and memory optimization

### Question 3: Statistical Assumptions
**Risk:** Data may not meet statistical test assumptions (normality)
**Mitigation:** Use non-parametric tests as fallback (Wilcoxon signed-rank)

### Question 4: Visualization Complexity
**Risk:** Complex visualizations may be difficult to generate
**Mitigation:** Start with simple charts, add complexity incrementally
