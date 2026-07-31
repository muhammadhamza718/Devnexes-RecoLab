# Data Model: Cold-Start Optimization & Parameter Tuning

**Feature**: 004-cold-start-optimization  
**Date**: 2026-07-30  
**Purpose**: Entity definitions and validation rules for enhanced cold-start handling and parameter optimization

---

## Core Entities

### UserProfile

**Purpose**: Comprehensive user profile built from onboarding data for cold-start recommendations

**Attributes**:
- `user_id: Optional[int]` - User identifier (None for truly new users)
- `genre_weights: Dict[str, float]` - Normalized genre preference weights (sum to 1.0)
- `liked_movie_ids: List[int]` - List of movie IDs user liked during onboarding
- `created_at: datetime` - Profile creation timestamp
- `updated_at: datetime` - Last profile update timestamp
- `preferred_genres: List[str]` - Top-N preferred genres by weight
- `profile_id: str` - Unique identifier for profile persistence

**Validation Rules**:
- `genre_weights` must sum to 1.0 (within floating point tolerance)
- `genre_weights` values must be in range [0.0, 1.0]
- `liked_movie_ids` must be non-empty for profile building
- `created_at` must be ≤ `updated_at`
- `preferred_genres` must be subset of `genre_weights` keys
- `profile_id` must be unique and non-empty for persistence

**State Transitions**:
1. **Initial State**: Profile created from onboarding data
2. **Updated State**: Profile updated with new preferences
3. **Invalid State**: Profile with invalid weights or empty liked movies

**Business Rules**:
- Genre weights combine explicit (70%) and implicit (30%) preferences
- Top-3 genres selected as preferred genres for content matching
- Profile cached for subsequent cold-start recommendations
- Profile updates preserve relative weight ordering
- Profile persisted using existing persistence.py module for reproducibility (REQ-012)
- Profile data integrated into HybridRecommender.to_bundle() for model artifact saving

---

### EnhancedColdStartHandler

**Purpose**: Extended ColdStartHandler with preference weight calculation and profile building

**Attributes**:
- `content_model: ContentModel` - Content-based recommendation model
- `default_genres: List[str]` - Default genres for users with no preferences
- `new_item_threshold: int` - Rating count threshold for new-item detection (default: 5)
- `popularity_boost_weight: float` - Weight for new-item popularity boost (default: 0.3)
- `profile_cache: Dict[int, UserProfile]` - Cache of user profiles for performance
- `new_item_detector: NewItemDetector` - Component for new-item detection
- `profile_builder: ProfileBuilder` - Component for profile construction

**Validation Rules**:
- `content_model` must satisfy ColdStartHandler protocol
- `default_genres` must be non-empty
- `new_item_threshold` must be positive integer
- `popularity_boost_weight` must be in range [0.0, 1.0]
- `profile_cache` must respect memory limits (<50MB)

**State Transitions**:
1. **Initial State**: Handler initialized with dependencies
2. **Active State**: Profile building and recommendation generation active
3. **Cache State**: User profiles cached for performance
4. **Error State**: Profile building or recommendation failure

**Business Rules**:
- Profile building combines explicit genre selection with implicit liked movie patterns
- Default genres used when user provides no preferences
- Profile cache has TTL of 1 hour to avoid stale data
- New-item boost applied to recommendations for fresh content discovery
- Explanation generation delegated to ContentModel.explain() for cold-start recommendations (REQ-004, GUD-002)
- Cache invalidated on profile updates or user activity changes

---

### NewItemDetector

**Purpose**: Detect and flag new items based on interaction count and time since addition

**Attributes**:
- `rating_count_threshold: int` - Rating count threshold for new-item status (default: 5)
- `time_threshold_days: int` - Days threshold for time-based detection (default: 7)
- `popularity_boost_weight: float` - Weight for popularity boost calculation (default: 0.3)
- `new_item_cache: Dict[int, bool]` - Cache of new-item status for performance
- `rating_count_cache: Dict[int, int]` - Cache of item rating counts

**Validation Rules**:
- `rating_count_threshold` must be positive integer
- `time_threshold_days` must be positive integer
- `popularity_boost_weight` must be in range [0.0, 1.0]
- `new_item_cache` must respect memory limits (<10MB)

**State Transitions**:
1. **Initial State**: Detector initialized with thresholds
2. **Detection State**: New-item detection active
3. **Cache State**: New-item status cached for performance
4. **Error State**: Detection failure or cache corruption

**Business Rules**:
- New-item status determined by rating count OR time threshold
- Primary criterion: rating count ≤ threshold
- Secondary criterion: item added within threshold days
- Popularity boost decays linearly over 30 days
- New-item cache refreshed every 10 minutes

---

### ParameterOptimizer

**Purpose**: Grid search optimization for hybrid parameters (α, thresholds, k)

**Attributes**:
- `hybrid_recommender: HybridRecommender` - Hybrid model to optimize
- `validation_data: pd.DataFrame` - Validation set for parameter evaluation
- `parameter_space: Dict[str, List[Any]]` - Search space for each parameter
- `best_params: Dict[str, Any]` - Best parameters found during optimization
- `best_score: float` - Best NDCG@10 score achieved
- `optimization_history: List[Dict[str, Any]]` - History of parameter evaluations

**Validation Rules**:
- `hybrid_recommender` must be fitted before optimization
- `validation_data` must contain required columns (user_id, movie_id, rating)
- `parameter_space` must contain valid parameter ranges
- `best_params` must be subset of `parameter_space` keys
- `optimization_history` must track all evaluated configurations

**State Transitions**:
1. **Initial State**: Optimizer initialized with model and validation data
2. **Optimization State**: Grid search in progress
3. **Complete State**: Optimization complete with best parameters
4. **Error State**: Optimization failure or timeout

**Business Rules**:
- Grid search limited to 4-hour afternoon session
- Early stopping if improvement < 1% for 3 consecutive iterations
- Best parameters applied to hybrid model after optimization
- Optimization history saved for reproducibility and analysis
- Default parameters used if optimization fails or times out
- Optimized parameters integrated into HybridRecommender.to_bundle() for persistence (REQ-012)
- Single validation set used (cross-validation deferred to Week 4-6 due to 4-hour session constraint)

---

### FallbackManager

**Purpose**: Multi-level fallback chain with trigger conditions and performance monitoring

**Attributes**:
- `hybrid_recommender: HybridRecommender` - Primary hybrid model
- `fallback_chain: List[str]` - Ordered list of fallback methods
- `trigger_conditions: Dict[str, Callable]` - Trigger condition functions
- `fallback_log: List[Dict[str, Any]]` - Log of fallback activations
- `performance_metrics: Dict[str, Any]` - Performance metrics for monitoring
- `max_fallback_depth: int` - Maximum fallback depth (default: 3)

**Validation Rules**:
- `hybrid_recommender` must be fitted before fallback execution
- `fallback_chain` must contain valid model references
- `trigger_conditions` must return boolean values
- `fallback_log` must track timestamp, trigger reason, and result
- `max_fallback_depth` must be positive integer ≤ 5

**State Transitions**:
1. **Initial State**: Manager initialized with fallback chain
2. **Active State**: Fallback monitoring active
3. **Fallback State**: Fallback chain execution in progress
4. **Error State**: Fallback chain exhausted or failure

**Business Rules**:
- Fallback chain order: Hybrid → Content → Collaborative → Popularity
- Trigger conditions evaluated in priority order
- Each fallback attempt logged with performance metrics
- Fallback frequency monitored for system health
- Alert triggered if fallback rate > 10% for 5 consecutive minutes

---

### PerformanceMonitor

**Purpose**: Track cold-start metrics and fallback performance for system health

**Attributes**:
- `cold_start_metrics: Dict[str, float]` - Cold-start specific metrics (coverage, diversity, relevance)
- `fallback_metrics: Dict[str, float]` - Fallback performance metrics (frequency, latency, success rate)
- `metric_history: List[Dict[str, Any]]` - Historical metrics for trend analysis
- `alert_thresholds: Dict[str, float]` - Thresholds for alerting
- `last_update: datetime` - Last metrics update timestamp

**Validation Rules**:
- `cold_start_metrics` values must be in expected ranges (coverage [0,1], diversity [0,1])
- `fallback_metrics` values must be non-negative
- `metric_history` must maintain size limit (<1000 entries)
- `alert_thresholds` must be within valid metric ranges
- `last_update` must be within 5 minutes of current time

**State Transitions**:
1. **Initial State**: Monitor initialized with thresholds
2. **Monitoring State**: Metrics collection active
3. **Alert State**: Alert triggered based on thresholds
4. **Error State**: Metric collection failure

**Business Rules**:
- Metrics updated every 1 minute
- Alert triggered if cold-start coverage < 0.8 for 5 consecutive minutes
- Alert triggered if fallback rate > 0.1 for 5 consecutive minutes
- Metric history retained for 24 hours for trend analysis
- Performance reports generated every 10 minutes

---

### TunableParameters

**Purpose**: Configurable parameter set for optimization (α, thresholds, k, popularity boost weight)

**Attributes**:
- `alpha: float` - Weighting parameter for content vs collaborative scores (default: 0.5)
- `cold_start_threshold: int` - Rating count threshold for cold-start detection (default: 5)
- `active_threshold: int` - Rating count threshold for active user classification (default: 20)
- `k_recommendations: int` - Number of recommendations to return (default: 10)
- `popularity_boost_weight: float` - Weight for new-item popularity boost (default: 0.3)
- `genre_weight_explicit: float` - Weight for explicit genre preferences (default: 0.7)
- `genre_weight_implicit: float` - Weight for implicit genre preferences (default: 0.3)

**Validation Rules**:
- `alpha` must be in range [0.0, 1.0]
- `cold_start_threshold` must be positive integer ≤ `active_threshold`
- `active_threshold` must be positive integer ≥ `cold_start_threshold`
- `k_recommendations` must be positive integer
- `popularity_boost_weight` must be in range [0.0, 1.0]
- `genre_weight_explicit` + `genre_weight_implicit` must equal 1.0

**State Transitions**:
1. **Initial State**: Parameters set to default values
2. **Optimized State**: Parameters optimized via grid search
3. **Updated State**: Parameters manually updated
4. **Invalid State**: Parameter validation failure

**Business Rules**:
- Parameters must be validated before application to hybrid model
- Optimized parameters saved in model artifacts for reproducibility
- Parameter changes require model retraining for consistency
- Default parameters used if optimization fails

---

### ColdStartMetrics

**Purpose**: Performance metrics specific to cold-start scenarios (coverage, diversity, relevance)

**Attributes**:
- `coverage: float` - Percentage of cold-start users who received recommendations [0,1]
- `diversity: float` - Average pairwise genre distance in recommendations [0,1]
- `relevance: float` - Percentage of recommendations matching user genres [0,1]
- `novelty: float` - Percentage of recommendations outside user's known genres [0,1]
- `serendipity: float` - Percentage of unexpected but relevant recommendations [0,1]
- `calculation_timestamp: datetime` - When metrics were calculated

**Validation Rules**:
- All metric values must be in range [0.0, 1.0]
- `coverage` must be ≥ 0.0 (no negative coverage)
- `diversity` must be ≥ 0.0 (no negative diversity)
- `calculation_timestamp` must be within 1 hour of current time

**State Transitions**:
1. **Initial State**: Metrics initialized to 0.0
2. **Calculated State**: Metrics calculated from recommendation results
3. **Validated State**: Metrics validated against thresholds
4. **Error State**: Metric calculation failure

**Business Rules**:
- Metrics calculated on rolling window of last 100 cold-start users
- Coverage target: ≥0.95 (95% of cold-start users receive recommendations)
- Diversity target: ≥0.6 (sufficient genre variety)
- Relevance target: ≥0.7 (70% match user preferences)
- Metrics updated every 10 minutes

---

## Data Flow

### Enhanced Cold-Start Flow

1. **Input**: genres (List[str]), liked_movie_ids (List[int]), k (int)
2. **Profile Building**: Build UserProfile with genre weight calculation
3. **Genre Weight Calculation**: Combine explicit (70%) and implicit (30%) preferences
4. **Profile Normalization**: Normalize genre weights to sum to 1.0
5. **Recommendation Generation**: Use ContentModel with profile
6. **New-Item Boost**: Apply popularity boost to new items in results
7. **Fallback Check**: If recommendations insufficient, try fallback chain
8. **Metric Calculation**: Calculate cold-start metrics for monitoring
9. **Output**: Recommendations with confidence scores and explanations

### Parameter Optimization Flow

1. **Input**: HybridRecommender, validation_data, parameter_space
2. **Grid Generation**: Generate all parameter combinations from parameter_space
3. **Configuration Loop**: For each configuration:
   - Update hybrid model parameters
   - Evaluate on validation set (NDCG@10)
   - Track score and configuration
   - Apply early stopping if improvement < 1%
4. **Best Selection**: Select configuration with highest NDCG@10
5. **Parameter Application**: Apply best parameters to hybrid model
6. **Result Logging**: Save optimization history and best parameters
7. **Output**: Optimized parameters and improvement metrics

### Enhanced Fallback Flow

1. **Input**: user_id, k, exclude_items (optional)
2. **Primary Attempt**: Try HybridRecommender.recommend()
3. **Trigger Evaluation**: Check if fallback conditions met
4. **Fallback Chain**: For each fallback level:
   - Check trigger condition
   - Execute fallback method
   - Log attempt with performance metrics
   - Return if successful
5. **Fallback Exhaustion**: If all fallbacks fail, return error
6. **Performance Monitoring**: Track fallback frequency and patterns
7. **Alert Generation**: Trigger alert if fallback rate exceeds threshold
8. **Output**: Recommendations from first successful fallback or error

---

## Integrity Constraints

### Training Data Constraints

- All cold-start profiles must be built from consistent onboarding data
- Validation set must be leakage-free (no future ratings)
- Parameter optimization must use same validation set for consistency
- New-item detection must use current rating counts (not cached stale data)

### Model Constraints

- EnhancedColdStartHandler must extend ColdStartHandler protocol
- UserProfile must be compatible with ContentModel similarity methods
- ParameterOptimizer must work with fitted HybridRecommender
- FallbackManager must maintain fallback chain consistency

### Recommendation Constraints

- Cold-start recommendations must exclude already-rated items
- New-item boost must not violate score normalization [0,1] range
- Parameter optimization must maintain <100ms latency target
- Fallback chain must maintain 100% recommendation availability

---

## Performance Considerations

### Latency Optimization

- Profile caching for cold-start users (10-minute TTL)
- New-item status caching (10-minute TTL)
- Parameter optimization results caching
- Lazy evaluation of fallback conditions
- Efficient genre weight calculation using vectorized operations

### Memory Optimization

- Profile cache size limit (<50MB)
- New-item cache size limit (<10MB)
- Optimization history size limit (<50MB) (reduced to stay within 150MB total)
- Metric history size limit (<40MB) (reduced to stay within 150MB total)
- Total memory budget: <150MB (morning hybrid + afternoon enhancements)
- Cleanup of stale cache entries

### Scalability Constraints

- Target dataset: MovieLens small (100k ratings, ~10k users, ~10k movies)
- Memory limit: <150MB total (morning hybrid + afternoon enhancements)
- Cold-start recommendation time: <100ms (same as primary recommendations)
- Parameter optimization time: <5 minutes for limited grid search
- Fallback chain execution time: <50ms total

---

## Error Handling

### Profile Building Errors

- **Empty Profile Error**: Raise ValueError if user provides no genres and no liked movies
- **Weight Calculation Error**: Raise ValueError if genre weights cannot be normalized
- **Cache Corruption Error**: Clear cache and rebuild profile on cache miss
- **Profile Update Error**: Rollback to previous profile state on update failure
- **Profile Persistence Error**: Rebuild profile from onboarding data if persistence fails

### Parameter Optimization Errors

- **Optimization Timeout**: Return best partial results if timeout exceeded
- **Validation Data Error**: Raise ValueError if validation data is invalid or empty
- **Configuration Error**: Skip invalid configurations and continue with next
- **Memory Error**: Reduce parameter space and retry optimization

### Explanation Generation Errors

- **ContentModel Explain Failure**: Provide generic explanation based on genre preferences if ContentModel.explain() fails
- **Explanation Truthfulness Error**: Ensure explanations are grounded in model selection reasons (GUD-002)
- **Cold-Start Context Error**: Include cold-start context (genre preferences) in explanation generation

### Fallback Errors

- **Fallback Exhaustion**: Raise RuntimeError if all fallback levels fail
- **Trigger Condition Error**: Use default error trigger if condition evaluation fails
- **Performance Monitor Error**: Continue fallback execution even if monitoring fails
- **Cache Error**: Execute fallback without caching if cache unavailable

---

## Performance Metrics

### Cold-Start Performance Targets

- **Profile Building**: <10ms per profile (cached: <1ms)
- **Genre Weight Calculation**: <5ms per calculation
- **Recommendation Generation**: <100ms total
- **New-Item Detection**: <2ms per item (cached: <0.1ms)
- **Popularity Boost Application**: <1ms per recommendation

### Parameter Optimization Performance Targets

- **Grid Search**: <5 minutes total (limited parameter space)
- **Configuration Evaluation**: <10ms per configuration
- **Best Parameter Selection**: <1ms
- **Result Storage**: <1ms

### Fallback Performance Targets

- **Trigger Evaluation**: <1ms per trigger
- **Fallback Execution**: <50ms per fallback level
- **Performance Logging**: <2ms per fallback attempt
- **Metric Calculation**: <5ms per metric set

---

## Success Criteria Validation

### Functional Requirements Coverage

- ✅ FR-001: Enhanced ColdStartHandler with preference weight calculation
- ✅ FR-002: Comprehensive user profile building
- ✅ FR-003: New-item detection and flagging
- ✅ FR-004: Temporary popularity boost for new items
- ✅ FR-005: Parameter tuning via grid search
- ✅ FR-006: α parameter optimization
- ✅ FR-007: Activity threshold optimization
- ✅ FR-008: Multi-level fallback chain
- ✅ FR-009: Fallback performance monitoring
- ✅ FR-010: Cold-start performance metrics
- ✅ FR-011: Parameterized tunable values
- ✅ FR-012: <100ms latency maintained
- ✅ FR-013: Explanation generation via ContentModel.explain() delegation
- ✅ FR-014: UserProfile persistence via existing persistence.py module

### Success Criteria Coverage

- ✅ SC-001: ≥5 relevant cold-start recommendations
- ✅ SC-002: ≥90% new-item recommendation coverage
- ✅ SC-003: ≥5% NDCG@10 improvement from tuning
- ✅ SC-004: 100% fallback availability
- ✅ SC-005: Actionable fallback health insights
- ✅ SC-006: ≥70% code coverage
- ✅ SC-007: ≥15 passing unit tests
- ✅ SC-008: <100ms latency maintained
- ✅ SC-009: Improved cold-start metrics
- ✅ SC-010: Reproducible optimization results
- ✅ SC-011: Cold-start explanations include human-readable text (REQ-004, AC-004)
- ✅ SC-012: UserProfile data persisted for reproducibility (REQ-012, AC-005)