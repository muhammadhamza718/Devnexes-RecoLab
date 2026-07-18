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
- [ ] **W1-D1-P1-T1**: Download MovieLens dataset
  - Download ml-latest-small from GroupLens
  - Extract to data/ directory
  - Verify file integrity

- [ ] **W1-D1-P1-T2**: Initialize repository
  - Create `Devnexes-RecoLab` repository
  - Initialize git
  - Create basic directory structure
  - Create .gitignore

- [ ] **W1-D1-P1-T3**: Set up environment
  - Create Python virtual environment
  - Create requirements.txt
  - Install dependencies
  - Create basic README skeleton

### Phase 2: Data Pipeline (4 hours)
- [ ] **W1-D1-P2-T1**: Load and validate dataset
  - Load ratings.csv and movies.csv
  - Basic validation (shape, types, missing values)
  - Quick statistics (users, movies, ratings)

- [ ] **W1-D1-P2-T2**: Implement chronological split with modern practices
  - Load ratings.csv with pandas datetime parsing
  - Sort user ratings by timestamp using pandas time series
  - Split per-user (80% train, 20% test) chronologically
  - Use `numpy.random.default_rng(42)` for reproducibility (modern approach)
  - Validate no data leakage between train/test
  - Save train.csv and test.csv with proper naming

- [ ] **W1-D1-P2-T3**: Basic data analysis and sparsity documentation
  - Calculate sparsity percentage of user-item matrix
  - Analyze rating distribution and popularity bias
  - Document cold-start limitations and data characteristics
  - Save sparsity analysis to notebook and summary document
  - **Learning Objective**: Understand sparsity challenges in recommendation systems

## Day 2 Tasks

### Phase 3: Baseline Model (3 hours)
- [ ] **W1-D2-P3-T1**: Implement popularity baseline
  - Calculate popularity from training data
  - Create top-N recommendation function
  - Test with sample users

### Phase 4: Evaluation (3 hours)
- [ ] **W1-D2-P4-T1**: Implement ranking metrics with scikit-learn
  - Explore scikit-learn ranking metrics (top_k_accuracy_score)
  - Implement custom Precision@K calculation function
  - Implement custom Recall@K calculation function
  - Implement NDCG@K (Normalized Discounted Cumulative Gain) calculation
  - Test metrics with simple known cases
  - Document metric formulas and implementation details

- [ ] **W1-D2-P4-T2**: Run evaluation and document results
  - Generate recommendations for test users
  - Calculate P@K, R@K, NDCG@K for K=5,10,20
  - Document baseline performance
  - Compare against expected performance floor

### Phase 5: Testing & Documentation (2 hours)
- [ ] **W1-D2-P5-T1**: Implement basic automated tests
  - Write unit tests for data validation functions
  - Write unit tests for metric calculation functions
  - Write unit tests for ranking correctness
  - Write integration test for complete pipeline
  - Configure pytest and run test suite

- [ ] **W1-D2-P5-T2**: Implement model artifact persistence
  - Implement model saving function (pickle/serialization)
  - Implement model loading function
  - Test save/load cycle with baseline model
  - Verify model state preservation
  - Document persistence strategy

- [ ] **W1-D2-P5-T3**: Create comprehensive README
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

- [ ] **W1-D2-P5-T4**: Create learning summary
  - Document key decisions
  - Note challenges faced
  - Record learnings
  - Prepare for portal submission

## Portal Submission Checklist
- [ ] Repository pushed to GitHub
- [ ] README comprehensive with all required sections
- [ ] Dataset analysis and sparsity documentation
- [ ] Baseline performance metrics (P@K, R@K, NDCG@K)
- [ ] Model artifact persistence verified
- [ ] Automated tests implemented and passing
- [ ] Learning summary prepared
- [ ] Ready for portal submission