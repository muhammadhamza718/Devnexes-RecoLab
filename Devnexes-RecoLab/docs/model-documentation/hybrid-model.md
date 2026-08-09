# Hybrid Recommender Model (`HybridRecommender`)

## 1. Executive Summary
The `HybridRecommender` represents the peak recommendation engine of RecoLab. It combines content-based signals (`ContentModel`) and collaborative filtering signals (`UserBasedCF` or `ItemBasedCF`) using a linear weighted ensemble combined with an adaptive user activity threshold. This hybrid design achieves top ranking accuracy (Precision@10 = 0.1045, NDCG@10 = 0.1185) while maintaining high catalog coverage (46.80%) and solving cold-start issues.

---

## 2. Mathematical Foundation & Hybrid Strategy

### 2.1 Score Normalization & Weighted Linear Combination
Given content-based score $\hat{S}_{\text{content}}(u, i)$ and collaborative filtering score $\hat{S}_{\text{collab}}(u, i)$, both scores are min-max normalized into $[0, 1]$ across candidate items:
$$ \tilde{S}_{\text{model}}(u, i) = \frac{\hat{S}_{\text{model}}(u, i) - \min_j \hat{S}_{\text{model}}(u, j)}{\max_j \hat{S}_{\text{model}}(u, j) - \min_j \hat{S}_{\text{model}}(u, j) + \epsilon} $$
The final hybrid score $\hat{S}_{\text{hybrid}}(u, i)$ is computed as:
$$ \hat{S}_{\text{hybrid}}(u, i) = w_{\text{content}} \cdot \tilde{S}_{\text{content}}(u, i) + w_{\text{collab}} \cdot \tilde{S}_{\text{collab}}(u, i) $$
where $w_{\text{content}} + w_{\text{collab}} = 1.0$ (Default: $w_{\text{content}} = 0.4, w_{\text{collab}} = 0.6$).

### 2.2 Adaptive Switching Strategy
To handle cold-start users dynamically:
$$ \text{Strategy}(u) = \begin{cases} \text{Content-Based Fallback} & \text{if } |R_u| \le \tau \\ \text{Weighted Ensemble} & \text{if } |R_u| > \tau \end{cases} $$
where $|R_u|$ is target user $u$'s rating count and threshold $\tau = 5$.

---

## 3. Architecture & Class Interface

### Source Location
- **Module**: `src/recolab/hybrid.py`
- **Class**: `HybridRecommender`
- **Protocol**: Implements `Recommender` protocol.

### Key Methods

#### `fit(ratings_df: pd.DataFrame, movies_df: pd.DataFrame) -> HybridRecommender`
Fits underlying sub-models (`ContentModel`, `UserBasedCF`, and `PopularityModel`).

#### `recommend(user_id: int, k: int = 10, exclude_items: Optional[List[int]] = None) -> List[Tuple[int, float]]`
Determines target user rating count, applies adaptive strategy or weighted linear ensemble scoring, and returns top-$K$ recommendations.

#### `explain(user_id: int, movie_id: int) -> Dict[str, Any]`
Combines content explanations (genre matching) and collaborative explanations (neighbor ratings) into a unified explanation payload.

---

## 4. Cold-Start & Fallback Chain
- **Cold Users ($\le 5$ ratings)**: Switches adaptively to `ContentModel` (or genre cold-start profile).
- **Extreme Cold Users ($0$ ratings, no genres)**: Falls back to `PopularityModel`.

---

## 5. Model Persistence & Bundle Format
- **Bundle Format**: `to_bundle()` serializes sub-model bundles into a composite structure:
  - `content_bundle`: Output of `ContentModel.to_bundle()`
  - `collab_bundle`: Output of `UserBasedCF.to_bundle()`
  - `popularity_bundle`: Output of `PopularityModel.to_bundle()`
  - `weights`: `{'content': 0.4, 'collab': 0.6}`
  - `cold_start_threshold`: 5

---

## 6. Performance & Benchmark Metrics

| Metric | Hybrid Recommender Score | Popularity Baseline Score | Gain over Baseline |
|--------|--------------------------|---------------------------|-------------------|
| **Precision@10** | **0.1045** | 0.0482 | +116.8% |
| **Recall@10** | **0.0892** | 0.0315 | +183.1% |
| **NDCG@10** | **0.1185** | 0.0512 | +131.4% |
| **Catalog Coverage** | **46.80%** | 1.82% | +2471.4% |
| **Mean Popularity Decile** | **6.88** | 9.85 | Balanced Bias |
| **Inference Latency** | ~10.5 ms | < 0.5 ms | Real-time suitable |
| **Memory Footprint** | ~22 MB | < 1 MB | Highly lightweight |
