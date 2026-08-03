# Day 3 Morning: Core UI Structure - Data Model

**Feature ID:** 005-day3-ui-core  
**Date:** 2026-08-03  
**Status:** Draft

---

## Session State Data Model

### State Dictionary Structure
```python
st.session_state = {
    # User Selection
    'selected_user_id': Optional[int],
    
    # Model Selection
    'selected_model': str,  # 'popularity', 'content', 'user_based_cf', 'item_based_cf', 'hybrid'
    
    # Model Parameters
    'model_params': {
        'alpha': float,              # Hybrid model weighting (0.0-1.0)
        'k_similar': int,            # CF: number of similar users/items (5-50)
        'n_recommendations': int     # Number of recommendations (5, 10, 20)
    },
    
    # Recommendations
    'recommendations': List[Dict[str, Any]],  # Generated recommendations
    'last_recommendation_time': Optional[str],  # Timestamp of last generation
    
    # User Profile
    'user_profile': {
        'user_id': int,
        'rating_count': int,
        'activity_level': str  # 'cold-start', 'intermediate', 'active'
    },
    
    # System State
    'models_loaded': bool,
    'data_loaded': bool,
    'app_initialized': bool,
    
    # Extensible for Day 3 Afternoon
    'visualization_data': Optional[Dict[str, Any]],
    'similar_items_data': Optional[List[Dict[str, Any]]],
    
    # Extensible for Day 4
    'onboarding_preferences': Optional[Dict[str, Any]],
    'dashboard_metrics': Optional[Dict[str, Any]]
}
```

---

## Model Manager Data Model

### Model Cache Structure
```python
class ModelManager:
    models: Dict[str, Any] = {
        'popularity': PopularityModel,
        'content': ContentModel,
        'user_based_cf': UserBasedCF,
        'item_based_cf': ItemBasedCF,
        'hybrid': HybridRecommender
    }
    
    model_paths: Dict[str, str] = {
        'popularity': 'data/models/popularity_model.bundle',
        'content': 'data/models/content_model.bundle',
        'user_based_cf': 'data/models/user_based_cf.bundle',
        'item_based_cf': 'data/models/item_based_cf.bundle',
        'hybrid': 'data/models/hybrid_recommender.bundle'
    }
```

---

## Recommendation Data Model

### Recommendation Item Structure
```python
class RecommendationItem:
    movie_id: int
    title: str
    year: Optional[int]
    genres: List[str]
    score: Optional[float]  # Recommendation score if available
    explanation: str        # Human-readable explanation
    confidence: Optional[float]  # Confidence score for hybrid model
```

### Recommendation Response Structure
```python
class RecommendationResponse:
    user_id: int
    model_name: str
    model_params: Dict[str, Any]
    recommendations: List[RecommendationItem]
    generation_time: float  # Time in seconds
    timestamp: str  # ISO format timestamp
```

---

## User Profile Data Model

### User Profile Structure
```python
class UserProfile:
    user_id: int
    rating_count: int
    activity_level: str  # 'cold-start', 'intermediate', 'active'
    favorite_genres: Optional[List[str]]  # For future enhancement
    avg_rating: Optional[float]  # For future enhancement
```

### Activity Level Classification
```python
ACTIVITY_LEVELS = {
    'cold-start': rating_count <= 5,
    'intermediate': 5 < rating_count <= 20,
    'active': rating_count > 20
}
```

---

## Movie Metadata Data Model

### Movie Info Structure
```python
class MovieInfo:
    movie_id: int
    title: str
    genres: List[str]
    year: Optional[int]
    poster_url: Optional[str]  # For Day 3 Afternoon
    rating_count: Optional[int]  # For future enhancement
    avg_rating: Optional[float]  # For future enhancement
```

---

## Error State Data Model

### Error Information Structure
```python
class ErrorInfo:
    error_type: str  # 'model_loading', 'recommendation', 'data_access', 'validation'
    error_message: str
    timestamp: str
    retry_available: bool
    user_friendly_message: str
```

---

## Component Communication Data Model

### Component Event Structure
```python
class ComponentEvent:
    source_component: str  # 'user_selection', 'model_selection', etc.
    event_type: str  # 'user_changed', 'model_changed', 'params_changed'
    event_data: Dict[str, Any]
    timestamp: str
```

---

## Backend Integration Data Model

### Model Bundle Structure
```python
class ModelBundle:
    model_type: str
    model_class: str
    model_params: Dict[str, Any]
    fitted: bool
    metadata: Dict[str, Any]
```

---

## Validation Data Model

### Input Validation Rules
```python
VALIDATION_RULES = {
    'user_id': {
        'type': int,
        'min': 1,
        'required': True
    },
    'alpha': {
        'type': float,
        'min': 0.0,
        'max': 1.0,
        'default': 0.5
    },
    'k_similar': {
        'type': int,
        'min': 5,
        'max': 50,
        'default': 20
    },
    'n_recommendations': {
        'type': int,
        'allowed_values': [5, 10, 20],
        'default': 10
    }
}
```

---

## Performance Metrics Data Model

### Performance Metrics Structure
```python
class PerformanceMetrics:
    app_load_time: float
    model_load_times: Dict[str, float]
    recommendation_generation_time: float
    ui_response_time: float
    memory_usage: float
    timestamp: str
```

---

## Extensibility Markers

### Day 3 Afternoon Extensions
```python
# Rich Features Extensions
'similar_items_data': List[Dict[str, Any]]  # For similar items view
'rating_history_data': Dict[str, Any]     # For rating history visualization
'poster_cache': Dict[int, str]             # For movie poster display
'visualization_settings': Dict[str, Any]  # For chart configuration
```

### Day 4 Extensions
```python
# Cold-Start Onboarding Extensions
'onboarding_preferences': Dict[str, Any]    # Genre preferences, liked movies
'onboarding_step': int                      # Current wizard step
'onboarding_complete': bool                # Onboarding completion status

# Dashboard Extensions
'dashboard_metrics': Dict[str, Any]         # Performance metrics
'model_comparison_data': Dict[str, Any]    # Side-by-side comparison results
'explanation_detail_level': str           # 'basic', 'detailed', 'visual'
```

---

## Data Flow Diagrams

### User Selection Data Flow
```
User Input → Validation → Session State Update → User Profile Lookup → UI Update
```

### Model Selection Data Flow
```
Model Selection → Validation → Session State Update → Model Loading → Parameter UI Update
```

### Recommendation Generation Data Flow
```
Recommendation Request → Parameter Validation → Model Selection → 
Recommendation Generation → Explanation Generation → Movie Metadata Lookup → 
Session State Update → UI Update
```

---

## Data Storage Requirements

### Temporary Storage (Session State)
- User selections and preferences
- Model parameters
- Generated recommendations
- User profile information
- Performance metrics

### Persistent Storage (File System)
- Model artifacts: data/models/*.bundle
- Movie metadata: data/movies.csv
- Rating data: data/ratings.csv (for user profiles)

---

## Data Validation Rules

### User ID Validation
- Must be positive integer
- Must exist in ratings dataset
- Must have rating history (except for cold-start scenario)

### Model Parameter Validation
- α must be between 0.0 and 1.0
- k_similar must be between 5 and 50
- n_recommendations must be in [5, 10, 20]

### Recommendation Validation
- Must return list of movie IDs
- Must not include already-rated items
- Must respect exclusion list
- Must handle empty results gracefully

---

## Data Migration Requirements

### No Migration Required
- This is a new UI layer on top of existing backend
- No data migration from previous systems
- Session state is transient (no persistence required)

### Future Migration Considerations
- If session persistence is needed (Day 4), consider database or file-based storage
- If user preferences need persistence (Day 4), consider user profile storage
