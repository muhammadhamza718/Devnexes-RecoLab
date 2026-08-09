# Model Comparison Summary

## 1. Overview

This document provides a high-level decision matrix and trade-off analysis across all five recommendation models implemented in RecoLab. Use this document to select the appropriate model for a given production context.

---

## 2. Decision Matrix

| Criterion | Popularity | Content | User-Based CF | Item-Based CF | Hybrid |
|-----------|:---------:|:-------:|:-------------:|:-------------:|:------:|
| **Precision@10** | ★★★★★ | ★★☆☆☆ | ★☆☆☆☆ | ★★★☆☆ | ★★☆☆☆ |
| **Recall@10** | ★★★★★ | ★★☆☆☆ | ★☆☆☆☆ | ★★☆☆☆ | ★★☆☆☆ |
| **Catalog Coverage** | ★☆☆☆☆ | ★★☆☆☆ | ★★★★☆ | ★★★★★ | ★★★★☆ |
| **Cold-Start Support** | ★★★★★ | ★★★★☆ | ★☆☆☆☆ | ★★☆☆☆ | ★★★☆☆ |
| **Personalization** | ★☆☆☆☆ | ★★★☆☆ | ★★★★☆ | ★★★★☆ | ★★★★★ |
| **Computation Cost** | ★★★★★ | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ | ★★☆☆☆ |
| **Interpretability** | ★★★★★ | ★★★★☆ | ★★★☆☆ | ★★★☆☆ | ★★☆☆☆ |

*★★★★★ = Best, ★☆☆☆☆ = Weakest*

---

## 3. Metric Comparison by Dimension

### Precision Performance

```
Precision@10 Rankings:
1. Popularity     ████████████████████ 0.0756
2. Item-Based CF  ████                 0.0152
3. Content        ████                 0.0134
4. Hybrid         ██                   0.0077
5. User-Based CF  ██                   0.0074
```

### Coverage Performance

```
Catalog Coverage Rankings:
1. Item-Based CF  ████████████████████ 37.64%
2. Hybrid         █████████            17.22%
3. User-Based CF  █████████            16.97%
4. Content        ██                    4.74%
5. Popularity     █                     1.97%
```

---

## 4. Trade-Off Matrix

| Model | Best Use Case | Key Strength | Key Weakness |
|-------|--------------|--------------|--------------|
| **Popularity** | Homepage teasers, new user landing | Highest precision; zero infrastructure complexity | Zero personalization; ignores user preferences |
| **Content** | Profile-based onboarding; cold-start new users | Works without ratings; genre-aware | Cannot capture collaborative taste patterns |
| **User-Based CF** | Long-term users with dense histories | Exploits community taste | Computationally expensive; fails cold-start |
| **Item-Based CF** | Active users; item-page "Similar Items" | High coverage; stable item-item correlations | High memory for precomputed similarity matrix |
| **Hybrid** | Primary personalized feed; adaptive scenarios | Balances personalization and coverage | Weight calibration is sensitive; underperforms both extremes without tuning |

---

## 5. Recommended Deployment Strategy

### Tier-Based Selection (Production)

Given the cold-start tiering architecture already implemented in `src/recolab/hybrid.py`, the recommended deployment is:

1. **Anonymous / New User** → Popularity Baseline (instant, no personalization needed)
2. **Onboarding (genres provided)** → Content `recommend_cold_start()` via TF-IDF genre query
3. **Sparse History ($\le 5$ ratings)** → Pure Content Model on the limited profile
4. **Active User ($> 5$ ratings)** → Hybrid (0.4 Content + 0.6 Collaborative) ensemble

### Key Insight

Item-Based CF should be exposed as a secondary "Similar Items" feature (item detail pages, carousels) rather than as the primary feed recommender. Its 37.64% coverage is a long-tail discovery asset that complements the higher-precision Hybrid primary feed.
