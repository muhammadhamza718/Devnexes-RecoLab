# Technology Research: Cold-Start Optimization & Parameter Tuning

**Feature**: 004-cold-start-optimization  
**Date**: 2026-07-30  
**Purpose**: Technology decisions and implementation patterns for enhanced cold-start handling and parameter optimization

---

## Decision 1: Genre Weight Calculation Method

### Options Considered

1. **Simple Genre Count**: Count genre occurrences in liked movies
2. **TF-IDF Weighting**: Apply TF-IDF to genre preferences
3. **Explicit + Implicit Weighting**: Combine explicit genre selection with implicit liked movie patterns
4. **Bayesian Genre Priors**: Use Bayesian priors for genre preferences

### Decision: Explicit + Implicit Weighting

**Rationale**:
- Captures both stated preferences (genre selection) and behavior (liked movies)
- More comprehensive than simple counting but less complex than Bayesian approaches
- Compatible with existing ContentModel TF-IDF infrastructure
- Allows user feedback incorporation through weight updates

**Implementation**:
```python
def calculate_genre_weights(genres: List[str], liked_movie_ids: List[int]) -> Dict[str, float]:
    # Explicit weights from genre selection (base weight 0.7)
    explicit_weights = {genre: 0.7 for genre in genres}
    
    # Implicit weights from liked movie genres (boost 0.3)
    implicit_weights = extract_genre_weights_from_movies(liked_movie_ids)
    
    # Combine weights with normalization
    combined = {genre: explicit_weights.get(genre, 0) + implicit_weights.get(genre, 0) 
                for genre in set(explicit_weights) | set(implicit_weights)}
    
    return normalize_weights(combined)
```

**Alternatives Rejected**:
- Simple Genre Count: Too basic, doesn't capture preference strength
- TF-IDF Weighting: Overkill for onboarding, computational overhead
- Bayesian Priors: Too complex for 4-hour afternoon session

---

## Decision 2: New-Item Detection Threshold

### Options Considered

1. **Absolute Threshold**: Fixed rating count (e.g., ≤5 ratings)
2. **Percentile Threshold**: Items in bottom 10% of rating count
3. **Time-Based Threshold**: Items added within last 7 days
4. **Adaptive Threshold**: Dynamic threshold based on dataset characteristics

### Decision: Absolute Threshold with Time-Based Enhancement

**Rationale**:
- Simple and interpretable for debugging
- Consistent with cold-start user threshold (≤5 ratings)
- Time-based enhancement handles catalog updates
- Easy to tune and monitor

**Implementation**:
```python
def detect_new_item(movie_id: int, rating_count: int, days_since_added: int) -> bool:
    # Rating count threshold (primary)
    if rating_count <= 5:
        return True
    
    # Time-based enhancement (secondary)
    if days_since_added <= 7:
        return True
    
    return False
```

**Alternatives Rejected**:
- Percentile Threshold: Requires full dataset scan, computationally expensive
- Time-Based Only: May miss older items with few ratings
- Adaptive Threshold: Too complex for afternoon session

---

## Decision 3: Grid Search Parameter Space

### Options Considered

1. **Full Grid Search**: All combinations of α ∈ [0.0, 0.1, ..., 1.0], thresholds ∈ [1, 2, ..., 30]
2. **Coarse Grid Search**: Limited parameter space α ∈ [0.2, 0.5, 0.8], thresholds ∈ [3, 5, 10, 20]
3. **Random Search**: Random parameter sampling
4. **Bayesian Optimization**: Sequential model-based optimization

### Decision: Coarse Grid Search with Early Stopping

**Rationale**:
- Fits within 4-hour afternoon session
- Focuses on most impactful parameter ranges
- Early stopping prevents unnecessary computation
- Provides interpretable results

**Implementation**:
```python
def grid_search_alpha(hybrid_recommender, validation_data, alpha_values=[0.2, 0.5, 0.8]):
    best_alpha = 0.5
    best_score = 0.0
    
    for alpha in alpha_values:
        hybrid_recommender.alpha = alpha
        score = evaluate_ndcg_at_k(hybrid_recommender, validation_data)
        
        if score > best_score:
            best_score = score
            best_alpha = alpha
        
        # Early stopping if improvement < 1%
        if score - best_score < 0.01:
            break
    
    return best_alpha
```

**Alternatives Rejected**:
- Full Grid Search: Too computationally expensive for 4-hour session
- Random Search: Less interpretable, may miss optimal regions
- Bayesian Optimization: Too complex for afternoon session

---

## Decision 4: Fallback Trigger Conditions

### Options Considered

1. **Error-Based Triggers**: Fallback only on exception
2. **Performance-Based Triggers**: Fallback on timeout or slow response
3. **Quality-Based Triggers**: Fallback on insufficient candidates
4. **Composite Triggers**: Combination of error, performance, and quality conditions

### Decision: Composite Triggers with Priority

**Rationale**:
- Comprehensive fallback coverage for different failure modes
- Priority-based approach ensures appropriate fallback level
- Performance monitoring enables system health insights
- Graceful degradation rather than complete failure

**Implementation**:
```python
def should_trigger_fallback(result, timeout_ms: int = 100) -> bool:
    # Error trigger (highest priority)
    if result.exception is not None:
        return True, "error"
    
    # Performance trigger
    if result.latency_ms > timeout_ms:
        return True, "timeout"
    
    # Quality trigger
    if len(result.recommendations) < 5:
        return True, "insufficient_candidates"
    
    return False, "ok"
```

**Alternatives Rejected**:
- Error-Based Only: Too narrow, misses performance and quality issues
- Performance-Based Only: May trigger unnecessarily on edge cases
- Quality-Based Only: Doesn't handle catastrophic failures

---

## Decision 5: Cold-Start Metrics

### Options Considered

1. **Standard Ranking Metrics**: P@K, R@K, NDCG@K
2. **Cold-Start Specific Metrics**: Coverage, diversity, novelty
3. **User Satisfaction Metrics**: Click-through rate, dwell time
4. **Hybrid Metrics**: Combination of ranking and cold-start specific

### Decision: Basic Cold-Start Specific Metrics

**Rationale**:
- Cold-start specific metrics better evaluate cold-start performance
- Coverage ensures new users receive recommendations
- Diversity prevents repetitive recommendations
- Basic implementation fits afternoon scope

**Implementation**:
```python
def calculate_cold_start_metrics(recommendations, user_profile, catalog):
    # Coverage: % of users who received recommendations
    coverage = len(recommendations) / len(user_profile)
    
    # Diversity: Average pairwise genre distance
    diversity = calculate_genre_diversity(recommendations)
    
    # Relevance: % of recommendations matching user genres
    relevance = calculate_genre_relevance(recommendations, user_profile)
    
    return {
        "coverage": coverage,
        "diversity": diversity,
        "relevance": relevance
    }
```

**Alternatives Rejected**:
- Standard Ranking Metrics: Don't capture cold-start specific challenges
- User Satisfaction Metrics: Require user interaction data (not available)
- Hybrid Metrics: Too complex for afternoon session

---

## Decision 6: Popularity Boost Mechanism

### Options Considered

1. **Fixed Boost**: Add constant to new item scores
2. **Percentage Boost**: Multiply new item scores by factor >1
3. **Time-Decaying Boost**: Boost decreases over time
4. **Adaptive Boost**: Boost based on category popularity

### Decision: Percentage Boost with Time Decay

**Rationale**:
- Percentage boost maintains relative score ordering
- Time decay ensures new items don't dominate indefinitely
- Simple implementation with tunable parameters
- Balances discovery with relevance

**Implementation**:
```python
def apply_popularity_boost(score: float, is_new: bool, days_since_added: int) -> float:
    if not is_new:
        return score
    
    # Base boost (30% increase)
    boost_factor = 1.3
    
    # Time decay (linear over 30 days)
    decay_factor = max(0.0, 1.0 - (days_since_added / 30.0))
    
    # Apply boost with decay
    boosted_score = score * (1.0 + (boost_factor - 1.0) * decay_factor)
    
    return min(boosted_score, 1.0)  # Cap at 1.0
```

**Alternatives Rejected**:
- Fixed Boost: Doesn't account for time decay
- Percentage Boost Only: No time decay, new items may dominate
- Adaptive Boost: Too complex for afternoon session

---

## Risk Assessment

### Technology Risks

1. **Profile Building Complexity**: Genre weight calculation may be too complex for 4-hour session
   - **Mitigation**: Start with simple weighted average, iterate if time allows
   - **Fallback**: Use existing ContentModel genre matching

2. **Parameter Optimization Time**: Grid search may exceed time budget
   - **Mitigation**: Limited parameter space, early stopping
   - **Fallback**: Use default parameters from morning

3. **Fallback Trigger Sensitivity**: Triggers may be too sensitive or too lax
   - **Mitigation**: Empirical tuning on validation set
   - **Fallback**: Revert to basic error-based triggers

### Integration Risks

1. **Morning Hybrid Compatibility**: Enhancements may break morning functionality
   - **Mitigation**: Maintain API contracts, extensive integration testing
   - **Fallback**: Rollback to morning implementation

2. **Performance Degradation**: Enhanced features may exceed 100ms latency target
   - **Mitigation**: Profile critical paths, optimize hotspots
   - **Fallback**: Disable non-critical features

---

## Performance Considerations

### Cold-Start Optimization

- **Profile Building**: <10ms target (cache profiles where possible)
- **Genre Weight Calculation**: <5ms target (use efficient data structures)
- **New-Item Detection**: <2ms target (maintain rating count cache)
- **Recommendation Generation**: <100ms total target (including profile building)

### Parameter Optimization

- **Grid Search**: <5 minutes total target (limited parameter space)
- **Evaluation per Configuration**: <10ms target (efficient metric calculation)
- **Result Storage**: <1ms target (simple dictionary/array)

### Fallback Monitoring

- **Trigger Evaluation**: <1ms target (simple condition checks)
- **Performance Logging**: <2ms target (minimal overhead)
- **Fallback Execution**: <50ms target (per fallback level)

---

## Success Criteria Validation

### Cold-Start Enhancement Validation

- **Coverage**: ≥95% of cold-start users receive recommendations
- **Diversity**: Average genre diversity ≥0.6 (on 0-1 scale)
- **Relevance**: ≥70% of recommendations match user genres
- **Latency**: <100ms for cold-start recommendations

### Parameter Optimization Validation

- **Improvement**: ≥5% NDCG@10 improvement over default parameters
- **Time**: <5 minutes for complete grid search
- **Reproducibility**: Same results with fixed seed
- **Stability**: Consistent results across multiple runs

### Fallback Enhancement Validation

- **Availability**: 100% recommendation availability with enhanced fallback
- **Monitoring**: Fallback frequency and patterns tracked accurately
- **Latency**: <50ms for fallback chain execution
- **Recovery**: System recovers from failures automatically

---

## Technology Dependencies

### Existing Dependencies

- **HybridRecommender**: From Day 2 morning (weighted scoring, adaptive selection)
- **ContentModel**: From Week 2 (genre similarity, TF-IDF)
- **Persistence Module**: From Day 1 IVP fixes (to_bundle/from_bundle)
- **Testing Framework**: pytest, pytest-cov (≥70% coverage requirement)

### New Dependencies

- **No new external dependencies** required
- **Optional**: scikit-learn for advanced metrics (if time allows)
- **Optional**: matplotlib for parameter optimization visualization (if time allows)

---

## Implementation Patterns

### Profile Building Pattern

```python
class UserProfile:
    def __init__(self, user_id: Optional[int], genres: List[str], liked_movies: List[int]):
        self.user_id = user_id
        self.genre_weights = self._calculate_initial_weights(genres, liked_movies)
        self.liked_movie_ids = liked_movies
        self.created_at = datetime.now()
    
    def _calculate_initial_weights(self, genres: List[str], liked_movies: List[int]) -> Dict[str, float]:
        # Combine explicit and implicit preferences
        explicit = {genre: 0.7 for genre in genres}
        implicit = self._extract_genre_weights(liked_movies)
        combined = {k: explicit.get(k, 0) + implicit.get(k, 0) 
                   for k in set(explicit) | set(implicit)}
        return self._normalize_weights(combined)
```

### Parameter Optimization Pattern

```python
class ParameterOptimizer:
    def __init__(self, hybrid: HybridRecommender, validation_data: pd.DataFrame):
        self.hybrid = hybrid
        self.validation_data = validation_data
        self.best_params = {}
    
    def optimize(self, param_space: Dict[str, List[Any]]) -> Dict[str, Any]:
        best_score = 0.0
        best_config = {}
        
        for config in self._generate_configs(param_space):
            self.hybrid.update_params(config)
            score = self._evaluate_config()
            
            if score > best_score:
                best_score = score
                best_config = config.copy()
        
        return best_config
```

### Fallback Monitoring Pattern

```python
class FallbackManager:
    def __init__(self, hybrid: HybridRecommender):
        self.hybrid = hybrid
        self.fallback_log = []
        self.performance_metrics = {}
    
    def execute_with_monitoring(self, user_id: int, k: int) -> Tuple[List[int], str]:
        start_time = time.time()
        try:
            recommendations = self.hybrid.recommend(user_id, k)
            latency = (time.time() - start_time) * 1000
            self._log_success(latency)
            return recommendations, "primary"
        except Exception as e:
            return self._execute_fallback(user_id, k, str(e))
```

---

## Next Steps

1. **Immediate**: Implement UserProfile class with genre weight calculation
2. **Follow-up**: Implement EnhancedColdStartHandler with profile building
3. **Then**: Implement NewItemDetector and popularity boost mechanism
4. **Finally**: Implement ParameterOptimizer and FallbackManager with monitoring