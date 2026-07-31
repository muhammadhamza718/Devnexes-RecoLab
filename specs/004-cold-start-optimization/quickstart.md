# Quickstart Guide: Cold-Start Optimization & Parameter Tuning

**Feature**: 004-cold-start-optimization  
**Date**: 2026-07-30  
**Purpose**: Development setup and initial implementation guidance for enhanced cold-start handling and parameter optimization

---

## Prerequisites

### Morning Dependencies
- ✅ Day 2 morning HybridRecommender fully implemented
- ✅ ColdStartHandler protocol from morning implementation
- ✅ ContentModel from Week 2 with genre similarity
- ✅ Persistence module with to_bundle()/from_bundle() methods
- ✅ 30+ passing tests for hybrid framework

### Technical Requirements
- Python 3.11+ (consistent with morning implementation)
- pytest and pytest-cov for testing (≥70% coverage requirement)
- pandas and numpy for data manipulation
- scikit-learn for metric calculations (optional, if time allows)

### Dataset Requirements
- MovieLens small dataset with ratings.csv and movies.csv
- Validation set for parameter optimization (20% of training data)
- Genre metadata in movies.csv for profile building

---

## Development Setup

### Environment Verification

```bash
# Verify morning implementation is available
cd F:\Courses\Hamza\Devnexes-Internship-Projects
python -c "from recolab.hybrid import HybridRecommender; print('HybridRecommender available')"

# Verify ContentModel is available
python -c "from recolab.content import ContentModel; print('ContentModel available')"

# Verify test infrastructure
pytest tests/test_hybrid.py -v --tb=short
```

### Project Structure Verification

```bash
# Verify directory structure
ls src/recolab/hybrid.py  # Should exist from morning
ls tests/test_hybrid.py     # Should exist from morning
ls tests/fixtures/          # Should exist from morning
```

---

## Implementation Steps

### Phase 1: Setup (15 minutes)

1. **Create UserProfile class**
   ```python
   # src/recolab/hybrid.py
   class UserProfile:
       def __init__(self, user_id: Optional[int], genres: List[str], liked_movie_ids: List[int]):
           self.user_id = user_id
           self.genre_weights = self._calculate_initial_weights(genres, liked_movie_ids)
           self.liked_movie_ids = liked_movie_ids
           self.created_at = datetime.now()
   ```

2. **Add test infrastructure**
   ```python
   # tests/test_hybrid.py
   def test_user_profile_creation():
       profile = UserProfile(None, ["Sci-Fi", "Action"], [1210, 587])
       assert profile.genre_weights is not None
       assert len(profile.liked_movie_ids) == 2
   ```

### Phase 2: Enhanced Cold-Start (60 minutes)

1. **Implement EnhancedColdStartHandler**
   ```python
   class EnhancedColdStartHandler(ColdStartHandler):
       def __init__(self, content_model: ContentModel, default_genres: List[str]):
           self.content_model = content_model
           self.default_genres = default_genres
           self.profile_cache = {}
       
       def build_user_profile(self, genres: List[str], liked_movie_ids: List[int]) -> UserProfile:
           return UserProfile(None, genres, liked_movie_ids)
   ```

2. **Implement genre weight calculation**
   ```python
   def calculate_genre_weights(self, genres: List[str], liked_movie_ids: List[int]) -> Dict[str, float]:
       # Explicit weights (70%)
       explicit = {genre: 0.7 for genre in genres}
       
       # Implicit weights from liked movies (30%)
       implicit = self._extract_genre_weights(liked_movie_ids)
       
       # Combine and normalize
       combined = {k: explicit.get(k, 0) + implicit.get(k, 0) 
                  for k in set(explicit) | set(implicit)}
       return self._normalize_weights(combined)
   ```

3. **Add comprehensive tests**
   ```python
   def test_enhanced_cold_start_recommendations():
       handler = EnhancedColdStartHandler(content_model, ["Sci-Fi", "Action"])
       recommendations = handler.recommend_cold_start(["Sci-Fi"], [1210], 10)
       assert len(recommendations) >= 5
   ```

### Phase 3: New-Item Handling (45 minutes)

1. **Implement NewItemDetector**
   ```python
   class NewItemDetector:
       def __init__(self, rating_count_threshold: int = 5):
           self.rating_count_threshold = rating_count_threshold
           self.new_item_cache = {}
       
       def detect_new_item(self, movie_id: int, rating_count: int) -> bool:
           return rating_count <= self.rating_count_threshold
       
       def apply_popularity_boost(self, score: float, is_new: bool) -> float:
           if not is_new:
               return score
           return min(score * 1.3, 1.0)  # 30% boost, capped at 1.0
   ```

2. **Integrate with cold-start recommendations**
   ```python
   def recommend_cold_start(self, genres: List[str], liked_movie_ids: List[int], k: int):
       # Build profile and get base recommendations
       profile = self.build_user_profile(genres, liked_movie_ids)
       recommendations = self.content_model.recommend_cold_start(genres, liked_movie_ids, k)
       
       # Apply new-item boost
       boosted_recs = [(item_id, self.new_item_detector.apply_popularity_boost(score, self._is_new_item(item_id)))
                      for item_id, score in recommendations]
       
       return sorted(boosted_recs, key=lambda x: x[1], reverse=True)[:k]
   ```

### Phase 4: Parameter Optimization (60 minutes)

1. **Implement ParameterOptimizer**
   ```python
   class ParameterOptimizer:
       def __init__(self, hybrid_recommender: HybridRecommender, validation_data: pd.DataFrame):
           self.hybrid = hybrid_recommender
           self.validation_data = validation_data
           self.best_params = {}
       
       def grid_search_alpha(self, alpha_values: List[float] = [0.2, 0.5, 0.8]):
           best_alpha = 0.5
           best_score = 0.0
           
           for alpha in alpha_values:
               self.hybrid.alpha = alpha
               score = self._evaluate_ndcg_at_k()
               
               if score > best_score:
                   best_score = score
                   best_alpha = alpha
           
           return best_alpha
   ```

2. **Implement evaluation function**
   ```python
   def _evaluate_ndcg_at_k(self, k: int = 10):
       # Calculate NDCG@10 on validation set
       # Return average NDCG across all users
       total_ndcg = 0.0
       user_count = 0
       
       for user_id in self.validation_data['user_id'].unique():
           recommendations = self.hybrid.recommend(user_id, k)
           actual_items = self.validation_data[self.validation_data['user_id'] == user_id]['movie_id'].values
           ndcg = self._calculate_ndcg(recommendations, actual_items)
           total_ndcg += ndcg
           user_count += 1
       
       return total_ndcg / user_count if user_count > 0 else 0.0
   ```

### Phase 5: Enhanced Fallback (30 minutes)

1. **Implement FallbackManager**
   ```python
   class FallbackManager:
       def __init__(self, hybrid_recommender: HybridRecommender):
           self.hybrid = hybrid_recommender
           self.fallback_log = []
       
       def execute_fallback_chain(self, user_id: int, k: int):
           # Try primary hybrid model
           try:
               recommendations = self.hybrid.recommend(user_id, k)
               return recommendations, "primary"
           except Exception as e:
               # Fallback to ContentModel
               try:
                   recommendations = self.hybrid.content_model.recommend(user_id, k)
                   self._log_fallback("content", str(e))
                   return recommendations, "content_fallback"
               except Exception as e2:
                   # Fallback to popularity
                   recommendations = self._get_popularity_recommendations(k)
                   self._log_fallback("popularity", str(e2))
                   return recommendations, "popularity_fallback"
   ```

### Phase 6: Testing & Validation (30 minutes)

1. **Run comprehensive tests**
   ```bash
   pytest tests/test_hybrid.py -v --tb=short --cov=src/recolab/hybrid
   ```

2. **Verify performance targets**
   ```python
   def test_cold_start_latency():
       handler = EnhancedColdStartHandler(content_model, default_genres)
       start = time.time()
       recommendations = handler.recommend_cold_start(["Sci-Fi"], [1210], 10)
       latency = (time.time() - start) * 1000
       assert latency < 100  # <100ms target
   ```

3. **Verify parameter optimization**
   ```python
   def test_parameter_optimization():
       optimizer = ParameterOptimizer(hybrid, validation_data)
       best_alpha = optimizer.grid_search_alpha()
       assert 0.2 <= best_alpha <= 0.8
       assert optimizer.best_score > 0.0
   ```

---

## Common Patterns

### Pattern 1: Profile Building with Genre Weights

```python
def build_enhanced_profile(genres: List[str], liked_movie_ids: List[int]) -> UserProfile:
    # Combine explicit (70%) and implicit (30%) preferences
    explicit_weights = {genre: 0.7 for genre in genres}
    implicit_weights = extract_genre_weights(liked_movie_ids)
    
    # Normalize to sum to 1.0
    combined = {k: explicit_weights.get(k, 0) + implicit_weights.get(k, 0) 
                for k in set(explicit_weights) | set(implicit_weights)}
    total = sum(combined.values())
    normalized = {k: v/total for k, v in combined.items()}
    
    return UserProfile(None, normalized, liked_movie_ids)
```

### Pattern 2: New-Item Detection with Caching

```python
def is_new_item(self, movie_id: int) -> bool:
    # Check cache first
    if movie_id in self.new_item_cache:
        return self.new_item_cache[movie_id]
    
    # Calculate new-item status
    rating_count = self._get_rating_count(movie_id)
    is_new = rating_count <= self.rating_count_threshold
    
    # Cache result
    self.new_item_cache[movie_id] = is_new
    return is_new
```

### Pattern 3: Parameter Optimization with Early Stopping

```python
def optimize_with_early_stopping(self, param_space: Dict[str, List[Any]]):
    best_score = 0.0
    no_improvement_count = 0
    
    for config in self._generate_configs(param_space):
        score = self._evaluate_config(config)
        
        if score > best_score:
            best_score = score
            self.best_params = config.copy()
            no_improvement_count = 0
        else:
            no_improvement_count += 1
        
        # Early stopping if no improvement for 3 iterations
        if no_improvement_count >= 3:
            break
    
    return self.best_params
```

### Pattern 4: Fallback with Performance Monitoring

```python
def execute_with_monitoring(self, user_id: int, k: int):
    start_time = time.time()
    trigger_reason = None
    
    try:
        recommendations = self.hybrid.recommend(user_id, k)
        latency = (time.time() - start_time) * 1000
        self._log_success(latency)
        return recommendations, "primary"
    except Exception as e:
        trigger_reason = str(e)
        recommendations = self._execute_fallback(user_id, k)
        self._log_fallback(trigger_reason, latency)
        return recommendations, f"fallback_{trigger_reason}"
```

---

## Testing Checklist

### Unit Tests (Target: 15+ tests)

- [ ] UserProfile creation and validation
- [ ] Genre weight calculation accuracy
- [ ] Profile normalization correctness
- [ ] EnhancedColdStartHandler profile building
- [ ] Cold-start recommendation quality
- [ ] New-item detection accuracy
- [ ] Popularity boost application
- [ ] Parameter optimization grid search
- [ ] NDCG@10 calculation correctness
- [ ] Fallback chain execution
- [ ] Fallback trigger conditions
- [ ] Performance monitoring accuracy
- [ ] Cold-start metrics calculation
- [ ] Cache consistency
- [ ] Error handling robustness

### Integration Tests

- [ ] EnhancedColdStartHandler with ContentModel integration
- [ ] ParameterOptimizer with HybridRecommender integration
- [ ] FallbackManager with all models integration
- [ ] End-to-end cold-start to recommendation flow
- [ ] Parameter optimization application to model

### Performance Tests

- [ ] Cold-start recommendation latency <100ms
- [ ] Profile building latency <10ms
- [ ] Parameter optimization time <5 minutes
- [ ] Fallback chain execution <50ms
- [ ] Cache hit performance

---

## Troubleshooting

### Common Issues

**Issue 1: Profile building fails with empty genres and liked movies**
- **Solution**: Use default genres and skip profile building, fall back to content-based recommendations

**Issue 2: Parameter optimization takes too long**
- **Solution**: Reduce parameter space, enable early stopping, use smaller validation subset

**Issue 3: Fallback chain fails completely**
- **Solution**: Add popularity baseline as final fallback, log detailed error information

**Issue 4: Cold-start metrics are not calculating correctly**
- **Solution**: Verify metric calculation logic, check validation data quality, review normalization

**Issue 5: New-item boost not applied correctly**
- **Solution**: Verify new-item detection logic, check cache consistency, review boost calculation

### Debugging Tips

1. **Profile Building**: Log genre weights at each step to verify calculation
2. **Parameter Optimization**: Log each configuration evaluation to track progress
3. **Fallback Chain**: Log each fallback attempt with trigger reason and performance
4. **Cache Issues**: Clear cache and rebuild if inconsistency detected
5. **Performance**: Profile critical paths to identify bottlenecks

---

## Verification Steps

### Before Implementation

1. Verify morning hybrid implementation is working (30+ tests passing)
2. Verify ContentModel has genre similarity functionality
3. Verify validation set is available for parameter optimization
4. Verify test infrastructure is functional

### During Implementation

1. Run tests after each phase completion
2. Verify performance targets are met (<100ms latency)
3. Check cache consistency and memory usage
4. Monitor fallback chain activation frequency

### After Implementation

1. Run full test suite with coverage report
2. Verify ≥15 new tests pass for afternoon features
3. Verify overall coverage ≥70%
4. Run performance benchmarks
5. Verify cold-start metrics meet targets

---

## Next Steps

1. **Immediate**: Implement UserProfile class with genre weight calculation
2. **Follow-up**: Implement EnhancedColdStartHandler with profile building
3. **Then**: Implement NewItemDetector and popularity boost mechanism
4. **Finally**: Implement ParameterOptimizer and FallbackManager with monitoring
5. **Completion**: Run comprehensive tests and verify all success criteria