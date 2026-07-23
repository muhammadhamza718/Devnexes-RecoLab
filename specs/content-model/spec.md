# Feature Specification: Content-Based Recommendation Model

**Feature Branch**: `content-model`
**Created**: 2026-07-22
**Status**: Approved
**Week**: 2 of 6 — builds on `specs/data-evaluation-foundation/`
**Carried Forward**: CF-2 (random floor assertion), CF-3 (cold-start interface), harness contract

---

## User Scenarios & Testing

### User Story 1 — Item Similarity (Priority: P1)

A user clicks a movie. The system shows similar movies based on genre content.

**Why this priority**: Core content-based feature. Everything else builds on it.

**Independent Test**: Call `ContentModel.similar_items(toy_story_id, k=5)` and verify "A Bug's Life" appears. All returned scores must be in [0, 1].

**Acceptance Scenarios**:

1. **Given** "Toy Story" (`Adventure|Animation|Children|Comedy|Fantasy`), **when** `similar_items(id, k=5)` is called, **then** "A Bug's Life" (`Adventure|Animation|Children|Comedy`) appears in results.
2. **Given** any movie ID, **when** `similar_items` is called, **then** the query movie itself is NOT in the returned list.
3. **Given** `exclude_items={A, B}`, **when** `similar_items` is called, **then** neither A nor B appear in results.
4. **Given** a movie with `genres = "(no genres listed)"`, **when** `similar_items` is called on it, **then** `FeatureError` is raised — never NaN.
5. **Given** the same movie ID called twice, **when** results compared, **then** they are identical (deterministic).

---

### User Story 2 — User Recommendations via Content (Priority: P1)

A returning user gets personalized top-N movie suggestions based on movies they liked.

**Why this priority**: Required by Devnexes brief (REQ-001 / REQ-003). Directly satisfies AC-003 (consumed-item filtering).

**Independent Test**: Call `recommend(user_id=1, k=10, exclude_items={1,2,3}, user_liked_items=[1,2,3])` and verify none of `{1,2,3}` appear in results.

**Acceptance Scenarios**:

1. **Given** a user with liked items `[1,2,3]` and `exclude_items={1,2,3}`, **when** `recommend` is called, **then** none of `{1,2,3}` appear in results.
2. **Given** `exclude_items` containing the entire catalog, **when** `recommend` is called, **then** an empty list is returned — not a crash.
3. **Given** duplicate entries in `user_liked_items`, **when** `recommend` is called, **then** duplicates are deduplicated before scoring (no double-weighting).
4. **Given** `user_liked_items=[]`, **when** `recommend` is called, **then** system falls back to popularity-prior, not an error.

---

### User Story 3 — Cold-Start for New Users (Priority: P1)

A brand-new user with no history picks genres or movies they like. The system gives them relevant suggestions immediately.

**Why this priority**: Project title is "Hybrid Recommendation Engine with **Cold-Start Handling**" — this is the defining feature. CF-3 from Week 1 audit.

**Independent Test**: Call `recommend_cold_start(genres=["Action","Sci-Fi"], liked_movie_ids=[], k=5)` and verify ≥1 result is returned, none of the liked movies appear, and no crash occurs.

**Acceptance Scenarios**:

1. **Given** `genres=["Action","Sci-Fi"]` and `liked_movie_ids=[]`, **when** `recommend_cold_start` is called, **then** ≥1 result returned, no fake history invented.
2. **Given** duplicate genres `["Action","Action","Sci-Fi"]`, **when** `recommend_cold_start` is called, **then** genres are deduplicated before scoring.
3. **Given** `liked_movie_ids=[1210]`, **when** `recommend_cold_start(k=5)` is called, **then** `1210` does NOT appear in results.
4. **Given** `genres=[]` and `liked_movie_ids=[]`, **when** `recommend_cold_start` is called, **then** `FeatureError` is raised (no query basis).
5. **Given** same inputs called twice, **when** results compared, **then** identical (deterministic — no randomness in content scoring).

---

### User Story 4 — Recommendation Explanations (Priority: P2)

Every recommended movie shows a plain-English reason why it was suggested.

**Why this priority**: Required by Devnexes brief (REQ-004 / GUD-002). Needed for Week 6 demo polish.

**Independent Test**: Call `get_explanation(toy_story_id, bugs_life_id)` and verify the string mentions at least one shared genre and is never empty.

**Acceptance Scenarios**:

1. **Given** two movies sharing `["Action","Adventure"]`, **when** `get_explanation` is called, **then** returned string contains those genre names.
2. **Given** two movies with no genre overlap, **when** `get_explanation` is called, **then** string does NOT claim genre similarity.
3. **Given** any two movies, **then** explanation string is never empty (fallback: `"Similar content profile"`).

---

### User Story 5 — Content Model Save & Load (Priority: P2)

A trained model is saved to disk and reloaded without retraining.

**Why this priority**: Required by brief (REQ-012). Enables reproducible evaluation and deployment.

**Independent Test**: Save `ContentModel` via `to_bundle()`, reload via `from_bundle()`, call `similar_items` — results must match original within floating-point tolerance.

**Acceptance Scenarios**:

1. **Given** a fitted `ContentModel`, **when** saved and reloaded, **then** `similar_items` returns identical results (tolerance `1e-9`).
2. **Given** an unfitted `ContentModel`, **when** `to_bundle()` is called, **then** `ValueError` is raised.

---

### Edge Cases

- Movie with `"(no genres listed)"` as query → `FeatureError`, never NaN
- All items in catalog excluded → empty list, not crash
- User has rated every movie → empty list with no error
- `user_liked_items` where all movies have zero-norm vectors → `FeatureError`
- Tags file has ~16% coverage (1,589 / 9,742 movies) → genres-only is primary; tags are optional augmentation only (see ADR-004)

---

## Requirements

### Functional Requirements

- **FR-001**: System MUST compute TF-IDF genre feature vectors for all catalog movies (genres as primary, tags as optional)
- **FR-002**: System MUST return top-k cosine-similar movies for any valid movie query
- **FR-003**: System MUST exclude already-rated/consumed items from all recommendation outputs
- **FR-004**: System MUST provide cold-start recommendations from genre preferences and/or liked movie IDs — without inventing fake history
- **FR-005**: System MUST raise `FeatureError` (not NaN / crash) when a zero-norm movie is queried
- **FR-006**: System MUST return a truthful, non-empty explanation string for each recommendation
- **FR-007**: A fitted `ContentModel` MUST be saveable and loadable via `ModelBundle` with identical results

### Technical Requirements (week-specific)

- **TR-001**: `ContentModel` MUST satisfy `Recommender` Protocol (`recommend(user_id, k, exclude_items) -> list[int]`)
- **TR-002**: `ContentModel` MUST satisfy `ColdStartHandler` Protocol (`recommend_cold_start(genres, liked_movie_ids, k) -> list[int]`)
- **TR-003**: `evaluate_all` callable signature `(user_id, train_items) -> list[int]` is FROZEN — no changes to `metrics.py`
- **TR-004**: Content model mean P@K MUST exceed random floor `K / 9724` for K ∈ {5, 10, 20} (CF-2)

### Key Entities

- **`ContentModel`**: TF-IDF feature matrix + cosine similarity engine + cold-start handler
- **`Recommender` Protocol**: Shared interface for all 4 models (popularity → content → collaborative → hybrid)
- **`ColdStartHandler` Protocol**: Interface for models that handle new users with no history
- **`FeatureError`**: Custom error for zero-norm / missing genre data — carries `movie_id`
- **`ModelBundle`**: Existing persistence container (Week 1) — reused for `ContentModel`

---

## Success Criteria

- **SC-001**: `similar_items("Toy Story", k=5)` returns "A Bug's Life" in results
- **SC-002**: Mean P@K > K/9724 for K ∈ {5,10,20} (content model beats random baseline — CF-2)
- **SC-003**: All consumed items are excluded from recommendations across all methods
- **SC-004**: Cold-start returns ≥1 recommendation from genres/liked-movies alone — no fake history
- **SC-005**: `FeatureError` raised (not NaN) when a zero-genre movie is queried
- **SC-006**: Fitted model saved + reloaded produces identical `similar_items` scores (within 1e-9)
- **SC-007**: `isinstance(content_model, Recommender)` and `isinstance(content_model, ColdStartHandler)` both → `True`
- **SC-008**: All existing 32 Week-1 tests still pass after Week-2 changes (additive only, no regressions)
- **SC-009**: `pytest --cov` shows ≥70% on `content.py`, ≥80% on `split.py`

---

## Out of Scope

- Collaborative filtering (Week 3)
- Hybrid logic and rating-count thresholds (Week 4)
- FastAPI backend and Next.js frontend (Week 5)
- Hosting platform validation (Week 5)
- Cold-start onboarding UI (Week 4)

---

## Assumptions & Decisions

| Decision | What | Why | ADR |
|---|---|---|---|
| Genres primary, tags optional | Use genre strings as feature source; tags augment only where available | Tags cover only 16% of movies — TF-IDF over tags gives zero vectors for 84% | ADR-004 |
| On-demand cosine similarity | Compute `feature_matrix @ query.T` per call, not precomputed | Full n×n matrix ≈ 760 MB RAM — exceeds free hosting tier | ADR-005 |
| `Protocol` over ABC | `Recommender` and `ColdStartHandler` use `typing.Protocol` | `PopularityModel` (Week 1) satisfies it with zero code changes | ADR-006 |
| Python 3.14 | Live environment version | `pyproject.toml` declares `requires-python = ">=3.14"` | — |

---

**References**: `specs/data-evaluation-foundation/` · `specs/recolab/spec.md` · `Devnexes_AI_ML_Individual_Project_Plans.pdf` (AI-06 pp.20-22) · ADR-004/005/006
