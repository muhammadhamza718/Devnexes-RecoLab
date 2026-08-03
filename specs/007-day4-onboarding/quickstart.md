# Day 4 Morning: Cold-Start Onboarding UI - Quickstart Guide

**Feature ID:** 007-day4-onboarding  
**Date:** 2026-08-03  
**Status:** Draft

---

## Prerequisites

### System Requirements
- Day 3 complete (Core UI + Rich Features)
- Streamlit application running locally
- ColdStartHandler protocol implemented in backend
- Complete movies.csv with genre information

### Backend Requirements
- ContentModel with recommend_cold_start() method
- HybridRecommender with cold-start support (optional)
- PopularityModel as fallback

---

## Quick Start

### 1. Extend Session State

Update `ui/session_manager.py` to add onboarding state:
```python
def initialize_state(self):
    # Existing Day 3 state...
    
    # Add onboarding extensions
    if 'onboarding_active' not in st.session_state:
        st.session_state.onboarding_active = False
    if 'onboarding_step' not in st.session_state:
        st.session_state.onboarding_step = 0
    if 'onboarding_complete' not in st.session_state:
        st.session_state.onboarding_complete = False
    if 'selected_genres' not in st.session_state:
        st.session_state.selected_genres = []
    if 'liked_movies' not in st.session_state:
        st.session_state.liked_movies = []
```

### 2. Create Onboarding Wizard

Create `ui/onboarding/wizard_controller.py`:
```python
class OnboardingWizard:
    def __init__(self, session_manager):
        self.session_manager = session_manager
        self.steps = ['genre_selection', 'liked_movies', 'confirmation']
        self.current_step = 0
    
    def next_step(self):
        if self.can_proceed():
            self.current_step = min(self.current_step + 1, len(self.steps) - 1)
            self.session_manager.update_state('onboarding_step', self.current_step)
    
    def can_proceed(self):
        current_step_name = self.steps[self.current_step]
        if current_step_name == 'genre_selection':
            return len(self.session_manager.get_state('selected_genres', [])) > 0
        return True
    
    def skip_onboarding(self):
        self.session_manager.update_state('selected_genres', ['Action', 'Comedy', 'Drama'])
        self.session_manager.update_state('liked_movies', [])
        self.session_manager.update_state('onboarding_complete', True)
```

### 3. Create Genre Provider

Create `ui/onboarding/genre_provider.py`:
```python
class GenreProvider:
    def __init__(self, data_provider):
        self.data_provider = data_provider
        self.genre_cache = None
    
    def get_all_genres(self):
        if self.genre_cache is not None:
            return self.genre_cache
        
        movies_df = self.data_provider.movies_df
        all_genres = set()
        for genres in movies_df['genres']:
            if isinstance(genres, str):
                all_genres.update(genres.split('|'))
        
        self.genre_cache = sorted(list(all_genres))
        return self.genre_cache
    
    def get_genre_popularity(self):
        movies_df = self.data_provider.movies_df
        genre_counts = {}
        for genres in movies_df['genres']:
            if isinstance(genres, str):
                for genre in genres.split('|'):
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
        return genre_counts
```

### 4. Create Movie Search Provider

Create `ui/onboarding/movie_search_provider.py`:
```python
class MovieSearchProvider:
    def __init__(self, data_provider):
        self.data_provider = data_provider
        self._build_search_index()
    
    def _build_search_index(self):
        movies_df = self.data_provider.movies_df
        self.search_index = movies_df.copy()
        self.search_index['search_title'] = movies_df['title'].str.lower()
    
    def search_movies(self, query, limit=10):
        if not query or len(query) < 2:
            return []
        
        query_lower = query.lower()
        matches = self.search_index[
            self.search_index['search_title'].str.contains(query_lower, na=False)
        ].head(limit)
        
        return [
            {
                'movie_id': row['movieId'],
                'title': row['title'],
                'genres': row['genres'].split('|') if isinstance(row['genres'], str) else []
            }
            for _, row in matches.iterrows()
        ]
```

### 5. Integrate into Main Application

Update `streamlit_app.py` to add onboarding:
```python
from ui.onboarding.wizard_controller import OnboardingWizard
from ui.onboarding.genre_provider import GenreProvider
from ui.onboarding.movie_search_provider import MovieSearchProvider

# In main function, after initialization
wizard = OnboardingWizard(session_manager)
genre_provider = GenreProvider(data_provider)
search_provider = MovieSearchProvider(data_provider)

# Add onboarding entry point
if st.session_state.get('onboarding_active', False):
    render_onboarding_wizard(wizard, genre_provider, search_provider)
else:
    # Check if user is cold-start
    user_profile = data_provider.get_user_profile(selected_user_id)
    if user_profile['activity_level'] == 'cold-start':
        if st.button("Start Personalization"):
            st.session_state.onboarding_active = True
            st.rerun()
```

### 6. Create Onboarding Render Function

Create `ui/onboarding/components/onboarding_render.py`:
```python
def render_onboarding_wizard(wizard, genre_provider, search_provider):
    st.title("Welcome! Let's personalize your recommendations")
    
    current_step = st.session_state.get('onboarding_step', 0)
    
    # Progress indicator
    progress = (current_step + 1) / 3
    st.progress(progress)
    st.write(f"Step {current_step + 1} of 3")
    
    # Render current step
    if current_step == 0:
        render_genre_selection(wizard, genre_provider)
    elif current_step == 1:
        render_liked_movies(wizard, search_provider)
    elif current_step == 2:
        render_confirmation(wizard, genre_provider)
```

---

## Component Usage Examples

### Onboarding Wizard
```python
from ui.onboarding.wizard_controller import OnboardingWizard

wizard = OnboardingWizard(session_manager)
wizard.next_step()  # Advance to next step
wizard.previous_step()  # Go back
wizard.skip_onboarding()  # Skip with defaults
```

### Genre Provider
```python
from ui.onboarding.genre_provider import GenreProvider

genre_provider = GenreProvider(data_provider)
all_genres = genre_provider.get_all_genres()
popularity = genre_provider.get_genre_popularity()
```

### Movie Search Provider
```python
from ui.onboarding.movie_search_provider import MovieSearchProvider

search_provider = MovieSearchProvider(data_provider)
results = search_provider.search_movies("Star Wars", limit=10)
```

---

## Common Workflows

### Complete Onboarding Flow
1. User clicks "Start Personalization"
2. Select favorite genres (at least one)
3. Optionally search and add liked movies
4. Review preferences and preview recommendations
5. Complete onboarding
6. View personalized recommendations

### Skip Onboarding Flow
1. User clicks "Skip to Defaults"
2. System selects popular genre defaults
3. Recommendations generated based on defaults
4. User can modify preferences later

### Modify Preferences After Onboarding
1. User clicks "Edit Preferences"
2. Returns to step 1 of wizard
3. Modify selections
4. Complete onboarding again
5. New recommendations generated

---

## Testing the Onboarding

### Manual Testing Checklist

- [ ] Onboarding entry point displays for cold-start users
- [ ] Genre selection works with multi-select
- [ ] Genre popularity indicators display correctly
- [ ] Suggested combinations work as quick-select
- [ ] Movie search returns relevant results
- [ ] Liked-movies management works correctly
- [ ] Confirmation step displays preferences correctly
- [ ] Cold-start recommendations generate correctly
- [ ] Skip functionality works with defaults
- [ ] Preference modification works after completion

### Backend Integration Testing

```python
# Test ColdStartHandler integration
from recolab.content import ContentModel

content_model = ContentModel.from_bundle(bundle)
recommendations = content_model.recommend_cold_start(
    genres=['Action', 'Comedy'],
    liked_movie_ids=[123, 456],
    k=10
)
print(f"Generated {len(recommendations)} recommendations")
```

---

## Troubleshooting

### Issue: Onboarding Not Triggering

**Solution**: 
- Check cold-start user detection logic
- Verify user activity level calculation
- Check onboarding_active session state

### Issue: Genre Selection Not Working

**Solution**:
- Verify genre provider returns genres correctly
- Check movies.csv has genre data
- Verify multi-select component configuration

### Issue: Movie Search Not Working

**Solution**:
- Check search index is built correctly
- Verify movies.csv has title data
- Check search query handling logic

### Issue: Cold-Start Recommendations Not Generating

**Solution**:
- Verify ColdStartHandler protocol implementation
- Check backend recommend_cold_start() method
- Verify parameter passing to backend
- Check error handling and fallback mechanisms

---

## Architecture Integration Points

### Backend Integration

The onboarding integrates with existing backend through these entry points:

```python
# Cold-start recommendation generation
from recolab.content import ContentModel
model = ContentModel.from_bundle(bundle)
recommendations = model.recommend_cold_start(genres, liked_movies, k=10)

# ColdStartHandler protocol
if hasattr(model, 'recommend_cold_start'):
    recommendations = model.recommend_cold_start(genres, liked_movies, k)
```

### Data Access

The onboarding accesses data through these methods:

```python
# Genre data extraction
movies_df = pd.read_csv('data/movies.csv')
genres = set()
for genre_list in movies_df['genres']:
    genres.update(genre_list.split('|'))

# Movie search
movies_df[movies_df['title'].str.contains(query, case=False)]
```

---

## Extension Points

### Adding New Onboarding Steps

1. Add step to OnboardingWizard.steps list
2. Create component for new step
3. Add validation logic for new step
4. Update progress indicator
5. Test complete workflow

### Adding New Preference Types

1. Extend preference data model
2. Add validation rules for new preference type
3. Create UI component for new preference
4. Integrate with ColdStartHandler API
5. Test with backend

### Enhancing Cold-Start Algorithm

1. Implement advanced cold-start in backend
2. Update parameter passing
3. Add preference weight optimization
4. Implement A/B testing for algorithms
5. Monitor recommendation quality

---

## Performance Optimization Tips

### Onboarding Performance
- Cache genre data and popularity metrics
- Implement lazy loading for movie search
- Optimize search index for faster lookups
- Limit search results to improve performance

### Backend Performance
- Use pre-computed genre similarity matrices
- Cache cold-start recommendations
- Implement efficient preference algorithms
- Optimize database queries for user data

### UI Performance
- Lazy render wizard steps
- Implement debouncing for search input
- Optimize component rendering
- Use efficient data structures

---

## Security Considerations

### User Privacy
- No personal information collected
- Preferences are session-based only
- No tracking of individual behavior
- Anonymous analytics only

### Input Validation
- Validate all user inputs
- Sanitize search queries
- Limit preference quantities
- Prevent injection attacks

### Data Minimization
- Collect only necessary preferences
- Session-only storage by default
- Clear session state on completion
- No persistent user tracking

---

## Deployment Considerations

### Local Development
- Onboarding works locally with Day 3 foundation
- No additional deployment requirements
- All data available from local files
- ColdStartHandler available locally

### Streamlit Cloud Deployment
- Package onboarding components with application
- Ensure ColdStartHandler works in cloud environment
- Test onboarding workflow in cloud
- Monitor performance metrics

---

## Next Steps

After completing Day 4 Morning:

1. **Day 4 Afternoon**: Add advanced features (dashboard, model comparison)
2. **Testing**: Comprehensive testing of all features
3. **Documentation**: Update user guides and technical documentation
4. **Performance**: Optimize based on testing results
5. **User Testing**: Conduct user testing for onboarding flow
