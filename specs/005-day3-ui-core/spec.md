# Day 3 Morning: Core UI Structure - Specification

**Feature ID:** 005-day3-ui-core  
**Date:** 2026-08-03  
**Status:** Draft  
**Effort:** 4 hours (Day 3 Morning)

---

## Overview

This specification defines the core UI structure for the Devnexes RecoLab recommendation system interface. The UI will provide users with an intuitive interface to interact with all four recommendation models (Popularity, Content, Collaborative, Hybrid) and receive personalized movie recommendations.

## Scope

### In Scope
- Streamlit application initialization and basic structure
- User selection interface with search functionality
- User profile display with metadata and activity indicators
- Model selection interface with parameter controls
- Basic recommendation display with movie metadata
- Error handling and loading states
- Session state management foundation
- Backend integration with all recommendation models

### Out of Scope
- Movie poster display (Day 3 Afternoon)
- Visualizations and charts (Day 3 Afternoon)
- Cold-start onboarding flow (Day 4 Morning)
- Performance metrics dashboard (Day 4 Afternoon)
- Advanced explanation panels (Day 4 Afternoon)

---

## Functional Requirements

### FR-001: Streamlit Application Initialization
The system shall initialize a Streamlit application with:
- Professional page layout with sidebar for controls
- Consistent styling and color scheme
- Responsive design for different screen sizes
- Session state management foundation for extensibility

### FR-002: User Selection Interface
The system shall provide a user selection interface with:
- Dropdown menu containing all available user IDs
- Search functionality to filter users by ID
- User profile display showing:
  - User ID
  - Total number of ratings
  - Activity level indicator (cold-start/intermediate/active)
  - Rating history summary

### FR-003: Model Selection Interface
The system shall provide a model selection interface with:
- Radio buttons for selecting recommendation models:
  - Popularity Model
  - Content Model
  - User-Based Collaborative Filtering
  - Item-Based Collaborative Filtering
  - Hybrid Recommender
- Model parameter controls:
  - Hybrid: α parameter (0.0-1.0)
  - Collaborative: k parameter (number of similar users/items)
  - All: Number of recommendations (k=5,10,20)
- Real-time model switching without page reload

### FR-004: Recommendation Display
The system shall display recommendations with:
- Top-N recommendation list (based on selected k)
- Movie title and year
- Genre information
- Recommendation score (when available)
- Basic explanation text
- Clear visual separation between recommendations

### FR-005: Backend Integration
The system shall integrate with the backend by:
- Loading all persisted model artifacts at startup
- Calling `recommend(user_id, k, exclude_items)` on selected model
- Handling model-specific cold-start scenarios
- Displaying confidence scores from HybridRecommender
- Calling `explain(user_id, movie_id)` for basic explanations

### FR-006: Error Handling
The system shall handle errors by:
- Showing loading states during model loading and recommendation generation
- Displaying user-friendly error messages for:
  - Invalid user IDs
  - Model loading failures
  - Recommendation generation failures
  - Empty recommendation results
- Providing empty state handling when no recommendations are available
- Validating user inputs before processing

### FR-007: Session State Management
The system shall implement session state management with:
- Extensible architecture for future enhancements
- Storage of selected user ID
- Storage of selected model and parameters
- Storage of recommendation results
- Foundation for preference storage (Day 4)

---

## Non-Functional Requirements

### NFR-001: Performance
- Initial application load time: < 5 seconds
- Model loading time: < 3 seconds per model
- Recommendation generation time: < 2 seconds
- UI response time: < 500ms for user interactions

### NFR-002: Usability
- Intuitive navigation flow: user selection → model selection → recommendations
- Clear visual hierarchy with prominent action buttons
- Consistent styling and color scheme throughout
- Responsive design for desktop and tablet screens

### NFR-003: Reliability
- Graceful degradation if models fail to load
- Session state persistence across page refreshes
- Error recovery with user-friendly messages
- Fallback to default parameters if inputs are invalid

### NFR-004: Maintainability
- Modular component architecture for future enhancements
- Clear separation between UI logic and backend integration
- Well-documented component interfaces
- Consistent code style and naming conventions

---

## Technical Requirements

### TR-001: Framework and Dependencies
- Streamlit >= 1.28.0 for UI framework
- Existing recolab package for backend models
- pandas for data manipulation
- Existing persistence layer for model loading

### TR-002: File Structure
```
Devnexes-RecoLab/
├── streamlit_app.py           # Main Streamlit application
├── ui/
│   ├── __init__.py
│   ├── components.py          # Reusable UI components
│   ├── user_selection.py      # User selection interface
│   ├── model_selection.py     # Model selection interface
│   └── recommendation_display.py  # Recommendation display
└── data/
    └── models/                # Saved model artifacts
```

### TR-003: Backend Integration Points
- Model loading: `persistence.load_model_bundle()`
- Recommendation API: `model.recommend(user_id, k, exclude_items)`
- Explanation API: `model.explain(user_id, movie_id)`
- Data access: Read movies.csv for metadata
- Confidence scoring: Access from HybridRecommender

### TR-004: Session State Architecture
- Design extensible session state structure:
  ```python
  st.session_state = {
      'selected_user_id': int,
      'selected_model': str,
      'model_params': dict,
      'recommendations': list,
      'user_profile': dict,
      # Extensible for Day 3 Afternoon and Day 4
  }
  ```

---

## Data Requirements

### DR-001: Model Artifacts
- All four models must be persisted and loadable:
  - popularity_model.bundle
  - content_model.bundle
  - user_based_cf.bundle
  - item_based_cf.bundle
  - hybrid_recommender.bundle

### DR-002: Movie Metadata
- movies.csv must contain:
  - movieId
  - title
  - genres
  - year (if available)

### DR-003: User Data
- Access to user rating counts for activity level calculation
- User rating history for profile display

---

## User Interface Requirements

### UIR-001: Layout
- Sidebar for controls (user selection, model selection, parameters)
- Main content area for recommendations
- Header with application title
- Footer with basic information

### UIR-002: User Selection
- Dropdown with search: "Select User ID"
- User profile card showing:
  - User ID: "User #123"
  - Rating count: "45 ratings"
  - Activity level: "Active User" (color-coded)

### UIR-003: Model Selection
- Radio buttons: "Select Recommendation Model"
- Parameter controls based on selected model:
  - Hybrid: Slider for α (0.0-1.0, default 0.5)
  - CF: Slider for k (5-50, default 20)
  - All: Number input for N (5, 10, 20)

### UIR-004: Recommendation Display
- Card-based layout for each recommendation
- Each card shows:
  - Movie title and year
  - Genre tags
  - Recommendation score (if available)
  - Basic explanation text
- "Get Recommendations" button to trigger generation

### UIR-005: Loading and Error States
- Spinner animation during model loading
- Progress indicator during recommendation generation
- Error banner for failures with retry option
- Empty state message when no recommendations available

---

## Acceptance Criteria

### AC-001: Application Initialization
- [ ] Streamlit app loads without errors
- [ ] Professional layout with sidebar and main content area
- [ ] Consistent styling applied throughout
- [ ] Session state initialized with default values

### AC-002: User Selection
- [ ] User dropdown populated with all available user IDs
- [ ] Search functionality filters user list correctly
- [ ] User profile displays correct metadata
- [ ] Activity level indicator shows correct classification

### AC-003: Model Selection
- [ ] All four models available for selection
- [ ] Model switching works without page reload
- [ ] Parameter controls update based on selected model
- [ ] Parameters persist across model switches

### AC-004: Recommendation Generation
- [ ] Recommendations generate successfully for all models
- [ ] Movie metadata displays correctly
- [ ] Recommendation scores display when available
- [ ] Basic explanations show for each recommendation

### AC-005: Error Handling
- [ ] Loading states show during model loading
- [ ] Error messages display for invalid inputs
- [ ] Empty states handle no recommendation scenarios
- [ ] Graceful degradation for model failures

### AC-006: Backend Integration
- [ ] All models load successfully from persistence
- [ ] Recommendation API calls work correctly
- [ ] Explanation API calls work correctly
- [ ] Confidence scores display for HybridRecommender

### AC-007: Performance
- [ ] Application loads in < 5 seconds
- [ ] Models load in < 3 seconds each
- [ ] Recommendations generate in < 2 seconds
- [ ] UI responds to interactions in < 500ms

---

## Testing Requirements

### TR-001: Unit Tests
- Test individual UI components in isolation
- Test session state management functions
- Test backend integration functions
- Test error handling functions

### TR-002: Integration Tests
- Test complete user workflow: selection → recommendation
- Test model switching scenarios
- Test parameter adjustment scenarios
- Test error recovery scenarios

### TR-003: Edge Case Tests
- Test with invalid user IDs
- Test with empty recommendation results
- Test with model loading failures
- Test with network connectivity issues

### TR-004: Performance Tests
- Measure application load time
- Measure model loading time
- Measure recommendation generation time
- Measure UI response time

---

## Dependencies

### Critical Dependencies
- All backend models must be complete (Days 1-2)
- Model persistence must be functional
- All model artifacts must be saved and loadable
- Movies.csv must contain complete metadata
- User rating data must be accessible

### External Dependencies
- Streamlit framework (new dependency)
- Existing recolab package
- pandas for data manipulation
- Existing persistence layer

---

## Risks and Mitigation

### Risk-001: Streamlit Learning Curve
- **Risk**: Team unfamiliar with Streamlit framework
- **Mitigation**: Allocate 1-2 hours for Streamlit tutorial and experimentation

### Risk-002: Model Loading Performance
- **Risk**: Loading all models may be slow
- **Mitigation**: Implement lazy loading with progress indicators

### Risk-003: Session State Complexity
- **Risk**: Complex session state may become unmanageable
- **Mitigation**: Use clear state management pattern with documentation

### Risk-004: Backend Integration Issues
- **Risk**: Backend models may not integrate as expected
- **Mitigation**: Test backend integration early and create fallback mechanisms

---

## Success Metrics

- Application loads successfully with all models
- User can select any user and receive recommendations
- All four models work correctly through the UI
- Error handling covers all major failure scenarios
- Performance meets all NFR requirements
- Session state architecture supports future enhancements
