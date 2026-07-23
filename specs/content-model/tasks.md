# Implementation Plan: Content Model Tasks

**Input**: `specs/content-model/plan.md`, `specs/content-model/spec.md`
**Week**: 2 — builds on `specs/data-evaluation-foundation/`
**Carried Forward**: CF-2 · CF-3 · harness contract

## Format: `[ID] [P?] [Story?] Description — file path`

- **[P]**: Parallelisable (independent files, no pending dependencies)
- **[US1–5]**: User story from spec.md
- Run gate after every phase: `ruff check src/ tests/` · `mypy src/` · `pytest -q`

---

## Overview

| Phase | Goal | Est. |
|---|---|---|
| 1 | Hygiene + dependency pins | 30 min |
| 2 | `interfaces.py` protocols | 45 min |
| 3 | Fixtures + `test_split.py` | 45 min |
| 4 | `ContentModel` core (6 sub-steps) | 2.5 hr |
| 5 | Complete `test_content.py` | 1.5 hr |
| 6 | `__init__.py` + integration gate | 30 min |
| 7 | Docs + portal prep | 30 min |
| 8 | IVP validation report | 30 min |

---

## Tasks

### Phase 1: Setup & Hygiene

**Purpose**: Clean house, update pins, verify 32 existing tests still pass before touching anything.

- [ ] 1. Check `recolab-hybrid-recommender/recolab/` is empty → add to `.gitignore` or delete — `.gitignore`
- [ ] 2. Update `scikit-learn>=1.3.0` → `scikit-learn>=1.4.0` — `pyproject.toml`
- [ ] 3. Add `pytest-cov>=4.0.0` under `[project.optional-dependencies.dev]` — `pyproject.toml`
- [ ] 4. Run `pip install -e ".[dev]"` in venv and verify `pytest -q` shows **32 passed**

**Checkpoint**: 32 tests pass. Ruff and mypy exit 0. Ready to build.

---

## Phase 2: Interfaces (Protocols + FeatureError)

**Goal**: Lock the shared `Recommender` and `ColdStartHandler` contracts before writing any model code. Resolves CF-3 (partial).

**Independent Test**: `isinstance(PopularityModel().fit(df), Recommender)` → `True`

- [ ] 5. Create `Recommender` Protocol (`recommend(user_id,k,exclude_items)->list[int]`) — `src/recolab/interfaces.py`
- [ ] 6. Create `ColdStartHandler` Protocol (`recommend_cold_start(genres,liked_ids,k)->list[int]`) — `src/recolab/interfaces.py`
- [ ] 7. Create `FeatureError(ValueError)` with `movie_id: int` attribute — `src/recolab/interfaces.py`
- [ ] 8. [P] Write `test_popularity_satisfies_recommender_protocol` (AC-007) — `tests/test_interfaces.py`
- [ ] 9. [P] Write `test_feature_error_carries_movie_id` and `test_feature_error_message_format` — `tests/test_interfaces.py`
- [ ] 10. Add placeholder `test_content_satisfies_protocols` with `pytest.skip` — `tests/test_interfaces.py`
- [ ] 11. Export `Recommender`, `ColdStartHandler`, `FeatureError` in `__all__` — `src/recolab/__init__.py`

**Checkpoint**: `pytest -q` → 34+ passed (2 new, 1 skipped). `mypy src/` clean.

---

## Phase 3: Test Fixtures + Fill Week-1 Gap

**Goal**: Commit a small dataset so CF-2 floor test always runs in CI. Cover `split.py` edge cases missed in Week 1.

**Independent Test**: `pytest tests/test_split.py -v` all pass. `pytest --cov=src/recolab/split` → ≥80%.

- [ ] 12. Run fixture-gen script locally and commit outputs — `tests/fixtures/ratings_sample.csv`, `tests/fixtures/movies_sample.csv`

  ```python
  # Run once locally:
  import pandas as pd, numpy as np
  rng = np.random.default_rng(42)
  ratings = pd.read_csv("data/ml-latest-small/ratings.csv")
  movies  = pd.read_csv("data/ml-latest-small/movies.csv")
  uids    = rng.choice(ratings["userId"].unique(), 50, replace=False)
  sub     = ratings[ratings["userId"].isin(uids)]
  sub.to_csv("tests/fixtures/ratings_sample.csv", index=False)
  movies[movies["movieId"].isin(sub["movieId"].unique())].to_csv(
      "tests/fixtures/movies_sample.csv", index=False)
  ```

- [ ] 13. [P] Write `test_split_no_leakage` — `tests/test_split.py`
- [ ] 14. [P] Write `test_leakage_detected` (AC-009, `validate_no_leakage` raises on shared pair) — `tests/test_split.py`
- [ ] 15. [P] Write `test_split_empty_dataframe` — `tests/test_split.py`
- [ ] 16. [P] Write `test_single_rating_user_goes_to_train` — `tests/test_split.py`
- [ ] 17. [P] Write `test_train_ratio_boundary` (`train_ratio=1.0`) — `tests/test_split.py`
- [ ] 18. [P] Write `test_save_split_creates_files` — `tests/test_split.py`

**Checkpoint**: 6+ new split tests pass. Coverage ≥80% on `split.py`.

---

## Phase 4: ContentModel Core

**Purpose**: Implement `ContentModel` satisfying `Recommender` + `ColdStartHandler` protocols.

**⚠️ CRITICAL**: Complete sub-steps in order — each one depends on the previous.

### 4a — `__init__` and `fit` (User Stories 1, 2, 3)

- [ ] 19. Create `ContentModel` class skeleton with `__init__(use_tags,min_tag_count)` — `src/recolab/content.py`
- [ ] 20. Implement `_build_corpus(movies_df, tags_df=None)->list[str]`: split genres on `|`, filter `"(no genres listed)"`, optionally append tag tokens — `src/recolab/content.py`
- [ ] 21. Implement `fit(movies_df, tags_df=None)->ContentModel`: fit `TfidfVectorizer(norm="l2")`, store `_feature_matrix`, `_movie_ids`, `_movie_id_to_row`, `_zero_norm_ids`, `_movies_df` — `src/recolab/content.py`
- [ ] 22. Implement `_get_row(movie_id)->int`: O(1) lookup, raises `FeatureError` if zero-norm — `src/recolab/content.py`

**Checkpoint**: `ContentModel(use_tags=False).fit(small_movies_df)` runs without error.

### 4b — `similar_items` (User Story 1)

- [ ] 23. [US1] Implement `similar_items(movie_id,k,exclude_items)->list[tuple[int,float]]`: on-demand `feature_matrix @ query.T`, clip scores to [0,1], exclude query + exclude_items, return top-k — `src/recolab/content.py`

**Checkpoint**: `test_similar_items_known_pair` passes (Toy Story → A Bug's Life).

### 4c — `recommend` (User Story 2)

- [ ] 24. [US2] Implement `recommend(user_id,k,exclude_items,user_liked_items)->list[int]`: deduplicate liked items, average their vectors as query, fallback to popularity-prior if none, filter exclude_items — `src/recolab/content.py`

**Checkpoint**: `test_recommend_excludes_consumed` passes.

### 4d — `recommend_cold_start` (User Story 3)

- [ ] 25. [US3] Implement `recommend_cold_start(genres,liked_movie_ids,k)->list[int]`: deduplicate genres, build genre_vec via `_tfidf.transform`, average liked_vec, combine 50/50, raise `FeatureError` if both empty, filter liked_movie_ids from results — `src/recolab/content.py`

**Checkpoint**: `test_cold_start_genres_only` passes.

### 4e — `get_explanation` (User Story 4)

- [ ] 26. [US4] Implement `get_explanation(query_id,target_id)->str`: intersect genre sets, return `"Because both are {genres} films"` or `"Similar content profile"` — `src/recolab/content.py`

**Checkpoint**: Explanation never empty, never cites a genre not in both movies.

### 4f — `to_bundle` / `from_bundle` (User Story 5)

- [ ] 27. [US5] Implement `to_bundle(metrics=None)->ModelBundle`: raises `ValueError` if unfitted; metadata schema per plan — `src/recolab/content.py`
- [ ] 28. [US5] Implement `from_bundle(cls,bundle)->ContentModel`: type-checks bundle.model — `src/recolab/content.py`

**Checkpoint**: `pytest -q` still passing. `mypy src/` clean.

---

## Phase 5: Complete Test Suite

**Goal**: All 20+ test functions for `ContentModel`. CF-2 floor test uses committed fixtures (no skip).

- [ ] 29. [P] [US1] Write `test_fit_produces_nonzero_vectors` — `tests/test_content.py`
- [ ] 30. [P] [US1] Write `test_feature_error_on_no_genres_listed` — `tests/test_content.py`
- [ ] 31. [P] [US1] Write `test_similar_items_returns_k_results` — `tests/test_content.py`
- [ ] 32. [P] [US1] Write `test_similar_items_excludes_query` — `tests/test_content.py`
- [ ] 33. [P] [US1] Write `test_similar_items_excludes_items` — `tests/test_content.py`
- [ ] 34. [P] [US1] Write `test_similar_items_scores_in_range` — `tests/test_content.py`
- [ ] 35. [P] [US1] Write `test_similar_items_known_pair` (AC-002) — `tests/test_content.py`
- [ ] 36. [P] [US1] Write `test_feature_error_on_zero_norm` (AC-005) — `tests/test_content.py`
- [ ] 37. [P] [US1] Write `test_new_item_cold_start_safe` (AC-004) — `tests/test_content.py`
- [ ] 38. [P] [US2] Write `test_recommend_excludes_consumed` (AC-003) — `tests/test_content.py`
- [ ] 39. [P] [US2] Write `test_recommend_empty_exclude_all_catalog` — `tests/test_content.py`
- [ ] 40. [P] [US2] Write `test_recommend_deduplicates_liked_items` — `tests/test_content.py`
- [ ] 41. [P] [US3] Write `test_cold_start_genres_only` (AC-004) — `tests/test_content.py`
- [ ] 42. [P] [US3] Write `test_cold_start_liked_movies_only` — `tests/test_content.py`
- [ ] 43. [P] [US3] Write `test_cold_start_deduplicates_genres` — `tests/test_content.py`
- [ ] 44. [P] [US3] Write `test_cold_start_empty_input_raises` — `tests/test_content.py`
- [ ] 45. [P] [US3] Write `test_cold_start_result_excludes_liked` — `tests/test_content.py`
- [ ] 46. [P] [US4] Write `test_explanation_cites_shared_genres` — `tests/test_content.py`
- [ ] 47. [P] [US4] Write `test_explanation_no_false_genre_claim` — `tests/test_content.py`
- [ ] 48. [P] [US4] Write `test_explanation_fallback_when_no_overlap` — `tests/test_content.py`
- [ ] 49. [P] [US5] Write `test_persistence_roundtrip` (AC-006) — `tests/test_content.py`
- [ ] 50. [P] [US5] Write `test_unfitted_model_to_bundle_raises` — `tests/test_content.py`
- [ ] 51. [P] Write `test_deterministic_same_input_same_output` — `tests/test_content.py`
- [ ] 52. Write `test_content_beats_random_floor` using fixtures (CF-2, AC-001) — `tests/test_content.py`
- [ ] 53. Un-skip `test_content_satisfies_protocols` (AC-007, AC-008) — `tests/test_interfaces.py`

**Checkpoint**: ~60 total tests pass. `pytest --cov` → ≥70% on `content.py`.

---

## Phase 6: Integration Gate

**Purpose**: Finalize public API, verify CI is green end-to-end.

- [ ] 54. Add `from recolab.content import ContentModel` to imports — `src/recolab/__init__.py`
- [ ] 55. Add `"ContentModel"` to `__all__` — `src/recolab/__init__.py`
- [ ] 56. Run full gate: `ruff check src/ tests/` + `mypy src/` + `pytest -q` + `pytest --cov`
- [ ] 57. Push to GitHub branch → verify CI (ruff + mypy + pytest) is green

**Checkpoint**: ~60 tests pass. CI green. No regressions vs Week-1 baseline.

---

## Phase 7: Documentation & Portal Prep

- [ ] 58. Update `README.md`: change title, add "What's Built" table (4 models with status), update tech stack, add Quick Start — `README.md`
- [ ] 59. Create `learning/week-2/technical-notes-week2.md` (references ADR-004, 005, 006, CF-2 results)
- [ ] 60. Fill in `learning/week-2/weekly-progress-note.md` with actual results, test output, screenshots
- [ ] 61. **USER ACTION**: Submit to Devnexes portal (GitHub link + commit + evidence)

---

## Phase 8: IVP Validation Report

**Purpose**: Independent 5-perspective review matching Week-1 validation quality.

- [ ] 62. Write `history/validation/week-2-ivp-report.md`:
  - **Security**: no secrets, no PII, FeatureError surfaces cleanly
  - **Constitution**: typed, modular, ruff + mypy pass, `default_rng` used where needed
  - **Specification**: verify each FR-001..007 and SC-001..009 against actual code
  - **Quality**: read `similar_items` math, verify L2-norm + clip + FeatureError guard
  - **Conflict**: no stale `week-1/` paths, ADR-004/005/006 match implementation
  - Record carried-forward items for Week 3

**Checkpoint**: Report exists. Overall verdict = **PASS**. Week 2 complete.

---

## Dependencies & Execution Order

- **Phase 1**: No dependencies — start immediately
- **Phase 2**: Depends on Phase 1 (gate must pass)
- **Phase 3**: Depends on Phase 1 (gate must pass) — can run in parallel with Phase 2
- **Phase 4**: Depends on Phase 2 (interfaces must exist) — sub-steps 4a→4b→4c→4d→4e→4f are sequential
- **Phase 5**: Depends on Phase 4 complete — all T029..T053 can run in parallel
- **Phase 6**: Depends on Phase 5 complete
- **Phase 7**: Depends on Phase 6 CI green
- **Phase 8**: Depends on Phase 7 complete

### User Story Dependencies

- **US1** (similar items): Depends on Phase 4a+4b
- **US2** (recommendations): Depends on Phase 4a+4b+4c
- **US3** (cold-start): Depends on Phase 4a+4d — independently testable
- **US4** (explanations): Depends on Phase 4a+4e — independently testable
- **US5** (persistence): Depends on Phase 4a-4f complete

---

## Implementation Strategy

### MVP (User Stories 1–3 only)

1. Complete Phases 1–4 (through 4d)
2. Write tests for US1, US2, US3 only (T029–T045, T052)
3. **Validate independently**: cold-start returns sensible results, consumed items excluded, Toy Story → A Bug's Life
4. Then add US4 (explanations) and US5 (persistence)

### Parallel Opportunities

All tasks marked `[P]` in Phase 5 can run simultaneously — they are different test functions in the same file with no shared state.

---

## Notes

- `[P]` tasks = different files or independent test functions, no shared state
- `[US1–5]` maps each task to a user story for traceability
- Never modify `metrics.py` or `baseline.py` — Week-1 contracts are frozen
- One commit per phase (or per logical sub-step in Phase 4)
- `pytest -q` gate runs after every phase before moving on

---

## Task Dependency Graph

```json
{
  "waves": [
    { "wave": 1, "tasks": ["T001","T002","T003","T004"], "description": "Hygiene" },
    { "wave": 2, "tasks": ["T005","T006","T007","T008","T009","T010","T011"], "description": "Interfaces" },
    { "wave": 3, "tasks": ["T012","T013","T014","T015","T016","T017","T018"], "description": "Fixtures + split tests — parallel with wave 2 after T001-T004" },
    { "wave": 4, "tasks": ["T019","T020","T021","T022","T023","T024","T025","T026","T027","T028"], "description": "ContentModel — sequential sub-steps" },
    { "wave": 5, "tasks": ["T029","T030","T031","T032","T033","T034","T035","T036","T037","T038","T039","T040","T041","T042","T043","T044","T045","T046","T047","T048","T049","T050","T051","T052","T053"], "description": "Test suite — all parallelisable" },
    { "wave": 6, "tasks": ["T054","T055","T056","T057"], "description": "Integration gate" },
    { "wave": 7, "tasks": ["T058","T059","T060","T061"], "description": "Docs + portal" },
    { "wave": 8, "tasks": ["T062"], "description": "IVP report" }
  ],
  "critical_path": ["T001","T005","T019","T023","T024","T025","T052","T056","T062"],
  "estimated_hours": "7-9"
}
```
