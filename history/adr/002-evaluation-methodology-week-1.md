---
title: Evaluation Methodology for Week 1
status: Accepted
date: 2026-07-18
---

# ADR-002: Evaluation Methodology for Week 1

## Context
Week 1 requires establishing an evaluation framework for recommendation system models. The Devnexes brief explicitly requires ranking metrics (P@K, R@K, NDCG@K) and leakage-free data splitting. The timeline constraint (2 days) necessitates focusing on essential metrics while maintaining methodological rigor. The evaluation must support future model comparisons in weeks 2-6.

## Decision
**Clustered Decision:** Chronological per-user data splitting with complete ranking metrics evaluation (Precision@K, Recall@K, NDCG@K) using modern reproducibility practices.

**Components:**
- **Chronological Per-User Split**: 80% train, 20% test per user based on timestamp
- **Fixed Random Seed**: Use `numpy.random.default_rng(42)` for reproducibility
- **Complete Ranking Metrics**: Precision@K, Recall@K, and NDCG@K as primary evaluation metrics
- **Leakage Prevention**: Strict train/test separation with validation
- **scikit-learn Integration**: Use top_k_accuracy_score where applicable
- **Sparsity Documentation**: Mandatory analysis and documentation of data sparsity characteristics
- **Model Artifact Persistence**: Pickle/serialization for trained model saving and loading

**Methodology:**
- Sort user ratings chronologically by timestamp
- Split each user's ratings individually (not global random split)
- Calculate Precision@K: fraction of relevant items in top-K recommendations
- Calculate Recall@K: fraction of relevant items captured in top-K recommendations
- Calculate NDCG@K: discounted cumulative gain accounting for ranking position
- Use ranking metrics rather than classification accuracy for recommendation quality
- Document sparsity, popularity bias, and cold-start limitations per REQ-011

## Consequences

**Positive Outcomes:**
- Chronological splitting mimics real-world recommendation scenarios
- Fixed seed ensures reproducible results for validation
- Ranking metrics capture recommendation quality better than accuracy
- Leak-free evaluation provides realistic performance estimates
- Methodology aligns with industry best practices for recommendation systems
- Foundation established for comparing advanced models in future weeks

**Negative Outcomes:**
- Chronological splitting more complex than random splitting
- Ranking metrics may be less intuitive than accuracy for beginners
- Time constraint limits comprehensive metric exploration (NDCG@K deferred)

**Risks:**
- Data sparsity may make ranking metrics less meaningful (mitigated by baseline comparison)
- Cold-start users may have insufficient test data (mitigated by documenting limitations)
- Manual implementation required for custom ranking metrics (mitigated by scikit-learn where possible)

## Alternatives Considered

**Alternative 1: Random Global Split**
- **Pros:** Simpler implementation, faster to implement
- **Cons:** Data leakage from future to past, inflated performance metrics
- **Rejected:** Devnexes brief explicitly requires leakage-free evaluation (REQ-008)

**Alternative 2: Classification Accuracy**
- **Pros:** Familiar metric, easy to implement
- **Cons:** Doesn't capture ranking quality important for recommendations
- **Rejected:** Brief requires ranking metrics (REQ-009), accuracy unsuitable for top-N recommendations

**Alternative 3: Comprehensive Metric Suite (P@K, R@K, NDCG@K, MAP, MRR)**
- **Pros:** Complete evaluation picture
- **Cons:** Implementation time, complexity, timeline constraint
- **Rejected:** NDCG@K essential per master spec, but additional metrics deferred due to timeline

## References
- Week 1 spec.md: Critical requirements REQ-008, REQ-009
- spec-architecture-recolab-hybrid-recommender.md: Acceptance criteria and evaluation requirements
- Devnexes_AI_ML_Individual_Project_Plans.pdf: Project evaluation requirements
- Context7 documentation: scikit-learn ranking metrics implementation