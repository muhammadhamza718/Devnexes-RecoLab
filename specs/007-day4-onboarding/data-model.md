# Day 4 Morning: Cold-Start Onboarding UI - Data Model

**Feature ID:** 007-day4-onboarding  
**Date:** 2026-08-03  
**Status:** Draft

---

## Session State Extensions

### Extended State Dictionary
```python
# Extensions to Day 3 session state
st.session_state.update({
    # Onboarding State
    'onboarding_active': bool,  # Whether onboarding is currently active
    'onboarding_step': int,  # Current wizard step (0, 1, 2)
    'onboarding_complete': bool,  # Whether onboarding is completed
    'onboarding_timestamp': str,  # ISO timestamp of onboarding completion
    
    # User Preferences
    'selected_genres': List[str],  # Selected genre preferences
    'liked_movies': List[int],  # Selected liked movie IDs
    'preference_weights': Dict[str, float],  # Genre preference weights
    
    # Onboarding Data
    'onboarding_preferences': Dict[str, Any],  # Complete preference set
    'precommendation_preview': List[Dict],  # Preview recommendations
})
```

---

## Onboarding State Data Model

### Wizard State Structure
```python
class OnboardingState:
    current_step: int  # 0: genre_selection, 1: liked_movies, 2: confirmation
    total_steps: int  # Always 3 for this implementation
    can_proceed: bool  # Whether current step is valid for proceeding
    step_validation: Dict[int, bool]  # Validation status per step
    timestamp: str  # State update timestamp
```

### Step Definitions
```python
ONBOARDING_STEPS = {
    0: 'genre_selection',
    1: 'liked_movies', 
    2: 'confirmation'
}
```

---

## Preference Data Model

### Genre Preference Structure
```python
class GenrePreference:
    genre: str
    selected: bool
    weight: float  # Preference weight (0.0-1.0)
    popularity: int  # Number of movies with this genre
    rank: int  # Popularity rank
```

### Liked Movie Structure
```python
class LikedMovie:
    movie_id: int
    title: str
    genres: List[str]
    year: Optional[int]
    preference_intensity: Optional[float]  # Optional intensity rating
    added_timestamp: str
```

### Complete Preference Set
```python
class UserPreferences:
    genres: List[GenrePreference]
    liked_movies: List[LikedMovie]
    preference_strength: str  # 'weak', 'medium', 'strong'
    diversity_score: float  # Genre diversity metric
    timestamp: str
```

---

## Genre Data Model

### Genre Metadata
```python
class GenreMetadata:
    genre: str
    count: int  # Number of movies with this genre
    percentage: float  # Percentage of total catalog
    popularity_rank: int
    related_genres: List[str]  # Commonly co-occurring genres
    average_rating: Optional[float]  # Average rating for this genre
```

### Genre Combination Structure
```python
class GenreCombination:
    genres: List[str]
    compatibility_score: float  # How well genres work together
    popularity_score: float  # How popular this combination is
    recommendation_count: int  # Number of users with similar preferences
```

---

## Movie Search Data Model

### Search Query Structure
```python
class SearchQuery:
    query: str
    limit: int  # Maximum results to return
    filters: Dict[str, Any]  # Optional filters (genre, year, etc.)
    timestamp: str
```

### Search Result Structure
```python
class SearchResult:
    movie_id: int
    title: str
    genres: List[str]
    year: Optional[int]
    relevance_score: float  # Search relevance score
    match_type: str  # 'exact', 'partial', 'fuzzy'
```

---

## Recommendation Data Model

### Cold-Start Recommendation Request
```python
class ColdStartRequest:
    genres: List[str]
    liked_movies: List[int]
    genre_weights: Dict[str, float]
    k: int  # Number of recommendations
    user_id: Optional[int]  # For session tracking
    timestamp: str
```

### Cold-Start Recommendation Response
```python
class ColdStartResponse:
    recommendations: List[Dict[str, Any]]
    explanation: str  # How preferences influenced recommendations
    confidence: float  # Confidence in recommendations
    method_used: str  # 'hybrid', 'content', 'popularity'
    generation_time: float
    timestamp: str
```

---

## Validation Data Model

### Validation Result Structure
```python
class ValidationResult:
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    field: str  # Field being validated
    timestamp: str
```

### Preference Validation Rules
```python
GENRE_VALIDATION_RULES = {
    'min_genres': 1,
    'max_genres': 5,
    'required': True
}

LIKED_MOVIES_VALIDATION_RULES = {
    'max_movies': 10,
    'required': False
}
```

---

## Component Communication Data Model

### Wizard Navigation Event
```python
class WizardNavigationEvent:
    action: str  # 'next', 'previous', 'skip', 'complete'
    current_step: int
    target_step: Optional[int]
    validation_passed: bool
    timestamp: str
```

### Preference Update Event
```python
class PreferenceUpdateEvent:
    preference_type: str  # 'genre', 'liked_movie'
    action: str  # 'add', 'remove', 'update'
    value: Any
    timestamp: str
```

---

## Backend Integration Data Model

### ColdStartHandler API Request
```python
class ColdStartAPIRequest:
    genres: List[str]
    liked_movie_ids: List[int]
    k: int
    request_id: str  # For tracking
    timestamp: str
```

### ColdStartHandler API Response
```python
class ColdStartAPIResponse:
    movie_ids: List[int]
    explanations: List[str]
    confidence_scores: List[float]
    method_used: str
    success: bool
    error_message: Optional[str]
    computation_time: float
```

---

## Error State Data Model

### Onboarding Error
```python
class OnboardingError:
    error_type: str  # 'validation', 'backend', 'search', 'recommendation'
    step: int  # Wizard step where error occurred
    error_message: str
    user_friendly_message: str
    recovery_action: str  # 'retry', 'skip', 'fallback'
    timestamp: str
```

---

## Performance Metrics Data Model

### Onboarding Performance
```python
class OnboardingPerformance:
    total_completion_time: float
    step_times: Dict[int, float]  # Time per step
    search_performance: Dict[str, float]
    recommendation_generation_time: float
    ui_response_time: float
    timestamp: str
```

---

## Data Validation Rules

### Genre Selection Validation
```python
GENRE_SELECTION_VALIDATION = {
    'min_selection': 1,
    'max_selection': 5,
    'allowed_genres': 'dynamic',  # From movies dataset
    'required': True
}
```

### Movie Search Validation
```python
MOVIE_SEARCH_VALIDATION = {
    'min_query_length': 2,
    'max_query_length': 100,
    'max_results': 20,
    'allowed_characters': 'alphanumeric_spaces'
}
```

### Preference Validation
```python
PREFERENCE_VALIDATION = {
    'max_genres': 5,
    'max_liked_movies': 10,
    'min_total_preferences': 1,
    'allow_empty_liked_movies': True
}
```

---

## Data Flow Diagrams

### Onboarding Flow
```
User Starts → Onboarding Detection → Step 1 (Genres) → Step 2 (Liked Movies) → 
Step 3 (Confirmation) → Backend API → Recommendations → Main Interface
```

### Preference Update Flow
```
User Action → Validation → Session State Update → UI Refresh → 
Backend Sync (if complete)
```

### Recommendation Generation Flow
```
Preferences Collected → Validation → ColdStartHandler API → 
Recommendation Generation → Formatting → UI Display
```

---

## Data Storage Requirements

### Temporary Storage (Session State)
- Onboarding state and progress
- User preferences (genres, liked movies)
- Search results cache
- Recommendation preview

### Persistent Storage (Future)
- User preferences for returning users
- Onboarding completion history
- Preference analytics and optimization

---

## Data Migration Requirements

### No Migration Required
- This extends Day 3 session state
- No data migration from previous systems
- Session state extensions are backward compatible

### Future Migration Considerations
- If user preferences need persistence, consider database storage
- If onboarding analytics needed, consider analytics storage
- If personalization improvement needed, consider ML model storage

---

## Data Consistency Requirements

### Preference Consistency
- Genre selections consistent with available genres
- Liked movies consistent with available movies
- Preference weights normalized correctly
- No duplicate selections

### State Consistency
- Wizard step consistent with actual progress
- Session state consistent with UI state
- Onboarding completion state consistent with recommendations

---

## Data Security Considerations

### User Privacy
- No personal information collected during onboarding
- Preferences are session-based only
- No tracking of individual user behavior
- Anonymous preference aggregation only

### Data Minimization
- Only collect necessary preferences
- No unnecessary data collection
- Session-only storage by default
- Clear data retention policy

---

## Data Quality Requirements

### Genre Data Quality
- Genre list complete and accurate
- Genre popularity metrics correct
- Genre combinations relevant and popular
- Genre metadata up-to-date

### Movie Data Quality
- Movie search results accurate and relevant
- Movie metadata complete and correct
- Search relevance scoring accurate
- No duplicate or invalid movie entries

### Preference Data Quality
- Preferences validated before submission
- Preference weights applied correctly
- Preference combinations logical
- No conflicting preferences

---

## Data Performance Requirements

### Search Performance
- Genre list load time: < 100ms
- Movie search response time: < 1 second
- Search result rendering: < 500ms

### Validation Performance
- Preference validation time: < 100ms
- Step validation time: < 50ms
- Form validation time: < 200ms

### Recommendation Performance
- Cold-start API call time: < 2 seconds
- Recommendation formatting time: < 500ms
- Total recommendation generation: < 3 seconds
