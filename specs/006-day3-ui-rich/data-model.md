# Day 3 Afternoon: Rich UI Features - Data Model

**Feature ID:** 006-day3-ui-rich  
**Date:** 2026-08-03  
**Status:** Draft

---

## Session State Extensions

### Extended State Dictionary
```python
# Extensions to Day 3 Morning session state
st.session_state.update({
    # Image Handling
    'poster_cache': Dict[int, str],  # movie_id -> poster_url
    'poster_loading_state': Dict[int, str],  # movie_id -> 'loading', 'loaded', 'error'
    
    # Similar Items
    'similar_items_data': List[Dict[str, Any]],  # Similar items for selected movie
    'selected_movie_for_similarity': Optional[int],  # Currently selected movie
    'show_similar_items': bool,  # Toggle for similar items view
    
    # Visualizations
    'visualization_data': Dict[str, Any],  # Aggregated statistics
    'show_visualizations': bool,  # Toggle for visualization panel
    'selected_visualization': str,  # Current visualization type
    
    # Item Details
    'selected_movie_detail': Optional[int],  # Currently selected movie for details
    'movie_detail_data': Optional[Dict[str, Any]],  # Detailed movie information
})
```

---

## Image Cache Data Model

### Poster Cache Structure
```python
class PosterCache:
    movie_id: int
    poster_url: str
    loading_state: str  # 'loading', 'loaded', 'error', 'placeholder'
    timestamp: str  # Cache timestamp
    source: str  # 'api', 'placeholder', 'cache'
```

### Poster Cache Entry
```python
class PosterCacheEntry:
    def __init__(self, movie_id: int):
        self.movie_id = movie_id
        self.poster_url = None
        self.loading_state = 'loading'
        self.timestamp = datetime.now(timezone.utc).isoformat()
        self.source = 'placeholder'
    
    def set_loaded(self, url: str, source: str = 'api'):
        self.poster_url = url
        self.loading_state = 'loaded'
        self.source = source
    
    def set_error(self):
        self.loading_state = 'error'
        self.poster_url = self._get_placeholder()
    
    def set_placeholder(self):
        self.poster_url = self._get_placeholder()
        self.loading_state = 'placeholder'
        self.source = 'placeholder'
```

---

## Similarity Data Model

### Similar Item Structure
```python
class SimilarItem:
    movie_id: int
    similarity_score: float
    title: str
    genres: List[str]
    year: Optional[int]
    similarity_type: str  # 'content', 'collaborative', 'hybrid'
```

### Similar Items Response
```python
class SimilarItemsResponse:
    source_movie_id: int
    source_movie_title: str
    similar_items: List[SimilarItem]
    similarity_method: str
    generation_time: float
    timestamp: str
```

---

## Statistics Data Model

### Rating Timeline Data
```python
class RatingTimelineData:
    user_id: int
    ratings: List[Dict[str, Any]]
    timeline_points: List[Dict[str, Any]]  # {'timestamp': str, 'rating': float}
    date_range: Tuple[str, str]  # (start_date, end_date)
    total_ratings: int
```

### Rating Distribution Data
```python
class RatingDistribution:
    user_id: int
    distribution: Dict[int, int]  # {rating: count}
    total_ratings: int
    average_rating: float
    most_common_rating: int
```

### Genre Preference Data
```python
class GenrePreference:
    user_id: int
    genre_preferences: Dict[str, float]  # {genre: percentage}
    total_genres: int
    top_genres: List[Tuple[str, float]]  # [(genre, percentage), ...]
```

### Activity Heatmap Data
```python
class ActivityHeatmap:
    user_id: int
    heatmap_data: pd.DataFrame  # 7x24 matrix (days x hours)
    day_labels: List[str]  # ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
    hour_labels: List[int]  # [0, 1, 2, ..., 23]
    total_activity_points: int
    most_active_day: str
    most_active_hour: int
```

---

## Item Detail Data Model

### Detailed Movie Information
```python
class MovieDetail:
    movie_id: int
    title: str
    year: Optional[int]
    genres: List[str]
    rating_count: int
    average_rating: float
    rating_distribution: Dict[int, int]
    popularity_rank: Optional[int]
    popularity_percentile: Optional[float]
    similar_items_count: int
    user_interactions: int  # Number of times this user rated/viewed
```

### Genre Tag Structure
```python
class GenreTag:
    genre: str
    preference_score: Optional[float]  # User's preference for this genre
    color_code: str  # For consistent color coding
    count_in_user_history: int  # How many times user rated this genre
```

---

## Visualization Data Model

### Chart Configuration
```python
class ChartConfig:
    chart_type: str  # 'line', 'bar', 'heatmap', 'scatter'
    title: str
    x_axis_label: str
    y_axis_label: str
    color_scheme: str
    interactive: bool
    show_legend: bool
    height: int
    width: int
```

### Visualization Data
```python
class VisualizationData:
    chart_config: ChartConfig
    data: Union[pd.DataFrame, Dict, List]
    metadata: Dict[str, Any]
    generated_at: str
    cache_key: str
```

---

## Component Communication Data Model

### Visualization Toggle Event
```python
class VisualizationToggleEvent:
    show_visualizations: bool
    selected_visualization: str
    user_id: int
    timestamp: str
```

### Similar Items Request Event
```python
class SimilarItemsRequestEvent:
    movie_id: int
    k: int  # Number of similar items
    similarity_method: str  # 'auto', 'content', 'collaborative'
    timestamp: str
```

### Poster Load Request Event
```python
class PosterLoadRequestEvent:
    movie_id: int
    force_refresh: bool
    timestamp: str
```

---

## Backend Integration Data Model

### Similarity API Response
```python
class SimilarityAPIResponse:
    similar_items: List[Tuple[int, float]]  # [(movie_id, score), ...]
    method_used: str
    computation_time: float
    success: bool
    error_message: Optional[str]
```

### Statistics API Response
```python
class StatisticsAPIResponse:
    timeline_data: pd.DataFrame
    distribution_data: Dict[int, int]
    genre_preferences: Dict[str, float]
    heatmap_data: pd.DataFrame
    computation_time: float
    success: bool
```

---

## Error State Data Model

### Visualization Error
```python
class VisualizationError:
    error_type: str  # 'data_unavailable', 'computation_failed', 'render_failed'
    visualization_type: str
    error_message: str
    timestamp: str
    retry_available: bool
```

### Image Loading Error
```python
class ImageLoadingError:
    movie_id: int
    error_type: str  # 'network_error', 'file_not_found', 'invalid_format'
    error_message: str
    timestamp: str
    fallback_used: bool
```

---

## Performance Metrics Data Model

### Visualization Performance
```python
class VisualizationPerformance:
    chart_type: str
    render_time: float
    data_size: int
    memory_usage: float
    timestamp: str
```

### Image Loading Performance
```python
class ImageLoadingPerformance:
    movie_id: int
    load_time: float
    image_size: int
    source: str  # 'api', 'placeholder', 'cache'
    timestamp: str
```

---

## Data Validation Rules

### Poster URL Validation
```python
POSTER_URL_VALIDATION = {
    'format': str,  # Must be valid URL
    'max_length': 2048,
    'allowed_schemes': ['http', 'https']
}
```

### Similarity Score Validation
```python
SIMILARITY_SCORE_VALIDATION = {
    'type': float,
    'min': 0.0,
    'max': 1.0,
    'default': 0.0
}
```

### Chart Data Validation
```python
CHART_DATA_VALIDATION = {
    'max_data_points': 10000,  # Maximum points per chart
    'max_categories': 50,  # Maximum categories for bar charts
    'max_series': 10  # Maximum series for line charts
}
```

---

## Data Flow Diagrams

### Poster Loading Flow
```
User Request → PosterCacheManager.get_poster() → Cache Check → 
Fetch/Load → Cache Update → UI Display
```

### Similar Items Flow
```
User Request → SimilarityProvider.get_similar_items() → Backend Similarity API → 
Data Processing → Session State Update → UI Display
```

### Visualization Flow
```
User Request → StatisticsAggregator → Data Computation → 
Chart Generation → Session State Update → UI Display
```

---

## Data Storage Requirements

### Temporary Storage (Session State)
- Poster cache in session state
- Similar items data in session state
- Aggregated statistics in session state
- Visualization configuration in session state

### Persistent Storage (File System)
- No additional persistent storage required
- All data derived from existing CSV files
- Poster URLs cached in session state only

---

## Data Migration Requirements

### No Migration Required
- This extends Day 3 Morning session state
- No data migration from previous systems
- Session state extensions are backward compatible

### Future Migration Considerations
- If poster persistence is needed, consider database storage
- If user preferences need persistence, consider profile storage
- If visualization history is needed, consider analytics storage

---

## Data Consistency Requirements

### Cache Consistency
- Poster cache consistency with actual poster availability
- Similar items cache consistency with backend similarity data
- Statistics cache consistency with user rating data

### Cache Invalidation
- Poster cache invalidation on data refresh
- Similar items cache invalidation on model updates
- Statistics cache invalidation on rating data changes

---

## Data Security Considerations

### External API Security
- If TMDB API integration added, secure API keys
- No sensitive data in poster URLs
- Rate limiting for external API calls

### User Data Privacy
- User rating data used only for visualizations
- No personal information exposed in visualizations
- Session state does not persist sensitive data

---

## Data Quality Requirements

### Poster Data Quality
- Poster URLs are valid and accessible
- Placeholder images are consistent
- Fallback mechanisms are reliable

### Similarity Data Quality
- Similarity scores are accurate
- Similarity methods are appropriate
- Similarity results are relevant

### Statistics Data Quality
- Timeline data is accurate and complete
- Distribution calculations are correct
- Genre preferences are accurately computed
- Heatmap data reflects actual user activity

---

## Data Performance Requirements

### Cache Performance
- Poster cache lookup time: < 50ms
- Similar items cache lookup time: < 100ms
- Statistics cache lookup time: < 100ms

### Computation Performance
- Similarity computation time: < 1 second
- Statistics aggregation time: < 2 seconds
- Chart rendering time: < 2 seconds

### Memory Performance
- Poster cache memory: < 50MB
- Similar items cache memory: < 10MB
- Statistics cache memory: < 20MB
- Total additional memory: < 100MB
