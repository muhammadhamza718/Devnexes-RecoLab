---
title: Devnexes RecoLab — Hybrid Recommendation Engine with Cold-Start Handling
version: 1.0
date_created: 2026-07-17
owner: Muhammad Hamza (Devnexes AI/ML Intern, Project AI-06)
tags: [architecture, ml, recommender-systems, fastapi, nextjs]
---

# Introduction

RecoLab is a hybrid movie recommendation engine combining content-based filtering (item similarity) and collaborative filtering (user-interaction patterns), with explicit cold-start handling for new users/items. Built as an individual 6-week Devnexes AI/ML internship deliverable (Project AI-06). This spec is self-contained and implementation-ready.

## 1. Purpose & Scope

**Purpose:** Define the complete technical design for RecoLab so it can be implemented without further clarification, while satisfying all Devnexes AI-06 brief requirements (mandatory standards, category-specific engineering requirements, weekly deliverables, acceptance criteria).

**In scope:** Data pipeline, 4 recommendation models (popularity, content-based, collaborative, hybrid), offline evaluation, FastAPI backend, Next.js frontend, deployment, testing.

**Out of scope:** Real e-commerce/catalog management, live user auth beyond a mock user-selector, production-scale infra (this is a portfolio-grade prototype, not a production system).

**Audience:** Solo intern (implementer), Devnexes reviewers.

## 2. Definitions

- **CF**: Collaborative Filtering — recommends based on user-item interaction patterns.
- **CBF**: Content-Based Filtering — recommends based on item metadata/feature similarity.
- **Cold-start**: The problem of recommending to new users/items with no/little interaction history.
- **Top-N**: The N highest-ranked recommended items returned to a user.
- **P@K / R@K / NDCG@K**: Precision/Recall/Normalized Discounted Cumulative Gain at rank K — standard ranking-quality metrics.
- **Implicit feedback**: User behavior signals (clicks, watches, ratings) treated as positive-only signals, vs. explicit 1–5 star ratings.
- **MovieLens**: The public benchmark dataset used (GroupLens ml-latest-small or ml-25m).

## 3. Requirements, Constraints & Guidelines

### Functional (from Devnexes brief §Project 6)
- **REQ-001**: System MUST generate personalized top-N recommendations for existing users.
- **REQ-002**: System MUST generate preference-based recommendations for new users (cold-start onboarding via genre/movie preference picks).
- **REQ-003**: System MUST return content-similar alternatives for any selected item.
- **REQ-004**: Each recommendation MUST include a human-readable explanation (e.g., "Because you liked X" / "Popular in Sci-Fi").
- **REQ-005**: System MUST filter already-consumed/rated items from recommendations.
- **REQ-006**: System MUST provide an evaluation view comparing popularity, content-based, collaborative, and hybrid methods.
- **REQ-007**: System MUST handle new-item cold-start (no interactions yet) via content-based fallback.

### Technical/Quality (from Devnexes brief §4, §Project 6 Technical Requirements)
- **REQ-008**: Data split MUST be reproducible (fixed random seed) and leakage-free (per-user chronological or stratified split, not naive random-row split).
- **REQ-009**: MUST report Precision@K, Recall@K, AND NDCG@K (not accuracy alone).
- **REQ-010**: MUST implement and compare exactly 3 baselines minimum: popularity, content-based, collaborative/hybrid.
- **REQ-011**: MUST document sparsity, popularity bias, and cold-start limitations in a written report.
- **REQ-012**: MUST save trained model artifacts (pickled/serialized) OR provide a deterministic retraining script.
- **REQ-013**: MUST include automated tests for ranking correctness, consumed-item filtering, and cold-start behavior.
- **SEC-001**: No secrets/API keys committed; all config via `.env` (backend) and `.env.local` (frontend), both gitignored.
- **SEC-002**: No PII — MovieLens user IDs are anonymous integers only; no real personal data used.
- **CON-001**: Dataset MUST be public/licensed (GroupLens MovieLens, CC-style research license) — cite it in README.
- **CON-002**: No medical/legal/financial/hiring decision-making (N/A for this domain, documented for completeness).
- **GUD-001**: Prefer simpler models first (popularity baseline before ML) per brief's "baseline before advanced" build order.
- **GUD-002**: Explanations must be truthful — never claim a reason not actually used in scoring.

## 4. Interfaces & Data Contracts

### 4.1 Dataset
- **Source**: MovieLens `ml-latest-small` (100K ratings, 9,742 movies, 610 users) — sufficient size for a 6-week solo project; upgradeable to `ml-25m` if compute allows.
- **Files used**: `ratings.csv` (userId, movieId, rating, timestamp), `movies.csv` (movieId, title, genres), `tags.csv` (optional, for content features).

### 4.2 Backend API (FastAPI, versioned `/api/v1`)

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/v1/users` | List demo user IDs for the selector UI |
| GET | `/api/v1/recommend/{user_id}?n=10` | Personalized top-N for existing user |
| POST | `/api/v1/recommend/cold-start` | Body: `{genres: string[], liked_movie_ids: int[]}` → recs for new user |
| GET | `/api/v1/similar/{movie_id}?n=10` | Content-similar items to a given movie |
| GET | `/api/v1/movies/search?q=` | Movie search/autocomplete for preference picking |
| GET | `/api/v1/eval/metrics` | Returns precision/recall/NDCG@K per model for the comparison dashboard |
| GET | `/api/v1/health` | Liveness check |

**Recommendation response schema:**
```json
{
  "user_id": 42,
  "method": "hybrid",
  "recommendations": [
    {
      "movie_id": 1210,
      "title": "Star Wars: Episode VI - Return of the Jedi (1983)",
      "genres": ["Action", "Adventure", "Sci-Fi"],
      "score": 0.87,
      "reason": "Because you rated similar Sci-Fi/Adventure movies highly",
      "source": "collaborative"
    }
  ]
}
```

### 4.3 Frontend (Next.js 16, App Router)
- `/` — user selector + top-N recommendations grid
- `/onboarding` — cold-start genre/movie preference picker for "new users"
- `/movie/[id]` — movie detail + "similar movies" rail
- `/evaluation` — model comparison dashboard (bar charts: P@K/R@K/NDCG@K per method)

## 5. Acceptance Criteria (from Devnexes brief, verbatim intent)

- **AC-001**: Given the test set, when hybrid model is evaluated, then it achieves higher NDCG@10 than the popularity baseline.
- **AC-002**: Given a user with zero ratings, when they complete onboarding, then the system returns ≥5 relevant recommendations without inventing fake history.
- **AC-003**: Given a user has already rated a movie, when recommendations are generated, then that movie MUST NOT appear in their recommendation list.
- **AC-004**: Given any recommendation, when displayed, then it includes a non-misleading, model-grounded explanation string.
- **AC-005**: Given a fresh clone of the repo, when the reviewer follows the README, then the evaluation results are reproducible (same seed → same metrics ±floating point tolerance).

## 6. Test Automation Strategy

- **Test Levels**: Unit (scoring functions, filtering logic, cold-start logic) + Integration (API endpoints via `httpx`/`TestClient`) + Manual checklist (UI flows).
- **Frameworks**: `pytest` + `pytest-cov` (backend), `Vitest` + `React Testing Library` (frontend, if time allows — manual checklist acceptable per brief).
- **Test Data**: A small fixed fixture subset (~50 users, ~200 movies) sampled from MovieLens with fixed seed, stored in `tests/fixtures/`.
- **Coverage Requirement**: ≥70% on `backend/models/` and `backend/services/` (core ML logic) — matches brief's "automated tests where practical."
- **CI/CD**: GitHub Actions workflow running `pytest` and `next lint` / `next build` on every push to `main`.
- **Manual Checklist** (required by brief for model scenarios): cold-start with 0 preferences, cold-start with conflicting genres, existing user with 1 rating, existing user with 500+ ratings, invalid movie_id, invalid user_id.

## 7. Rationale & Context

- **Why MovieLens**: Purpose-built for recommender research, clean schema, well-documented sparsity characteristics, avoids the "private data" prohibition in the brief.
- **Why hybrid = weighted switching, not a learned meta-model**: A learned stacking model adds a 4th layer of complexity not justified in a 6-week solo timeline; a documented weighted/switching hybrid (e.g., collaborative when user has ≥5 ratings, else content-based blend) is simpler, explainable, and still satisfies "documented hybrid strategy."
- **Why per-user chronological split over random split**: Random row-splitting leaks future ratings into training for the same user, inflating metrics — the brief explicitly requires leakage prevention (REQ-008).
- **Why FastAPI + Next.js over Streamlit**: User confirmed comfort with Pandas/Scikit-learn and requested this stack; also satisfies brief's "lightweight interface/API so reviewer can test the model."

## 8. Dependencies & External Integrations

### External Systems
- **EXT-001**: GroupLens MovieLens dataset — static CSV download, no live API dependency.

### Third-Party Services
- **SVC-001**: None required for core functionality (no external LLM/API needed — this is classical ML, keeping runtime cost at $0).

### Infrastructure Dependencies
- **INF-001**: Render (or Railway) — FastAPI backend hosting with persistent disk for model artifacts.
- **INF-002**: Vercel — Next.js frontend hosting.
- **INF-003 (optional)**: Postgres on Render, only if moving beyond CSV/pickle storage; SQLite is sufficient for this scope and reduces infra surface.

### Technology Platform Dependencies
- **PLT-001**: Python 3.12+ (current FastAPI-recommended baseline as of mid-2026).
- **PLT-002**: Node.js 20 LTS+ for Next.js 16.
- **PLT-003**: Next.js 16.2.x (current stable as of July 2026) with App Router + Turbopack.
- **PLT-004**: FastAPI (latest PyPI release, requires Pydantic ≥2.9).
- **PLT-005**: Core ML libs: `pandas`, `numpy`, `scikit-learn` (TF-IDF + cosine similarity for content-based), `scikit-surprise` or `implicit` (collaborative filtering — use `implicit` if `scikit-surprise` has install friction on target Python version; verify at setup time).

### Compliance Dependencies
- **COM-001**: MovieLens license requires citation of GroupLens in README and any publication — non-negotiable, include in credits section.

## 9. Examples & Edge Cases

```python
# Cold-start fallback logic (simplified)
def get_recommendations(user_id: int, n: int = 10):
    rating_count = get_user_rating_count(user_id)
    if rating_count == 0:
        raise ValueError("Use /recommend/cold-start for users with no history")
    elif rating_count < 5:
        # Sparse user: blend popularity + content-based (weight collaborative low)
        return hybrid_score(user_id, cf_weight=0.2, cbf_weight=0.5, pop_weight=0.3)
    else:
        # Established user: collaborative-dominant hybrid
        return hybrid_score(user_id, cf_weight=0.7, cbf_weight=0.3, pop_weight=0.0)
```

**Edge cases to test:**
- New item with zero ratings → must appear only via content-based similarity, never via collaborative score (avoid divide-by-zero / NaN propagation).
- User requests recommendations after rating literally every movie in the demo catalog → return empty list with a clear "no more items" message, not a crash.
- Duplicate genre selection in onboarding → dedupe before scoring.

## 10. Validation Criteria

- All REQ/AC items above are demonstrably met and mapped to a specific test.
- `pytest` suite passes with ≥70% coverage on `backend/models/`, `backend/services/`.
- Evaluation report (`docs/evaluation-report.md`) contains: metrics table (all 4 methods × P@K/R@K/NDCG@K), sparsity analysis, popularity-bias discussion, cold-start walkthrough with screenshots.
- README allows a fresh clone → running app in <15 minutes with no private assistance (brief's Final Submission Checklist item 3).

## 11. Related Specifications / Further Reading

- GroupLens MovieLens dataset docs: https://grouplens.org/datasets/movielens/
- Devnexes AI/ML Internship Project Plans PDF (source brief, Project AI-06, pp. 20–22)
- `scikit-surprise` docs / `implicit` library docs (verify current install compatibility with chosen Python version at Week 1 setup)
