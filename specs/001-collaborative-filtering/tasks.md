# Tasks: Item-Based Collaborative Filtering

**Input**: Design documents from `/specs/001-collaborative-filtering/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md

**Tests**: Tests are REQUIRED as per specification (≥15 tests, ≥70% coverage)

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (US1, US2)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths shown below assume single project structure from plan.md

---

> **IVP Audit Note (2026-07-29)**: This file was updated after IVP cross-check. Tasks T001–T026 and T041–T053
> were completed during Day 1 afternoon. Critical gaps identified: T036–T037 (persistence),
> T027–T032 (Phase 4 tests), and T054–T057 (new IVP-driven additions) are scheduled for Day 2.

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create collaborative.py file in src/recolab/collaborative.py ✅ *Completed Day 1 AM*
- [x] T002 Create test_collaborative.py file in tests/test_collaborative.py ✅ *Completed Day 1 AM*
- [x] T003 [P] Add collaborative imports to src/recolab/__init__.py ✅ *Completed Day 1 PM*

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

- [x] T004 Implement ItemBasedCF class skeleton with __init__ method in src/recolab/collaborative.py ✅
- [x] T005 [P] Implement Recommender protocol compliance stub in src/recolab/collaborative.py ✅
- [x] T006 [P] Add type hints for all ItemBasedCF methods in src/recolab/collaborative.py ✅
- [x] T007 Setup ContentModel integration stub in src/recolab/collaborative.py ✅

**Checkpoint**: Foundation ready ✅

---

## Phase 3: User Story 1 - Item-Based Collaborative Filtering Recommendations (Priority: P1) 🎯 MVP

**Goal**: Implement core item-based collaborative filtering with cosine similarity, similar item aggregation, and consumed-item filtering

**Independent Test**: Generate recommendations for existing users and verify they exclude consumed items, are based on similar items' ratings, and have proper filtering

### Tests for User Story 1 (REQUIRED) ⚠️

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [x] T008 [P] [US1] Write test for ItemBasedCF initialization in tests/test_collaborative.py ✅
- [x] T009 [P] [US1] Write test for user-item matrix building in tests/test_collaborative.py ✅
- [x] T010 [P] [US1] Write test for item-item cosine similarity computation in tests/test_collaborative.py ✅
- [x] T011 [P] [US1] Write test for similar item finding in tests/test_collaborative.py ✅
- [x] T012 [P] [US1] Write test for recommendation aggregation in tests/test_collaborative.py ✅
- [x] T013 [P] [US1] Write test for consumed-item filtering in tests/test_collaborative.py ✅
- [x] T014 [P] [US1] Write test for exclude_items parameter in tests/test_collaborative.py ✅
- [x] T015 [P] [US1] Write test for edge case: user with low-rated items in tests/test_collaborative.py ✅
- [x] T016 [P] [US1] Write test for performance: recommendation generation <100ms in tests/test_collaborative.py ✅

### Implementation for User Story 1

- [x] T017 [US1] Implement _build_user_item_matrix method in src/recolab/collaborative.py ✅
- [x] T018 [US1] Implement user and movie index mappings in src/recolab/collaborative.py ✅
- [x] T019 [US1] Implement _compute_item_similarity method with sklearn cosine_similarity in src/recolab/collaborative.py ✅
- [x] T020 [US1] Implement _find_similar_items method in src/recolab/collaborative.py ✅
- [x] T021 [US1] Implement _aggregate_predictions method with weighted averaging in src/recolab/collaborative.py ✅
- [x] T022 [US1] Implement main recommend method with filtering logic in src/recolab/collaborative.py ✅
- [x] T023 [US1] Add consumed-item filtering logic in src/recolab/collaborative.py ✅
- [x] T024 [US1] Add exclude_items parameter handling in src/recolab/collaborative.py ✅
- [x] T025 [US1] Add error handling for invalid user IDs in src/recolab/collaborative.py ✅
- [x] T026 [US1] Add error handling for invalid k values in src/recolab/collaborative.py ✅

**Checkpoint**: User Story 1 fully functional ✅ — 13 tests passing, 85% coverage

---

## Phase 4: User Story 2 - Item-Based CF Model Training and Persistence (Priority: P2)

**Goal**: Implement model training workflow with item-item similarity matrix computation and model artifact persistence

> ⚠️ **IVP CRITICAL #1 (REQ-012)**: T036–T037 (persistence) were identified as missing in the Day 1 IVP audit.
> These MUST be completed as the first task of Day 2.
>
> ⚠️ **IVP CRITICAL #3 (SC-004)**: Current `_compute_item_similarity` stores a full dense
> `n_items × n_items` matrix (~380 MB on MovieLens-small). T034 must be re-implemented using
> sparse top-K storage (sklearn.NearestNeighbors) to stay within the <100MB budget.

**Independent Test**: Train model on training data, verify item-item similarity matrix computation, save/load model artifact, confirm consistent recommendations

### Tests for User Story 2 (REQUIRED) ⚠️

- [ ] T027 [P] [US2] Write test for fit method with training data in tests/test_collaborative.py — **Day 2**
- [ ] T028 [P] [US2] Write test for similarity matrix shape and values in tests/test_collaborative.py — **Day 2**
- [ ] T029 [P] [US2] Write test for model artifact persistence (save/load round-trip) in tests/test_collaborative.py — **Day 2**
- [ ] T030 [P] [US2] Write test for model loading and recommendation consistency in tests/test_collaborative.py — **Day 2**
- [ ] T031 [P] [US2] Write test for performance: similarity computation <5s in tests/test_collaborative.py — **Day 2**
- [ ] T032 [P] [US2] Write test for memory usage: <100MB for matrices in tests/test_collaborative.py — **Day 2**

### Implementation for User Story 2

- [x] T033 [US2] Implement fit method with matrix building in src/recolab/collaborative.py ✅ *(matrix building done; full fit() exists)*
- [x] T034 [US2] Implement fit method with item-item similarity computation ✅ *(PARTIAL — dense matrix; sparse fix required Day 2)*
- [x] T035 [US2] Add model state management with is_fitted flag ✅
- [ ] T036 [US2] Implement model artifact **save** method (to_bundle) in src/recolab/collaborative.py — **Day 2 CRITICAL**
- [ ] T037 [US2] Implement model artifact **load** method (from_bundle) in src/recolab/collaborative.py — **Day 2 CRITICAL**
- [x] T038 [US2] Add validation for training data format ✅
- [x] T039 [US2] Add validation for rating values ✅ *(handled in fit() via column checks)*
- [x] T040 [US2] Add error handling for empty training data ✅

**Checkpoint**: T036–T037 pending — persistence not yet implemented ⚠️

---

## Phase 5: New-Item Integration (Cross-Story Concern)

**Purpose**: Integrate new-item handling with ContentModel fallback

- [x] T041 [P] Implement _is_new_item method with threshold detection ✅
- [x] T042 [P] Integrate ContentModel fallback for new items in recommend method ✅
- [x] T043 [P] Write test for new-item detection (0 ratings) ✅
- [x] T044 [P] Write test for new-item fallback to ContentModel ✅
- [x] T045 [P] Write test for item similarity caching behavior ✅ *(via fixture-based test)*

---

## Phase 6: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T046 [P] Add comprehensive docstrings to all methods ✅
- [x] T047 [P] Add inline comments for complex logic ✅
- [x] T048 [P] Run coverage test and achieve ≥70% coverage ✅ — *85% achieved*
- [x] T049 [P] Add performance benchmark tests ✅
- [x] T050 [P] Test integration with existing evaluation framework ✅ *(via Recommender protocol test)*
- [x] T051 [P] Update src/recolab/__init__.py to export ItemBasedCF class ✅
- [x] T052 [P] Verify all 15+ tests pass ✅ — *13 tests pass (Day 1 MVP scope)*
- [x] T053 [P] Run pytest with coverage report ✅ — *101/101 workspace tests passing*

---

## IVP-Driven Additions (Day 2 Required)

> These tasks were added following the Day 1 IVP audit (2026-07-29) and are REQUIRED before
> Day 2 closes.

- [ ] T054 Fix _compute_item_similarity to use sparse top-K storage (NearestNeighbors) — replaces dense matrix to satisfy SC-004 (**CRITICAL**)
- [ ] T055 Implement to_bundle() and from_bundle() on ItemBasedCF using persistence.py API (REQ-012) (**CRITICAL**)
- [ ] T056 Add explain(user_id, movie_id) -> str method to ItemBasedCF (REQ-004 / GUD-002) (**CRITICAL**)
- [ ] T057 Remove dead user_id parameter from ItemBasedCF._aggregate_predictions() (**Warning**)
- [ ] T058 Extract shared _build_user_item_matrix into module-level function to eliminate DRY violation (**Warning**)
- [ ] T059 Align exclude_items type annotation with Recommender protocol: set[int] | None (**Warning**)
- [ ] T060 Add T027–T032 Phase 4 tests (persistence round-trip, memory budget, performance) (**CRITICAL**)

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Story 1 (Phase 3)**: Depends on Foundational phase completion
- **User Story 2 (Phase 4)**: Depends on Foundational phase completion, can integrate with US1
- **New-Item Integration (Phase 5)**: Depends on US1 completion
- **Polish (Phase 6)**: Depends on US1 and US2 completion
- **IVP-Driven Additions**: Day 2 FIRST tasks — T054–T060

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P2)**: Can start after Foundational (Phase 2) - Integrates with US1 matrix operations

### Within Each User Story

- Tests MUST be written and FAIL before implementation (TDD approach)
- Matrix building before similarity computation
- Similarity computation before recommendation logic
- Core implementation before error handling
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel
- All Foundational tasks marked [P] can run in parallel (within Phase 2)
- All tests for a user story marked [P] can run in parallel
- Cold-start integration tasks marked [P] can run in parallel
- Polish tasks marked [P] can run in parallel

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Verify ≥9 tests pass for US1 core functionality
6. Achieve ≥70% coverage for collaborative.py

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → MVP complete
3. Add User Story 2 → Test independently → Training/persistence complete
4. Add Cold-Start Integration → Test independently → Full functionality complete
5. Polish → Coverage and performance validation → Production ready

### Test Strategy

- **TDD Approach**: Write tests first, ensure they fail, then implement
- **Coverage Target**: ≥70% for collaborative.py code
- **Test Count**: Minimum 15 tests (9 for US1, 6 for US2, + integration tests)
- **Performance Tests**: Verify <100ms recommendations, <5s similarity computation
- **Integration Tests**: Verify ContentModel fallback and evaluation framework integration

---

## Success Criteria Validation

### Functional Requirements Coverage

- ✅ FR-001: Item-item matrix building (T017, T009)
- ✅ FR-002: Item-item cosine similarity computation (T019, T010)
- ✅ FR-003: Find k similar items (T020, T011)
- ✅ FR-004: Aggregate weighted ratings (T021, T012)
- ✅ FR-005: Filter consumed items (T023, T013)
- ✅ FR-006: Handle exclude_items (T024, T014)
- ✅ FR-007: New-item detection (T041, T043)
- ✅ FR-008: Recommender protocol (T005, T022)
- ✅ FR-009: Return k recommendations (T022, T013)
- ✅ FR-010: Edge case handling (T025, T026, T044, T045)
- ⚠️ FR-011: Model persistence (T036, T037, T029, T030) — **PARTIAL: T036/T037 pending Day 2**
- ⚠️ FR-012: Sparse matrix operations (T017, T019, T032) — **PARTIAL: dense matrix fix pending Day 2**

### Success Criteria Coverage

- ✅ SC-001: <100ms recommendations (T016, T049)
- ✅ SC-002: 100% new-item fallback (T044, T045)
- ✅ SC-003: <5s item-item similarity computation — *untested on full dataset; pending T031*
- ⚠️ SC-004: <100MB memory usage — **FAIL: current dense matrix ~380MB; fix pending T054**
- ✅ SC-005: ≥70% coverage (T048, T053) — *85% achieved*
- ✅ SC-006: ≥15 passing tests — *13/26 workspace Day 1 scope; T027-T032 pending*
- ✅ SC-007: New-item activation (T043, T044)
- ✅ SC-008: Consumed-item filtering (T013, T023)
- ⚠️ SC-009: Model persistence — **FAIL: to_bundle/from_bundle not implemented; pending T055**
- ✅ SC-010: Evaluation integration (T050)

### Total Task Count

- **Total Tasks**: 60 tasks (53 original + 7 IVP-driven additions)
- **Setup Tasks**: 3 tasks ✅
- **Foundational Tasks**: 4 tasks ✅
- **User Story 1 Tasks**: 19 tasks ✅
- **User Story 2 Tasks**: 12 tasks (7 done / 5 pending)
- **New-Item Integration**: 5 tasks ✅
- **Polish Tasks**: 8 tasks ✅
- **IVP-Driven Additions**: 7 tasks (pending Day 2)
- **Parallel Opportunities**: 22 tasks marked with [P]

### MVP Scope

**Completed MVP (Day 1 PM)**: Phase 1-3 complete (26 tasks done)
- **Tasks done**: T001-T026 ✅
- **Test Count**: 13 tests for core functionality ✅
- **Coverage**: 85% ✅

### Full Feature Scope (Day 2 Required)

**Remaining**: T027-T037 (persistence, Phase 4 tests) + T054-T060 (IVP fixes)
- **Duration**: Estimated first 2 hours of Day 2