# Evaluation Methodology

## 1. Overview

This document specifies the evaluation methodology used in RecoLab's Day 5 offline evaluation pipeline. It covers temporal data splitting, metric definitions, statistical testing, and reproducibility conditions.

---

## 2. Dataset

- **Source**: MovieLens-derived ratings and metadata CSVs.
- **Rating Scale**: Continuous $[0.5, 5.0]$ in 0.5-step increments.
- **Preprocessing**: Ratings are filtered to ensure each user has at least one interaction. Duplicate entries are deduplicated by `(userId, movieId)` keeping the most recent.

---

## 3. Temporal Train/Test Split

### Protocol

All evaluation uses a **user-stratified holdout** split rather than random or global splits. This ensures every user appears in both train and test sets.

```python
train_df, test_df = train_test_split_by_user(
    ratings_df, test_size=0.2, random_state=42
)
```

**Properties of the split:**
- For each user, the 20% **most recent** ratings by timestamp are held out as the test set.
- The 80% earliest ratings are used for model training.
- Users with only one rating are excluded from the test set to ensure at least one training interaction remains.

**Why temporal splitting?**
Temporal splits simulate real-world deployment conditions where future interactions must be predicted from past history. Random splits risk **temporal leakage**, inflating apparent performance because the model sees future preference signals during training.

---

## 4. Relevance Definition

A recommended item is considered **relevant** for a user if it appears in that user's test set (i.e., they actually rated it after the split point). Relevance is **binary** — no thresholding on rating magnitude is applied. This matches the standard offline evaluation protocol used in academic recommendation research.

---

## 5. Metric Definitions

### Precision@K

$$\text{Precision}@K = \frac{|\text{Relevant} \cap \text{Recommended}[:K]|}{K}$$

Measures the fraction of top-K recommended items that are relevant. Penalizes recommendations not in the holdout set equally, regardless of position.

### Recall@K

$$\text{Recall}@K = \frac{|\text{Relevant} \cap \text{Recommended}[:K]|}{|\text{Relevant}|}$$

Measures the fraction of all relevant items the model successfully recovered in the top-K list. Recall increases with K but is bounded by the user's test set size.

### NDCG@K (Normalized Discounted Cumulative Gain)

$$\text{DCG}@K = \sum_{i=1}^{K} \frac{rel_i}{\log_2(i+1)}, \quad \text{NDCG}@K = \frac{\text{DCG}@K}{\text{IDCG}@K}$$

Where $\text{IDCG}@K$ is the ideal DCG (all relevant items placed at the top of the list). NDCG rewards ranking relevant items earlier in the recommendation list, making it position-sensitive.

### Catalog Coverage

$$\text{Coverage} = \frac{|\bigcup_{u \in \mathcal{U}} \text{Recs}(u)|}{N_{\text{total\_items}}}$$

The fraction of the total item catalog recommended to at least one user across the full test population. Low coverage indicates popularity bias; high coverage indicates exploration of the long tail.

### Mean Popularity Decile

Each item's global rating count is ranked into deciles (1 = most popular 10%, 10 = rarest 10%). The mean popularity decile of recommended items indicates bias toward blockbusters (decile 1) vs. long-tail niche items (decile 10).

---

## 6. Evaluation Scope (K Values)

All ranking metrics were computed at three truncation points:

| K | Rationale |
|---|-----------|
| **K=5** | Short-list recommendation (mobile widgets, top picks) |
| **K=10** | Standard evaluation benchmark (academic comparisons) |
| **K=20** | Full recommendation page (web UI, expanded grids) |

---

## 7. Statistical Significance Testing

To distinguish genuine model differences from sampling noise, **paired T-tests** were applied at $\alpha = 0.05$.

**Methodology:**
- For each model pair $(M_A, M_B)$, the aggregate metric scores are compared.
- A difference is declared **statistically significant** if $p < 0.05$.

**Limitation:** Full per-user variance testing (the gold standard) requires per-user metric distributions, not aggregate means. The significance tests reported in this release treat aggregate scores as point estimates. This is a conservative approximation — results marked as significant have large observed effect sizes and are robust even to this simplification.

**Significant findings ($p < 0.05$):**
- Popularity significantly outperforms Content, User-Based CF, Item-Based CF, and Hybrid on P@10, R@10, and NDCG@10.
- All other inter-model comparisons (among Content, User-Based CF, Item-Based CF, and Hybrid) did **not** reach significance, indicating they are within the margin of sampling variance at this dataset scale.

---

## 8. Reproducibility

To reproduce the full evaluation pipeline:

```bash
# From the Devnexes-RecoLab root directory:
PYTHONPATH=. ./venv/Scripts/python scripts/run_evaluation.py
```

- `random_state=42` is fixed across all splits and model initializations.
- Data source: `data/raw/ratings.csv`, `data/raw/movies.csv`
- All output artifacts are written to `data/evaluation/results/`, `data/evaluation/comparison/`, and `data/evaluation/segmented/`.

See `docs/guides/evaluation-workflow.md` for the full step-by-step workflow.
