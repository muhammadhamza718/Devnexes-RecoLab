# Tasks: Cold-Start Optimization & Parameter Tuning

**Input**: Design documents from `/specs/004-cold-start-optimization/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Tests are REQUIRED as per specification (≥15 tests, ≥70% coverage)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3, US4)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Add UserProfile class skeleton to src/recolab/hybrid.py
- [x] T002 Add EnhancedColdStartHandler class skeleton to src/recolab/hybrid.py
- [x] T003 [P] Add cold-start optimization imports to src/recolab/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T004 Implement UserProfile class with __init__ method in src/recolab/hybrid.py
- [x] T005 [P] Implement genre weight calculation in UserProfile in src/recolab/hybrid.py
- [x] T006 [P] Implement profile normalization in UserProfile in src/recolab/hybrid.py
- [x] T007 [P] Add type hints for all UserProfile methods in src/recolab/hybrid.py
- [x] T008 Setup EnhancedColdStartHandler integration stub in src/recolab/hybrid.py

**Checkpoint**: Foundation ready

---

## Phase 3: User Story 1 - Enhanced Cold-Start Onboarding (Priority: P1) 🎯 MVP

**Goal**: Implement sophisticated cold-start user onboarding with profile building and preference weight calculation

**Independent Test**: Simulate new user onboarding with different genre preferences and liked movie combinations, verify profile building quality and recommendation relevance

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Write test for UserProfile creation in tests/test_hybrid.py
- [x] T010 [P] [US1] Write test for genre weight calculation accuracy in tests/test_hybrid.py
- [x] T011 [P] [US1] Write test for profile normalization correctness in tests/test_hybrid.py
- [x] T012 [P] [US1] Write test for EnhancedColdStartHandler profile building in tests/test_hybrid.py
- [x] T013 [P] [US1] Write test for enhanced cold-start recommendations quality in tests/test_hybrid.py
- [x] T014 [P] [US1] Write test for explanation generation delegation in tests/test_hybrid.py

### Implementation for User Story 1

- [x] T014 [US1] Implement _calculate_initial_weights method in UserProfile in src/recolab/hybrid.py
- [x] T015 [US1] Implement _extract_genre_weights from liked movies in UserProfile in src/recolab/hybrid.py
- [x] T016 [US1] Implement _normalize_weights method in UserProfile in src/recolab/hybrid.py
- [x] T017 [US1] Implement get_preferred_genres method in UserProfile in src/recolab/hybrid.py
- [x] T018 [US1] Implement build_user_profile method in EnhancedColdStartHandler in src/recolab/hybrid.py
- [x] T019 [US1] Implement calculate_genre_weights method in EnhancedColdStartHandler in src/recolab/hybrid.py
- [x] T020 [US1] Implement enhanced recommend_cold_start method in EnhancedColdStartHandler in src/recolab/hybrid.py
- [x] T021 [US1] Add profile caching mechanism in EnhancedColdStartHandler in src/recolab/hybrid.py
- [x] T022 [US1] Add default genre handling for users with no preferences in src/recolab/hybrid.py
- [x] T023 [US1] Implement explain method with ContentModel.explain() delegation in src/recolab/hybrid.py
- [x] T024 [US1] Implement UserProfile.to_bundle() method for persistence in src/recolab/hybrid.py
- [x] T025 [US1] Implement UserProfile.from_bundle() class method for persistence in src/recolab/hybrid.py
- [x] T026 [US1] Implement UserProfile.invalidate_cache() method in src/recolab/hybrid.py

**Checkpoint**: User Story 1 fully functional

---

## Phase 4: User Story 2 - New-Item Handling Strategy (Priority: P1) 🎯 MVP

**Goal**: Implement comprehensive new-item handling with detection, popularity boost, and similarity mechanisms

**Independent Test**: Add new items to the catalog and verify they appear in recommendations through content similarity and popularity boost mechanisms

### Tests for User Story 2 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T027 [P] [US2] Write test for NewItemDetector detection logic in tests/test_hybrid.py
- [x] T028 [P] [US2] Write test for popularity boost application in tests/test_hybrid.py
- [x] T029 [P] [US2] Write test for new-item flagging accuracy in tests/test_hybrid.py
- [x] T030 [P] [US2] Write test for new-item recommendation coverage in tests/test_hybrid.py

### Implementation for User Story 2

- [x] T031 [US2] Implement NewItemDetector class in src/recolab/hybrid.py
- [x] T032 [US2] Implement detect_new_items method in NewItemDetector in src/recolab/hybrid.py
- [x] T033 [US2] Implement apply_popularity_boost method in NewItemDetector in src/recolab/hybrid.py
- [x] T034 [US2] Implement time decay for popularity boost in NewItemDetector in src/recolab/hybrid.py
- [x] T035 [US2] Add new-item status caching in NewItemDetector in src/recolab/hybrid.py
- [x] T036 [US2] Integrate NewItemDetector with EnhancedColdStartHandler in src/recolab/hybrid.py
- [x] T037 [US2] Add new-item boost to cold-start recommendations in src/recolab/hybrid.py

**Checkpoint**: User Story 2 fully functional

---

## Phase 5: User Story 3 - Parameter Tuning & Optimization (Priority: P2)

**Goal**: Implement parameter tuning through grid search on validation sets to optimize hybrid performance

**Independent Test**: Run grid search on validation data and verify that optimized parameters achieve better performance than defaults

### Tests for User Story 3 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T038 [P] [US3] Write test for ParameterOptimizer grid search in tests/test_hybrid.py
- [x] T039 [P] [US3] Write test for α parameter optimization in tests/test_hybrid.py
- [x] T040 [P] [US3] Write test for threshold optimization in tests/test_hybrid.py
- [x] T041 [P] [US3] Write test for parameter optimization reproducibility in tests/test_hybrid.py

### Implementation for User Story 3

- [x] T042 [US3] Implement ParameterOptimizer class in src/recolab/hybrid.py
- [x] T043 [US3] Implement grid_search_alpha method in ParameterOptimizer in src/recolab/hybrid.py
- [x] T044 [US3] Implement grid_search_thresholds method in ParameterOptimizer in src/recolab/hybrid.py
- [x] T045 [US3] Implement _evaluate_ndcg_at_k method in ParameterOptimizer in src/recolab/hybrid.py
- [x] T046 [US3] Implement _generate_configs method in ParameterOptimizer in src/recolab/hybrid.py
- [x] T047 [US3] Implement early stopping logic in ParameterOptimizer in src/recolab/hybrid.py
- [x] T048 [US3] Implement optimize_all_parameters method in ParameterOptimizer in src/recolab/hybrid.py
- [x] T049 [US3] Add optimization history tracking in ParameterOptimizer in src/recolab/hybrid.py
- [x] T050 [US3] Implement get_optimized_params_bundle() method for persistence in src/recolab/hybrid.py

**Checkpoint**: User Story 3 fully functional

---

## Phase 6: User Story 4 - Enhanced Fallback Strategy (Priority: P2)

**Goal**: Implement multi-level fallback chain with trigger conditions and performance monitoring

**Independent Test**: Simulate model failures and verify fallback chain activation, trigger conditions, and performance monitoring

### Tests for User Story 4 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T051 [P] [US4] Write test for FallbackManager chain execution in tests/test_hybrid.py
- [x] T052 [P] [US4] Write test for fallback trigger conditions in tests/test_hybrid.py
- [x] T053 [P] [US4] Write test for fallback performance monitoring in tests/test_hybrid.py
- [x] T054 [P] [US4] Write test for fallback chain 100% availability in tests/test_hybrid.py

### Implementation for User Story 4

- [x] T055 [US4] Implement FallbackManager class in src/recolab/hybrid.py
- [x] T056 [US4] Implement execute_fallback_chain method in FallbackManager in src/recolab/hybrid.py
- [x] T057 [US4] Implement trigger condition evaluation in FallbackManager in src/recolab/hybrid.py
- [x] T058 [US4] Implement monitor_fallback_performance method in FallbackManager in src/recolab/hybrid.py
- [x] T059 [US4] Implement _log_fallback method in FallbackManager in src/recolab/hybrid.py
- [x] T060 [US4] Implement _log_success method in FallbackManager in src/recolab/hybrid.py
- [x] T061 [US4] Add alert generation for high fallback rates in FallbackManager in src/recolab/hybrid.py
- [x] T062 [US4] Integrate FallbackManager with HybridRecommender in src/recolab/hybrid.py

**Checkpoint**: User Story 4 fully functional

---

## Phase 7: Integration & Testing (Cross-Story Concerns)

**Purpose**: System integration, performance validation, and comprehensive testing

- [x] T063 [P] Implement PerformanceMonitor class in src/recolab/hybrid.py
- [x] T064 [P] Implement cold-start metrics calculation in PerformanceMonitor in src/recolab/hybrid.py
- [x] T065 [P] Implement metric history tracking in PerformanceMonitor in src/recolab/hybrid.py
- [x] T066 [P] Integrate PerformanceMonitor with EnhancedColdStartHandler in src/recolab/hybrid.py
- [x] T067 [P] Integrate PerformanceMonitor with FallbackManager in src/recolab/hybrid.py
- [x] T068 [P] Add comprehensive error handling for all new components in src/recolab/hybrid.py
- [x] T069 [P] Run integration tests with existing models (ContentModel, UserBasedCF, ItemBasedCF)
- [x] T070 [P] Run performance tests for cold-start recommendations (<100ms target)
- [x] T071 [P] Run performance tests for parameter optimization (<5 minutes target)
- [x] T072 [P] Run performance tests for fallback chain execution (<50ms target)
- [x] T073 [P] Update src/recolab/__init__.py to export new classes
- [x] T074 [P] Verify ≥17 passing unit tests for cold-start optimization (updated from 15 to account for explanation and persistence tests)
- [x] T075 [P] Run pytest with coverage report and verify ≥70% coverage
- [x] T076 [P] Test protocol compliance (EnhancedColdStartHandler extends ColdStartHandler)

**Checkpoint**: Integration and testing complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on US1 completion (integrates with profile building)
- **User Story 3 (Phase 5)**: Depends on HybridRecommender from morning (independent of US1, US2)
- **User Story 4 (Phase 6)**: Depends on HybridRecommender from morning (independent of US1, US2, US3)
- **Integration (Phase 7)**: Depends on US1, US2, US3, US4 completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Depends on US1 - Integrates with profile building for new-item recommendations
- **User Story 3 (P2)**: Independent of US1, US2 - Depends only on morning HybridRecommender
- **User Story 4 (P2)**: Independent of US1, US2, US3 - Depends only on morning HybridRecommender

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Profile building before new-item handling
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- All tests for a user story marked [P] can run in parallel
- Integration tasks marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Stories 1 & 2 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Enhanced Cold-Start Onboarding)
4. **STOP and VALIDATE**: Test US1 independently
5. Verify ≥5 tests pass for US1 core functionality
6. Achieve ≥70% coverage for new code

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Enhanced cold-start complete
3. Add User Story 2 → Test independently → New-item handling complete
4. Add User Story 3 → Test independently → Parameter optimization complete
5. Add User Story 4 → Test independently → Enhanced fallback complete
6. Integration → Coverage and performance validation → Production ready

### Test Strategy

- **TDD Approach**: Write tests first, ensure they fail, then implement
- **Coverage Target**: ≥70% for enhanced cold-start code
- **Test Count**: Minimum 15 tests (5 for US1, 4 for US2, 4 for US3, 4 for US4, + integration tests)
- **Performance Tests**: Verify <100ms cold-start recommendations, <5 minutes parameter optimization
- **Integration Tests**: Verify multi-model coordination and protocol compliance

---

## Success Criteria Validation

### Functional Requirements Coverage

- ✅ FR-001: Enhanced ColdStartHandler with preference weight calculation (T018, T019)
- ✅ FR-002: Comprehensive user profile building (T014-T017)
- ✅ FR-003: New-item detection and flagging (T027, T029)
- ✅ FR-004: Temporary popularity boost for new items (T028, T030)
- ✅ FR-005: Parameter tuning via grid search (T038, T044)
- ✅ FR-006: α parameter optimization (T039)
- ✅ FR-007: Activity threshold optimization (T040)
- ✅ FR-008: Multi-level fallback chain (T050, T051)
- ✅ FR-009: Fallback performance monitoring (T053, T054)
- ✅ FR-010: Cold-start performance metrics (T058, T059)
- ✅ FR-011: Parameterized tunable values (T043, T045)
- ✅ FR-012: <100ms recommendation latency maintained (T065)

### Success Criteria Coverage

- ✅ SC-001: ≥5 relevant cold-start recommendations (T013)
- ✅ SC-002: ≥90% new-item recommendation coverage (T026)
- ✅ SC-003: ≥5% NDCG@10 improvement from tuning (T034-T037)
- ✅ SC-004: 100% fallback availability (T049)
- ✅ SC-005: Actionable fallback health insights (T053, T054)
- ✅ SC-006: ≥70% coverage (T070)
- ✅ SC-007: ≥15 passing unit tests (T069)
- ✅ SC-008: <100ms latency maintained (T070)
- ✅ SC-009: Improved cold-start metrics (T064, T065)
- ✅ SC-010: Reproducible optimization results (T041)
- ✅ SC-011: Cold-start explanations include human-readable text (T014)
- ✅ SC-012: UserProfile data persisted for reproducibility (T024, T025)

### Total Task Count

- **Total Tasks**: 76 tasks (updated from 71 to account for explanation and persistence)
- **Setup Tasks**: 3 tasks
- **Foundational Tasks**: 5 tasks
- **User Story 1 Tasks**: 18 tasks (6 tests + 12 implementation, updated for explanation and persistence)
- **User Story 2 Tasks**: 11 tasks (4 tests + 7 implementation)
- **User Story 3 Tasks**: 13 tasks (4 tests + 9 implementation, updated for persistence integration)
- **User Story 4 Tasks**: 12 tasks (4 tests + 8 implementation)
- **Integration Tasks**: 14 tasks
- **Parallel Opportunities**: 17 tasks marked with [P]

### MVP Scope

**Completed MVP (Day 2 PM)**: Phase 1-4 complete (37 tasks done, updated)
- **Tasks done**: T001-T037 ✅
- **Test Count**: 10 tests for core functionality ✅ (updated)

### Full Feature Scope (Day 2 Required)

**Remaining**: T038-T076 (parameter tuning, enhanced fallback, integration, testing)
- **Duration**: Estimated remainder of Day 2 afternoon