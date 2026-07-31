# Data Model: Hybrid Recommendation Framework

**Feature**: 003-hybrid-framework  
**Date**: 2026-07-30  
**Purpose**: Entity definitions and validation rules for hybrid recommendation system

---

## Core Entities

### HybridRecommender

**Purpose**: Main class implementing hybrid recommendation with Recommender and ColdStartHandler protocols

**Attributes**:
- `alpha: float` - Weighting parameter for content vs collaborative scores (default: 0.5, range: [0,1])
- `cold_start_threshold: int` - Rating count threshold for cold-start detection (default: 5)
- `active_threshold: int` - Rating count threshold for active user classification (default: 20)
- `content_model: ContentModel` - Content-based recommendation model (from Week 2)
- `user_based_cf: UserBasedCF` - User-based collaborative filtering model (from Day 1)
- `item_based_cf: ItemBasedCF` - Item-based collaborative filtering model (from Day 1)
- `normalization_params: Dict[str, Any]` - Normalization parameters for each model (min, max values)
- `model_selection_log: List[Dict[str, Any]]` - Log of model selection decisions for debugging
- `is_fitted: bool` - Flag indicating if all models have been trained
- `selected_model: str` - Name of model selected for last recommendation (for explanation delegation)

**Validation Rules**:
- `alpha` must be in range [0.0, 1.0]
- `cold_start_threshold` must be positive integer ≤ `active_threshold`
- `active_threshold` must be positive integer ≥ `cold_start_threshold`
- All model instances must satisfy Recommender protocol
- `content_model` must satisfy ColdStartHandler protocol
- Normalization parameters must be consistent with model score ranges
- `is_fitted` must be True before calling recommend()

**State Transitions**:
1. **Initial State**: `is_fitted = False`, models can be None or unfitted
2. **Fitted State**: `is_fitted = True`, all models trained and normalization params set
3. **Error State**: Model training failure or invalid configuration

---

### Score Combination

**Purpose**: Combine normalized scores from multiple models using weighted averaging

**Structure**:
- Input: Dict[str, List[Tuple[int, float]]] - Scores from each model {model_name: [(item_id, score), ...]}
- Normalization: Min-max normalization per model to [0,1] range
- Combination: weighted_score = α × content_score + (1-α) × collaborative_score
- Output: List[Tuple[int, float]] - Combined scores sorted by score descending

**Validation Rules**:
- Input scores must be non-negative (after normalization)
- All models must have scores for the same item set (or handle missing)
- Alpha parameter must be in [0,1] range
- Output must maintain consistent item IDs across models
- No NaN or infinite values in combined scores

**Business Rules**:
- Missing scores from one model are handled by using available scores
- If both models missing score for an item, item is excluded
- Ties in combined scores are broken by item_id ascending
- Normalization parameters are computed during fit() phase

---

### Model Selection

**Purpose**: Select optimal recommendation approach based on user activity level

**Structure**:
- Input: user_id, user_rating_count
- Decision Logic:
  - If rating_count ≤ cold_start_threshold: select "content"
  - If rating_count ≥ active_threshold: select "collaborative" (user-based or item-based)
  - Otherwise: select "hybrid"
- Output: Selected model instance and selection reason

**Validation Rules**:
- user_id must be present in training data
- rating_count must be non-negative integer
- Thresholds must be consistent (cold_start ≤ active)
- Selected model must be available and fitted
- Selection reason must be logged for debugging

**Business Rules**:
- Cold-start users get content-based recommendations (genre similarity)
- Active users get collaborative recommendations (user/item similarity)
- Intermediate users get hybrid recommendations (combined approach)
- Model selection is deterministic based on rating count
- Selection can be overridden by explicit model choice (future feature)

---

### Confidence Scoring

**Purpose**: Compute confidence scores indicating recommendation reliability

**Structure**:
- Activity Confidence: Based on user rating count (0.0 for new users, 1.0 for active users)
- Popularity Confidence: Based on item rating count (0.0 for new items, 1.0 for popular items)
- Agreement Confidence: Based on model agreement (0.0 for disagreement, 1.0 for agreement)
- Composite Confidence: 0.4 × activity + 0.3 × popularity + 0.3 × agreement
- Output: Confidence score ∈ [0,1] for each recommendation

**Validation Rules**:
- All confidence components must be in [0,1] range
- Weights must sum to 1.0
- Activity confidence must be monotonically increasing with rating count
- Popularity confidence must be based on item rating frequency
- Agreement confidence must measure correlation between model scores

**Business Rules**:
- Activity confidence: 0.0 for ≤5 ratings, 1.0 for ≥20 ratings, linear interpolation
- Popularity confidence: Based on percentile of item rating count in dataset
- Agreement confidence: Higher when models agree on top recommendations
- Composite confidence provides overall reliability assessment
- Confidence scores are returned alongside recommendations

---

### Fallback Chain

**Purpose**: Implement graceful degradation when models fail

**Structure**:
- Chain Order: Hybrid → Content → Collaborative → Popularity
- Fallback Trigger: Model exception, empty results, or timeout
- Fallback Action: Try next model in chain, log fallback event
- Fallback Limit: Maximum 3 fallback attempts before error
- Output: Recommendations from first successful model or error

**Validation Rules**:
- All models in chain must satisfy Recommender protocol
- Fallback must preserve original parameters (user_id, k, exclude_items)
- Fallback events must be logged with diagnostic information
- Fallback limit must prevent infinite loops
- Original error must be preserved in final error message

**Business Rules**:
- Each fallback attempts to satisfy original request parameters
- Fallback to popularity baseline only as last resort
- Fallback chain maintains recommendation availability (100% target)
- Fallback frequency is monitored for system health
- Fallback events are aggregated for performance analysis

---

### Persistence (IVP-Required)

**Purpose**: Save and load hybrid model artifacts using existing persistence.py module

**Structure**:
- Integration: Uses existing recolab.persistence module (ModelBundle, save_artifact, load_artifact)
- Pattern: to_bundle()/from_bundle() methods following Day 1 UserBasedCF/ItemBasedCF pattern
- Storage: Hybrid configuration, normalization parameters, model references, and selection log
- Format: Pickle serialization via existing persistence infrastructure

**Validation Rules**:
- to_bundle() must return ModelBundle with all necessary state for reconstruction
- from_bundle() must restore HybridRecommender to same state (normalization params, model references)
- save() must delegate to persistence.save_artifact() function
- load() must delegate to persistence.load_artifact() function
- Bundle must include: alpha, thresholds, normalization_params, selected_model, model_selection_log
- Model references are saved as identifiers (not full model states) to avoid large artifacts

**Business Rules**:
- Follows same pattern as UserBasedCF and ItemBasedCF persistence from Day 1
- Maintains compatibility with existing persistence.py module
- Supports evaluation reproducibility (REQ-12, AC-005)
- Normalization parameters must be saved for consistent score normalization after loading
- Model selection log is preserved for debugging and analysis

---

### Explanation Generation (IVP-Required)

**Purpose**: Generate human-readable explanations by delegating to selected underlying model

**Structure**:
- Strategy: Delegate to selected model's explain() method (ContentModel, UserBasedCF, or ItemBasedCF)
- Selection: Based on which model was selected for the recommendation
- Fallback: If selected model's explain() fails, provide generic explanation based on model selection reason
- Content: Explanation reflects actual factors used in scoring (GUD-002 truthful explanation requirement)

**Validation Rules**:
- explain() method must be available on all underlying models (from Day 1 IVP fixes)
- Selected model must be stored in selected_model attribute during recommendation
- Explanation must be string type and human-readable
- Explanation must be truthful based on actual scoring factors (GUD-002)
- Fallback explanation must still be meaningful (e.g., "Selected for hybrid approach")

**Business Rules**:
- ContentModel explanations: Based on genre similarity and user's liked movie genres
- UserBasedCF explanations: Based on similar users' preferences
- ItemBasedCF explanations: Based on similar items to user's rated items
- Hybrid explanations: Based on combined scoring approach (weighted average)
- Cold-start explanations: Based on genre preferences from onboarding
- Explanations satisfy REQ-004 and AC-004 architecture requirements

---

## Data Flow

### Training Flow

1. **Input**: pandas DataFrames for ratings and movies
2. **Model Training**: Train ContentModel, UserBasedCF, ItemBasedCF independently
3. **Normalization Setup**: Compute min/max scores from each model on validation set
4. **Parameter Storage**: Store normalization parameters in HybridRecommender
5. **Model Assignment**: Assign trained models to HybridRecommender instance
6. **State Update**: Set `is_fitted = True`

### Recommendation Flow

1. **Input**: user_id, k, exclude_items (optional)
2. **Activity Check**: Evaluate user rating count from training data
3. **Model Selection**: Select optimal model based on activity level
4. **Score Generation**: Get recommendations from selected model
5. **Confidence Computation**: Calculate confidence scores for recommendations
6. **Fallback Check**: If selected model fails, try next in fallback chain
7. **Filtering**: Apply exclude_items parameter if provided
8. **Logging**: Record model selection and confidence scores
9. **Output**: Recommendations with confidence scores

### Cold-Start Flow

1. **Input**: genres, liked_movie_ids, k
2. **Model Selection**: Force selection of ContentModel
3. **Preference Building**: Build user profile from genres and liked movies
4. **Recommendation Generation**: Use ContentModel.recommend_cold_start()
5. **Confidence Computation**: Calculate lower confidence (cold-start penalty)
6. **Output**: Recommendations with confidence scores

---

## Integrity Constraints

### Training Data Constraints

- All models must be trained on the same training data split
- Rating DataFrame must contain [user_id, movie_id, rating] columns
- Movies DataFrame must contain [movie_id, title, genres] columns
- No duplicate (user_id, movie_id) pairs in training data
- All models must have consistent user/item ID spaces

### Model Constraints

- All models must satisfy Recommender protocol
- ContentModel must satisfy ColdStartHandler protocol
- All models must be fitted before hybrid composition
- Model score ranges must be compatible for normalization
- Model performance must meet <100ms recommendation target

### Recommendation Constraints

- Must return exactly k recommendations (or fewer if insufficient candidates)
- Recommendations must exclude already-rated items
- Recommendations must respect exclude_items parameter
- Confidence scores must be in [0,1] range
- Model selection must be deterministic based on user activity
- Fallback chain must maintain 100% recommendation availability
- Explanations must be provided for each recommendation (REQ-004, GUD-002)
- Hybrid model artifacts must be persistable for evaluation reproducibility (REQ-012)

---

## Performance Considerations

### Latency Optimization

- Lazy model loading (load only when needed)
- Cache user activity level to avoid repeated computation
- Precompute normalization parameters during training
- Use vectorized operations for score combination
- Parallel model execution where beneficial

### Memory Optimization

- Share model instances (no duplication)
- Store only lightweight metadata (confidence scores, selection info)
- Avoid storing duplicate rating matrices
- Clean up intermediate results after combination
- Monitor memory usage during training

### Scalability Constraints

- Target dataset: MovieLens small (100k ratings, ~10k users, ~10k movies)
- Memory limit: <120MB total (existing models + hybrid overhead)
- Recommendation time: <100ms per request (same as individual models)
- Model selection overhead: <10ms per request
- Confidence computation overhead: <5ms per request

---

## Error Handling

### Training Errors

- **Model Training Failure**: Raise RuntimeError with specific model information
- **Normalization Failure**: Raise ValueError with score range details
- **Inconsistent Data**: Raise ValueError for mismatched user/item ID spaces
- **Memory Error**: Raise MemoryError with model-specific guidance

### Persistence Errors

- **Bundle Creation Failure**: Raise RuntimeError if to_bundle() cannot create valid ModelBundle
- **Bundle Load Failure**: Raise RuntimeError if from_bundle() cannot restore valid state
- **Artifact Save Failure**: Propagate persistence.save_artifact() exceptions
- **Artifact Load Failure**: Propagate persistence.load_artifact() exceptions
- **Model Reference Error**: Raise ValueError if saved model references are not available

### Explanation Errors

- **Selected Model Missing**: Raise RuntimeError if selected_model attribute is None
- **Explain Method Failure**: Provide generic explanation based on model selection reason
- **Missing Underlying explain()**: Raise NotImplementedError if model doesn't have explain() method

### Recommendation Errors

- **Unfitted Hybrid**: Raise RuntimeError if recommend() called before fit()
- **All Models Failed**: Raise RuntimeError with fallback chain details
- **Invalid User ID**: Raise KeyError for user_id not in training data
- **Invalid k Value**: Raise ValueError for k ≤ 0
- **Configuration Error**: Raise ValueError for invalid alpha or thresholds

### Cold-Start Errors

- **ContentModel Failure**: Propagate ContentModel exceptions
- **Invalid Genres**: Raise ValueError for non-existent or empty genres
- **Invalid Movie IDs**: Raise ValueError for movie_ids not in training data
- **Profile Building Failure**: Raise RuntimeError with diagnostic information

### Fallback Errors

- **Fallback Limit Exceeded**: Raise RuntimeError after 3 failed attempts
- **Parameter Mismatch**: Raise ValueError if fallback cannot preserve parameters
- **Logging Failure**: Log warning but continue with fallback
- **Timeout**: Raise TimeoutError with model-specific information