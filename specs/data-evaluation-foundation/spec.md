---
title: Week 1 - Data & Evaluation Design Specification (Time-Optimized)
version: 1.0
date_created: 2026-07-18
derived_from: spec-architecture-recolab-hybrid-recommender.md, Devnexes_AI_ML_Individual_Project_Plans.pdf
week: 1
note: This week-1 slice targets Python 3.14 (current env) and a time-optimized 2-day scope. The master spec (specs/recolab/) plans the full 6-week build (FastAPI serving, Python 3.9+ floor); treat it as the canonical long-term source of truth. Where they differ, week-1 decisions are scoped to Week 1 only.
timeline: 2-days
---

# Week 1 - Data & Evaluation Design Specification (Time-Optimized)

## 1. Week 1 Scope (2-Day Timeline)

**Project Context:**
This is a **portfolio-grade prototype** (not a production system) as specified in the master architecture document. Week 1 focuses on establishing the data foundation and evaluation framework for the RecoLab recommendation system prototype.

**Must-Have (Priority 1):**
- Download MovieLens ml-latest-small dataset
- Initialize `Devnexes-RecoLab` repository
- Implement basic chronological per-user split
- Implement simple popularity baseline
- Implement evaluation metrics (P@K, R@K, NDCG@K)
- Model artifact persistence (pickle/serialization)
- Sparsity analysis and documentation
- Create essential learning documentation

**Nice-to-Have (Priority 2):**
- Basic data analysis notebook
- Extended learning documentation

**Out of Scope:**
- Detailed data visualization
- Complex error handling
- Hosting platform testing
- Comprehensive documentation
- Content-based and collaborative filtering baselines (planned for weeks 2-3)

## 2. Technology Stack (Latest Stable with Best Practices)

**Core Dependencies (Latest Stable as of 2026-07-18):**
- **Python 3.14** - Latest stable in use (per project decision; environment runs 3.14.0)
- **pandas (latest stable)** - Data manipulation with time series support for chronological splitting
- **numpy (latest stable)** - Numerical computing with modern random number generation (default_rng)
- **scikit-learn (latest stable)** - Machine learning utilities with ranking metrics

**Best Practices Integration:**
- Use `numpy.random.default_rng(seed)` for reproducibility (not legacy `numpy.random.seed`)
- Use pandas time series functionality for chronological data handling
- Implement top-N ranking metrics (Precision@K, Recall@K, NDCG@K) directly; scikit-learn `top_k_accuracy_score` is for multiclass label ranking, NOT a substitute for these metrics

## 3. Critical Requirements (Time-Constrained)

### REQ-008: Chronological Split (Modern Best Practices)
- Implement per-user chronological train/test split using pandas time series functionality
- Set fixed random seed using `numpy.random.default_rng(42)` (modern approach, not legacy)
- Save split datasets to CSV files
- Validate no data leakage between train/test sets
- Use pandas datetime parsing for timestamp handling

### CON-001: Dataset Citation
- Add GroupLens citation to README
- Document dataset source and license

### GUD-001: Popularity Baseline (Simplified)
- Calculate item popularity from training data
- Implement simple top-N recommendation function
- Skip complex filtering for now

### REQ-009: Ranking Metrics (Complete Implementation)
- Implement Precision@K directly (top-N hit ratio over recommended list)
- Implement Recall@K directly (fraction of relevant items recovered)
- Implement NDCG@K (Normalized Discounted Cumulative Gain) directly for ranking quality
- NOTE: scikit-learn has NO NDCG@K function; `top_k_accuracy_score` measures multiclass label ranking and is NOT a substitute. Metrics are hand-implemented and unit-tested against known cases.
- CRITICAL EVAL RULE: evaluation MUST exclude each user's already-rated training items before scoring, or metrics are inflated.
- Focus on ranking quality rather than classification accuracy

### REQ-012: Model Artifact Persistence
- Implement model artifact saving (pickle/serialization)
- Implement model artifact loading functionality
- Test save/load cycle to verify state preservation
- Document persistence strategy for deployment

### REQ-011: Sparsity Documentation & Cold-Start
- Calculate and document data sparsity percentage
- Analyze popularity distribution and bias
- Document cold-start limitations AND outline a cold-start handling approach (see plan Phase 6 / master spec: new-user and new-item fallback)
- Create sparsity analysis report for future reference

## 4. Acceptance Criteria (Minimum Viable)

### AC-W1-001: Dataset Ready
- Dataset downloaded and accessible
- Basic data validation complete
- Chronological split implemented

### AC-W1-002: Repository Ready
- Repository initialized as `Devnexes-RecoLab`
- Comprehensive README with all required sections:
  - Problem statement
  - Objectives
  - Feature list
  - Architecture overview
  - Tech stack with versions
  - Setup steps
  - Environment variable instructions
  - Screenshots (placeholder for Week 1)
  - Testing notes
  - Deployment link (placeholder)
- requirements.txt with dependencies
- .gitignore properly configured

### AC-W1-003: Baseline Working
- Popularity baseline generates recommendations
- Ranking metrics calculated (P@K, R@K, NDCG@K)
- Model artifacts saved and loaded successfully
- Sparsity analysis documented
- Results documented
- Basic automated tests implemented

## 5. Success Criteria (Time-Constrained)

Week 1 success when:
- [ ] Dataset downloaded and split
- [ ] Repository initialized and pushed to GitHub
- [ ] Baseline model working
- [ ] Ranking metrics calculated (P@K, R@K, NDCG@K)
- [ ] Model artifacts persisted successfully
- [ ] Sparsity analysis documented
- [ ] Comprehensive README with all required sections
- [ ] Basic automated tests implemented
- [ ] Essential learning documented
- [ ] Ready for portal submission

## 6. Cross-References

**Master Files:**
- Main architecture: `spec-architecture-recolab-hybrid-recommender.md`
- Project brief: `Devnexes_AI_ML_Individual_Project_Plans.pdf`
- Constitution: `.specify/memory/constitution.md`
- Methodology: `.specify/methodology/sdd-methodology.md`

**Related Specifications:**
- Main project spec: `specs/recolab/spec.md`
- Main project plan: `specs/recolab/plan.md`
- Main project tasks: `specs/recolab/tasks.md`