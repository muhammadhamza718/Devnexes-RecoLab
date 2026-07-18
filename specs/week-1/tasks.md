---
title: Week 1 - Data & Evaluation Design Tasks (Time-Optimized)
version: 1.0
date_created: 2026-07-18
derived_from: spec-architecture-recolab-hybrid-recommender.md, Devnexes_AI_ML_Individual_Project_Plans.pdf
week: 1
timeline: 2-days
---

# Week 1 - Data & Evaluation Design Tasks (Time-Optimized)

**Project Context:** Portfolio-grade prototype for recommendation system demonstration. Week 1 focuses on first baseline (popularity) of 3 required baselines.

## Day 1 Tasks

### Phase 1: Quick Setup (4 hours)
- [x] **W1-D1-P1-T1**: Download MovieLens dataset
  - Download ml-latest-small from GroupLens
  - Extract to data/ directory
  - Verify file integrity

- [x] **W1-D1-P1-T2**: Initialize repository
  - Create `Devnexes-RecoLab` repository
  - Initialize git
  - Create basic directory structure
  - Create .gitignore

- [x] **W1-D1-P1-T3**: Set up environment
  - Create Python virtual environment
  - Create requirements.txt
  - Install dependencies
  - Create basic README skeleton

### Phase 2: Data Pipeline (4 hours)
- [x] **W1-D1-P2-T1**: Load and validate dataset
  - Load ratings.csv and movies.csv
  - Basic validation (shape, types, missing values)
  - Quick statistics (users, movies, ratings)

- [x] **W1-D1-P2-T2**: Implement chronological split with modern practices
  - Load ratings.csv with pandas datetime parsing
  - Sort user ratings by timestamp using pandas time series
  - Split per-user (80% train, 20% test) chronologically
  - Use `numpy.random.default_rng(42)` for reproducibility (modern approach)
  - Validate no data leakage between train/test
  - Save train.csv and test.csv with proper naming

- [x] **W1-D1-P2-T3**: Basic data analysis and sparsity documentation
  - Calculate sparsity percentage of user-item matrix
  - Analyze rating distribution and popularity bias
  - Document cold-start limitations and data characteristics
  - Save sparsity analysis to notebook and summary document
  - **Learning Objective**: Understand sparsity challenges in recommendation systems

## Day 2 Tasks

### Phase 3: Baseline Model (3 hours)
- [x] **W1-D2-P3-T1**: Implement popularity baseline
  - Calculate popularity from training data (`compute_popularity`, `PopularityModel`)
  - Create top-N recommendation function (`recommend`, excludes known items)
  - Test with sample users (8 tests in test_baseline.py pass)

### Phase 4: Evaluation (3 hours)
- [x] **W1-D2-P4-T1**: Implement ranking metrics (direct implementation)
  - WARNING: scikit-learn has NO NDCG@K function; `top_k_accuracy_score` measures multiclass label ranking, NOT a substitute for P@K/R@K/NDCG@K.
  - Implement Precision@K directly (assert known cases)
  - Implement Recall@K directly (assert known cases)
  - Implement NDCG@K directly (assert known cases)
  - Evaluation MUST exclude each user's already-rated training items before scoring (`evaluate_user` asserts recommended ∩ train_items == ∅)
  - Document metric formulas and implementation details

- [x] **W1-D2-P4-T2**: Run evaluation and document results
  - Generate recommendations for test users (excluding already-rated items)
  - Calculate P@K, R@K, NDCG@K for K=5,10,20 (`evaluate_all`)
  - Document baseline performance
  - Compare against expected performance floor (e.g., random baseline Precision@K ~ K/num_items = K/9724) — floor value recorded in code/test docstrings; spec acceptance value carried forward (CF-2)

### Phase 5: Testing & Documentation (2 hours)
- [x] **W1-D2-P5-T1**: Implement basic automated tests
  - Write unit tests for data validation functions
  - Write unit tests for metric calculation functions
  - Write unit tests for ranking correctness
  - Write integration test for complete pipeline
  - Configure pytest and run test suite → **32 passed** (baseline 8, metrics 14, persistence 10)

- [x] **W1-D2-P5-T2**: Implement model artifact persistence
  - Implement model saving function (pickle/serialization) (`save_artifact`/`save_model_bundle`, protocol 5)
  - Implement model loading function (`load_artifact`/`load_model_bundle`)
  - Test save/load cycle with baseline model (round-trip test passes)
  - Verify model state preservation
  - Document persistence strategy

- [x] **W1-D2-P5-T3**: Create comprehensive README
  - Add problem statement
  - Add project objectives
  - Add feature list (future weeks)
  - Add architecture overview
  - Add tech stack with versions
  - Add setup steps
  - Add environment variable instructions
  - Add data source and licensing section
  - Add GroupLens citation (COM-001)
  - Add testing notes
  - Add deployment link placeholder
  - Add screenshots placeholder
  - *(Note: package README completed in Day 1; root README.md added Day 2 as self-sufficient entry point)*

- [x] **W1-D2-P5-T4**: Create learning summary
  - Document key decisions
  - Note challenges faced
  - Record learnings
  - Prepare for portal submission
  - *(learning/week-1/technical-acquisition-record-day2.md + deprecated id 001)*

### Phase 6: Cold-Start Handling (Planning)
- [ ] **W1-D2-P6-T1**: Document + plan cold-start handling
  - Project theme = "Hybrid Recommendation Engine with Cold-Start Handling" (must be addressed, not only noted)
  - New-user fallback: popularity/demographic prior until enough ratings accrue
  - New-item fallback: recency/genre prior (66.4% of items have <=5 ratings)
  - Record strategy + evaluation gap; full mitigation deferred to later weeks (master spec specs/recolab/)
  - *(Status: behavioral fallback implemented in baseline.py; designed interface deferred to Week 4 per audit CF-3 — intentionally partial for Week 1 scope)*

## Portal Submission Checklist
- [x] Repository pushed to GitHub (`main` at github.com/muhammadhamza718/Devnexes-RecoLab; pushed 2026-07-19)
- [x] README comprehensive with all required sections
- [x] Dataset analysis and sparsity documentation (data/analysis, 98.3% sparsity, 66.4% cold items)
- [x] Baseline performance metrics (P@K, R@K, NDCG@K) — evaluate_all implemented
- [x] Model artifact persistence verified (ModelBundle round-trip test passes)
- [x] Automated tests implemented and passing (32 passed)
- [x] Learning summary prepared (learning/week-1/technical-acquisition-record-day2.md)
- [ ] Ready for portal submission — **USER ACTION**: fill Devnexes portal form (repo URL live; demo link = Week 5, leave blank)