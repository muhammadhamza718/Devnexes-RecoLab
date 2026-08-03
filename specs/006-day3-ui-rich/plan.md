# Day 3 Afternoon: Rich UI Features - Implementation Plan

**Feature ID:** 006-day3-ui-rich  
**Date:** 2026-08-03  
**Status:** Draft  
**Effort:** 4 hours (Day 3 Afternoon)

---

## Architecture Overview

The rich UI features extend the core UI structure with visualization components, image handling, and enhanced data presentation. The architecture follows the progressive enhancement pattern established in Day 3 Morning.

### System Architecture Extension

```
┌─────────────────────────────────────────────────────────────┐
│                    Extended UI Layer                           │
├─────────────────────────────────────────────────────────────┤
│  New Rich Components                                         │
│  ├── Poster Display Component                               │
│  ├── Similar Items Component                                │
│  ├── Visualization Components                                │
│  │   ├── Rating Timeline Chart                               │
│  │   ├── Rating Distribution Histogram                      │
│  │   ├── Genre Preference Chart                             │
│  │   └── Activity Heatmap                                   │
│  ├── Item Detail Component                                   │
│  └── Visual Enhancement Utilities                           │
├─────────────────────────────────────────────────────────────┤
│  Extended Business Logic                                     │
│  ├── Visualization Data Provider                            │
│  ├── Image Cache Manager                                    │
│  ├── Similarity Provider                                    │
│  └── Statistics Aggregator                                  │
├─────────────────────────────────────────────────────────────┤
│  Extended Backend Integration                                │
│  ├── Similarity API Wrapper                                 │
│  ├── Statistics API Wrapper                                 │
│  └── Image Provider                                         │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Image Cache Manager

**Purpose**: Manage movie poster loading, caching, and fallback handling

**Design Pattern**: Cache Pattern with Fallback Strategy

**Interface**:
```python
class ImageCacheManager:
    def __init__(self):
        self.poster_cache = {}
        self.placeholder_image = self._load_placeholder()
    
    def get_poster(self, movie_id: int) -> str:
        """Get poster URL or placeholder"""
        if movie_id in self.poster_cache:
            return self.poster_cache[movie_id]
        
        # Try to fetch poster (placeholder for now)
        poster_url = self._fetch_poster(movie_id)
        self.poster_cache[movie_id] = poster_url
        return poster_url
    
    def _fetch_poster(self, movie_id: int) -> str:
        """Fetch poster URL (placeholder implementation)"""
        # In production, this would call TMDB API or similar
        return self.placeholder_image
    
    def _load_placeholder(self) -> str:
        """Load placeholder image"""
        return "https://via.placeholder.com/300x450?text=No+Poster"
```

---

### 2. Similarity Provider

**Purpose**: Provide similarity data for "More like this" functionality

**Design Pattern**: Provider Pattern with Multiple Backend Support

**Interface**:
```python
class SimilarityProvider:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
    
    def get_similar_items(self, movie_id: int, k: int = 10) -> List[Dict]:
        """Get similar items using best available method"""
        # Try content similarity first
        content_model = self.model_manager.get_model('content')
        if hasattr(content_model, 'similar_items'):
            return self._get_content_similarity(content_model, movie_id, k)
        
        # Fallback to item-based CF similarity
        item_cf = self.model_manager.get_model('item_based_cf')
        if hasattr(item_cf, 'similar_items'):
            return self._get_cf_similarity(item_cf, movie_id, k)
        
        return []
    
    def _get_content_similarity(self, model, movie_id: int, k: int) -> List[Dict]:
        """Get content-based similar items"""
        similar_items = model.similar_items(movie_id, k)
        return [{'movie_id': mid, 'score': score} for mid, score in similar_items]
    
    def _get_cf_similarity(self, model, movie_id: int, k: int) -> List[Dict]:
        """Get collaborative filtering similar items"""
        # Implementation depends on CF model structure
        return []
```

---

### 3. Statistics Aggregator

**Purpose**: Aggregate user statistics for visualizations

**Design Pattern**: Aggregator Pattern with Lazy Computation

**Interface**:
```python
class StatisticsAggregator:
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
        self.cache = {}
    
    def get_rating_timeline(self, user_id: int) -> pd.DataFrame:
        """Get user rating timeline data"""
        cache_key = f'rating_timeline_{user_id}'
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        user_ratings = self.data_provider.ratings_df[
            self.data_provider.ratings_df['userId'] == user_id
        ].sort_values('timestamp')
        
        self.cache[cache_key] = user_ratings
        return user_ratings
    
    def get_rating_distribution(self, user_id: int) -> Dict:
        """Get user rating distribution"""
        user_ratings = self.data_provider.ratings_df[
            self.data_provider.ratings_df['userId'] == user_id
        ]
        
        distribution = user_ratings['rating'].value_counts().to_dict()
        return distribution
    
    def get_genre_preferences(self, user_id: int) -> Dict[str, float]:
        """Get user genre preferences"""
        user_ratings = self.data_provider.ratings_df[
            self.data_provider.ratings_df['userId'] == user_id
        ]
        
        genre_counts = {}
        for _, row in user_ratings.iterrows():
            movie_info = self.data_provider.get_movie_info(row['movieId'])
            for genre in movie_info['genres']:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        # Normalize to percentages
        total = sum(genre_counts.values())
        if total > 0:
            genre_prefs = {g: count/total for g, count in genre_counts.items()}
        else:
            genre_prefs = {}
        
        return genre_prefs
    
    def get_activity_heatmap(self, user_id: int) -> pd.DataFrame:
        """Get user activity heatmap data"""
        user_ratings = self.data_provider.ratings_df[
            self.data_provider.ratings_df['userId'] == user_id
        ]
        
        # Convert timestamp to datetime and extract hour/day
        user_ratings['datetime'] = pd.to_datetime(user_ratings['timestamp'], unit='s')
        user_ratings['hour'] = user_ratings['datetime'].dt.hour
        user_ratings['day'] = user_ratings['datetime'].dt.dayofweek
        
        # Create heatmap data
        heatmap_data = user_ratings.groupby(['day', 'hour']).size().unstack(fill_value=0)
        return heatmap_data
```

---

## Visualization Components

### 1. Rating Timeline Chart

**Purpose**: Display user rating history over time

**Implementation**:
```python
def render_rating_timeline(user_id: int, stats_aggregator: StatisticsAggregator):
    """Render rating timeline chart"""
    timeline_data = stats_aggregator.get_rating_timeline(user_id)
    
    if timeline_data.empty:
        st.info("No rating history available")
        return
    
    fig = px.line(
        timeline_data, 
        x='datetime', 
        y='rating',
        title='Rating History Timeline',
        labels={'datetime': 'Date', 'rating': 'Rating'}
    )
    
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Rating",
        yaxis=dict(tickmode='linear', tick0=0.5, dtick=0.5)
    )
    
    st.plotly_chart(fig, use_container_width=True)
```

### 2. Rating Distribution Histogram

**Purpose**: Display user rating distribution

**Implementation**:
```python
def render_rating_distribution(user_id: int, stats_aggregator: StatisticsAggregator):
    """Render rating distribution histogram"""
    distribution = stats_aggregator.get_rating_distribution(user_id)
    
    if not distribution:
        st.info("No rating distribution available")
        return
    
    fig = px.bar(
        x=list(distribution.keys()),
        y=list(distribution.values()),
        title='Rating Distribution',
        labels={'x': 'Rating', 'y': 'Count'}
    )
    
    fig.update_layout(
        xaxis_title="Rating",
        yaxis_title="Count"
    )
    
    st.plotly_chart(fig, use_container_width=True)
```

### 3. Genre Preference Chart

**Purpose**: Display user genre preferences

**Implementation**:
```python
def render_genre_preferences(user_id: int, stats_aggregator: StatisticsAggregator):
    """Render genre preference bar chart"""
    genre_prefs = stats_aggregator.get_genre_preferences(user_id)
    
    if not genre_prefs:
        st.info("No genre preferences available")
        return
    
    # Sort by preference
    sorted_genres = sorted(genre_prefs.items(), key=lambda x: x[1], reverse=True)
    
    fig = px.bar(
        x=[g for g, _ in sorted_genres],
        y=[p * 100 for _, p in sorted_genres],
        title='Genre Preferences',
        labels={'x': 'Genre', 'y': 'Preference %'}
    )
    
    fig.update_layout(
        xaxis_title="Genre",
        yaxis_title="Preference %"
    )
    
    st.plotly_chart(fig, use_container_width=True)
```

### 4. Activity Heatmap

**Purpose**: Display user activity patterns

**Implementation**:
```python
def render_activity_heatmap(user_id: int, stats_aggregator: StatisticsAggregator):
    """Render activity heatmap"""
    heatmap_data = stats_aggregator.get_activity_heatmap(user_id)
    
    if heatmap_data.empty:
        st.info("No activity data available")
        return
    
    fig = px.imshow(
        heatmap_data,
        title='Activity Heatmap (Day vs Hour)',
        labels=dict(x="Day of Week", y="Hour", color="Rating Count"),
        color_continuous_scale='Viridis'
    )
    
    st.plotly_chart(fig, use_container_width=True)
```

---

## Integration with Day 3 Morning

### Session State Extensions

Extend session state from Day 3 Morning:
```python
# Add to session state initialization
'poster_cache': {},
'similar_items_data': [],
'visualization_data': {},
'show_visualizations': False,
'show_similar_items': False
```

### Component Integration

Integrate new components into main Streamlit app:
```python
# In main app, after recommendation display
if st.session_state.get('show_visualizations', False):
    render_rating_timeline(selected_user_id, stats_aggregator)
    render_rating_distribution(selected_user_id, stats_aggregator)
    render_genre_preferences(selected_user_id, stats_aggregator)
    render_activity_heatmap(selected_user_id, stats_aggregator)

if st.session_state.get('show_similar_items', False):
    render_similar_items(selected_movie_id, similarity_provider)
```

---

## File Structure Extensions

```
Devnexes-RecoLab/
├── ui/
│   ├── visualization_components.py     # New: Visualization components
│   ├── image_manager.py               # New: Image cache manager
│   ├── similarity_provider.py          # New: Similarity provider
│   ├── statistics_aggregator.py        # New: Statistics aggregator
│   └── components/
│       ├── poster_display.py          # New: Poster display component
│       ├── similar_items.py           # New: Similar items component
│       ├── visualizations.py          # New: Visualization components
│       └── item_detail.py             # New: Item detail component
```

---

## Implementation Phases

### Phase 1: Image Handling (1 hour)
- Implement ImageCacheManager
- Create placeholder system
- Implement poster display component
- Add poster grid to recommendation display

### Phase 2: Similar Items (1 hour)
- Implement SimilarityProvider
- Create similar items component
- Add "More like this" functionality
- Integrate with recommendation display

### Phase 3: Visualizations (1.5 hours)
- Implement StatisticsAggregator
- Create rating timeline chart
- Create rating distribution histogram
- Create genre preference chart
- Create activity heatmap
- Add visualization panel to main app

### Phase 4: Polish and Integration (0.5 hours)
- Implement visual enhancements
- Add animated transitions
- Integrate all components
- Test and optimize performance

---

## Key Technical Decisions

### Decision-001: Placeholder Poster System
**Options Considered**:
1. TMDB API integration (complex, requires API key)
2. Placeholder system (chosen for simplicity)
3. Local poster database (manual maintenance)

**Rationale**: Placeholder system provides immediate functionality without external dependencies. Can be upgraded to TMDB API in production.

### Decision-002: Plotly for Visualizations
**Options Considered**:
1. Plotly (chosen - interactive, Streamlit native)
2. Matplotlib (static, less interactive)
3. Altair (declarative, less customization)

**Rationale**: Plotly provides best interactivity and Streamlit integration for rich visualizations.

### Decision-003: Similarity Method Selection
**Options Considered**:
1. Content similarity only
2. CF similarity only
3. Hybrid approach with fallback (chosen)

**Rationale**: Hybrid approach provides best results by using content similarity when available, falling back to CF similarity.

---

## Performance Optimization

### Image Caching
- Cache poster URLs in session state
- Lazy load posters on demand
- Implement placeholder fallbacks

### Chart Optimization
- Use Plotly's efficient rendering
- Cache aggregated statistics
- Lazy render charts when panel is expanded

### Similarity Computation
- Use pre-computed similarity matrices when available
- Cache similarity results
- Limit similar items to top-K results

---

## Testing Strategy

### Visual Testing
- Manual testing of all visualizations
- Cross-browser testing for chart rendering
- Responsive testing for different screen sizes

### Performance Testing
- Measure poster loading times
- Measure chart rendering times
- Identify performance bottlenecks

### Data Accuracy Testing
- Verify visualization data accuracy
- Test similarity computation accuracy
- Validate statistics aggregation

---

## Success Criteria

- [ ] All rich features implemented and functional
- [ ] Poster display works with fallback system
- [ ] Similar items view integrates with backend
- [ ] All visualizations render correctly
- [ ] Performance meets all targets
- [ ] Visual enhancements improve UX
- [ ] Architecture supports Day 4 enhancements
