# Implementation Plan: Content Model

**Branch**: `content-model` | **Date**: 2026-07-22 | **Spec**: `specs/content-model/spec.md`

---

## Summary

Build `ContentModel` — a TF-IDF + cosine similarity recommender with cold-start support. Introduces the `Recommender` and `ColdStartHandler` typed protocols that all future models (collaborative, hybrid) must satisfy. Resolves CF-2 (random baseline floor assertion), CF-3 (cold-start interface), and fills the missing `split.py` test coverage gap from Week 1.

---

## Technical Context

**Language/Version**: Python 3.14 (live env, `pyproject.toml requires-python=">=3.14"`)
**Primary Dependencies**: `pandas>=2.0`, `numpy>=1.24`, `scikit-learn>=1.4.0` (TF-IDF, cosine sim), `pytest-cov>=4.0.0` (new)
**Storage**: Pickle via existing `ModelBundle` — no new storage mechanism
**Testing**: `pytest` — target ≥70% on `content.py`, ≥80% on `split.py`
**Performance Goals**: `similar_items` < 50ms per query (on-demand sparse matrix-vector product — see ADR-005)
**Constraints**: All changes additive — zero modifications to Week-1 production code

---

## Constitution Check

| Rule | Status | Note |
|---|---|---|
| No `any` type | ✅ | All functions typed; `mypy` must exit 0 |
| No unused imports | ✅ | `ruff` check after every task |
| No hardcoded secrets | ✅ | No external services; no `.env` needed |
| Modular, small functions | ✅ | Each method ≤ 50 lines; helpers extracted |
| `default_rng(42)` for randomness | ✅ | No randomness in content scoring |
| Tests before ship | ✅ | Each phase ends with gate run |

---

## Project Structure

### Documentation (this feature)

```text
specs/content-model/
├── spec.md          ← requirements and user stories
├── plan.md          ← this file
└── tasks.md         ← implementation task list
```

### Source Code Changes

```text
src/recolab/
├── interfaces.py    ← NEW: Recommender + ColdStartHandler + FeatureError
├── content.py       ← NEW: ContentModel
├── __init__.py      ← UPDATE: add new exports
│
│   (unchanged from Week 1)
├── split.py
├── baseline.py
├── metrics.py
└── persistence.py

tests/
├── test_interfaces.py   ← NEW: protocol conformance
├── test_content.py      ← NEW: ~25 tests
├── test_split.py        ← NEW: Week-1 gap — split edge cases
└── fixtures/
    ├── ratings_sample.csv   ← NEW: 50-user CI-safe sample
    └── movies_sample.csv    ← NEW: matching movies

history/adr/
├── 004-content-feature-strategy.md     ← NEW
├── 005-similarity-computation-strategy.md ← NEW
└── 006-recommender-protocol-design.md  ← NEW
```

---

## Data Model

### `ContentModel` Internal State (after `fit`)

```python
_tfidf: TfidfVectorizer          # fitted on genre (+optional tag) corpus
_feature_matrix: scipy CSR       # shape (n_items, n_features), L2-normalised rows
_movie_ids: np.ndarray[int]      # row index → movieId
_movie_id_to_row: dict[int,int]  # movieId → row index (O(1) lookup)
_zero_norm_ids: set[int]         # movies with no-genre entries (querying raises FeatureError)
_movies_df: pd.DataFrame         # preserved for explanation generation
_is_fitted: bool
```

### Genre Preprocessing

```
"Action|Adventure|Sci-Fi"  →  "Action Adventure Sci-Fi"   (TF-IDF document)
"(no genres listed)"        →  ""                          (→ zero-norm → FeatureError on query)
```

### Cold-Start Query Construction

```
query = 0.5 × genre_vec + 0.5 × liked_movies_avg_vec
       (if only one source available, full weight goes to it)
       (if both empty → FeatureError)
```

### `ModelBundle` Metadata Schema

```python
{
  "version": "content_v1",
  "model_type": "content",
  "features": ["genres"],          # or ["genres", "tags"]
  "n_items": 9742,
  "python_version": "3.14",
  "trained_on": "train.csv"
}
```

---

## API Contracts

### New: `Recommender` Protocol

```python
class Recommender(Protocol):
    def recommend(self, user_id: int, k: int,
                  exclude_items: set[int] | None = None) -> list[int]: ...
```

### New: `ColdStartHandler` Protocol

```python
class ColdStartHandler(Protocol):
    def recommend_cold_start(self, genres: list[str],
                             liked_movie_ids: list[int], k: int) -> list[int]: ...
```

### New: `FeatureError`

```python
class FeatureError(ValueError):
    movie_id: int
    # message: "movie_id={id}: {reason}"
```

### Frozen: `evaluate_all` harness wrapper

```python
# Use this pattern in tests/evaluation — do NOT change metrics.py
fn = lambda uid, excl: model.recommend(uid, k=10, exclude_items=excl)
result = evaluate_all(test_df, fn, train_df, ks=[5, 10, 20])
```

---

## Phase-by-Phase Plan

### Phase 1 — Hygiene & Pins (30 min)
Fix empty `recolab/` dir. Update `pyproject.toml`: `scikit-learn>=1.4.0`, add `pytest-cov>=4.0.0`. Run baseline gate → must show 32 passed.

### Phase 2 — Interfaces (45 min)
Create `interfaces.py` with `Recommender`, `ColdStartHandler`, `FeatureError`. Create `test_interfaces.py` (protocol conformance). Update `__init__.py`. Gate → 34 passed.

### Phase 3 — Fixtures + Split Tests (45 min)
Generate `tests/fixtures/` 50-user sample dataset (committed to repo). Create `test_split.py` for Week-1 gap. Gate → ≥80% coverage on `split.py`.

### Phase 4 — `ContentModel` (2.5 hrs)
Implement in sub-steps: `fit` → `similar_items` → `recommend` → `recommend_cold_start` → `get_explanation` → `to_bundle`/`from_bundle`. Gate after each sub-step.

### Phase 5 — Test Suite (1.5 hrs)
Complete `test_content.py` (~25 functions). Include CF-2 floor test using fixtures. Un-skip ContentModel protocol test. Gate → ≥70% coverage on `content.py`.

### Phase 6 — Integration Gate (30 min)
Finalize `__init__.py` exports. Full gate: ruff + mypy + pytest (~60 tests) + coverage. Push → CI green.

### Phase 7 — Docs (30 min)
Update `README.md` (title, What's Built table, tech stack, Quick Start). Fill `learning/week-2/technical-notes-week2.md`. Fill `learning/week-2/weekly-progress-note.md`.

### Phase 8 — IVP Report (30 min)
Write `history/validation/week-2-ivp-report.md` with 5-perspective review. Must reach PASS verdict before portal submission.

---

## Complexity Tracking

| Item | Why Needed | Simpler Alternative Rejected |
|---|---|---|
| On-demand cosine (not precomputed) | Precomputed = ~760 MB RAM | Exceeds Render free tier (512 MB) — ADR-005 |
| `Protocol` (not ABC) | `PopularityModel` satisfies it with zero changes | ABC would require modifying Week-1 code — ADR-006 |
| `tests/fixtures/` committed | CI cannot access gitignored MovieLens data | Without it, floor test always skips in CI |

---

**References**: ADR-004 · ADR-005 · ADR-006 · `specs/recolab/plan.md` (master 6-week plan)
