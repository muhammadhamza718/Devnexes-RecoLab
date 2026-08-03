# Day 4 Morning: Cold-Start Onboarding UI - Implementation Plan

**Feature ID:** 007-day4-onboarding  
**Date:** 2026-08-03  
**Status:** Draft  
**Effort:** 4 hours (Day 4 Morning)

---

## Architecture Overview

The cold-start onboarding UI extends the Day 3 UI foundation with a wizard-based onboarding flow that integrates with the existing ColdStartHandler protocol. The architecture follows the module pattern established in Day 3, with onboarding as a separate toggleable module.

### System Architecture Extension

```
┌─────────────────────────────────────────────────────────────┐
│                    Onboarding Module                          │
├─────────────────────────────────────────────────────────────┤
│  Onboarding Components                                       │
│  ├── Onboarding Wizard Controller                           │
│  ├── Genre Selection Component                              │
│  ├── Liked-Movies Component                                 │
│  ├── Preference Confirmation Component                      │
│  └── Onboarding State Manager                               │
├─────────────────────────────────────────────────────────────┤
│  Extended Business Logic                                     │
│  ├── Genre Provider                                          │
│  ├── Movie Search Provider                                   │
│  ├── Preference Validator                                    │
│  └── Onboarding Recommender                                  │
├─────────────────────────────────────────────────────────────┤
│  Extended Backend Integration                                │
│  ├── ColdStartHandler API Wrapper                            │
│  ├── Preference API Wrapper                                  │
│  └── Recommendation Generator                                │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Onboarding Wizard Controller

**Purpose**: Manage multi-step onboarding flow with state transitions

**Design Pattern**: State Machine Pattern with Wizard Controller

**Interface**:
```python
class OnboardingWizard:
    def __init__(self, session_manager: SessionStateManager):
        self.session_manager = session_manager
        self.steps = ['genre_selection', 'liked_movies', 'confirmation']
        self.current_step = 0
    
    def next_step(self):
        """Advance to next step with validation"""
        if self.can_proceed():
            self.current_step = min(self.current_step + 1, len(self.steps) - 1)
            self.session_manager.update_state('onboarding_step', self.current_step)
    
    def previous_step(self):
        """Go back to previous step"""
        self.current_step = max(self.current_step - 1, 0)
        self.session_manager.update_state('onboarding_step', self.current_step)
    
    def can_proceed(self) -> bool:
        """Validate current step before proceeding"""
        current_step_name = self.steps[self.current_step]
        if current_step_name == 'genre_selection':
            return len(self.session_manager.get_state('selected_genres', [])) > 0
        elif current_step_name == 'liked_movies':
            return True  # Liked movies is optional
        return True
    
    def skip_onboarding(self):
        """Skip onboarding with default preferences"""
        self.session_manager.update_state('selected_genres', self._get_default_genres())
        self.session_manager.update_state('liked_movies', [])
        self.session_manager.update_state('onboarding_complete', True)
    
    def complete_onboarding(self):
        """Complete onboarding and generate recommendations"""
        self.session_manager.update_state('onboarding_complete', True)
        self._generate_preference_recommendations()
    
    def _get_default_genres(self) -> List[str]:
        """Get default popular genres"""
        return ['Action', 'Comedy', 'Drama']
    
    def _generate_preference_recommendations(self):
        """Generate recommendations based on preferences"""
        genres = self.session_manager.get_state('selected_genres', [])
        liked_movies = self.session_manager.get_state('liked_movies', [])
        # Call backend cold-start API
        # recommendations = cold_start_handler.recommend_cold_start(genres, liked_movies, k=10)
        # self.session_manager.update_state('recommendations', recommendations)
```

---

### 2. Genre Provider

**Purpose**: Extract and manage genre data with popularity metrics

**Design Pattern**: Provider Pattern with Caching

**Interface**:
```python
class GenreProvider:
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
        self.genre_cache = None
    
    def get_all_genres(self) -> List[str]:
        """Get all unique genres from movies dataset"""
        if self.genre_cache is not None:
            return self.genre_cache
        
        movies_df = self.data_provider.movies_df
        all_genres = set()
        for genres in movies_df['genres']:
            if isinstance(genres, str):
                all_genres.update(genres.split('|'))
        
        self.genre_cache = sorted(list(all_genres))
        return self.genre_cache
    
    def get_genre_popularity(self) -> Dict[str, int]:
        """Get genre popularity metrics"""
        movies_df = self.data_provider.movies_df
        genre_counts = {}
        
        for genres in movies_df['genres']:
            if isinstance(genres, str):
                for genre in genres.split('|'):
                    genre_counts[genre] = genre_counts.get(genre, 0) + 1
        
        return genre_counts
    
    def get_suggested_combinations(self) -> List[List[str]]:
        """Get suggested genre combinations"""
        popular_genres = sorted(self.get_genre_popularity().items(), 
                              key=lambda x: x[1], reverse=True)[:5]
        top_genres = [g for g, _ in popular_genres]
        
        return [
            top_genres[:2],
            top_genres[1:3],
            top_genres[:3],
            ['Action', 'Comedy'],
            ['Drama', 'Romance']
        ]
```

---

### 3. Movie Search Provider

**Purpose**: Provide movie search functionality with efficient lookup

**Design Pattern**: Search Provider with Indexing

**Interface**:
```python
class MovieSearchProvider:
    def __init__(self, data_provider: DataProvider):
        self.data_provider = data_provider
        self.search_index = None
        self._build_search_index()
    
    def _build_search_index(self):
        """Build search index for efficient movie lookup"""
        movies_df = self.data_provider.movies_df
        self.search_index = movies_df.copy()
        # Create searchable title field
        self.search_index['search_title'] = movies_df['title'].str.lower()
    
    def search_movies(self, query: str, limit: int = 10) -> List[Dict]:
        """Search movies by title"""
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
    
    def get_movie_preview(self, movie_id: int) -> Dict:
        """Get movie preview information"""
        movie_info = self.data_provider.get_movie_info(movie_id)
        return {
            'movie_id': movie_id,
            'title': movie_info['title'],
            'genres': movie_info['genres'],
            'year': movie_info.get('year')
        }
```

---

### 4. Preference Validator

**Purpose**: Validate user preferences before submission

**Design Pattern**: Validator Pattern with Rule-Based Validation

**Interface**:
```python
class PreferenceValidator:
    def __init__(self, genre_provider: GenreProvider):
        self.genre_provider = genre_provider
    
    def validate_genres(self, genres: List[str]) -> Tuple[bool, List[str]]:
        """Validate genre selections"""
        available_genres = set(self.genre_provider.get_all_genres())
        invalid_genres = [g for g in genres if g not in available_genres]
        
        if invalid_genres:
            return False, [f"Invalid genres: {', '.join(invalid_genres)}"]
        
        if len(genres) == 0:
            return False, ["Please select at least one genre"]
        
        if len(genres) > 5:
            return False, ["Please select no more than 5 genres"]
        
        return True, []
    
    def validate_liked_movies(self, movie_ids: List[int]) -> Tuple[bool, List[str]]:
        """Validate liked movie selections"""
        if len(movie_ids) > 10:
            return False, ["Please select no more than 10 liked movies"]
        
        return True, []
    
    def validate_preferences(self, preferences: Dict) -> Tuple[bool, List[str]]:
        """Validate complete preference set"""
        genres = preferences.get('genres', [])
        liked_movies = preferences.get('liked_movies', [])
        
        genre_valid, genre_errors = self.validate_genres(genres)
        if not genre_valid:
            return False, genre_errors
        
        movies_valid, movie_errors = self.validate_liked_movies(liked_movies)
        if not movies_valid:
            return False, movie_errors
        
        return True, []
```

---

## Wizard Step Components

### Step 1: Genre Selection

**Implementation**:
```python
def render_genre_selection_step(wizard: OnboardingWizard, genre_provider: GenreProvider):
    """Render genre selection step"""
    st.subheader("Step 1: Select Your Favorite Genres")
    
    all_genres = genre_provider.get_all_genres()
    genre_popularity = genre_provider.get_genre_popularity()
    
    # Multi-select genre picker
    selected_genres = st.multiselect(
        "Select genres you enjoy",
        options=all_genres,
        default=st.session_state.get('selected_genres', []),
        format_func=lambda x: f"{x} ({genre_popularity.get(x, 0)} movies)"
    )
    
    st.session_state.selected_genres = selected_genres
    
    # Suggested combinations
    if not selected_genres:
        st.write("Or try these popular combinations:")
        suggestions = genre_provider.get_suggested_combinations()
        for i, combo in enumerate(suggestions):
            if st.button(f"{' + '.join(combo)}", key=f"suggestion_{i}"):
                st.session_state.selected_genres = combo
                st.rerun()
    
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Skip to Defaults"):
            wizard.skip_onboarding()
    with col2:
        if st.button("Back", disabled=True):
            pass
    with col3:
        if st.button("Next", disabled=len(selected_genres) == 0):
            wizard.next_step()
            st.rerun()
```

### Step 2: Liked-Movies Input

**Implementation**:
```python
def render_liked_movies_step(wizard: OnboardingWizard, search_provider: MovieSearchProvider):
    """Render liked-movies input step"""
    st.subheader("Step 2: Select Movies You Like (Optional)")
    
    # Movie search
    search_query = st.text_input("Search for movies you enjoy")
    
    if search_query:
        results = search_provider.search_movies(search_query)
        if results:
            st.write("Search results:")
            for movie in results:
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.write(f"**{movie['title']}** ({', '.join(movie['genres'])})")
                with col2:
                    if st.button("Add", key=f"add_{movie['movie_id']}"):
                        liked_movies = st.session_state.get('liked_movies', [])
                        if movie['movie_id'] not in liked_movies:
                            liked_movies.append(movie['movie_id'])
                            st.session_state.liked_movies = liked_movies
                            st.rerun()
        else:
            st.info("No movies found")
    
    # Display selected liked movies
    liked_movies = st.session_state.get('liked_movies', [])
    if liked_movies:
        st.write("Your selected movies:")
        for movie_id in liked_movies:
            preview = search_provider.get_movie_preview(movie_id)
            col1, col2 = st.columns([4, 1])
            with col1:
                st.write(f"**{preview['title']}**")
            with col2:
                if st.button("Remove", key=f"remove_{movie_id}"):
                    st.session_state.liked_movies.remove(movie_id)
                    st.rerun()
    
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Skip This Step"):
            pass  # Just proceed without liked movies
    with col2:
        if st.button("Back"):
            wizard.previous_step()
            st.rerun()
    with col3:
        if st.button("Next"):
            wizard.next_step()
            st.rerun()
```

### Step 3: Confirmation

**Implementation**:
```python
def render_confirmation_step(wizard: OnboardingWizard, genre_provider: GenreProvider):
    """Render preference confirmation step"""
    st.subheader("Step 3: Confirm Your Preferences")
    
    selected_genres = st.session_state.get('selected_genres', [])
    liked_movies = st.session_state.get('liked_movies', [])
    
    # Display preferences summary
    st.write("Your preferences:")
    st.write(f"**Genres:** {', '.join(selected_genres)}")
    if liked_movies:
        st.write(f"**Liked Movies:** {len(liked_movies)} movies selected")
    else:
        st.write("**Liked Movies:** None selected")
    
    # Preview recommendations
    st.write("Generating your personalized recommendations...")
    # Call backend cold-start API here
    # recommendations = cold_start_handler.recommend_cold_start(selected_genres, liked_movies, k=5)
    # st.write("Preview of your recommendations:")
    # for rec in recommendations:
    #     st.write(f"- {rec['title']}")
    
    # Navigation buttons
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("Edit Preferences"):
            wizard.current_step = 0
            st.rerun()
    with col2:
        if st.button("Back"):
            wizard.previous_step()
            st.rerun()
    with col3:
        if st.button("Complete Onboarding"):
            wizard.complete_onboarding()
            st.rerun()
```

---

## Session State Extensions

### Extended Session State
```python
# Add to session state initialization
'onboarding_active': bool,
'onboarding_step': int,  # Current wizard step (0, 1, 2)
'onboarding_complete': bool,
'selected_genres': List[str],
'liked_movies': List[int],
'onboarding_preferences': Dict[str, Any],
'onboarding_timestamp': str
```

---

## File Structure Extensions

```
Devnexes-RecoLab/
├── ui/
│   ├── onboarding/
│   │   ├── __init__.py
│   │   ├── wizard_controller.py       # Onboarding wizard controller
│   │   ├── genre_provider.py          # Genre data provider
│   │   ├── movie_search_provider.py   # Movie search provider
│   │   ├── preference_validator.py    # Preference validation
│   │   └── components/
│   │       ├── genre_selection.py     # Genre selection component
│   │       ├── liked_movies.py        # Liked-movies component
│   │       └── confirmation.py        # Confirmation component
```

---

## Implementation Phases

### Phase 1: Foundation (1 hour)
- Implement OnboardingWizard controller
- Create GenreProvider for genre data
- Create MovieSearchProvider for search functionality
- Implement PreferenceValidator
- Extend session state for onboarding

### Phase 2: Wizard Components (1.5 hours)
- Implement genre selection component
- Implement liked-movies component
- Implement confirmation component
- Create wizard navigation logic
- Add step validation

### Phase 3: Backend Integration (1 hour)
- Integrate with ColdStartHandler protocol
- Implement cold-start recommendation generation
- Add preference parameter passing
- Implement error handling for cold-start failures
- Add fallback mechanisms

### Phase 4: Integration and Testing (0.5 hours)
- Integrate onboarding into main application
- Test complete onboarding workflow
- Test skip functionality
- Test preference modification
- Performance testing

---

## Key Technical Decisions

### Decision-001: Wizard vs. Single Form
**Options Considered**:
1. Multi-step wizard (chosen)
2. Single long form
3. Progressive disclosure

**Rationale**: Multi-step wizard reduces cognitive load, provides clear progress indication, and allows for validation at each step.

### Decision-002: Optional Liked-Movies
**Options Considered**:
1. Required liked-movies input
2. Optional liked-movies input (chosen)
3. Skip liked-movies entirely

**Rationale**: Optional liked-movies reduces onboarding friction while still allowing for enhanced personalization when available.

### Decision-003: Default Preferences
**Options Considered**:
1. No defaults, require user input
2. Popular genre defaults (chosen)
3. Random defaults

**Rationale**: Popular genre defaults provide sensible recommendations while allowing users to proceed quickly if desired.

---

## Backend Integration Strategy

### ColdStartHandler Protocol Integration

```python
class OnboardingRecommender:
    def __init__(self, model_manager: ModelManager):
        self.model_manager = model_manager
    
    def generate_cold_start_recommendations(
        self, 
        genres: List[str], 
        liked_movies: List[int], 
        k: int = 10
    ) -> List[Dict]:
        """Generate recommendations using cold-start handler"""
        try:
            # Try hybrid recommender first
            hybrid = self.model_manager.get_model('hybrid')
            if hasattr(hybrid, 'recommend_cold_start'):
                recommendations = hybrid.recommend_cold_start(genres, liked_movies, k)
                return self._format_recommendations(recommendations)
            
            # Fallback to content model
            content = self.model_manager.get_model('content')
            if hasattr(content, 'recommend_cold_start'):
                recommendations = content.recommend_cold_start(genres, liked_movies, k)
                return self._format_recommendations(recommendations)
            
            # Final fallback to popularity
            popularity = self.model_manager.get_model('popularity')
            recommendations = popularity.recommend(user_id=None, k=k)
            return self._format_recommendations(recommendations)
            
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")
            return []
    
    def _format_recommendations(self, recommendations: List[int]) -> List[Dict]:
        """Format recommendations for display"""
        formatted = []
        for movie_id in recommendations:
            movie_info = self.data_provider.get_movie_info(movie_id)
            formatted.append({
                'movie_id': movie_id,
                'title': movie_info['title'],
                'genres': movie_info['genres'],
                'year': movie_info.get('year')
            })
        return formatted
```

---

## Success Criteria

- [ ] Onboarding wizard implemented with all steps
- [ ] Genre selection works with popularity indicators
- [ ] Movie search functionality works correctly
- [ ] Liked-movies management works
- [ ] ColdStartHandler integration works
- [ ] Preference-based recommendations generate correctly
- [ ] Skip functionality works with defaults
- [ ] Session management handles all scenarios
- [ ] Performance meets all targets
- [ ] Architecture supports Day 4 enhancements
