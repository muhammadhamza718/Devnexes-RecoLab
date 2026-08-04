# Day 4 Morning Implementation Prompt: Cold-Start Onboarding UI

## Objective

Implement a cold-start onboarding UI that enables new users to provide preferences (genre selection, liked movies) to receive personalized recommendations without requiring rating history. This 4-hour implementation integrates with the existing ColdStartHandler protocol from Day 2 and builds upon the Day 3 UI foundation.

## Project Context

- **Project:** Devnexes-RecoLab - Movie Recommendation System
- **Branch:** 009-day4-advanced
- **Location:** F:\Courses\Hamza\Devnexes-Internship-Projects\Devnexes-RecoLab
- **Time Allocation:** 4 hours
- **SDD Reference:** F:\Courses\Hamza\Devnexes-Internship-Projects\specs\007-day4-onboarding/

## Pre-Implementation Verification (15 minutes)

Before starting implementation, verify the following:

### 1. Day 3 Foundation
- Navigate to Devnexes-RecoLab/
- Verify Day 3 Morning and Afternoon implementations are complete
- Check that streamlit_app.py exists and runs correctly
- Verify ui/ package structure exists (session_manager.py, data_provider.py, model_manager.py, components/)
- Test: `python streamlit_app.py` loads without errors

### 2. ColdStartHandler Protocol
- Verify ColdStartHandler protocol exists in src/recolab/interfaces.py
- Check that ContentModel implements recommend_cold_start() method
- Verify HybridRecommender has cold-start handling capabilities
- Test: Backend cold-start methods are accessible

### 3. Data Files
- Verify movies.csv exists in data/ml-latest-small/
- Verify ratings.csv exists in data/ml-latest-small/
- Verify train.csv exists in data/split_datasets/

### 4. Session State Architecture
- Verify SessionManager has extensible architecture
- Check that DEFAULT_SESSION_STATE can be extended
- Verify session state persistence works from Day 3 Morning
- Verify no conflicts with Day 3 Afternoon session state keys

## Implementation Instructions

### Step 1: Read SDD Documentation (10 minutes)

Read the following files from the parent directory:

```
F:\Courses\Hamza\Devnexes-Internship-Projects\specs\007-day4-onboarding/
- spec.md - Requirements and acceptance criteria (MUST DO / MUST NOT DO constraints)
- plan.md - Architecture and component design
- tasks.md - Detailed task breakdown (MUST DO / MUST NOT DO constraints)
- data-model.md - Extended session state structure
- quickstart.md - Implementation examples
```

**Note:** The SDD documents are in the parent directory, not in Devnexes-RecoLab/

### Step 2: Extend Session State Architecture (10 minutes)

Extend the session state schema in ui/session_manager.py to support onboarding:

```python
# Add to DEFAULT_SESSION_STATE in ui/session_manager.py
DEFAULT_SESSION_STATE: dict[str, Any] = {
    # Existing Day 3 Morning + Day 3 Afternoon state
    "selected_user_id": None,
    "selected_model": "Hybrid",
    "model_params": {"alpha": 0.5, "k": 10, "n": 10},
    "recommendations": [],
    "user_profile": {},
    "poster_cache": {},
    "similar_items": [],
    "similar_source_title": None,
    "current_view": "recommendations",
    "visualization_panel_open": False,
    "rating_statistics": {},
    
    # Day 4 Morning: Onboarding state (namespaced to avoid conflicts)
    "onboarding_active": False,  # Whether onboarding is currently active
    "onboarding_step": 0,  # Current wizard step (0, 1, 2)
    "onboarding_complete": False,  # Whether onboarding is completed
    "onboarding_timestamp": None,  # ISO timestamp of onboarding completion
    "selected_genres": [],  # Selected genre preferences
    "liked_movies": [],  # Selected liked movie IDs
    "preference_weights": {},  # Genre preference weights
    "onboarding_preferences": {},  # Complete preference set
    "precommendation_preview": [],  # Preview recommendations
}
```

Add corresponding accessor methods in SessionManager class.

### Step 3: Core Implementation (3.5 hours)

Follow the task sequence from specs/007-day4-onboarding/tasks.md:

**Phase 1: Foundation (1 hour)**
- Task-001: Onboarding Wizard Controller (ui/onboarding/wizard_controller.py)
- Task-002: Genre Provider Implementation (ui/onboarding/genre_provider.py)
- Task-003: Movie Search Provider (ui/onboarding/movie_search_provider.py)
- Task-004: Preference Validator (ui/onboarding/preference_validator.py)

**Phase 2: Wizard Components (1.5 hours)**
- Task-005: Genre Selection Component (ui/onboarding/components/genre_selection.py)
- Task-006: Liked-Movies Component (ui/onboarding/components/liked_movies.py)
- Task-007: Confirmation Component (ui/onboarding/components/confirmation.py)
- Task-008: Wizard Navigation Logic

**Phase 3: Backend Integration (1 hour)**
- Task-009: ColdStartHandler Integration
- Task-010: Preference Parameter Passing
- Task-011: Error Handling for Cold-Start

### Step 4: Implementation Guidelines

#### Component Structure
- Create `ui/onboarding/` directory for all onboarding components
- Create `ui/onboarding/components/` for wizard step components
- Follow the component pattern established in Day 3 Afternoon

#### Session State Extensions
- Follow the extensible session state pattern from Day 3 Morning
- Add new state keys to DEFAULT_SESSION_STATE
- Ensure backward compatibility with Day 3 Morning + Day 3 Afternoon state
- Test session state persistence across refreshes

#### Backend Integration
- Use existing ModelManager for model access
- Use existing DataProvider for movie search and genre extraction
- Call existing ColdStartHandler protocol methods
- Implement proper error handling with user-friendly messages

#### User Experience
- Implement intuitive onboarding flow (≤ 3 minutes to complete)
- Provide clear instructions at each step
- Implement skip functionality with default genres: ['Action', 'Comedy', 'Drama']
- Ensure smooth transition to main recommendation interface after completion

### Step 5: Testing and Validation (30 minutes)

#### Functional Testing
- Test complete onboarding workflow
- Test skip flow with defaults
- Test step navigation (forward/back)
- Test preference modification
- Test onboarding re-entry

#### Preference Tests
- Test genre selection validation
- Test liked-movies validation
- Test preference combination validation
- Test preference storage and retrieval

#### Backend Integration Tests
- Test ColdStartHandler integration
- Test genre parameter passing
- Test liked-movies parameter passing
- Test error handling for cold-start failures

### Step 6: Acceptance Criteria Verification

Verify all acceptance criteria from specs/007-day4-onboarding/spec.md:

**AC-001: Genre Preference Selection**
- [ ] Multi-select genre picker works correctly
- [ ] Genre popularity indicators display correctly
- [ ] Preference weighting applies correctly
- [ ] Genre suggestions display appropriately
- [ ] Visual feedback is clear and immediate

**AC-002: Liked-Movies Input**
- [ ] Movie search returns relevant results
- [ ] Movie preview displays correctly
- [ ] Liked-movies list management works
- [ ] Preference intensity applies correctly
- [ ] Removal and editing capabilities work

**AC-003: Onboarding Flow**
- [ ] Wizard navigation works correctly
- [ ] Progress indicator shows current step
- [ ] Skip option works with sensible defaults
- [ ] Step validation prevents invalid transitions
- [ ] Instructions are clear at each step

**AC-004: Recommendation Display**
- [ ] Preference-based recommendations generate correctly
- [ ] Explanations show preference influence
- [ ] Adjustment suggestions display appropriately
- [ ] Onboarding completion state works
- [ ] Transition to main interface is smooth

**AC-005: Session Management**
- [ ] Onboarding preferences store correctly
- [ ] User profile updates based on preferences
- [ ] Session persistence works across refreshes
- [ ] Preference modification works after completion
- [ ] Onboarding state management is clear

**AC-006: Backend Integration**
- [ ] ColdStartHandler protocol integrates correctly
- [ ] recommend_cold_start() calls work correctly
- [ ] Genre and liked-movies parameters pass correctly
- [ ] Fallback to content model works if needed
- [ ] Error handling covers cold-start failures

## Success Criteria

Day 4 Morning is complete when:

- ✅ Onboarding wizard with 3 steps works correctly
- ✅ Genre selection with multi-select and popularity indicators works
- ✅ Liked-movies input with search and management works
- ✅ Preference confirmation step works
- ✅ Cold-start recommendations generate correctly
- ✅ Skip functionality with default genres works
- ✅ Session state extensions work correctly
- ✅ All 11 tasks from tasks.md are completed
- ✅ All acceptance criteria from spec.md are met
- ✅ Integration with Day 3 + Day 3 Afternoon is smooth
- ✅ No conflicts with existing functionality

## Post-Implementation

### Commit Changes
```bash
git add .
git commit -m "feat: implement Day 4 Morning - Cold-Start Onboarding UI"
```

### Document Issues
- Note any deviations from the SDD
- Document any workarounds or limitations
- Record any environment-specific issues

### Prepare for Day 4 Afternoon
- Verify session state architecture supports dashboard features
- Check if metrics framework is functional
- Confirm foundation supports dashboard components

## Important Notes

### Time Management
- Each task should take approximately 15-20 minutes
- Wizard components may take longer than estimated
- Prioritize core functionality over polish if time runs out

### Architecture Considerations
- Maintain extensible session state architecture for Day 4 Afternoon
- Keep modular component structure for future enhancements
- Ensure backward compatibility with Day 3 + Day 3 Afternoon
- Use namespaced session state keys to avoid conflicts

### SDD Reference
- **Critical**: SDD documents are in parent directory: `F:\Courses\Hamza\Devnexes-Internship-Projects\specs\007-day4-onboarding/`
- Not in Devnexes-RecoLab/specs/

### MUST DO / MUST NOT DO Constraints
- **MUST** follow all MUST DO constraints from spec.md
- **MUST NOT** violate any MUST NOT DO constraints from spec.md
- **MUST** use existing SessionManager, DataProvider, ModelManager
- **MUST NOT** create new state management systems
- **MUST** use text-based poster placeholders (as per Day 3 architectural decision)

### Lessons from Day 3
- Model fitting at startup with `@st.cache_resource` is acceptable for demo
- Data adaptations are acceptable for demo environment
- Performance optimizations not in SDD are acceptable if essential
- Session state persistence is key for user experience

## Emergency Procedures

### If ColdStartHandler Issues Occur
- Fallback to ContentModel.recommend_cold_start() directly
- Implement placeholder cold-start recommendations
- Document limitation and proceed

### If Search Performance Issues Occur
- Implement simpler substring matching
- Limit search results to 10 items
- Add search caching for performance
- Document performance limitations

### If Session State Conflicts Occur
- Ensure all onboarding keys are properly namespaced
- Verify no conflicts with Day 3 Afternoon keys
- Test session state persistence across refreshes
- Document any key conflicts and resolutions

---

**Start Implementation:** Begin with Step 1 (Read SDD Documentation) and proceed sequentially through the steps. Remember that SDD documents are in the parent directory, not in the Devnexes-RecoLab directory.
