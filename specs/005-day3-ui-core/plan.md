# Day 3 Morning: Core UI Structure - Implementation Plan

**Feature ID:** 005-day3-ui-core  
**Date:** 2026-08-03  
**Status:** Draft  
**Effort:** 4 hours (Day 3 Morning)

---

## Architecture Overview

The core UI structure will be built using Streamlit as the primary framework, with a modular component architecture designed for extensibility. The application will follow a clear separation of concerns between UI presentation, business logic, and backend integration.

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Streamlit Application                       │
├─────────────────────────────────────────────────────────────┤
│  UI Layer (Components)                                        │
│  ├── User Selection Component                                │
│  ├── Model Selection Component                               │
│  ├── Recommendation Display Component                         │
│  └── Error Handling Component                                │
├─────────────────────────────────────────────────────────────┤
│  Business Logic Layer                                         │
│  ├── Session State Manager                                   │
│  ├── Model Manager                                            │
│  ├── Recommendation Controller                                │
│  └── Data Provider                                            │
├─────────────────────────────────────────────────────────────┤
│  Backend Integration Layer                                   │
│  ├── Model Loader                                             │
│  ├── Recommendation API Wrapper                               │
│  └── Data Access Layer                                        │
├─────────────────────────────────────────────────────────────┤
│  Backend Systems (Existing)                                   │
│  ├── HybridRecommender                                        │
│  ├── ContentModel                                             │
│  ├── UserBasedCF / ItemBasedCF                                │
│  ├── PopularityModel                                          │
│  └── Persistence Layer                                        │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Design

### 1. Session State Manager

**Purpose**: Centralized session state management with extensible architecture

**Design Pattern**: State Management Pattern with Extensible State Dictionary

**Interface**:
```python
class SessionStateManager:
    def __init__(self):
        self.initialize_state()
    
    def initialize_state(self):
        """Initialize session state with default values"""
        if 'selected_user_id' not in st.session_state:
            st.session_state.selected_user_id = None
        if 'selected_model' not in st.session_state:
            st.session_state.selected_model = 'hybrid'
        if 'model_params' not in st.session_state:
            st.session_state.model_params = {
                'alpha': 0.5,
                'k_similar': 20,
                'n_recommendations': 10
            }
        if 'recommendations' not in st.session_state:
            st.session_state.recommendations = []
        if 'user_profile' not in st.session_state:
            st.session_state.user_profile = {}
        # Extensible for future enhancements
    
    def update_state(self, key: str, value: Any):
        """Update a specific session state value"""
        st.session_state[key] = value
    
    def get_state(self, key: str) -> Any:
        """Get a specific session state value"""
        return st.session_state.get(key)
```

**Extensibility**: Designed to accommodate Day 3 Afternoon (visualizations, rich features) and Day 4 (onboarding, dashboard) additions without breaking changes.

---

### 2. Model Manager

**Purpose**: Centralized model loading, caching, and access

**Design Pattern**: Singleton Pattern with Lazy Loading

**Interface**:
```python
class ModelManager:
    def __init__(self):
        self.models = {}
        self.model_paths = {
            'popularity': 'data/models/popularity_model.bundle',
            'content': 'data/models/content_model.bundle',
            'user_based_cf': 'data/models/user_based_cf.bundle',
            'item_based_cf': 'data/models/item_based_cf.bundle',
            'hybrid': 'data/models/hybrid_recommender.bundle'
        }
    
    def load_model(self, model_name: str):
        """Load a specific model with lazy loading and caching"""
        if model_name not in self.models:
            with st.spinner(f"Loading {model_name} model..."):
                bundle = load_model_bundle(self.model_paths[model_name])
                self.models[model_name] = self._load_from_bundle(bundle, model_name)
        return self.models[model_name]
    
    def get_model(self, model_name: str):
        """Get a model, loading if necessary"""
        return self.load_model(model_name)
    
    def load_all_models(self):
        """Pre-load all models for performance"""
        for model_name in self.model_paths:
            self.load_model(model_name)
```

**Performance Strategy**: Load all models during initialization to avoid loading delays during user interactions.

---

### 3. Recommendation Controller

**Purpose**: Orchestrate recommendation generation with error handling

**Design Pattern**: Controller Pattern with Error Boundary

**Interface**:
```python
class RecommendationController:
    def __init__(self, model_manager: ModelManager, session_manager: SessionStateManager):
        self.model_manager = model_manager
        self.session_manager = session_manager
    
    def generate_recommendations(self, user_id: int, model_name: str, params: dict):
        """Generate recommendations with error handling"""
        try:
            model = self.model_manager.get_model(model_name)
            k = params.get('n_recommendations', 10)
            
            if model_name == 'hybrid':
                # Apply hybrid-specific parameters
                model.alpha = params.get('alpha', 0.5)
            elif model_name in ['user_based_cf', 'item_based_cf']:
                # Apply CF-specific parameters
                model.k_similar_users = params.get('k_similar', 20)
            
            recommendations = model.recommend(user_id=user_id, k=k)
            
            # Add explanations
            recommendations_with_explanations = []
            for movie_id in recommendations:
                explanation = model.explain(user_id, movie_id)
                recommendations_with_explanations.append({
                    'movie_id': movie_id,
                    'explanation': explanation
                })
            
            return recommendations_with_explanations
            
        except Exception as e:
            st.error(f"Error generating recommendations: {str(e)}")
            return []
```

---

### 4. Data Provider

**Purpose**: Centralized data access for movie metadata and user information

**Design Pattern**: Data Access Object Pattern

**Interface**:
```python
class DataProvider:
    def __init__(self):
        self.movies_df = None
        self.ratings_df = None
        self.load_data()
    
    def load_data(self):
        """Load movie and rating data"""
        self.movies_df = pd.read_csv('data/movies.csv')
        self.ratings_df = pd.read_csv('data/ratings.csv')
    
    def get_movie_info(self, movie_id: int) -> dict:
        """Get movie metadata"""
        movie = self.movies_df[self.movies_df['movieId'] == movie_id]
        if movie.empty:
            return {'title': f'Movie {movie_id}', 'genres': 'Unknown'}
        return {
            'title': movie.iloc[0]['title'],
            'genres': movie.iloc[0]['genres'],
            'year': self._extract_year(movie.iloc[0]['title'])
        }
    
    def get_user_profile(self, user_id: int) -> dict:
        """Get user profile information"""
        user_ratings = self.ratings_df[self.ratings_df['userId'] == user_id]
        rating_count = len(user_ratings)
        
        # Determine activity level
        if rating_count <= 5:
            activity_level = 'cold-start'
        elif rating_count <= 20:
            activity_level = 'intermediate'
        else:
            activity_level = 'active'
        
        return {
            'user_id': user_id,
            'rating_count': rating_count,
            'activity_level': activity_level
        }
    
    def get_all_user_ids(self) -> list:
        """Get all available user IDs"""
        return sorted(self.ratings_df['userId'].unique())
```

---

## Data Flow Architecture

### User Selection Flow
```
User Action → User Selection Component → SessionStateManager.update_state()
                                                     ↓
                                             DataProvider.get_user_profile()
                                                     ↓
                                             SessionStateManager.update_state()
                                                     ↓
                                             UI Display Update
```

### Model Selection Flow
```
User Action → Model Selection Component → SessionStateManager.update_state()
                                                     ↓
                                             ModelManager.get_model()
                                                     ↓
                                             UI Parameter Controls Update
```

### Recommendation Generation Flow
```
User Action → "Get Recommendations" → RecommendationController.generate_recommendations()
                                                     ↓
                                             ModelManager.get_model()
                                                     ↓
                                             model.recommend()
                                                     ↓
                                             model.explain() for each item
                                                     ↓
                                             DataProvider.get_movie_info()
                                                     ↓
                                             SessionStateManager.update_state()
                                                     ↓
                                             UI Display Update
```

---

## File Structure

```
Devnexes-RecoLab/
├── streamlit_app.py           # Main Streamlit application entry point
├── ui/
│   ├── __init__.py           # UI package initialization
│   ├── session_manager.py     # Session state management
│   ├── model_manager.py       # Model loading and caching
│   ├── recommendation_controller.py  # Recommendation orchestration
│   ├── data_provider.py       # Data access layer
│   ├── components/
│   │   ├── __init__.py
│   │   ├── user_selection.py      # User selection UI component
│   │   ├── model_selection.py     # Model selection UI component
│   │   ├── recommendation_display.py  # Recommendation display component
│   │   └── error_handling.py      # Error handling components
│   └── utils/
│       ├── __init__.py
│       ├── styling.py          # Consistent styling utilities
│       └── validators.py       # Input validation utilities
└── data/
    └── models/                # Saved model artifacts
```

---

## Implementation Phases

### Phase 1: Foundation (1 hour)
- Set up Streamlit project structure
- Create session state manager
- Implement data provider
- Set up basic layout with sidebar

### Phase 2: Model Integration (1 hour)
- Implement model manager with lazy loading
- Create model loader functionality
- Test all model loading scenarios
- Implement error handling for model failures

### Phase 3: UI Components (1.5 hours)
- Implement user selection component
- Implement model selection component
- Implement recommendation display component
- Implement error handling components

### Phase 4: Integration and Testing (0.5 hours)
- Integrate all components
- Test complete user workflows
- Performance testing
- Bug fixes and polish

---

## Key Technical Decisions

### Decision-001: Streamlit Framework Choice
**Options Considered**:
1. Streamlit (chosen)
2. Dash
3. Gradio
4. Custom Flask/FastAPI frontend

**Rationale**: Streamlit provides the fastest development time for data science applications, built-in component library, and requires minimal frontend expertise. It aligns with the accelerated timeline.

**Trade-offs**: Less customization compared to custom solutions, but sufficient for the project requirements.

---

### Decision-002: Session State Architecture
**Options Considered**:
1. Simple dictionary (chosen with extensibility)
2. Class-based state management
3. Database-backed session state

**Rationale**: Simple dictionary with extensible architecture provides the right balance of simplicity and future extensibility for Day 3 Afternoon and Day 4 features.

**Trade-offs**: Limited persistence across sessions, but acceptable for prototype scope.

---

### Decision-003: Model Loading Strategy
**Options Considered**:
1. Load all models at startup (chosen)
2. Lazy load models on demand
3. Load models in background threads

**Rationale**: Loading all models at startup provides the best user experience during interactions, despite longer initial load time. The 4-hour session allows for this approach.

**Trade-offs**: Longer initial load time, but smoother user experience during interactions.

---

### Decision-004: Component Architecture
**Options Considered**:
1. Monolithic script (rejected)
2. Modular components (chosen)
3. Class-based components

**Rationale**: Modular components provide better maintainability, reusability, and extensibility for future enhancements.

**Trade-offs**: Slightly more complex initial setup, but better long-term maintainability.

---

## Error Handling Strategy

### Error Categories
1. **Model Loading Errors**: Graceful degradation with user feedback
2. **Recommendation Generation Errors**: Fallback to simpler models or default recommendations
3. **Data Access Errors**: Empty state handling with retry options
4. **User Input Errors**: Input validation with clear error messages

### Error Recovery
- **Model Loading**: Display error message, offer retry, disable affected model selection
- **Recommendation Generation**: Display error message, show last successful recommendations
- **Data Access**: Use fallback data or placeholder information
- **User Input**: Clear validation messages with correction suggestions

---

## Performance Optimization

### Optimization Strategies
1. **Model Caching**: Load models once and cache in memory
2. **Data Caching**: Load movie/rating data once and cache
3. **Lazy Component Rendering**: Only render components when visible
4. **Progressive Loading**: Show UI incrementally as components load

### Performance Targets
- Initial load: < 5 seconds
- Model loading: < 3 seconds per model
- Recommendation generation: < 2 seconds
- UI interactions: < 500ms response time

---

## Testing Strategy

### Unit Tests
- Test session state manager functions
- Test model manager loading logic
- Test data provider functions
- Test individual UI components

### Integration Tests
- Test complete user workflow
- Test model switching scenarios
- Test error recovery scenarios
- Test parameter adjustment scenarios

### Performance Tests
- Measure load times
- Measure recommendation generation times
- Measure UI response times
- Identify bottlenecks

---

## Security Considerations

### Input Validation
- Validate user IDs are integers
- Validate parameter ranges (α: 0.0-1.0, k: positive integers)
- Sanitize movie metadata before display

### Error Message Safety
- Avoid exposing system internals in error messages
- Provide user-friendly error messages
- Log detailed errors for debugging

---

## Accessibility Considerations

### Basic Accessibility
- High contrast color scheme
- Readable font sizes
- Clear keyboard navigation
- Screen reader compatible labels
- Alt text for images (future)

---

## Deployment Considerations

### Local Development
- Streamlit runs locally during development
- Models loaded from local file system
- Data accessed from local CSV files

### Future Deployment
- Streamlit Cloud deployment option
- Model artifact packaging
- Data file deployment strategy
- Environment variable configuration

---

## Success Criteria

- [ ] Streamlit application loads successfully
- [ ] All four models load and integrate correctly
- [ ] User selection works with search functionality
- [ ] Model selection works with parameter controls
- [ ] Recommendations generate for all models
- [ ] Error handling covers major failure scenarios
- [ ] Performance meets all targets
- [ ] Session state architecture supports future enhancements
- [ ] Component architecture is modular and maintainable
