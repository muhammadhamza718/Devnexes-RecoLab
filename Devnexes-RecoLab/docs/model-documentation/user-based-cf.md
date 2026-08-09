# User-Based Collaborative Filtering (`UserBasedCF`)

## 1. Executive Summary
`UserBasedCF` is a memory-based collaborative filtering model that finds users with similar historical rating patterns and aggregates their ratings to predict candidate item preferences. It utilizes sparse CSR matrix operations to calculate user-user cosine similarity and handles cold-start users via an integrated fallback mechanism.

---

## 2. Mathematical Foundation & Formulas

### 2.1 User-User Cosine Similarity Matrix
Given user-item rating matrix $\mathbf{R} \in \mathbb{R}^{U \times I}$, the similarity between user $u$ and user $v$ is:
$$ S(u, v) = \cos(\mathbf{r}_u, \mathbf{r}_v) = \frac{\sum_{i \in I_{u,v}} r_{u,i} r_{v,i}}{\sqrt{\sum_{i \in I_u} r_{u,i}^2} \sqrt{\sum_{i \in I_v} r_{v,i}^2}} $$
where $I_{u,v}$ is the set of items co-rated by both user $u$ and user $v$.

### 2.2 Rating Prediction & Score Aggregation
For target user $u$ and unrated item $i$, the predicted score is calculated over top-$N$ nearest neighbors $\mathcal{N}_u(i)$:
$$ \hat{r}_{u,i} = \bar{r}_u + \frac{\sum_{v \in \mathcal{N}_u(i)} S(u, v) \cdot (r_{v,i} - \bar{r}_v)}{\sum_{v \in \mathcal{N}_u(i)} |S(u, v)|} $$
where $\bar{r}_u$ is the mean rating of user $u$.

---

## 3. Architecture & Class Interface

### Source Location
- **Module**: `src/recolab/collaborative.py`
- **Class**: `UserBasedCF`
- **Protocol**: Implements `Recommender` protocol.

### Key Methods

#### `fit(ratings_df: pd.DataFrame, movies_df: Optional[pd.DataFrame] = None) -> UserBasedCF`
Constructs sparse user-item CSR rating matrix, computes user mean ratings, and precalculates pairwise user similarity matrix.

#### `recommend(user_id: int, k: int = 10, exclude_items: Optional[List[int]] = None) -> List[Tuple[int, float]]`
Identifies top neighbors for target user, aggregates neighbor ratings for unrated candidate items, and returns top-$K$ recommendations.

#### `explain(user_id: int, movie_id: int) -> Dict[str, Any]`
Returns list of top similar neighbors who rated `movie_id` along with their individual similarity weights and rating values.

---

## 4. Cold-Start Handling
- **Threshold**: Target users with fewer than `min_ratings=5` interactions cannot yield reliable neighbor similarities.
- **Fallback**: Automatically delegates recommendation calls for cold-start users to `ContentModel` (or `PopularityModel`).

---

## 5. Model Persistence & State
- **Bundle Format**: `to_bundle()` exports:
  - `user_item_matrix`: `scipy.sparse.csr_matrix`
  - `user_similarity_matrix`: Dense/sparse similarity array
  - `user_id_to_idx` / `idx_to_user_id`: ID mapping dictionaries
  - `item_id_to_idx` / `idx_to_item_id`: Item ID mapping dictionaries
  - `user_means`: Dictionary of user mean ratings

---

## 6. Performance Characteristics

| Metric | Benchmark Score |
|--------|-----------------|
| **Precision@10** | 0.0895 |
| **Recall@10** | 0.0712 |
| **NDCG@10** | 0.0984 |
| **Catalog Coverage** | 31.40% |
| **Mean Popularity Decile** | 7.15 |
| **Inference Latency** | ~8.0 ms per recommendation call |
| **Memory Footprint** | ~12 MB |
