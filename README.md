# RecoLab — Hybrid Recommender (Devnexes AI-06)

Portfolio-grade recommendation system built for the Devnexes Internship individual project (Project AI-06). RecoLab progresses from a data/evaluation foundation (Week 1) toward content-based, collaborative, hybrid models, and a live demo (Weeks 2–5), finishing with a multi-approach comparison table (Weeks 4–6).

> **Status:** Week 1 finished — data processing foundation + popularity baseline + hand-implemented Top-N ranking metrics + typed persistence, with an independent 5-perspective validation (IVP) **PASS** and **32 passing tests**.

---

## What's in this repo

- `recolab-hybrid-recommender/` — the Python package (`recolab`) and its tests.
  - `src/recolab/baseline.py` — popularity baseline (`PopularityModel`, `compute_popularity`).
  - `src/recolab/metrics.py` — hand-written **Precision@K, Recall@K, NDCG@K** + popularity-bias instrumentation.
  - `src/recolab/persistence.py` — typed pickle persistence (`ModelBundle`, `save_artifact`/`load_artifact`).
  - `tests/` — 32 tests (`test_baseline` 8, `test_metrics` 14, `test_persistence` 10).
  - `data/` — MovieLens analysis outputs and the train/test split CSVs.
  - See `recolab-hybrid-recommender/README.md` for package-level detail.
- `specs/week-1/` — Spec-Driven Development docs (spec, plan, tasks) for Week 1.
- `history/adr/` — Architecture Decision Records (001 data stack, 002 evaluation methodology, 003 persistence + testing).
- `history/validation/` — Day-1 and Day-2 IVP reports + recommender-domain audit.
- `learning/week-1/` — technical acquisition records (corrected record: `technical-acquisition-record-day2.md`).
- `Devnexes_AI_ML_Individual_Project_Plans.pdf` — the source project brief (Project 6).

> Note: `CLAUDE.md` / `AGENTS.md` contain local agent/runtime instructions and are **not** part of the deliverable; this README is self-sufficient.

---

## Tech stack

- **Python 3.14** (pinned: `requires-python = ">=3.14"` in `pyproject.toml`).
- **pandas 3.0.3**, **numpy 2.5.1**, **scikit-learn 1.9.0**, **pytest 9.1.1**.
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
pip install pandas numpy scikit-learn pytest
```

---

## Run the tests

```bash
cd recolab-hybrid-recommender
pytest tests/ -q
# -> 32 passed
```

(Tests use `pythonpath = ["src"]` from `pyproject.toml`, so `import recolab` works directly.)

---

## Dataset (reproducibility note)

The raw MovieLens **ml-latest-small** dataset is **not committed** (gitignored, public data, re-downloadable). The derived artifacts we *do* commit are:

- `recolab-hybrid-recommender/data/split_datasets/train.csv` and `test.csv` — an 80/20 **chronological per-user** split (seeded with `numpy.random.default_rng(42)`).
- `recolab-hybrid-recommender/data/analysis/*` — data-characterisation outputs.

To regenerate from scratch, download [MovieLens ml-latest-small](https://grouplens.org/datasets/movielens/) (GroupLens, CC BY 4.0; Harper & Konstan, 2015) and place it under `recolab-hybrid-recommender/data/ml-latest-small/`.

**Dataset facts:** 100,836 ratings · 610 users · 9,724 movies · sparsity ≈ 98.3% · ~66.4% of items are "cold" (≤ 5 ratings). These numbers drive the evaluation design (ranking metrics + coverage/decile rather than raw accuracy).

---

## Key engineering decisions (why, not just what)

- **Hand-written metrics, not `sklearn`.** scikit-learn ships **no NDCG@K** and **no** `precision_at_k`/`recall_at_k`, and `top_k_accuracy_score` is a *multiclass-label* ranking metric — semantically wrong for Top-N recommendation. P@K / R@K / NDCG@K are implemented from scratch in `metrics.py` for exact control + verifiability.
- **Exclude-known-items guard (REQ-009).** Evaluation must exclude each user's already-rated training items before scoring, or metrics are silently inflated. Enforced twice: `baseline.recommend` removes them, and `metrics.evaluate_user` *asserts* the exclusion held.
- **Popularity-bias instrumentation.** `evaluate_all` reports `catalog_coverage` and `mean_popularity_decile` so bias is *evidenced*, not hidden.
- **Reproducibility.** Fixed `default_rng(42)` split, deterministic popularity tie-break, deterministic decile map, picklable `ModelBundle` artifacts.

---

## Validation

- **IVP (Independent Validation Perspective): PASS** across Security, Constitution, Specification, Quality, and Conflict perspectives — see `history/validation/day-2-ivp-report.md`.
- 32/32 tests pass on a clean run; two metric known-cases (P@2 = 0.5, R@3 = 2/3) and exact NDCG values are asserted.

---

## Roadmap

| Week | Deliverable |
|------|-------------|
| 1 ✅ | Data foundation, popularity baseline, ranking metrics, persistence |
| 2 | Content-based model |
| 3 | Collaborative / implicit-feedback model |
| 4 | Hybrid strategy + designed cold-start onboarding |
| 5 | Live demo (FastAPI/Streamlit) with explanations + confidence |
| 4–6 | Real comparison table: popularity vs content vs collaborative vs hybrid on P@K/R@K/NDCG@K |

> A **live demo / deployed link is planned for Week 5.** The Week 1–2 foundation is a library + tests, not a hosted service, so no deployment link exists yet.

---

## License & data

- Source code: MIT (portfolio project).
- MovieLens data: GroupLens Research, CC BY 4.0 — see `recolab-hybrid-recommender/data/ml-latest-small/` when present.
