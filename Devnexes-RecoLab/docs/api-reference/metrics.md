# API Reference: Ranking & Evaluation Metrics (`src/recolab/metrics.py`)

## Core Evaluation Functions

### `precision_at_k(actual: List[int], recommended: List[int], k: int = 10) -> float`
Calculates Precision@K:
$$ \text{Precision}@K = \frac{|\text{actual} \cap \text{recommended}[:K]|}{K} $$

---

### `recall_at_k(actual: List[int], recommended: List[int], k: int = 10) -> float`
Calculates Recall@K:
$$ \text{Recall}@K = \frac{|\text{actual} \cap \text{recommended}[:K]|}{|\text{actual}|} $$

---

### `ndcg_at_k(actual: List[int], recommended: List[int], k: int = 10) -> float`
Calculates Normalized Discounted Cumulative Gain (NDCG@K) with binary relevance:
$$ \text{DCG}@K = \sum_{i=1}^K \frac{rel_i}{\log_2(i + 1)}, \quad \text{NDCG}@K = \frac{\text{DCG}@K}{\text{IDCG}@K} $$

---

### `catalog_coverage(all_recommendations: List[List[int]], total_items: int) -> float`
Calculates Catalog Coverage percentage:
$$ \text{Coverage} = \frac{|\bigcup_{u} \text{Recs}(u)|}{N_{\text{total}}} $$

---

### `evaluate_recommender(model: Recommender, train_df: pd.DataFrame, test_df: pd.DataFrame, k: int = 10) -> Dict[str, float]`
Evaluates model across full test set and returns dictionary with keys `precision`, `recall`, `ndcg`, `coverage`, and `mean_popularity_decile`.
