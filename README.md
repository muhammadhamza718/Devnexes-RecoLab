# RecoLab — Hybrid Recommender (Devnexes AI-06)

Portfolio-grade recommendation system built for the Devnexes Internship individual project (Project AI-06). RecoLab progresses from a data/evaluation foundation (Week 1) toward content-based, collaborative, hybrid models, and a live demo (Weeks 2–5), finishing with a multi-approach comparison table (Weeks 4–6).

> **Status:** Week 2 finished — content-based recommendation model with TF-IDF + cosine similarity, cold-start handling, protocol-oriented design, comprehensive testing (73 tests, 84% coverage), and Devnexes-compliant documentation.

---

## What's in this repo

- `Devnexes-RecoLab/` — the Python package (`recolab`) and its tests.
  - `src/recolab/baseline.py` — popularity baseline (`PopularityModel`, `compute_popularity`).
  - `src/recolab/content.py` — content-based model with TF-IDF + cosine similarity (`ContentModel`).
  - `src/recolab/interfaces.py` — shared protocols (`Recommender`, `ColdStartHandler`, `FeatureError`).
  - `src/recolab/metrics.py` — hand-written **Precision@K, Recall@K, NDCG@K** + popularity-bias instrumentation.
  - `src/recolab/persistence.py` — typed pickle persistence (`ModelBundle`, `save_artifact`/`load_artifact`).
  - `src/recolab/split.py` — data splitting utilities.
  - `tests/` — 73 tests (baseline 8, content 34, metrics 14, persistence 10, interfaces 5, fixtures 3).
  - `data/` — MovieLens analysis outputs and the train/test split CSVs.
  - `docs/` — documentation including screenshot evidence for Week 2.
  - `WEEKLY_PROGRESS.md` — Devnexes-compliant weekly progress notes.
  - `TESTING_EVIDENCE.md` — comprehensive testing evidence and quality gates.
  - See `Devnexes-RecoLab/README.md` for package-level detail.
- `specs/content-model/` — Spec-Driven Development docs (spec, plan, tasks) for Week 2.
- `specs/data-evaluation-foundation/` — Spec-Driven Development docs (spec, plan, tasks) for Week 1.
- `history/adr/` — Architecture Decision Records (001 data stack, 002 evaluation methodology, 003 persistence + testing, 004 content feature strategy, 005 similarity computation, 006 recommender protocol design).
- `history/validation/` — Comprehensive IVP reports and recommender-domain audits.
- `history/prompts/` — Prompt History Records for all development sessions.
- `learning/week-1/` — technical acquisition records for Week 1.
- `learning/week-2/` — technical acquisition records for Week 2.
- `Devnexes_AI_ML_Individual_Project_Plans.pdf` — the source project brief (Project 6).

> Note: `CLAUDE.md` / `AGENTS.md` contain local agent/runtime instructions and are **not** part of the deliverable; this README is self-sufficient.

---

## Tech stack

- **Python 3.14** (pinned: `requires-python = ">=3.14"` in `pyproject.toml`).
- **pandas 3.0.3**, **numpy 2.5.1**, **scikit-learn 1.9.0**, **pytest 9.1.1**, **ruff 0.6.0**, **mypy 1.10.0**.
- Standard library only for persistence (no extra deps).

---

## Setup

```bash
# 1. Python 3.14 (project pin). Check your version:
python --version

# 2. Create and activate a virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # Linux/macOS

# 3. Install dependencies
pip install -e ".[dev]"
```

---

## Run the tests

```bash
cd Devnexes-RecoLab
pytest -m "not full_dataset" -q
# -> 73 passed

# With coverage
pytest -m "not full_dataset" --cov=src/recolab --cov-report=term
# -> 84% overall coverage, 92% for content.py
```

(Tests use `pythonpath = ["src"]` from `pyproject.toml`, so `import recolab` works directly.)

---

## Dataset (reproducibility note)

The raw MovieLens **ml-latest-small** dataset is **not committed** (gitignored, public data, re-downloadable). The derived artifacts we *do* commit are:

- `Devnexes-RecoLab/data/split_datasets/train.csv` and `test.csv` — an 80/20 **chronological per-user** split (seeded with `numpy.random.default_rng(42)`).
- `Devnexes-RecoLab/data/analysis/*` — data-characterisation outputs.

To regenerate from scratch, download [MovieLens ml-latest-small](https://grouplens.org/datasets/movielens/) (GroupLens, CC BY 4.0; Harper & Konstan, 2015) and place it under `Devnexes-RecoLab/data/ml-latest-small/`.

**Dataset facts:** 100,836 ratings · 610 users · 9,724 movies · sparsity ≈ 98.3% · ~66.4% of items are "cold" (≤ 5 ratings). These numbers drive the evaluation design (ranking metrics + coverage/decile rather than raw accuracy).

---

## Key engineering decisions (why, not just what)

- **Hand-written metrics, not `sklearn`.** scikit-learn ships **no NDCG@K** and **no** `precision_at_k`/`recall_at_k`, and `top_k_accuracy_score` is a *multiclass-label* ranking metric — semantically wrong for Top-N recommendation. P@K / R@K / NDCG@K are implemented from scratch in `metrics.py` for exact control + verifiability.
- **Exclude-known-items guard (REQ-009).** Evaluation must exclude each user's already-rated training items before scoring, or metrics are silently inflated. Enforced twice: `baseline.recommend` removes them, and `metrics.evaluate_user` *asserts* the exclusion held.
- **Popularity-bias instrumentation.** `evaluate_all` reports `catalog_coverage` and `mean_popularity_decile` so bias is *evidenced*, not hidden.
- **Reproducibility.** Fixed `default_rng(42)` split, deterministic popularity tie-break, deterministic decile map, picklable `ModelBundle` artifacts.

---

## Validation

- **IVP (Independent Validation Perspective): PASS** across Security, Constitution, Specification, Quality, and Conflict perspectives — see `history/validation/comprehensive-project-audit-ivp-report.md` and `history/validation/week-2-ivp-validation-report.md`.
- 73/73 tests pass on a clean run; comprehensive test coverage (84% overall, 92% for content.py).
- Protocol conformance verified for both Recommender and ColdStartHandler protocols.
- Code quality checks passing (ruff linting, mypy type checking).

---

## Week 2 Implementation (Content-Based Model)

### ContentModel Features
- **TF-IDF Feature Extraction**: Converts movie genres to numerical features using Term Frequency-Inverse Document Frequency
- **Cosine Similarity**: Computes item-to-item similarity scores for recommendation matching
- **User-Based Recommendations**: Uses user's rated items to find similar content
- **Cold-Start Handling**: Recommends based on genre preferences without rating history
- **Persistence**: Save/load models with pickle serialization via bundle pattern
- **Protocol-Oriented Design**: Satisfies both Recommender and ColdStartHandler protocols

### Key Methods
- `fit(ratings, movies)`: Train model on ratings and item metadata
- `recommend(user_id, k, exclude_items)`: Get personalized recommendations
- `similar_items(item_id, k)`: Find items similar to a given item
- `recommend_cold_start(genres, liked_movie_ids, k)`: Handle new users
- `get_explanation(user_id, item_id)`: Generate recommendation explanations
- `save(path) / load(path)`: Model persistence

### Week 2 Technical Decisions
- **TF-IDF over Word2Vec**: Chosen for simplicity and interpretability with genre data
- **Protocol-Oriented Design**: Enables flexibility without inheritance complexity
- **CI-Safe Fixtures**: Sample fixtures for fast automated testing (50 users, 5858 ratings)
- **MyPy Configuration**: Configured to ignore scikit-learn (no official type stubs)

### Week 2 Quality Metrics
- **Tests**: 73 passing (baseline 8, content 34, metrics 14, persistence 10, interfaces 5, fixtures 3)
- **Coverage**: 84% overall, 92% for content.py
- **Performance**: <5ms latency for all core operations
- **Protocol Conformance**: ✅ Both Recommender and ColdStartHandler satisfied

---

## Roadmap

| Week | Deliverable |
|------|-------------|
| 1 ✅ | Data foundation, popularity baseline, ranking metrics, persistence |
| 2 ✅ | Content-based model with TF-IDF + cosine similarity, cold-start handling, protocol-oriented design |
| 3 | Collaborative / implicit-feedback model |
| 4 | Hybrid strategy + designed cold-start onboarding |
| 5 | Live demo (FastAPI/Streamlit) with explanations + confidence |
| 4–6 | Real comparison table: popularity vs content vs collaborative vs hybrid on P@K/R@K/NDCG@K |

> A **live demo / deployed link is planned for Week 5.** The Week 1–2 foundation is a library + tests, not a hosted service, so no deployment link exists yet.

---

## License & data

- Source code: MIT (portfolio project).
- MovieLens data: GroupLens Research, CC BY 4.0 — see `Devnexes-RecoLab/data/ml-latest-small/` when present.

---

## Weekly Progress and Testing Evidence

For detailed weekly progress notes, testing evidence, and Devnexes submission requirements:
- **Devnexes-RecoLab/WEEKLY_PROGRESS.md** — Weekly progress notes (completed work, pending work, blockers, decisions, next week tasks)
- **Devnexes-RecoLab/TESTING_EVIDENCE.md** — Comprehensive testing evidence (test results, known defects, fix plan, quality gates)
- **Devnexes-RecoLab/docs/screenshots/** — Week 2 submission screenshots (test coverage, code quality checks)
