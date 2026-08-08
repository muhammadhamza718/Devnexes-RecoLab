# Day 5 Afternoon: Advanced Analysis - Research

**Feature ID:** 009-day5-evaluation-afternoon  
**Date:** 2026-08-08  
**Status:** Draft

---

## Research Context

This document captures research findings, best practices, and technical decisions for implementing advanced analysis of model performance, error patterns, bias quantification, and limitations documentation. The analysis framework leverages Day 5 Morning evaluation results to provide deep insights into model behavior.

---

## Existing Infrastructure Analysis

### Day 5 Morning Evaluation Results

**Available Data:**
- Model evaluation results (per-model metrics)
- Segmented evaluation results (cold-start, active users, etc.)
- Statistical significance test results
- Performance comparison data
- Per-user metrics for statistical analysis

**Integration Strategy:**
- Load results via EvaluationResultLoader
- Use per-user metrics for error analysis
- Use segmented results for edge case analysis
- Use coverage and popularity metrics for bias analysis
- Maintain read-only access to Day 5 Morning results

### Test Data Integration

**Available Data:**
- Test dataset (test.csv) from data/split_datasets/
- User-item ratings with timestamps
- Movie metadata for genre analysis
- User activity data for segmentation

**Integration Strategy:**
- Load test data for additional analysis
- Calculate additional metrics if needed
- Perform genre-specific analysis
- Analyze temporal patterns if timestamps available
- Maintain data consistency with Day 5 Morning

---

## Error Analysis Best Practices

### Error Classification

**Best Practice:** Classify errors based on prediction quality

**Implementation Approach:**
```python
def classify_error(predicted_rating, actual_rating, threshold=3.0):
    """Classify prediction as error if rating below threshold."""
    if actual_rating < threshold:
        return "low_rating_ground_truth"
    if predicted_rating < threshold:
        return "poor_prediction"
    if abs(predicted_rating - actual_rating) > 2.0:
        return "large_prediction_error"
    return "no_error"
```

**Key Considerations:**
- Use threshold-based classification (default: rating < 3.0)
- Consider absolute error magnitude
- Distinguish between poor predictions and ground truth issues
- Track error types for pattern analysis

### User Error Pattern Analysis

**Best Practice:** Analyze error patterns by user characteristics

**Implementation Approach:**
```python
def analyze_user_error_patterns(user_errors, user_activity):
    """Analyze error patterns by user activity level."""
    patterns = {}
    
    for user_id, errors in user_errors.items():
        activity = user_activity.get(user_id, 0)
        error_rate = errors['error_count'] / errors['total_predictions']
        
        if activity <= 5:
            pattern_type = "cold_start_error"
        elif activity > 20:
            pattern_type = "active_user_error"
        else:
            pattern_type = "moderate_user_error"
        
        patterns[user_id] = {
            'error_rate': error_rate,
            'pattern_type': pattern_type,
            'activity_level': activity
        }
    
    return patterns
```

**Key Considerations:**
- Segment users by activity level
- Calculate error rates per segment
- Identify systematic patterns
- Compare to overall error rate

### Systematic Bias Detection

**Best Practice:** Detect systematic bias in error patterns

**Implementation Approach:**
```python
def detect_systematic_bias(error_patterns):
    """Detect systematic bias in error patterns."""
    # Check for popularity bias
    popularity_errors = [e for e in error_patterns if e['item_popularity'] > 8]
    if len(popularity_errors) / len(error_patterns) > 0.7:
        return {
            'has_bias': True,
            'bias_type': 'popularity_bias',
            'bias_direction': 'high_popularity_items',
            'confidence': 0.85
        }
    
    # Check for cold-start bias
    cold_start_errors = [e for e in error_patterns if e['user_activity'] <= 5]
    if len(cold_start_errors) / len(error_patterns) > 0.6:
        return {
            'has_bias': True,
            'bias_type': 'cold_start_bias',
            'bias_direction': 'cold_start_users',
            'confidence': 0.90
        }
    
    return {'has_bias': False}
```

**Key Considerations:**
- Check for popularity bias (errors on popular items)
- Check for cold-start bias (errors for new users)
- Check for genre bias (errors in specific genres)
- Use statistical significance for confidence

---

## Edge Case Analysis Best Practices

### Sparse User Analysis

**Definition:** Users with ≤ 3 ratings in training data

**Implementation:**
```python
def analyze_sparse_users(evaluation_results, user_counts):
    """Analyze performance for sparse users."""
    sparse_users = user_counts[user_counts <= 3].index
    
    sparse_metrics = {
        'user_count': len(sparse_users),
        'avg_precision': calculate_avg_precision(evaluation_results, sparse_users),
        'avg_recall': calculate_avg_recall(evaluation_results, sparse_users),
        'error_rate': calculate_error_rate(evaluation_results, sparse_users)
    }
    
    # Compare to overall performance
    overall_precision = calculate_overall_precision(evaluation_results)
    sparse_metrics['comparison_to_overall'] = {
        'precision_diff': sparse_metrics['avg_precision'] - overall_precision,
        'relative_diff': (sparse_metrics['avg_precision'] / overall_precision) - 1
    }
    
    return sparse_metrics
```

**Rationale:** Sparse users are challenging for collaborative filtering, so analyzing their performance separately is important.

### Power User Analysis

**Definition:** Users with > 50 ratings in training data

**Implementation:**
```python
def analyze_power_users(evaluation_results, user_counts):
    """Analyze performance for power users."""
    power_users = user_counts[user_counts > 50].index
    
    power_metrics = {
        'user_count': len(power_users),
        'avg_precision': calculate_avg_precision(evaluation_results, power_users),
        'avg_recall': calculate_avg_recall(evaluation_results, power_users),
        'diversity': calculate_diversity(evaluation_results, power_users)
    }
    
    return power_metrics
```

**Rationale:** Power users provide strong collaborative signals, so their performance indicates model effectiveness for active users.

### New Item Analysis

**Definition:** Items with ≤ 5 ratings in training data

**Implementation:**
```python
def analyze_new_items(evaluation_results, item_counts):
    """Analyze performance for new items."""
    new_items = item_counts[item_counts <= 5].index
    
    new_item_metrics = {
        'item_count': len(new_items),
        'recommendation_rate': calculate_recommendation_rate(evaluation_results, new_items),
        'avg_rating': calculate_avg_rating(evaluation_results, new_items),
        'precision': calculate_precision_for_items(evaluation_results, new_items)
    }
    
    return new_item_metrics
```

**Rationale:** New items lack collaborative signals, so content-based performance is critical.

---

## Bias Analysis Best Practices

### Popularity Bias Quantification

**Best Practice:** Measure popularity of recommended items

**Implementation Approach:**
```python
def calculate_popularity_bias(recommendations, item_popularity):
    """Calculate popularity bias metrics."""
    popularity_scores = []
    
    for recs in recommendations:
        item_pops = [item_popularity.get(item, 0) for item in recs]
        popularity_scores.extend(item_pops)
    
    mean_popularity = np.mean(popularity_scores)
    popularity_decile = np.percentile(popularity_scores, 80)
    
    # Classify bias level
    if popularity_decile >= 8:
        bias_level = "high"
    elif popularity_decile >= 5:
        bias_level = "medium"
    else:
        bias_level = "low"
    
    return {
        'mean_popularity_decile': mean_popularity,
        'high_popularity_percentage': np.mean([p >= 8 for p in popularity_scores]),
        'bias_level': bias_level
    }
```

**Key Considerations:**
- Use popularity deciles for measurement
- Compare against random baseline
- Classify bias level for interpretability
- Track distribution across deciles

### Catalog Coverage Calculation

**Best Practice:** Measure percentage of catalog recommended

**Implementation Approach:**
```python
def calculate_catalog_coverage(all_recommendations, catalog_size):
    """Calculate catalog coverage percentage."""
    unique_items = set()
    for recs in all_recommendations:
        unique_items.update(recs)
    
    coverage = len(unique_items) / catalog_size
    
    return {
        'overall_coverage': coverage,
        'unique_items': len(unique_items),
        'total_catalog': catalog_size,
        'coverage_percentage': coverage * 100
    }
```

**Key Considerations:**
- Track unique items across all recommendations
- Compare against total catalog size
- Report as percentage
- Consider coverage at different K values

### Diversity Metrics

**Best Practice:** Calculate intra-list and inter-list diversity

**Implementation Approach:**
```python
def calculate_diversity_metrics(recommendations, item_similarity_matrix):
    """Calculate diversity metrics."""
    intra_list_diversities = []
    
    for recs in recommendations:
        # Calculate average pairwise dissimilarity within list
        diversity = 0
        count = 0
        for i in range(len(recs)):
            for j in range(i+1, len(recs)):
                sim = item_similarity_matrix[recs[i]][recs[j]]
                diversity += (1 - sim)
                count += 1
        
        if count > 0:
            intra_list_diversities.append(diversity / count)
    
    avg_intra_list_diversity = np.mean(intra_list_diversities)
    
    # Calculate inter-list diversity (average Jaccard similarity between users)
    inter_list_diversity = calculate_inter_list_diversity(recommendations)
    
    return {
        'intra_list_diversity': avg_intra_list_diversity,
        'inter_list_diversity': inter_list_diversity,
        'overall_diversity_score': (avg_intra_list_diversity + inter_list_diversity) / 2
    }
```

**Key Considerations:**
- Intra-list diversity: diversity within a single user's recommendations
- Inter-list diversity: diversity across different users' recommendations
- Use item similarity matrix for calculation
- Combine metrics for overall diversity score

---

## Limitations Documentation Best Practices

### Model-Specific Limitations

**Best Practice:** Document limitations per model with impact assessment

**Implementation Approach:**
```python
def analyze_model_limitations(model_name, evaluation_results, error_analysis):
    """Analyze model-specific limitations."""
    limitations = {}
    
    # Cold-start performance
    cold_start_performance = error_analysis['activity_level_errors']['sparse_users']['error_rate']
    if cold_start_performance > 0.4:
        limitations['cold_start_performance'] = "poor"
        limitations['cold_start_impact'] = "high"
    elif cold_start_performance > 0.2:
        limitations['cold_start_performance'] = "moderate"
        limitations['cold_start_impact'] = "medium"
    else:
        limitations['cold_start_performance'] = "good"
        limitations['cold_start_impact'] = "low"
    
    # Scalability assessment
    avg_latency = evaluation_results.get('evaluation_time_seconds', 0) / len(evaluation_results['per_user_metrics'])
    if avg_latency > 1.0:
        limitations['scalability'] = "poor"
    elif avg_latency > 0.5:
        limitations['scalability'] = "moderate"
    else:
        limitations['scalability'] = "good"
    
    return limitations
```

**Key Considerations:**
- Use quantitative metrics for assessment
- Classify limitations (poor/moderate/good)
- Assess impact level (high/medium/low)
- Provide actionable mitigation strategies

### Data Limitations

**Best Practice:** Document dataset-related limitations

**Implementation Approach:**
```python
def analyze_data_limitations(test_data, movies_data):
    """Analyze data-related limitations."""
    limitations = {}
    
    # Dataset size
    limitations['dataset_size'] = len(test_data)
    
    # Sparsity
    total_possible = len(test_data['userId'].unique()) * len(test_data['movieId'].unique())
    sparsity = 1 - (len(test_data) / total_possible)
    limitations['sparsity'] = sparsity
    
    # Temporal coverage
    if 'timestamp' in test_data.columns:
        time_span = test_data['timestamp'].max() - test_data['timestamp'].min()
        limitations['temporal_coverage'] = f"{time_span.days} days"
    else:
        limitations['temporal_coverage'] = "unknown"
    
    # Genre balance
    genre_counts = movies_data['genres'].str.split('|', expand=True).stack().value_counts()
    genre_balance = genre_counts.std() / genre_counts.mean()
    limitations['genre_balance'] = "balanced" if genre_balance < 0.5 else "imbalanced"
    
    return limitations
```

**Key Considerations:**
- Quantify dataset characteristics
- Assess sparsity and coverage
- Evaluate genre balance
- Document missing data

---

## Visualization Best Practices

### Error Distribution Heatmap

**Best Practice:** Use heatmap for error pattern visualization

**Implementation:**
```python
import seaborn as sns

def create_error_heatmap(error_patterns):
    """Create error distribution heatmap."""
    # Aggregate errors by user activity and item popularity
    heatmap_data = aggregate_errors(error_patterns)
    
    plt.figure(figsize=(12, 8))
    sns.heatmap(heatmap_data, annot=True, fmt='.2f', cmap='YlOrRd')
    plt.title('Error Distribution by User Activity and Item Popularity')
    plt.xlabel('Item Popularity Decile')
    plt.ylabel('User Activity Level')
    plt.tight_layout()
```

**Key Considerations:**
- Use color scale to indicate error rate
- Annotate with actual values
- Label axes clearly
- Use colorblind-friendly colormap

### User Activity vs. Performance Scatter Plot

**Best Practice:** Use scatter plot for activity-performance relationship

**Implementation:**
```python
def create_activity_scatter(user_activity, user_performance):
    """Create user activity vs. performance scatter plot."""
    plt.figure(figsize=(10, 6))
    plt.scatter(user_activity, user_performance, alpha=0.5)
    plt.xlabel('User Activity (Number of Ratings)')
    plt.ylabel('Performance (Precision@10)')
    plt.title('User Activity vs. Performance')
    plt.grid(True, alpha=0.3)
    
    # Add trend line
    z = np.polyfit(user_activity, user_performance, 1)
    p = np.poly1d(z)
    plt.plot(user_activity, p(user_activity), "r--", alpha=0.8)
```

**Key Considerations:**
- Show individual users as points
- Add trend line for pattern
- Use transparency for overlapping points
- Include grid for readability

### Genre-Specific Radar Chart

**Best Practice:** Use radar chart for multi-dimensional genre comparison

**Implementation:**
```python
def create_genre_radar(genre_performance):
    """Create genre-specific performance radar chart."""
    genres = list(genre_performance.keys())
    metrics = list(genre_performance.values())
    
    # Close the radar chart
    metrics += metrics[:1]
    angles = [n / len(genres) * 2 * np.pi for n in range(len(genres) + 1)]
    
    plt.figure(figsize=(8, 8))
    ax = plt.subplot(111, polar=True)
    ax.plot(angles, metrics, 'o-', linewidth=2)
    ax.fill(angles, metrics, alpha=0.25)
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(genres)
    ax.set_ylim(0, 1)
    plt.title('Genre-Specific Performance')
```

**Key Considerations:**
- Use polar coordinates for radar chart
- Fill area for visual impact
- Label each genre clearly
- Set appropriate axis limits

---

## Statistical Analysis Considerations

### Non-Parametric Tests

**Best Practice:** Use non-parametric tests when assumptions violated

**Implementation:**
```python
from scipy.stats import wilcoxon, mannwhitneyu

def non_parametric_comparison(group1, group2):
    """Perform non-parametric comparison."""
    # Wilcoxon signed-rank test for paired data
    stat, p_value = wilcoxon(group1, group2)
    
    return {
        'test_type': 'wilcoxon_signed_rank',
        'statistic': stat,
        'p_value': p_value,
        'significant': p_value < 0.05
    }
```

**Key Considerations:**
- Use when data not normally distributed
- More robust to outliers
- Less powerful than parametric tests
- Appropriate for ordinal data

### Effect Size Calculation

**Best Practice:** Calculate effect size for practical significance

**Implementation:**
```python
def calculate_effect_size(group1, group2):
    """Calculate Cohen's d effect size."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    cohens_d = (np.mean(group1) - np.mean(group2)) / pooled_std
    
    # Interpret effect size
    if abs(cohens_d) < 0.2:
        interpretation = "small"
    elif abs(cohens_d) < 0.5:
        interpretation = "medium"
    else:
        interpretation = "large"
    
    return {
        'cohens_d': cohens_d,
        'interpretation': interpretation
    }
```

**Key Considerations:**
- Provides practical significance
- Complements statistical significance
- Small (<0.2), medium (0.2-0.5), large (>0.5)
- Important for real-world impact

---

## Key Decisions Documented

### Decision 1: Analysis-Based on Day 5 Morning Results

**Decision:** Use Day 5 Morning evaluation results as input for advanced analysis

**Rationale:**
- Avoids re-running time-consuming evaluation
- Ensures consistency between evaluation and analysis
- Leverages already-computed metrics
- Reduces computational overhead

### Decision 2: Quantified Bias Metrics

**Decision:** Use quantified metrics for bias analysis (not qualitative)

**Rationale:**
- Provides objective bias measurement
- Enables comparison across models
- Supports statistical testing
- Required for rigorous analysis

### Decision 3: Comprehensive Limitations Documentation

**Decision:** Document limitations across models, data, evaluation, and deployment

**Rationale:**
- Provides complete picture of system constraints
- Enables informed decision-making
- Required for comprehensive documentation
- Identifies areas for future improvement

### Decision 4: Actionable Insights Requirement

**Decision:** Provide actionable insights from analysis (not just observations)

**Rationale:**
- Analysis should drive improvement
- Provides concrete recommendations
- Enables prioritization of fixes
- Required for practical value

---

## Open Questions & Risks

### Question 1: Analysis Depth
**Risk:** Analysis may be too shallow to provide meaningful insights
**Mitigation:** Define minimum analysis depth requirements and validate against known patterns

### Question 2: Statistical Power
**Risk:** Sample sizes may be insufficient for statistical significance
**Mitigation:** Use appropriate statistical tests and report confidence intervals

### Question 3: Bias Metric Selection
**Risk:** Selected bias metrics may not capture all relevant biases
**Mitigation:** Use multiple bias metrics and validate against domain knowledge

### Question 4: Visualization Complexity
**Risk:** Complex visualizations may be difficult to interpret
**Mitigation:** Start with simple visualizations, add complexity incrementally with clear legends
