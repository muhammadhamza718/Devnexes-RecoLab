# Tasks: Hybrid Recommendation Framework

**Input**: Design documents from `/specs/003-hybrid-framework/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Tests are REQUIRED as per specification (≥20 tests, ≥70% coverage)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure from plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create hybrid.py file in src/recolab/hybrid.py
- [x] T002 Create test_hybrid.py file in tests/test_hybrid.py
- [x] T003 [P] Add hybrid imports to src/recolab/__init__.py

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T004 Implement HybridRecommender class skeleton with __init__ method in src/recolab/hybrid.py
- [x] T005 [P] Implement Recommender protocol compliance stub in src/recolab/hybrid.py
- [x] T006 [P] Implement ColdStartHandler protocol compliance stub in src/recolab/hybrid.py
- [x] T007 [P] Add type hints for all HybridRecommender methods in src/recolab/hybrid.py
- [x] T008 Setup existing model integration stubs (ContentModel, UserBasedCF, ItemBasedCF) in src/recolab/hybrid.py

**Checkpoint**: Foundation ready

---

## Phase 3: User Story 1 - Weighted Hybrid Strategy (Priority: P1) 🎯 MVP

**Goal**: Implement weighted scoring mechanism to combine content and collaborative signals

**Independent Test**: Generate hybrid recommendations with different α values and verify score combination logic

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T009 [P] [US1] Write test for HybridRecommender initialization in tests/test_hybrid.py
- [x] T010 [P] [US1] Write test for alpha parameter validation in tests/test_hybrid.py
- [x] T011 [P] [US1] Write test for score normalization in tests/test_hybrid.py
- [x] T012 [P] [US1] Write test for weighted score combination in tests/test_hybrid.py
- [x] T013 [P] [US1] Write test for missing score handling in tests/test_hybrid.py
- [x] T014 [P] [US1] Write test for different alpha values (0.2, 0.5, 0.8) in tests/test_hybrid.py

### Implementation for User Story 1

- [x] T015 [US1] Implement _normalize_scores method in src/recolab/hybrid.py
- [x] T016 [US1] Implement _combine_weighted_scores method in src/recolab/hybrid.py
- [x] T017 [US1] Add alpha parameter validation in src/recolab/hybrid.py
- [x] T018 [US1] Add missing score handling logic in src/recolab/hybrid.py
- [x] T019 [US1] Implement hybrid recommendation generation with score combination in src/recolab/hybrid.py

**Checkpoint**: User Story 1 fully functional

---

## Phase 4: User Story 2 - Adaptive Model Selection (Priority: P1) 🎯 MVP

**Goal**: Implement adaptive model selection based on user activity levels

**Independent Test**: Simulate users with different activity levels and verify appropriate model selection

### Tests for User Story 2 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T020 [P] [US2] Write test for cold-start user detection (≤5 ratings) in tests/test_hybrid.py
- [x] T021 [P] [US2] Write test for active user detection (>20 ratings) in tests/test_hybrid.py
- [x] T022 [P] [US2] Write test for intermediate user detection (5-20 ratings) in tests/test_hybrid.py
- [x] T023 [P] [US2] Write test for model selection logic in tests/test_hybrid.py
- [x] T024 [P] [US2] Write test for threshold boundary cases (exactly 5, 20 ratings) in tests/test_hybrid.py

### Implementation for User Story 2

- [x] T025 [US2] Implement _get_user_rating_count method in src/recolab/hybrid.py
- [x] T026 [US2] Implement _select_model method with adaptive logic in src/recolab/hybrid.py
- [x] T027 [US2] Add activity level evaluation logic in src/recolab/hybrid.py
- [x] T028 [US2] Implement threshold validation in src/recolab/hybrid.py
- [x] T029 [US2] Add model selection logging in src/recolab/hybrid.py
- [x] T030 [US2] Integrate model selection into recommend method in src/recolab/hybrid.py

**Checkpoint**: User Story 2 fully functional

---

## Phase 5: User Story 3 - Confidence Scoring System (Priority: P2)

**Goal**: Implement confidence scoring based on user activity, item popularity, and model agreement

**Independent Test**: Generate recommendations for different user types and verify confidence scores reflect appropriate factors

### Tests for User Story 3 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T031 [P] [US3] Write test for activity confidence computation in tests/test_hybrid.py
- [x] T032 [P] [US3] Write test for popularity confidence computation in tests/test_hybrid.py
- [x] T033 [P] [US3] Write test for model agreement confidence computation in tests/test_hybrid.py
- [x] T034 [P] [US3] Write test for composite confidence score in tests/test_hybrid.py
- [x] T035 [P] [US3] Write test for confidence score range validation [0,1] in tests/test_hybrid.py

### Implementation for User Story 3

- [x] T036 [US3] Implement _compute_activity_confidence method in src/recolab/hybrid.py
- [x] T037 [US3] Implement _compute_popularity_confidence method in src/recolab/hybrid.py
- [x] T038 [US3] Implement _compute_agreement_confidence method in src/recolab/hybrid.py
- [x] T039 [US3] Implement _compute_composite_confidence method in src/recolab/hybrid.py
- [x] T040 [US3] Add confidence score validation in src/recolab/hybrid.py
- [x] T041 [US3] Integrate confidence scoring into recommend method in src/recolab/hybrid.py

**Checkpoint**: User Story 3 fully functional

---

## Phase 6: User Story 4 - Recommendation Explanation Generation (Priority: P1)

**Goal**: Generate human-readable explanations by delegating to selected underlying model

**Independent Test**: Generate recommendations for different model selection scenarios and verify explanations are appropriate to selected model

### Tests for User Story 4 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T042 [P] [US4] Write test for explanation delegation to ContentModel in tests/test_hybrid.py
- [x] T043 [P] [US4] Write test for explanation delegation to UserBasedCF in tests/test_hybrid.py
- [x] T044 [P] [US4] Write test for explanation delegation to ItemBasedCF in tests/test_hybrid.py
- [x] T045 [P] [US4] Write test for explanation fallback when selected model explain() fails in tests/test_hybrid.py
- [x] T046 [P] [US4] Write test for explanation truthfulness based on model selection reason in tests/test_hybrid.py

### Implementation for User Story 4

- [x] T047 [US4] Implement explain method in src/recolab/hybrid.py with model delegation
- [x] T048 [US4] Add selected_model tracking during recommendation generation in src/recolab/hybrid.py
- [x] T049 [US4] Implement fallback explanation generation when model explain() fails in src/recolab/hybrid.py
- [x] T050 [US4] Add explanation truthfulness validation (GUD-002) in src/recolab/hybrid.py
- [x] T051 [US4] Integrate explain method with recommend method in src/recolab/hybrid.py

**Checkpoint**: User Story 4 fully functional

---

## Phase 7: User Story 5 - Model Artifact Persistence (Priority: P1)

**Goal**: Save and load hybrid model artifacts using existing persistence.py module

**Independent Test**: Save hybrid model artifact, load it, and verify consistent state and recommendations

### Tests for User Story 5 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T052 [P] [US5] Write test for to_bundle() method creating valid ModelBundle in tests/test_hybrid.py
- [x] T053 [P] [US5] Write test for from_bundle() method restoring consistent state in tests/test_hybrid.py
- [x] T054 [P] [US5] Write test for save() method using persistence.save_artifact in tests/test_hybrid.py
- [x] T055 [P] [US5] Write test for load() method using persistence.load_artifact in tests/test_hybrid.py
- [x] T056 [P] [US5] Write test for roundtrip persistence (save → load → consistent recommendations) in tests/test_hybrid.py

### Implementation for User Story 5

- [x] T057 [US5] Implement to_bundle() method in src/recolab/hybrid.py following Day 1 pattern
- [x] T058 [US5] Implement from_bundle() class method in src/recolab/hybrid.py following Day 1 pattern
- [x] T059 [US5] Implement save() method delegating to persistence.save_artifact in src/recolab/hybrid.py
- [x] T060 [US5] Implement load() class method delegating to persistence.load_artifact in src/recolab/hybrid.py
- [x] T061 [US5] Add persistence validation (configuration, normalization params, model references) in src/recolab/hybrid.py
- [x] T062 [US5] Test persistence roundtrip with existing persistence.py module in tests/test_hybrid.py

**Checkpoint**: User Story 5 fully functional

---

## Phase 8: Integration & Testing (Cross-Story Concerns)

**Purpose**: System integration, fallback mechanisms, and comprehensive testing

- [x] T063 [P] Implement fit method to train all underlying models in src/recolab/hybrid.py
- [x] T064 [P] Implement recommend_cold_start method for ColdStartHandler protocol in src/recolab/hybrid.py
- [x] T065 [P] Implement fallback chain logic in src/recolab/hybrid.py
- [x] T066 [P] Add fallback event logging in src/recolab/hybrid.py
- [x] T067 [P] Implement get_confidence method for external confidence queries in src/recolab/hybrid.py
- [x] T068 [P] Implement get_model_selection_info method for debugging in src/recolab/hybrid.py
- [x] T069 [P] Add comprehensive error handling for model failures in src/recolab/hybrid.py
- [x] T070 [P] Run integration tests with existing models (ContentModel, UserBasedCF, ItemBasedCF)
- [x] T071 [P] Run performance tests for recommendation latency (<100ms target)
- [x] T072 [P] Run performance tests for model selection overhead (<10ms target)
- [x] T073 [P] Run memory usage tests to verify overhead limits
- [x] T074 [P] Update src/recolab/__init__.py to export HybridRecommender class
- [x] T075 [P] Verify ≥30 passing unit tests for hybrid framework (updated from 20 to account for US4, US5)
- [x] T076 [P] Run pytest with coverage report and verify ≥70% coverage
- [x] T077 [P] Test protocol compliance (Recommender and ColdStartHandler)

**Checkpoint**: Integration and testing complete

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion, can integrate with US1
- **User Story 3 (Phase 5)**: Depends on US1 and US2 completion (needs score combination and model selection)
- **User Story 4 (Phase 6)**: Depends on US2 completion (needs model selection for explanation delegation)
- **User Story 5 (Phase 7)**: Depends on US1, US2, US3 completion (needs complete hybrid state for persistence)
- **Integration (Phase 8)**: Depends on US1, US2, US3, US4, US5 completion

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Integrates with US1 score combination
- **User Story 3 (P2)**: Depends on US1 and US2 - Needs both score combination and model selection to compute confidence
- **User Story 4 (P1)**: Depends on US2 - Needs model selection for explanation delegation
- **User Story 5 (P1)**: Depends on US1, US2, US3 - Needs complete hybrid state for persistence

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Score combination before model selection
- Model selection before confidence scoring
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
3. Complete Phase 3: User Story 1 (Weighted Hybrid Strategy)
4. **STOP and VALIDATE**: Test US1 independently
5. Verify ≥7 tests pass for US1 core functionality
6. Achieve ≥70% coverage for hybrid.py

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Weighted hybrid complete
3. Add User Story 2 → Test independently → Model selection complete
4. Add User Story 3 → Test independently → Confidence scoring complete
5. Add User Story 4 → Test independently → Explanation generation complete
6. Add User Story 5 → Test independently → Persistence complete
7. Integration → Coverage and performance validation → Production ready

### Test Strategy

- **TDD Approach**: Write tests first, ensure they fail, then implement
- **Coverage Target**: ≥70% for hybrid.py code
- **Test Count**: Minimum 30 tests (7 for US1, 6 for US2, 5 for US3, 5 for US4, 5 for US5, + integration tests)
- **Performance Tests**: Verify <100ms recommendations, <10ms model selection overhead
- **Integration Tests**: Verify multi-model coordination and protocol compliance

---

## Success Criteria Validation

### Functional Requirements Coverage

- ✅ FR-001: Weighted hybrid scoring (T015, T012)
- ✅ FR-002: Score normalization (T015, T011)
- ✅ FR-003: Missing score handling (T018, T013)
- ✅ FR-004: Adaptive model selection (T025, T023)
- ✅ FR-005: Confidence scoring (T036-T041)
- ✅ FR-006: Recommender protocol compliance (T005, T063)
- ✅ FR-007: ColdStartHandler protocol compliance (T006, T064)
- ✅ FR-008: Fallback chain implementation (T065, T066)
- ✅ FR-009: Model selection logging (T029, T068)
- ✅ FR-010: Return k recommendations (T019, T030)
- ✅ FR-011: <100ms recommendation latency (T071)
- ✅ FR-012: Edge case handling (T069)
- ✅ FR-013: Explanation generation (T047-T051)
- ✅ FR-014: Model artifact persistence (T057-T062)
- ✅ FR-015: Content-similar alternatives (delegated to ContentModel.similar_items())

### Success Criteria Coverage

- ✅ SC-001: <100ms recommendations (T071)
- ✅ SC-002: 100% model selection correctness (T020-T024)
- ✅ SC-003: Confidence score accuracy (T031-T035)
- ✅ SC-004: 100% fallback success rate (T065, T066)
- ✅ SC-005: ≥70% coverage (T076, T073)
- ✅ SC-006: ≥30 passing tests (T075)
- ✅ SC-007: Weighted scoring correctness (T011-T014)
- ✅ SC-008: Protocol compliance (T077)
- ✅ SC-009: Model selection logging (T029, T068)
- ✅ SC-010: Integration with existing models (T070)
- ✅ SC-011: Explanation generation (T042-T046)
- ✅ SC-012: Model artifact persistence (T052-T056)
- ✅ SC-013: Content-similar alternatives (ContentModel.similar_items())

### Total Task Count

- **Total Tasks**: 77 tasks
- **Setup Tasks**: 3 tasks
- **Foundational Tasks**: 5 tasks
- **User Story 1 Tasks**: 11 tasks (6 tests + 5 implementation)
- **User Story 2 Tasks**: 11 tasks (5 tests + 6 implementation)
- **User Story 3 Tasks**: 11 tasks (5 tests + 6 implementation)
- **User Story 4 Tasks**: 10 tasks (5 tests + 5 implementation)
- **User Story 5 Tasks**: 11 tasks (5 tests + 6 implementation)
- **Integration Tasks**: 15 tasks
- **Parallel Opportunities**: 21 tasks marked with [P]

### MVP Scope

**Completed MVP (Day 2 AM)**: Phase 1-4 complete (30 tasks done)
- **Tasks done**: T001-T030 ✅
- **Test Count**: 16 tests for core functionality ✅

### Full Feature Scope (Day 2 Required)

**Remaining**: T031-T077 (confidence scoring, explanation generation, persistence, integration, testing)
- **Duration**: Estimated Day 2 AM + Day 2 PM (explanation and persistence added to morning scope)
- **Coverage**: ≥70% target ✅

### Full Feature Scope (Day 2 Required)

**Remaining**: T031-T056 (confidence scoring, integration, testing)
- **Duration**: Estimated second half of Day 2 morning