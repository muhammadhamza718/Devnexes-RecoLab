# Day 3 Afternoon: Rich UI Features - Quickstart Guide

**Feature ID:** 006-day3-ui-rich  
**Date:** 2026-08-03  
**Status:** Draft

---

## Prerequisites

### System Requirements
- Day 3 Morning core UI structure completed
- Streamlit application running locally
- All backend models loaded and functional
- Plotly library installed for visualizations

### Additional Dependencies
```bash
# Add to pyproject.toml
plotly>=5.17.0
Pillow>=10.0.0  # For image processing
```

Install dependencies:
```bash
pip install plotly Pillow
```

---

## Quick Start

### 1. Extend Session State

Update `ui/session_manager.py` to add rich feature state:
```python
def initialize_state(self):
    # Existing Day 3 Morning state...
    
    # Add rich feature extensions
    if 'poster_cache' not in st.session_state:
        st.session_state.poster_cache = {}
    if 'similar_items_data' not in st.session_state:
        st.session_state.similar_items_data = []
    if 'visualization_data' not in st.session_state:
        st.session_state.visualization_data = {}
    if 'show_visualizations' not in st.session_state:
        st.session_state.show_visualizations = False
    if 'show_similar_items' not in st.session_state:
        st.session_state.show_similar_items = False
```

### 2. Create Image Manager

Create `ui/image_manager.py`:
```python
class ImageCacheManager:
    def __init__(self):
        self.poster_cache = {}
        self.placeholder_image = "https://via.placeholder.com/300x450?text=No+Poster"
    
    def get_poster(self, movie_id: int) -> str:
        if movie_id in self.poster_cache:
            return self.poster_cache[movie_id]
        
        # Use placeholder for now
        self.poster_cache[movie_id] = self.placeholder_image
        return self.placeholder_image
```

### 3. Create Similarity Provider

Create `ui/similarity_provider.py`:
```python
class SimilarityProvider:
    def __init__(self, model_manager):
        self.model_manager = model_manager
    
    def get_similar_items(self, movie_id: int, k: int = 10):
        content_model = self.model_manager.get_model('content')
        if hasattr(content_model, 'similar_items'):
            similar = content_model.similar_items(movie_id, k)
            return [{'movie_id': mid, 'score': score} for mid, score in similar]
        return []
```

### 4. Create Statistics Aggregator

Create `ui/statistics_aggregator.py`:
```python
class StatisticsAggregator:
    def __init__(self, data_provider):
        self.data_provider = data_provider
        self.cache = {}
    
    def get_rating_timeline(self, user_id: int):
        cache_key = f'rating_timeline_{user_id}'
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        user_ratings = self.data_provider.ratings_df[
            self.data_provider.ratings_df['userId'] == user_id
        ].sort_values('timestamp')
        
        self.cache[cache_key] = user_ratings
        return user_ratings
    
    def get_rating_distribution(self, user_id: int):
        user_ratings = self.data_provider.ratings_df[
            self.data_provider.ratings_df['userId'] == user_id
        ]
        return user_ratings['rating'].value_counts().to_dict()
    
    def get_genre_preferences(self, user_id: int):
        user_ratings = self.data_provider.ratings_df[
            self.data_provider.ratings_df['userId'] == user_id
        ]
        
        genre_counts = {}
        for _, row in user_ratings.iterrows():
            movie_info = self.data_provider.get_movie_info(row['movieId'])
            for genre in movie_info['genres']:
                genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        total = sum(genre_counts.values())
        if total > 0:
            return {g: count/total for g, count in genre_counts.items()}
        return {}
```

### 5. Add Visualization Components

Create `ui/visualization_components.py`:
```python
import plotly.express as px

def render_rating_timeline(user_id: int, stats_aggregator):
    timeline_data = stats_aggregator.get_rating_timeline(user_id)
    if timeline_data.empty:
        st.info("No rating history available")
        return
    
    fig = px.line(timeline_data, x='timestamp', y='rating',
                  title='Rating History Timeline')
    st.plotly_chart(fig, use_container_width=True)

def render_rating_distribution(user_id: int, stats_aggregator):
    distribution = stats_aggregator.get_rating_distribution(user_id)
    if not distribution:
        st.info("No rating distribution available")
        return
    
    fig = px.bar(x=list(distribution.keys()), y=list(distribution.values()),
                  title='Rating Distribution')
    st.plotly_chart(fig, use_container_width=True)

def render_genre_preferences(user_id: int, stats_aggregator):
    genre_prefs = stats_aggregator.get_genre_preferences(user_id)
    if not genre_prefs:
        st.info("No genre preferences available")
        return
    
    sorted_genres = sorted(genre_prefs.items(), key=lambda x: x[1], reverse=True)
    fig = px.bar(x=[g for g, _ in sorted_genres], 
                  y=[p * 100 for _, p in sorted_genres],
                  title='Genre Preferences')
    st.plotly_chart(fig, use_container_width=True)
```

### 6. Integrate into Main Application

Update `streamlit_app.py` to add rich features:
```python
from ui.image_manager import ImageCacheManager
from ui.similarity_provider import SimilarityProvider
from ui.statistics_aggregator import StatisticsAggregator
from ui.visualization_components import (
    render_rating_timeline, render_rating_distribution, render_genre_preferences
)

# In main function, after initialization
image_manager = ImageCacheManager()
similarity_provider = SimilarityProvider(model_manager)
stats_aggregator = StatisticsAggregator(data_provider)

# Add visualization toggle in sidebar
with st.sidebar:
    st.divider()
    st.subheader("Rich Features")
    show_viz = st.checkbox("Show Visualizations", value=False)
    show_similar = st.checkbox("Show Similar Items", value=False)

# In main content area
if show_viz:
    st.subheader("User Statistics")
    col1, col2 = st.columns(2)
    with col1:
        render_rating_timeline(selected_user_id, stats_aggregator)
        render_rating_distribution(selected_user_id, stats_aggregator)
    with col2:
        render_genre_preferences(selected_user_id, stats_aggregator)

if show_similar and selected_movie_id:
    st.subheader("Similar Items")
    similar_items = similarity_provider.get_similar_items(selected_movie_id)
    for item in similar_items:
        st.write(f"Movie {item['movie_id']}: {item['score']:.2f}")
```

---

## Component Usage Examples

### Image Cache Manager
```python
from ui.image_manager import ImageCacheManager

image_manager = ImageCacheManager()
poster_url = image_manager.get_poster(123)
st.image(poster_url, width=200)
```

### Similarity Provider
```python
from ui.similarity_provider import SimilarityProvider

similarity_provider = SimilarityProvider(model_manager)
similar_items = similarity_provider.get_similar_items(456, k=10)
```

### Statistics Aggregator
```python
from ui.statistics_aggregator import StatisticsAggregator

stats_aggregator = StatisticsAggregator(data_provider)
timeline = stats_aggregator.get_rating_timeline(user_id)
distribution = stats_aggregator.get_rating_distribution(user_id)
preferences = stats_aggregator.get_genre_preferences(user_id)
```

---

## Common Workflows

### View User Statistics
1. Select user ID from dropdown
2. Enable "Show Visualizations" checkbox
3. View rating timeline, distribution, and genre preferences
4. Charts update when user selection changes

### View Similar Items
1. Select a movie from recommendations
2. Enable "Show Similar Items" checkbox
3. View similar items with similarity scores
4. Navigate back to recommendations

### Handle Missing Posters
1. System automatically uses placeholder images
2. Loading states show during poster fetching
3. Fallback mechanisms handle loading failures
4. Text-only display if image system fails

---

## Testing the Features

### Manual Testing Checklist

- [ ] Posters display with placeholder system
- [ ] Similar items view works with backend integration
- [ ] Rating timeline chart displays correctly
- [ ] Rating distribution histogram displays correctly
- [ ] Genre preference chart displays correctly
- [ ] Visual enhancements improve user experience
- [ ] Performance meets all targets

### Performance Testing

```python
import time

# Test poster loading
start = time.time()
poster = image_manager.get_poster(123)
load_time = time.time() - start
st.write(f"Poster load time: {load_time:.2f}s")

# Test similarity computation
start = time.time()
similar_items = similarity_provider.get_similar_items(456, k=10)
sim_time = time.time() - start
st.write(f"Similarity computation time: {sim_time:.2f}s")

# Test statistics aggregation
start = time.time()
timeline = stats_aggregator.get_rating_timeline(123)
stats_time = time.time() - start
st.write(f"Statistics aggregation time: {stats_time:.2f}s")
```

---

## Troubleshooting

### Issue: Posters Not Displaying

**Solution**: 
- Check image manager implementation
- Verify placeholder image URL is accessible
- Check network connectivity for external images

### Issue: Similar Items Not Working

**Solution**:
- Verify backend models have similarity methods
- Check similarity provider implementation
- Test with different movie IDs

### Issue: Charts Not Rendering

**Solution**:
- Verify Plotly installation
- Check data format for charts
- Verify statistics aggregation is working
- Check browser console for errors

### Issue: Performance Issues

**Solution**:
- Implement caching for expensive operations
- Limit chart data points
- Use lazy loading for visualizations
- Optimize image sizes

---

## Architecture Integration Points

### Backend Integration

The rich features integrate with existing backend through these entry points:

```python
# Similarity computation
from recolab.content import ContentModel
model = ContentModel.from_bundle(bundle)
similar_items = model.similar_items(movie_id, k=10)

# Statistics aggregation
ratings_df = pd.read_csv('data/ratings.csv')
user_stats = ratings_df[ratings_df['userId'] == user_id]
```

### Data Access

The rich features access data through these methods:

```python
# User rating data
ratings_df = pd.read_csv('data/ratings.csv')
user_timeline = ratings_df[ratings_df['userId'] == user_id]

# Movie metadata
movies_df = pd.read_csv('data/movies.csv')
movie_genres = movies_df[movies_df['movieId'] == movie_id]['genres']
```

---

## Extension Points

### Adding New Visualizations

1. Create new visualization function in `ui/visualization_components.py`
2. Add aggregation method to `StatisticsAggregator`
3. Integrate into main application
4. Add toggle in sidebar

### Adding New Similarity Methods

1. Add new similarity method to `SimilarityProvider`
2. Update fallback logic
3. Test with different movie IDs
4. Update UI with new similarity type

### Adding Enhanced Poster System

1. Implement TMDB API integration
2. Replace placeholder system with real posters
3. Add poster metadata (year, resolution, etc.)
4. Update poster display component

---

## Performance Optimization Tips

### Image Optimization
- Cache poster URLs in session state
- Use placeholder images initially
- Lazy load posters on demand
- Limit poster image sizes

### Chart Optimization
- Cache aggregated statistics
- Limit chart data points
- Use efficient chart types
- Lazy render charts when panel expanded

### Similarity Optimization
- Use pre-computed similarity matrices
- Cache similarity results
- Limit similar items to top-K
- Use efficient similarity methods

---

## Security Considerations

### External API Security
- If using TMDB API, secure API keys
- Implement rate limiting
- No sensitive data in URLs

### Data Privacy
- User data used only for visualizations
- No personal information exposed
- Session state doesn't persist sensitive data

---

## Deployment Considerations

### Local Development
- Rich features work locally with Day 3 Morning foundation
- No additional deployment requirements
- All data available from local files

### Streamlit Cloud Deployment
- Package additional dependencies (plotly, Pillow)
- Upload data files with application
- Configure resource limits for visualizations
- Test chart rendering in cloud environment

---

## Next Steps

After completing Day 3 Afternoon:

1. **Day 4 Morning**: Implement cold-start onboarding flow
2. **Day 4 Afternoon**: Add advanced features (dashboard, model comparison)
3. **Testing**: Comprehensive testing of all features
4. **Documentation**: Update user guides and technical documentation
5. **Performance**: Optimize based on testing results
