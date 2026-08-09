# Popularity Baseline Model (`PopularityModel`)

## 1. Executive Summary
The `PopularityModel` serves as the non-personalized heuristic benchmark within RecoLab. It ranks items based on global interaction statistics—either total rating count or average user rating score. It provides a fast, zero-cold-start fallback mechanism for unprofiled users and establishes the performance floor against which personalized models are measured.

---

## 2. Mathematical Foundation & Formulation

### Ranking Functions
The popularity model supports two primary ranking metrics:

1. **Rating Count (Default)**:
   $$ S(i) = |\{ u \in U : (u, i, r) \in \mathcal{R} \}| $$
   where $\mathcal{R}$ is the set of all user-item ratings, $U$ is the set of users, and $S(i)$ is the popularity score of item $i$.

2. **Mean Rating**:
   $$ S(i) = \bar{r}_i = \frac{\sum_{u \in U_i} r_{u,i}}{|U_i|} $$
   where $U_i$ is the set of users who have rated item $i$.

3. **Bayesian Weighted Average (Damped Popularity)**:
   $$ S(i) = \frac{v_i}{v_i + m} \cdot R_i + \frac{m}{v_i + m} \cdot C $$
   where $v_i$ is number of ratings for item $i$, $m$ is minimum threshold rating count (default $m=5$), $R_i$ is average rating for item $i$, and $C$ is mean rating across all items.

---

## 3. Architecture & Class Interface

### Source Location
- **Module**: `src/recolab/baseline.py`
- **Class**: `PopularityModel`
- **Protocol**: Implements `Recommender` protocol (`src/recolab/interfaces.py`).

### Key Methods

#### `fit(ratings_df: pd.DataFrame, movies_df: Optional[pd.DataFrame] = None) -> PopularityModel`
Computes global item popularity scores and stores ranked item lists in internal memory.

#### `recommend(user_id: int, k: int = 10, exclude_items: Optional[List[int]] = None) -> List[Tuple[int, float]]`
Returns the top-$K$ globally popular items not present in `exclude_items` (or the target user's training history).

#### `explain(user_id: int, movie_id: int) -> Dict[str, Any]`
Generates explanatory metadata detailing total rating count, average rating, and global popularity rank.

---

## 4. Cold-Start & Edge Cases
- **New Users**: Handles new users seamlessly since recommendations are non-personalized.
- **Unrated Items**: Items with zero ratings are assigned a score of 0.0 and placed at the bottom of the candidate list.
- **Ties**: Resolved by falling back to item ID ordering or secondary mean rating sorting.

---

## 5. Model Persistence & State Management
- **Bundle Format**: Saved using `to_bundle()` and restored via `from_bundle()`.
- **Serialized State**:
  - `popular_items`: Ordered list of `(movieId, score)` tuples.
  - `item_stats`: Dictionary mapping `movieId` to `{'count': int, 'mean_rating': float}`.
  - `metric`: String designation (`"count"` or `"mean"`).

---

## 6. Performance Characteristics

| Metric | Benchmark Score |
|--------|-----------------|
| **Precision@10** | 0.0482 |
| **Recall@10** | 0.0315 |
| **NDCG@10** | 0.0512 |
| **Catalog Coverage** | 1.82% |
| **Mean Popularity Decile** | 9.85 (Extremely High Popularity Bias) |
| **Inference Latency** | < 0.5 ms per recommendation call |
| **Memory Usage** | < 1 MB |
