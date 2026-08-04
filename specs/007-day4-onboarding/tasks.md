# Day 4 Morning: Cold-Start Onboarding UI - Tasks

**Feature ID:** 007-day4-onboarding  
**Date:** 2026-08-03  
**Status:** Draft  
**Effort:** 4 hours (Day 4 Morning)

---

## Implementation Constraints (MUST DO / MUST NOT DO)

### MUST DO
- **MUST** extend existing SessionManager with onboarding-specific methods
- **MUST** use `ui/onboarding/` directory for all onboarding components
- **MUST** maintain Day 3 backward compatibility
- **MUST** integrate with existing ColdStartHandler protocol
- **MUST** use existing DataProvider for movie search
- **MUST** implement proper error handling with user-friendly messages
- **MUST** ensure onboarding state persists across page refreshes
- **MUST** provide skip functionality with default genres ['Action', 'Comedy', 'Drama']

### MUST NOT DO
- **MUST NOT** modify existing Day 3 session state keys
- **MUST NOT** create new state management systems
- **MUST NOT** break existing Day 3 UI functionality
- **MUST NOT** hardcode movie data or genre lists
- **MUST NOT** implement real poster image loading
- **MUST NOT** create conflicts with Day 4 Afternoon session state
- **MUST NOT** modify backend model implementations
- **MUST NOT** use external APIs for movie data

---

## Task Breakdown

### Phase 1: Foundation (1 hour)

#### Task-001: Onboarding Wizard Controller
**Description**: Implement multi-step wizard controller with state management

**Acceptance Criteria**:
- [ ] OnboardingWizard class created in ui/onboarding/wizard_controller.py
- [ ] next_step() method advances with validation
- [ ] previous_step() method goes back correctly
- [ ] can_proceed() validates current step
- [ ] skip_onboarding() sets default preferences
- [ ] complete_onboarding() generates recommendations

**Test Cases**:
- Test: Wizard advances through steps correctly
- Test: Step validation prevents invalid transitions
- Test: Skip functionality sets default preferences
- Test: Complete onboarding generates recommendations
- Test: State management persists across page refreshes

**Dependencies**: Day 3 session manager

**Time Estimate**: 20 minutes

---

#### Task-002: Genre Provider Implementation
**Description**: Implement genre data provider with popularity metrics

**Acceptance Criteria**:
- [ ] GenreProvider class created in ui/onboarding/genre_provider.py
- [ ] get_all_genres() returns unique genres
- [ ] get_genre_popularity() returns genre counts
- [ ] get_suggested_combinations() returns popular combinations
- [ ] Caching implemented for performance

**Test Cases**:
- Test: All genres extracted correctly
- Test: Genre popularity calculated correctly
- Test: Suggested combinations are relevant
- Test: Caching improves performance

**Dependencies**: Day 3 data provider

**Time Estimate**: 15 minutes

---

#### Task-003: Movie Search Provider
**Description**: Implement movie search provider with efficient lookup

**Acceptance Criteria**:
- [ ] MovieSearchProvider class created in ui/onboarding/movie_search_provider.py
- [ ] search_movies() returns relevant results
- [ ] get_movie_preview() returns movie information
- [ ] Search index built for efficient lookup
- [ ] Search handles edge cases (empty query, no results)

**Test Cases**:
- Test: Search returns relevant movies
- Test: Search handles substring matching
- Test: Preview returns correct information
- Test: Empty query handled gracefully
- Test: No results handled gracefully

**Dependencies**: Day 3 data provider

**Time Estimate**: 15 minutes

---

#### Task-004: Preference Validator
**Description**: Implement preference validation with rule-based checks

**Acceptance Criteria**:
- [ ] PreferenceValidator class created in ui/onboarding/preference_validator.py
- [ ] validate_genres() validates genre selections
- [ ] validate_liked_movies() validates movie selections
- [ ] validate_preferences() validates complete preferences
- [ ] Error messages are clear and actionable

**Test Cases**:
- Test: Invalid genres rejected with clear error
- Test: Empty genres rejected with clear error
- Test: Too many genres rejected with clear error
- Test: Too many movies rejected with clear error
- Test: Valid preferences pass validation

**Dependencies**: Task-002

**Time Estimate**: 10 minutes

---

### Phase 2: Wizard Components (1.5 hours)

#### Task-005: Genre Selection Component
**Description**: Create genre selection step with multi-select and suggestions

**Acceptance Criteria**:
- [ ] Genre selection component created in ui/onboarding/components/genre_selection.py
- [ ] Multi-select genre picker works correctly
- [ ] Genre popularity indicators display
- [ ] Suggested combinations work as quick-select
- [ ] Navigation buttons function correctly

**Test Cases**:
- Test: Multi-select works with genre list
- Test: Popularity indicators display correctly
- Test: Suggested combinations set genres correctly
- Test: Next button enables with valid selection
- Test: Skip button sets default genres

**Dependencies**: Task-001, Task-002

**Time Estimate**: 25 minutes

---

#### Task-006: Liked-Movies Component
**Description**: Create liked-movies input with search and management

**Acceptance Criteria**:
- [ ] Liked-movies component created in ui/onboarding/components/liked_movies.py
- [ ] Movie search returns relevant results
- [ ] Add button adds movies to selection
- [ ] Remove button removes movies from selection
- [ ] Selected movies display correctly

**Test Cases**:
- Test: Search returns relevant movies
- Test: Add button adds movie to selection
- Test: Remove button removes movie from selection
- Test: Selected movies display correctly
- Test: Navigation buttons work correctly

**Dependencies**: Task-001, Task-003

**Time Estimate**: 30 minutes

---

#### Task-007: Confirmation Component
**Description**: Create preference confirmation step with preview

**Acceptance Criteria**:
- [ ] Confirmation component created in ui/onboarding/components/confirmation.py
- [ ] Preferences summary displays correctly
- [ ] Recommendation preview generates
- [ ] Edit preferences returns to step 1
- [ ] Complete onboarding triggers finalization

**Test Cases**:
- Test: Preferences summary displays correctly
- Test: Recommendation preview generates
- Test: Edit preferences returns to correct step
- Test: Complete onboarding finalizes correctly
- Test: Navigation buttons work correctly

**Dependencies**: Task-001, Task-002

**Time Estimate**: 20 minutes

---

#### Task-008: Wizard Navigation Logic
**Description**: Implement wizard navigation with step management

**Acceptance Criteria**:
- [ ] Wizard navigation integrated across all steps
- [ ] Progress indicator shows current step
- [ ] Step validation prevents invalid transitions
- [ ] Back/Next buttons work correctly
- [ ] Skip functionality works at any step

**Test Cases**:
- Test: Progress indicator shows correct step
- Test: Next button validates before advancing
- Test: Back button returns to previous step
- Test: Skip functionality works correctly
- Test: Wizard completes successfully

**Dependencies**: Tasks 005-007

**Time Estimate**: 15 minutes

---

### Phase 3: Backend Integration (1 hour)

#### Task-009: ColdStartHandler Integration
**Description**: Integrate with ColdStartHandler protocol for recommendations

**Acceptance Criteria**:
- [ ] OnboardingRecommender class created
- [ ] recommend_cold_start() calls backend correctly
- [ ] Genre parameters pass correctly
- [ ] Liked-movies parameters pass correctly
- [ ] Fallback to content model works

**Test Cases**:
- Test: ColdStartHandler called with correct parameters
- Test: Recommendations generate correctly
- Test: Genre parameters pass correctly
- Test: Liked-movies parameters pass correctly
- Test: Fallback mechanisms work

**Dependencies**: Day 3 model manager, backend ColdStartHandler

**Time Estimate**: 25 minutes

---

#### Task-010: Preference Parameter Passing
**Description**: Implement preference parameter passing to backend

**Acceptance Criteria**:
- [ ] Genre preferences format correctly for backend
- [ ] Liked-movies preferences format correctly for backend
- [ ] Preference weights apply correctly
- [ ] Parameter validation before backend call
- [ ] Error handling for invalid parameters

**Test Cases**:
- Test: Genre preferences format correctly
- Test: Liked-movies preferences format correctly
- Test: Preference weights apply correctly
- Test: Invalid parameters caught before backend call
- Test: Error handling works for parameter issues

**Dependencies**: Task-009

**Time Estimate**: 15 minutes

---

#### Task-011: Error Handling for Cold-Start
**Description**: Implement comprehensive error handling for cold-start failures

**Acceptance Criteria**:
- [ ] Cold-start failures handled gracefully
- [ ] User-friendly error messages display
- [ ] Fallback to simpler model on failure
- [ ] Retry mechanism for transient failures
- [ ] Error logging for debugging

**Test Cases**:
- Test: Cold-start failure shows user-friendly error
- Test: Fallback to simpler model works
- Test: Retry mechanism works for transient failures
- Test: Error logging captures details
- Test: Application continues after error

**Dependencies**: Task-009

**Time Estimate**: 10 minutes

---

#### Task-012: Recommendation Formatting
**Description**: Format backend recommendations for UI display

**Acceptance Criteria**:
- [ ] Recommendations format for UI display
- [ ] Movie metadata added to recommendations
- [ ] Explanations added when available
- [ ] Confidence scores added when available
- [ ] Empty results handled gracefully

**Test Cases**:
- Test: Recommendations format correctly
- Test: Movie metadata added correctly
- Test: Explanations added when available
- Test: Confidence scores added when available
- Test: Empty results handled gracefully

**Dependencies**: Task-009

**Time Estimate**: 10 minutes

---

### Phase 4: Integration and Testing (0.5 hours)

#### Task-013: Main Application Integration
**Description**: Integrate onboarding into main Streamlit application

**Acceptance Criteria**:
- [ ] Onboarding entry point added to main app
- [ ] Cold-start user detection works
- [ ] Onboarding toggle works correctly
- [ ] Session state extended for onboarding
- [ ] Integration with main recommendation interface

**Test Cases**:
- Test: Onboarding entry point displays correctly
- Test: Cold-start users detected correctly
- Test: Onboarding toggle works
- Test: Session state extensions work
- Test: Integration with main interface smooth

**Dependencies**: All previous tasks

**Time Estimate**: 15 minutes

---

#### Task-014: Complete Workflow Testing
**Description**: Test complete onboarding workflow end-to-end

**Acceptance Criteria**:
- [ ] Complete onboarding workflow tested
- [ ] Skip flow tested with defaults
- [ ] Preference modification tested
- [ ] Onboarding re-entry tested
- [ ] All edge cases tested

**Test Cases**:
- Test: Complete workflow from start to finish
- Test: Skip flow with default preferences
- Test: Preference modification after completion
- Test: Onboarding re-entry after completion
- Test: Edge cases (empty selections, invalid inputs)

**Dependencies**: Task-013

**Time Estimate**: 10 minutes

---

#### Task-015: Performance Testing
**Description**: Test onboarding performance and optimization

**Acceptance Criteria**:
- [ ] Onboarding completion time < 2 seconds
- [ ] Preference generation time < 2 seconds
- [ ] UI response time < 500ms
- [ ] Movie search response time < 1 second
- [ ] Memory usage acceptable

**Test Cases**:
- Test: Onboarding completion time measured
- Test: Preference generation time measured
- Test: UI response time measured
- Test: Movie search time measured
- Test: Memory usage monitored

**Dependencies**: Task-014

**Time Estimate**: 5 minutes

---

## Task Dependencies

```
Phase 1: Foundation
Task-001 (Wizard Controller)
    ├── Task-005 (Genre Selection)
    ├── Task-006 (Liked-Movies)
    ├── Task-007 (Confirmation)
    └── Task-008 (Wizard Navigation)

Task-002 (Genre Provider)
    ├── Task-004 (Preference Validator)
    └── Task-005 (Genre Selection)

Task-003 (Movie Search Provider)
    └── Task-006 (Liked-Movies)

Task-004 (Preference Validator)
    └── Task-008 (Wizard Navigation)

Phase 2: Wizard Components
Task-005, Task-006, Task-007 → Task-008 (Wizard Navigation)

Phase 3: Backend Integration
Task-009 (ColdStartHandler Integration)
    ├── Task-010 (Parameter Passing)
    ├── Task-011 (Error Handling)
    └── Task-012 (Recommendation Formatting)

Phase 4: Integration
Task-013 (Main Integration)
    ├── Task-014 (Complete Workflow Testing)
    └── Task-015 (Performance Testing)
```

---

## Total Time Estimate

- **Phase 1: Foundation**: 1 hour (Tasks 001-004)
- **Phase 2: Wizard Components**: 1.5 hours (Tasks 005-008)
- **Phase 3: Backend Integration**: 1 hour (Tasks 009-012)
- **Phase 4: Integration**: 0.5 hours (Tasks 013-015)

**Total**: 4 hours

---

## Risk Mitigation

### Risk-001: Cold-Start Integration Complexity
- **Mitigation**: Test backend integration early, create fallback mechanisms
- **Contingency**: Use simpler content-based cold-start if hybrid integration fails

### Risk-002: User Confusion in Onboarding
- **Mitigation**: Clear instructions, intuitive design, extensive testing
- **Contingency**: Simplify onboarding if testing reveals confusion

### Risk-003: Preference Quality Impact
- **Mitigation**: Provide suggestions, validation, and ability to modify
- **Contingency**: Allow easy preference modification after onboarding

---

## Success Criteria Summary

- [ ] All 15 tasks completed
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
