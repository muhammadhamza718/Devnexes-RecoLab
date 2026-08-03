# Day 3 Morning: Core UI Structure - Quickstart Guide

**Feature ID:** 005-day3-ui-core  
**Date:** 2026-08-03  
**Status:** Draft

---

## Prerequisites

### System Requirements
- Python 3.8 or higher
- Existing Devnexes-RecoLab project with Days 1-2 completed
- All model artifacts saved and loadable
- movies.csv and ratings.csv available in data/ directory

### Dependencies
```bash
# Add to pyproject.toml
streamlit>=1.28.0
plotly>=5.17.0  # For Day 3 Afternoon
```

Install dependencies:
```bash
pip install streamlit plotly
```

---

## Quick Start

### 1. Project Setup

Create the UI directory structure:
```bash
cd Devnexes-RecoLab
mkdir -p ui/components ui/utils
touch ui/__init__.py ui/components/__init__.py ui/utils/__init__.py
```

### 2. Create Main Application

Create `streamlit_app.py`:
```python
import streamlit as st
from ui.session_manager import SessionStateManager
from ui.model_manager import ModelManager
from ui.data_provider import DataProvider
from ui.components.user_selection import render_user_selection
from ui.components.model_selection import render_model_selection
from ui.components.recommendation_display import render_recommendations
from ui.components.error_handling import render_loading_state

def main():
    # Initialize session state
    session_manager = SessionStateManager()
    session_manager.initialize_state()
    
    # Initialize data provider
    data_provider = DataProvider()
    
    # Initialize model manager
    model_manager = ModelManager()
    
    # App layout
    st.set_page_config(
        page_title="Devnexes RecoLab",
        page_icon="🎬",
        layout="wide"
    )
    
    # Sidebar for controls
    with st.sidebar:
        st.header("Recommender Controls")
        
        # User selection
        render_user_selection(session_manager, data_provider)
        
        st.divider()
        
        # Model selection
        render_model_selection(session_manager, model_manager)
    
    # Main content area
    st.header("Movie Recommendations")
    
    # Recommendation display
    if not session_manager.get_state('models_loaded'):
        render_loading_state("Loading models...")
        model_manager.load_all_models()
        session_manager.update_state('models_loaded', True)
    
    render_recommendations(session_manager, model_manager, data_provider)

if __name__ == "__main__":
    main()
```

### 3. Run the Application

```bash
cd Devnexes-RecoLab
streamlit run streamlit_app.py
```

The application will open in your browser at `http://localhost:8501`

---

## Component Usage Examples

### Session State Manager

```python
from ui.session_manager import SessionStateManager

session_manager = SessionStateManager()
session_manager.initialize_state()

# Update state
session_manager.update_state('selected_user_id', 123)

# Get state
user_id = session_manager.get_state('selected_user_id')
```

### Model Manager

```python
from ui.model_manager import ModelManager

model_manager = ModelManager()

# Load specific model
hybrid_model = model_manager.get_model('hybrid')

# Load all models
model_manager.load_all_models()
```

### Data Provider

```python
from ui.data_provider import DataProvider

data_provider = DataProvider()

# Get movie info
movie_info = data_provider.get_movie_info(123)

# Get user profile
user_profile = data_provider.get_user_profile(456)

# Get all user IDs
user_ids = data_provider.get_all_user_ids()
```

---

## Common Workflows

### Generate Recommendations for User

1. Select user ID from dropdown
2. Select recommendation model (e.g., Hybrid)
3. Adjust model parameters if needed
4. Click "Get Recommendations"
5. View recommendations with explanations

### Switch Between Models

1. Select different model from radio buttons
2. Parameters update automatically based on model
3. Recommendations generate with new model
4. Compare results between models

### Handle Errors

1. If model loading fails, error message displays
2. Click "Retry" to attempt loading again
3. If recommendation fails, error message shows
4. Try different model or adjust parameters

---

## Testing the Application

### Manual Testing Checklist

- [ ] Application loads without errors
- [ ] User dropdown populates with user IDs
- [ ] User profile displays correctly
- [ ] All four models available for selection
- [ ] Parameter controls update based on model
- [ ] Recommendations generate for each model
- [ ] Explanations display for recommendations
- [ ] Error handling works for invalid inputs
- [ ] Loading states show during operations

### Performance Testing

```python
import time
import streamlit as st

# Test model loading time
start = time.time()
model_manager.load_all_models()
load_time = time.time() - start
st.write(f"Model loading time: {load_time:.2f}s")

# Test recommendation generation time
start = time.time()
recommendations = model.recommend(user_id=123, k=10)
gen_time = time.time() - start
st.write(f"Recommendation generation time: {gen_time:.2f}s")
```

---

## Troubleshooting

### Issue: Models Fail to Load

**Solution**: 
- Check model file paths in ModelManager
- Verify model artifacts exist in data/models/
- Check persistence module is working correctly

### Issue: Application Loads Slowly

**Solution**:
- Implement lazy loading instead of pre-loading
- Add progress indicators for user feedback
- Consider reducing model complexity

### Issue: Session State Lost on Refresh

**Solution**:
- Session state is designed to persist across refreshes
- Check session state initialization logic
- Verify Streamlit session state is properly configured

### Issue: Recommendations Are Empty

**Solution**:
- Check user has rating history
- Verify model is fitted correctly
- Check exclusion list logic
- Test with different user IDs

---

## Architecture Integration Points

### Backend Integration

The UI integrates with existing backend through these entry points:

```python
# Model loading
from recolab.persistence import load_model_bundle
bundle = load_model_bundle('data/models/hybrid_recommender.bundle')

# Recommendation generation
from recolab.hybrid import HybridRecommender
model = HybridRecommender.from_bundle(bundle)
recommendations = model.recommend(user_id=123, k=10)

# Explanation generation
explanation = model.explain(user_id=123, movie_id=456)
```

### Data Access

The UI accesses data through these methods:

```python
# Movie metadata
movies_df = pd.read_csv('data/movies.csv')
movie_info = movies_df[movies_df['movieId'] == movie_id]

# User ratings
ratings_df = pd.read_csv('data/ratings.csv')
user_ratings = ratings_df[ratings_df['userId'] == user_id]
```

---

## Extension Points

### Adding New UI Components

1. Create component file in `ui/components/`
2. Implement render function
3. Import and use in `streamlit_app.py`
4. Update session state if needed

### Adding New Models

1. Add model to ModelManager.model_paths
2. Add model option to model selection component
3. Implement model-specific parameter controls
4. Test integration

### Adding New Visualizations (Day 3 Afternoon)

1. Add visualization libraries (plotly, matplotlib)
2. Create visualization components
3. Extend session state for visualization data
4. Integrate into main layout

---

## Performance Optimization Tips

### Model Loading
- Use lazy loading for infrequently used models
- Implement model caching in memory
- Show progress indicators during loading

### Data Loading
- Load CSV files once at startup
- Cache frequently accessed data
- Use efficient data structures

### UI Rendering
- Use Streamlit's built-in caching (@st.cache_data)
- Lazy load heavy components
- Optimize chart rendering for large datasets

---

## Security Considerations

### Input Validation
- Validate all user inputs before processing
- Sanitize data before display
- Use parameterized queries to prevent injection

### Error Messages
- Avoid exposing system internals
- Provide user-friendly error messages
- Log detailed errors for debugging

### Session State
- Don't store sensitive information in session state
- Be aware of session state size limits
- Clear session state when appropriate

---

## Deployment Considerations

### Local Development
- Streamlit runs locally during development
- Models loaded from local file system
- Data accessed from local CSV files

### Streamlit Cloud Deployment
- Package model artifacts with application
- Upload data files to Streamlit Cloud
- Configure environment variables if needed
- Set resource limits appropriately

### Custom Deployment
- Consider Docker containerization
- Set up reverse proxy (nginx)
- Configure SSL/TLS for production
- Implement monitoring and logging

---

## Next Steps

After completing Day 3 Morning:

1. **Day 3 Afternoon**: Add rich features (posters, visualizations, similar items)
2. **Day 4 Morning**: Implement cold-start onboarding flow
3. **Day 4 Afternoon**: Add advanced features (dashboard, model comparison)
4. **Testing**: Comprehensive testing of all features
5. **Documentation**: Update user guides and technical documentation
