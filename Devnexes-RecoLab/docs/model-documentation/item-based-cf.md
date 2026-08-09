# Item-Based Collaborative Filtering (`ItemBasedCF`)

## 1. Executive Summary
`ItemBasedCF` computes relationships between pairs of items based on historical user rating patterns. Rather than searching for similar users at inference time, it precomputes item-item similarity relationships, allowing for faster recommendation generation and intuitive item-to-item explanations ("Users who liked item X also liked item Y").

---

## 2. Mathematical Foundation & Formulas

### 2.1 Item-Item Cosine Similarity
For items $i$ and $j$ represented by interaction column vectors $\mathbf{c}_i, \mathbf{c}_j \in \mathbb{R}^U$:
$$ S(i, j) = \cos(\mathbf{c}_i, \mathbf{c}_j) = \frac{\sum_{u \in U_{i,j}} r_{u,i} r_{u,j}}{\sqrt{\sum_{u \in U_i} r_{u,i}^2} \sqrt{\sum_{u \in U_j} r_{u,j}^2}} $$

### 2.2 Recommendation Score Aggregation
For user $u$ who has rated items $I_u$, the predicted rating for candidate item $j \notin I_u$ is:
$$ \hat{r}_{u,j} = \frac{\sum_{i \in I_u} S(i, j) \cdot r_{u,i}}{\sum_{i \in I_u} |S(i, j)|} $$

---

## 3. Architecture & Class Interface

### Source Location
- **Module**: `src/recolab/collaborative.py`
- **Class**: `ItemBasedCF`
- **Protocol**: Implements `Recommender` protocol.

### Key Methods

#### `fit(ratings_df: pd.DataFrame, movies_df: Optional[pd.DataFrame] = None) -> ItemBasedCF`
Builds sparse user-item CSR matrix and computes item-item cosine similarity matrix $\mathbf{S}_{\text{item}} \in \mathbb{R}^{I \times I}$.

#### `recommend(user_id: int, k: int = 10, exclude_items: Optional[List[int]] = None) -> List[Tuple[int, float]]`
Looks up target user's rated items $I_u$ and computes weighted item-neighborhood scores for all candidate items $j \notin I_u$.

#### `similar_items(item_id: int, k: int = 10) -> List[Tuple[int, float]]`
Retrieves top-$K$ most similar items to a given item ID directly from the precomputed item similarity matrix.

---

## 4. Cold-Start & Fallback Behavior
- **New Items**: Items with no rating history have zero similarity vectors and are excluded from recommendation candidate pools.
- **New Users**: Users with $\le 5$ ratings fall back to `ContentModel` or `PopularityModel`.

---

## 5. Model Persistence & State
- **Bundle Format**: `to_bundle()` exports:
  - `item_similarity_matrix`: `scipy.sparse.csr_matrix` or `np.ndarray`
  - `user_ratings`: Dictionary mapping `user_id` to list of `(movie_id, rating)`
  - `item_id_to_idx` / `idx_to_item_id`: ID mapping dicts

---

## 6. Performance Characteristics

| Metric | Benchmark Score |
|--------|-----------------|
| **Precision@10** | 0.0841 |
| **Recall@10** | 0.0658 |
| **NDCG@10** | 0.0912 |
| **Catalog Coverage** | 28.90% |
| **Mean Popularity Decile** | 7.62 |
| **Inference Latency** | ~4.5 ms per recommendation call |
| **Memory Footprint** | ~15 MB |
