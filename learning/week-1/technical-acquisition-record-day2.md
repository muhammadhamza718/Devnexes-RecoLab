---
id: 002
title: Week 1 Foundation + Day 2 Implementation — Corrected Technical Record
stage: red
date: 2026-07-18
surface: agent
model: claude-sonnet-4
feature: week-1
branch: data-processing-foundation
user: Muhammad Hamza
command: Build Day 2 implementation (baseline + metrics + persistence) and document the full Week 1 + Day 2 learning record
labels: [week-1, day-2, technical-acquisition, evaluation, persistence, popularity-baseline]
links:
  spec: specs/week-1/spec.md
  ticket: null
  adr: history/adr/001-data-technology-stack-week-1.md, history/adr/002-evaluation-methodology-week-1.md, history/adr/003-model-persistence-and-testing-week-1.md
  pr: null
files:
  - recolab-hybrid-recommender/src/recolab/baseline.py
  - recolab-hybrid-recommender/src/recolab/metrics.py
  - recolab-hybrid-recommender/src/recolab/persistence.py
  - recolab-hybrid-recommender/tests/test_baseline.py
  - recolab-hybrid-recommender/tests/test_metrics.py
  - recolab-hybrid-recommender/tests/test_persistence.py
  - history/validation/day-2-ivp-report.md
tests:
  - python -m pytest tests/ -q -> 32 passed (baseline 8, metrics 14, persistence 10)
  - grep -rn top_k_accuracy_score src/ -> only a docstring warning; no import / no usage for ranking
  - exclude-known-items enforced at metrics.py:153 and baseline.py:112
---

# Week 1 Foundation + Day 2 Implementation — Corrected Technical Record

## ⚠️ Read this first — correction to the earlier record (id 001)

The earlier learning file `technical-acquisition-record.md` (id 001) contains **stale / incorrect guidance**. This record (id 002) supersedes it for the items below. The two concrete errors in id 001 that must NOT be copied into your mental model:

1. **Python version is wrong in id 001.** The project runs on **Python 3.14**, not 3.12. `pyproject.toml` declares `requires-python = ">=3.14"`, the venv is 3.14.0, and compiled `.pyc` artifacts are `cpython-314`. The Week-1 `specs/week-1` tree is pinned to 3.14; the long-term `specs/recolab` tree is 3.12+ (that is the master 6-week tree, intentionally different).
2. **`top_k_accuracy_score` is NOT a ranking metric — do not use it for P@K/R@K/NDCG@K.** id 001 lists `from sklearn.metrics import precision_at_k, recall_at_k` (these functions **do not exist** in scikit-learn) and treats `top_k_accuracy_score` as a valid Top-N ranking metric. That is incorrect and would produce wrong / misleading evaluation. The full correction is in §3 below.

Everything else in id 001 (the "kitchen analogy", the project framing, the sparsity/cold-start story) is still broadly fine as *background* — but treat its tool specifics and its metric section as superseded by this file.

---

## Executive Summary

Week 1 builds the **data-processing and evaluation foundation** for RecoLab (Project AI-06 in the Devnexes PDF). It splits MovieLens into train/test, characterises the dataset's sparsity and cold-start structure, and then — in Day 2 — implements the **popularity baseline**, the **hand-written Top-N ranking metrics (P@K / R@K / NDCG@K)**, and a **typed pickle persistence layer**. All three Day-2 modules shipped with 32 passing tests and passed an independent 5-perspective validation (IVP).

This record explains, in depth, the tools and the *decisions* behind the code — especially the two traps we deliberately avoided: (a) the `top_k_accuracy_score` metric trap, and (b) the exclude-known-items leakage trap.

---

## 1. The runtime foundation (corrected)

### Language / version
- **Python 3.14.0** (project pin: `requires-python = ">=3.14"`).
- Reproducibility via **`numpy.random.default_rng(42)`** — the *modern* numpy RNG (PCG64), not the legacy `np.seed()`. Used for the chronological split and for deterministic tie-breaking in popularity ranking.
- Typed, modular code; `from __future__ import annotations` throughout.

### Core libraries (versions present in the venv)
- **pandas 3.0.3** — data frames, groupby, the split pipeline.
- **numpy 2.5.1** — the math behind the metrics (DCG discounts, decile maps).
- **scikit-learn 1.9.0** — used for the data split train/test helpers and the pipeline *framework*; **NOT** used for ranking metrics (see §3).
- **pytest 9.1.1** — the 32-test suite (`pythonpath = ["src"]` set in `pyproject.toml` so `import recolab` works).

### Why these and not "just sklearn for everything"
The PDF (p.21) explicitly asks for **Precision@K, Recall@K or NDCG@K** and for documenting **sparsity, bias and popularity effects**. scikit-learn does **not** ship NDCG@K and its ranking helpers don't fit the Top-N "ranked hit" semantics we need. Hand-implementing the three metrics gives us: (1) exact control over the exclude-known-items guard, (2) exact, verifiable known-case values in tests, (3) built-in popularity-bias instrumentation (coverage + decile) that off-the-shelf metrics don't provide.

---

## 2. Week 1 Day 1 foundation (recap, since Day 2 builds on it)

### 2.1 Dataset
- **MovieLens ml-latest-small**: 100,836 ratings, 9,724 movies, 610 users.
- The raw zip + raw `ml-latest-small/` folder are **gitignored** (repo hygiene — public data, re-downloadable). The generated split CSVs (`split_datasets/train.csv`, `test.csv`) and analysis artifacts ARE tracked, so a clone reproduces evaluation without the raw zip (README documents the download step).

### 2.2 Split methodology — chronological, leakage-safe
- **Chronological per-user 80/20 split**: for each user, sort ratings by timestamp and hold out the most recent 20% as test. This prevents *future* ratings leaking into training and intentionally creates a realistic **cold-start / temporal generalization** problem.
- Seed fixed (`default_rng(42)`) so the split is reproducible.

### 2.3 Data characterisation (drives design)
- **Sparsity ≈ 98.3%** — very few of the possible (user × item) pairs are observed. This is why we need ranked metrics + coverage, not raw accuracy.
- **~66.4% of items are "cold"** (≤ 5 ratings). Popularity bias will dominate unless we measure and report it.
- These numbers are exactly why the Day-2 metrics report `catalog_coverage` and `mean_popularity_decile`: to *evidence* the popularity bias rather than hide it.

### 2.4 Warm / cold-start contract (REQ-009 region)
- **Warm user**: has training ratings → recommend from global popularity minus the items they already rated.
- **Cold-start user**: no training history → fall back to global top-N. (Implemented as behavioural fallback in Day 2; the *designed* cold-start interface is deferred to Week 4 per scope — flagged as CF-3 in the recommender audit.)

---

## 3. THE METRIC TRAP — read carefully (corrects id 001)

### 3.1 Why scikit-learn's ranking helpers don't apply here
| Function | What it actually is | Verdict for Top-N recsys |
|---|---|---|
| `sklearn.metrics.top_k_accuracy_score` | Multiclass **label** ranking: given true class + a score vector over *all classes*, checks if the true class is within the top-k scores. Requires a *score per candidate label*. | **NOT a substitute** for P@K/R@K/NDCG@K. It scores a single multi-class prediction, not an ordered recommendation list against a relevance set. |
| `sklearn.metrics.precision_at_k` / `recall_at_k` | **Do not exist** in scikit-learn. | id 001's `from sklearn.metrics import precision_at_k, recall_at_k` would raise `ImportError`. |
| NDCG@K | **Not shipped by scikit-learn.** | Must be hand-written. |

### 3.2 The correct implementation (what Day 2 actually shipped)
All three metrics are hand-implemented in `metrics.py` using numpy. Gains are binary (relevant = 1, else 0). Definitions:

- **Precision@K** = (# relevant items in top-K) / K.
  - Known case verified in tests: P@2 = 0.5 when 1 of 2 recommended items is relevant.
- **Recall@K** = (# relevant items in top-K) / (# relevant items total).
  - Known case verified: R@3 = 2/3 when 2 of 3 recommended are relevant and 3 relevant exist.
- **NDCG@K** = DCG@K / IDCG@K.
  - DCG uses **log2 position discount**: `discounts = log2(arange(1, k+1) + 1)` (1-indexed positions).
  - IDCG is computed from the relevant set alone (capped at k), so a relevant item at rank 1 scores 1.0 and NDCG stays in [0,1] even when |relevant| < k (graceful).
  - Known cases verified: NDCG top = 1.0; second relevant item at rank 3 → 1/log2(3).

### 3.3 The exclude-known-items guard (REQ-009 — the leakage trap)
If a user's already-rated training items are allowed into `recommended` before scoring, metrics are **inflated**: test items are typically popular, so they'd be "hit" trivially. We enforce this **twice**:
- `baseline.recommend` removes `exclude_items` (`baseline.py:112`).
- `metrics.evaluate_user` **asserts** `recommended ∩ train_items == ∅` (`metrics.py:153`) and raises `AssertionError` if the caller forgot to exclude — instead of silently inflating.

### 3.4 Popularity-bias instrumentation (REQ-009, CF-4)
`evaluate_all` additionally reports:
- `catalog_coverage` = fraction of the distinct training catalog that ever gets recommended (diversity / long-tail reach).
- `mean_popularity_decile` = average decile (1 = most popular) of recommended items; **low values evidence popularity bias**.

---

## 4. Day 2 modules — what each one does

### 4.1 `baseline.py` — PopularityModel (the P3-T1 baseline)
**Purpose:** a trivial-but-honest baseline: "recommend whatever is globally most popular, minus what the user already rated." This is the floor every smarter model (content, collaborative, hybrid) must beat.

- `compute_popularity(train_df, weight_by_rating=True)` → per-item popularity (`sum` of ratings if weighted, else `count`), sorted descending, **deterministic tie-break** via `default_rng(42)` jitter + `mergesort`.
- `PopularityModel.fit(train_df)` → stores `_global_top` (ranked movieIds). Plain, picklable container (no open handles) so the persistence layer can save it.
- `PopularityModel.recommend(user_id, k, exclude_items=None)`:
  - removes `exclude_items` (`baseline.py:112`),
  - cold-start (no exclusion needed) → global top-N,
  - all-rated / `k<=0` → empty list.
- `save(path)` / `load(path)` pickle hooks.

### 4.2 `metrics.py` — hand-written ranking metrics (P4-T1 / P4-T2 / REQ-009)
- `precision_at_k`, `recall_at_k`, `ndcg_at_k` — see §3.2.
- `evaluate_user(user_id, recommended, test_items, train_items, ks=(5,10,20))` — per-user P/R/NDCG@K with the leakage assertion guard (§3.3).
- `_build_popularity_decile_map(train_df)` — maps each item to decile 1–10 (deterministic, ties broken by ascending movieId).
- `evaluate_all(test_df, recommendations_fn, train_df, ks=(5,10,20))` — aggregates **mean** P/R/NDCG@K over all test users **plus** `catalog_coverage` + `mean_popularity_decile` + `n_users`. Fully deterministic (no randomness inside).

### 4.3 `persistence.py` — typed pickle layer (REQ-012 / P5-T2)
**Purpose:** save/load trained artifacts *exactly* for reproducible evaluation.

- `ARTIFACT_PROTOCOL = 5` (broadly readable; supports out-of-band buffers for large numpy arrays).
- `save_artifact` / `load_artifact` — generic pickle with **up-front path validation**; missing/corrupt/dir paths raise a dedicated `PersistError` instead of leaking raw `FileNotFoundError`/`EOFError`.
- `ModelBundle` dataclass (slots=True): `{model, metrics, metadata}` — one self-describing file.
- `save_model_bundle` / `load_model_bundle` — round-trip tested (P5-T2).
- Standard-library only (pickle/pathlib/dataclasses) → no import-order problems with the other modules.

---

## 5. Tests & validation (the proof)

- **32 tests, all passing**: `test_baseline.py` (8), `test_metrics.py` (14), `test_persistence.py` (10).
  - What they cover: data validation, metric **known-cases** (P@2=0.5, R@3=2/3, NDCG exact values), ranking correctness, edge cases (cold-start, all-rated, missing/corrupt file, leakage `AssertionError`), and a pickle **round-trip** equality test.
- **IVP (Independent Validation Perspective) — verdict PASS**, 5 perspectives:
  - *Security*: no network/secrets/PII; public data only. ✓
  - *Constitution*: typed, modular, small functions, modern RNG, PHR written. ✓
  - *Specification*: REQ-009 (metrics + exclude-known-items + coverage/decile) and REQ-012 (pickle + ModelBundle) satisfied; P@K/R@K/NDCG@K hand-implemented at K=5,10,20. ✓
  - *Quality*: metric math read and verified against known cases; reproducible. ✓
  - *Conflict*: no spec/ADR contradiction; Python 3.14 aligned everywhere; no `top_k_accuracy_score` misuse. ✓

### Carried-forward (non-blocking, for later weeks — from the IVP + recommender audit)
1. **CF-2**: record `P@K_random = K/9724` (random floor = K / 9,724 movies) as a hardcoded acceptance value in `specs/week-1/spec.md` REQ-009. Code is correct; the *spec* acceptance value is still just a note.
2. **CF-3**: cold-start is a behavioural fallback, not a designed interface contract — to be designed in Week 4.
3. Add `ruff`/`mypy` to CI once installed in the venv (constitution lint gate; deferred because the linters aren't in the venv yet).

---

## 6. Conceptual understanding — the "why" behind Week 1

- **Why a popularity baseline at all?** It's the honesty floor. A recommender that can't beat "recommend the most popular movies" isn't earning its complexity. Day 2 gives us that floor on *correct* metrics so Weeks 2–6 (content / collaborative / hybrid) have a real comparison table.
- **Why hand-write metrics instead of importing?** Because the *only* correct, auditable way to get NDCG@K + the exclude-known-items guard + popularity-bias instrumentation is to own the math. The sklearn trap (`top_k_accuracy_score`) is the single most common way student recsys projects quietly produce **wrong numbers** — we deliberately avoided it and documented why in `metrics.py`'s docstring.
- **Why the leakage assertion?** Evaluation validity is the whole game. A metric that includes training items is not measuring generalization; it's measuring memorization. The assert turns a silent correctness bug into a loud, immediate failure.
- **Why persistence for a baseline?** REQ-012 wants saved model artifacts; more importantly, `ModelBundle` (model + metrics + metadata) is the *uniform artifact shape* every later model will use, so the comparison table in Weeks 4–6 can load any model the same way.

---

## 7. Interview / reviewer prep (the points that show engineering maturity)

- "Why not sklearn for NDCG?" → sklearn has no NDCG@K; `top_k_accuracy_score` is multiclass-label ranking, semantically wrong for Top-N. We hand-implemented for control + verifiability.
- "How do you avoid evaluation leakage?" → two layers: `recommend` excludes known items, `evaluate_user` asserts the exclusion held; otherwise it raises.
- "How do you show the model isn't just popularity-biased?" → `catalog_coverage` + `mean_popularity_decile` are reported alongside P/R/NDCG.
- "How is this reproducible?" → fixed `default_rng(42)` split, deterministic popularity tie-break, deterministic decile map, and pickled `ModelBundle` artifacts.
- "What's the plan beyond the baseline?" → content-based (W2), collaborative/implicit (W3), hybrid + designed cold-start (W4), live demo w/ explanations + confidence (W5), real 4-way comparison table (W4–6). Source: `memory/team/recolab-week2-6-scope.md`.

---

## 8. References
- `specs/week-1/spec.md`, `plan.md`, `tasks.md` — Week-1 SDD slice (Python 3.14, pandas-only).
- `specs/recolab/` — master 6-week tree (Python 3.12+, FastAPI) — intentionally the long-term tree.
- `history/adr/001` (data/tech stack), `002` (evaluation methodology), `003` (persistence + testing).
- `history/validation/day-2-ivp-report.md` — the 5-perspective PASS report.
- `history/validation/day-2-audit-recommender.md` — the NEEDS-FIX recommender-domain audit (CF-1..CF-4; CF-1/CF-4 resolved in code, CF-2/CF-3 carried forward).
- `Devnexes_AI_ML_Individual_Project_Plans.pdf` — Project 6 (RecoLab), p.21 metrics, p.23 quality-over-size principle.

---

## PHR block

### Prompt (user, verbatim)
"register the ivp-validator subagent properly, commit the day 2 progress correctly (no push), then create a new learning file detailed as the other learning file for day 2 work AND the whole week 1 tasks. I want to understand each and everything you did based on your understanding."

### Response snapshot
- Registered `ivp-validator` across all three local agent trees (was missing from `.claude/agents/quality-assurance/`).
- Committed Day 2 progress as `1eccdcb` (no push): 3 source modules (baseline, metrics, persistence), 3 test files (32 passing), `__init__.py` exports, `pyproject.toml` pythonpath, `.gitignore`, plus the IVP report and PHR 010.
- Created this learning record (id 002): a *corrected* deep dive covering the full Week 1 foundation + Day 2 implementation, explicitly fixing the two errors in id 001 (Python 3.12 → 3.14; `top_k_accuracy_score` is NOT a ranking metric, `precision_at_k`/`recall_at_k` don't exist in sklearn, NDCG@K must be hand-written).

### Outcome
- ✅ Impact: Day 2 code complete, validated (IVP PASS), committed; accurate learning record supersedes stale id 001.
- 🧪 Tests: 32 passing; IVP 5/5 PASS; no `top_k_accuracy_score` import.
- 📁 Files: this record + the Day-2 commit artifacts.
- 🔁 Next: optionally fold id 002's corrections back into id 001 (or retire id 001); record random floor in spec (CF-2); design cold-start interface in Week 4 (CF-3).
- 🧠 Reflection: the single highest-value correctness decision this week was refusing the `top_k_accuracy_score` shortcut and hand-writing the metrics with the leakage assertion — that's what separates a defensible evaluation from a silently-wrong one.
