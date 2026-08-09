# Limitations and Future Work

## 1. Current Limitations

### 1.1 Algorithmic Limitations

**Cold-Start Fallback Quality**
The current cold-start tiers (Tier 3 and Tier 4) for anonymous and new users rely on non-personalized popularity or rough TF-IDF genre queries. These are adequate fallbacks but do not leverage contextual signals (device, time of day, geographic region) that production systems exploit.

**Fixed Hybrid Weights**
The Hybrid model uses a static weighted combination of $0.4 \times \text{Content} + 0.6 \times \text{Collaborative}$. This fixed ratio is not calibrated per user or per context. As demonstrated in the evaluation results, the Hybrid ensemble actually underperforms Content-only and Item-Based CF on several metrics, indicating the weights need adaptive tuning.

**TF-IDF Feature Sparsity**
The Content model's TF-IDF matrix is built on genre strings alone. Movies with identical genres (e.g., all Action-Comedy films) produce nearly identical feature vectors. Incorporating cast, director, or plot-keyword embeddings (e.g., via Word2Vec or sentence transformers) would dramatically improve semantic discrimination.

**User-Based CF Scalability**
User-based collaborative filtering computes user-user cosine similarities at inference time. For large user bases (>100K users), this is computationally prohibitive without an approximate nearest neighbor (ANN) index (e.g., FAISS or HNSW).

### 1.2 Scalability Limits

| Component | Current Limit | Production Threshold |
|-----------|:-------------:|:-------------------:|
| User-User similarity | ~10K users | ~100K users |
| Item-Item precomputed matrix | ~10K items | ~50K items |
| Content TF-IDF inference | ~10K items | Scales to 100K+ |
| Popularity aggregation | Unlimited | Unlimited |

Beyond these thresholds, matrix operations become memory-bound and require distributed sparse linear algebra or approximations.

### 1.3 Offline Evaluation Constraints

- **Popularity bias in test sets**: Because users naturally rate popular items more frequently, precision metrics favor the Popularity model. This is a known artifact of standard offline evaluation and does not reflect real user utility or satisfaction.
- **Absence of diversity and serendipity metrics**: Current metrics (P, R, NDCG) do not capture novelty or surprise, which are critical for long-term user engagement.
- **Single holdout split**: All comparisons use one temporal split. Bootstrap sampling or k-fold user splits would produce tighter confidence intervals on metric estimates.

---

## 2. Known Trade-Offs

| Trade-Off | Current Behavior | Alternative |
|-----------|-----------------|-------------|
| Precision vs. Coverage | Popularity wins precision; Item-Based wins coverage | Multi-objective ranking (e.g., MMR - Maximal Marginal Relevance) |
| Personalization vs. Cold-Start | Deep CF needs history | Hybrid cold-start via content seeds mitigates partially |
| Inference speed vs. accuracy | Content model is slow (~20s evaluation time) | Precomputed offline item-item similarity matrices |
| Serendipity vs. Precision | High precision models recommend popular items | Intentional diversification via post-processing re-ranking |

---

## 3. Roadmap

### Short-Term (1–2 Weeks)
- [ ] **Hybrid weight calibration**: Grid search or Bayesian optimization over $(\alpha_\text{content}, \alpha_\text{collab})$ using NDCG@10 as the objective.
- [ ] **Diversity post-processing**: Implement MMR re-ranking to improve intra-list diversity without sacrificing top-K precision.
- [ ] **Per-user significance testing**: Collect per-user metric distributions to enable proper Wilcoxon signed-rank tests.

### Medium-Term (1 Month)
- [ ] **ANN index for User-Based CF**: Integrate FAISS for approximate user-user retrieval, enabling sub-100ms latency at 1M users.
- [ ] **Enriched content features**: Replace genre-string TF-IDF with movie plot synopsis embeddings (sentence-transformers) to improve semantic discrimination.
- [ ] **Matrix Factorization (ALS/SVD)**: Implement latent factor models as a stronger collaborative baseline. Alternating Least Squares (ALS) with implicit feedback is the natural next step after explicit-rating CF.

### Long-Term (3+ Months)
- [ ] **Online A/B Testing**: Deploy the top 2 models behind a feature flag and collect real click-through rate (CTR) and engagement data.
- [ ] **Contextual bandits**: Replace static recommendations with contextual multi-armed bandit policies that learn from real-time feedback signals.
- [ ] **Session-based recommendations**: Add recurrent or transformer-based session models (e.g., SASRec) to capture in-session intent rather than long-term profile preferences.
- [ ] **Knowledge graph enrichment**: Augment item representations with external knowledge graphs (IMDb, Wikidata) for richer item-item relationships.

---

## 4. Experimental Protocol for Future Comparisons

Any new model added to RecoLab must pass the following acceptance criteria before being merged into the main benchmark:

1. Evaluated on the same `train_test_split_by_user(random_state=42)` holdout.
2. NDCG@10 ≥ current best personalized model (Item-Based CF: 0.0172).
3. Catalog Coverage ≥ 10% (prevents degenerate popularity-collapse).
4. Cold-start compatibility documented (Tier assignment in `cold-start-strategy.md`).
5. Unit tests added in `tests/` with ≥ 90% line coverage of new module.
