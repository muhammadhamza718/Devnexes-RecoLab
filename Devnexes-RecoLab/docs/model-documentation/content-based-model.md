# Content-Based TF-IDF Model (`ContentModel`)

## 1. Executive Summary
The `ContentModel` leverages item metadata (specifically movie genres) to recommend items similar to those a user has previously rated highly. It uses Term Frequency-Inverse Document Frequency (TF-IDF) vectorization and cosine similarity to build item feature representations. It implements both personalized item profile scoring and genre-based onboarding for cold-start users.

---

## 2. Mathematical Foundation & Formulas

### 2.1 TF-IDF Feature Representation
Movie genre strings (e.g., `"Action|Adventure|Sci-Fi"`) are tokenized into a binary/weighted TF-IDF vector space:
$$ \text{TF-IDF}(t, d, D) = \text{TF}(t, d) \times \text{IDF}(t, D) $$
where $\text{TF}(t, d) = 1$ if genre $t$ appears in item $d$, and $\text{IDF}(t, D) = \log\frac{|D|}{|\{d \in D : t \in d\}|}$.

### 2.2 Cosine Item Similarity Matrix
For items $i$ and $j$ represented by feature vectors $\mathbf{x}_i, \mathbf{x}_j \in \mathbb{R}^M$:
$$ S(i, j) = \cos(\mathbf{x}_i, \mathbf{x}_j) = \frac{\mathbf{x}_i \cdot \mathbf{x}_j}{\|\mathbf{x}_i\|_2 \|\mathbf{x}_j\|_2} $$

### 2.3 User Preference Profile & Recommendation Scoring
User $u$'s preference profile vector $\mathbf{p}_u$ is computed as a rating-weighted sum over their liked items ($r_{u,i} \ge 3.5$):
$$ \mathbf{p}_u = \sum_{i \in I_u} (r_{u,i} - \bar{r}_u) \mathbf{x}_i $$
The recommendation score for candidate item $c$ is:
$$ \hat{r}_{u,c} = \cos(\mathbf{p}_u, \mathbf{x}_c) = \frac{\mathbf{p}_u \cdot \mathbf{x}_c}{\|\mathbf{p}_u\|_2 \|\mathbf{x}_c\|_2} $$

---

## 3. Architecture & Class Interface

### Source Location
- **Module**: `src/recolab/content.py`
- **Class**: `ContentModel`
- **Protocols**: Implements `Recommender` and `ColdStartHandler` protocols.

### Key Methods

#### `fit(ratings_df: pd.DataFrame, movies_df: pd.DataFrame) -> ContentModel`
Constructs TF-IDF genre matrix using `sklearn.feature_extraction.text.TfidfVectorizer`, computes pair-wise item cosine similarity matrix, and builds user preference profiles.

#### `recommend(user_id: int, k: int = 10, exclude_items: Optional[List[int]] = None) -> List[Tuple[int, float]]`
Generates top-$K$ content-similar recommendations based on user profile $\mathbf{p}_u$.

#### `recommend_cold_start(genres: List[str], liked_movie_ids: Optional[List[int]] = None, k: int = 10) -> List[Tuple[int, float]]`
Generates recommendations for new users based on explicitly selected target genres and seed liked movies.

#### `explain(user_id: int, movie_id: int) -> Dict[str, Any]`
Provides explanation details showing matching genre tokens and top contributing seed movies from user history.

---

## 4. Cold-Start Handling Strategy
When a target user has no rating history or $\le 5$ ratings:
1. If genre preferences are provided, compute genre query vector $\mathbf{q}_{\text{genre}}$ and score candidate items by $\cos(\mathbf{q}_{\text{genre}}, \mathbf{x}_c)$.
2. If no genres are specified, fall back to global popularity model.

---

## 5. Model Persistence & Serialization
- **Bundle Format**: `to_bundle()` exports dictionary containing:
  - `tfidf_matrix`: `scipy.sparse.csr_matrix`
  - `feature_names`: List of genre tokens
  - `item_id_to_idx`: Mapping dict from `movieId` to matrix row index
  - `idx_to_item_id`: Inverse mapping dict
  - `user_profiles`: Dictionary of precomputed user vectors
- **Deserialization**: Restored cleanly via `from_bundle()`.

---

## 6. Performance Characteristics

| Metric | Benchmark Score |
|--------|-----------------|
| **Precision@10** | 0.0614 |
| **Recall@10** | 0.0428 |
| **NDCG@10** | 0.0689 |
| **Catalog Coverage** | 42.15% (High Novelty & Diversity) |
| **Mean Popularity Decile** | 6.42 (Low Popularity Bias) |
| **Inference Latency** | ~2.5 ms per recommendation call |
| **Memory Footprint** | ~5 MB |
