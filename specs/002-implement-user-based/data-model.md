# Data Model: User-Based Collaborative Filtering

**Feature**: 002-implement-user-based  
**Date**: 2026-07-29  
**Purpose**: Entity definitions and validation rules for user-based CF

---

## Core Entities

### UserBasedCF

**Purpose**: Main class implementing user-based collaborative filtering with Recommender protocol

**Attributes**:
- `user_item_matrix: scipy.sparse.csr_matrix` - Sparse user-item rating matrix (n_users × n_items)
- `similarity_matrix: scipy.sparse.csr_matrix` - Precomputed user-user cosine similarity (n_users × n_users)
- `user_mapping: Dict[int, int]` - Mapping from user_id to matrix row index
- `movie_mapping: Dict[int, int]` - Mapping from movie_id to matrix column index
- `reverse_user_mapping: Dict[int, int]` - Mapping from matrix row index to user_id
- `reverse_movie_mapping: Dict[int, int]` - Mapping from matrix column index to movie_id
- `k_similar_users: int` - Number of similar users to consider (default: 50)
- `min_similarity: float` - Minimum similarity threshold (default: 0.1)
- `content_model: ContentModel` - Fallback model for cold-start users
- `is_fitted: bool` - Flag indicating if model has been trained

**Validation Rules**:
- `user_item_matrix` must be CSR format with shape (n_users, n_items)
- `similarity_matrix` must be CSR format with shape (n_users, n_users)
- Mapping dictionaries must be consistent with matrix dimensions
- `k_similar_users` must be positive integer
- `min_similarity` must be between 0.0 and 1.0
- `content_model` must satisfy Recommender protocol
- `is_fitted` must be True before calling recommend()

**State Transitions**:
1. **Initial State**: `is_fitted = False`, matrices and mappings undefined
2. **Fitted State**: `is_fitted = True`, all matrices and mappings populated
3. **Error State**: Invalid input data or computation failure

---

### User-Item Matrix

**Purpose**: Sparse representation of user ratings for efficient computation

**Structure**:
- Rows: Users (indexed by user_mapping)
- Columns: Movies (indexed by movie_mapping)
- Values: User ratings (1-5 scale), 0 for missing/unrated
- Format: scipy.sparse.csr_matrix

**Validation Rules**:
- Must be sparse matrix (sparsity >90% typical)
- Shape must match dimensions of user_mapping and movie_mapping
- Values must be in range [0, 5] (0 indicates missing)
- No NaN values allowed
- Matrix must be immutable after fitting

**Business Rules**:
- Only rated movies have non-zero values
- Users with no ratings should be handled separately
- Matrix is built from training data only

---

### Similarity Matrix

**Purpose**: Precomputed user-user cosine similarity scores for efficient lookup

**Structure**:
- Rows: Users (indexed by user_mapping)
- Columns: Users (indexed by user_mapping)
- Values: Cosine similarity scores [-1, 1]
- Format: scipy.sparse.csr_matrix
- Diagonal: 1.0 (self-similarity)

**Validation Rules**:
- Must be symmetric matrix (similarity[i,j] = similarity[j,i])
- Diagonal values must equal 1.0
- Values must be in range [-1, 1]
- Shape must match user_item_matrix row count
- Matrix must be immutable after computation

**Business Rules**:
- Similarity computed on normalized rating vectors
- Used for finding k most similar users
- Cached after computation to avoid recomputation

---

### Index Mappings

**Purpose**: Efficient bidirectional conversion between IDs and matrix indices

**User Mapping**:
- Keys: user_id (int)
- Values: matrix row index (int)
- Validation: One-to-one mapping, no duplicates

**Movie Mapping**:
- Keys: movie_id (int)
- Values: matrix column index (int)
- Validation: One-to-one mapping, no duplicates

**Reverse Mappings**:
- Keys: matrix indices (int)
- Values: original IDs (int)
- Validation: Inverse of forward mappings

**Validation Rules**:
- Mappings must be consistent with matrix dimensions
- No gaps in index sequences
- Bidirectional consistency maintained
- All IDs in training data must be mapped

---

## Data Flow

### Training Flow

1. **Input**: pandas DataFrame with columns [user_id, movie_id, rating]
2. **Matrix Building**: Create user-item matrix from DataFrame
3. **Index Creation**: Build user and movie mappings
4. **Similarity Computation**: Compute user-user cosine similarity
5. **Storage**: Store matrices and mappings in UserBasedCF instance
6. **State Update**: Set `is_fitted = True`

### Recommendation Flow

1. **Input**: user_id, k, exclude_items (optional)
2. **Cold-Start Check**: Detect if user has ≤5 ratings
3. **Fallback**: If cold-start, delegate to ContentModel
4. **Index Lookup**: Convert user_id to matrix index
5. **Similar User Search**: Find k most similar users above threshold
6. **Aggregation**: Compute weighted average of similar users' ratings
7. **Filtering**: Exclude already-rated items and exclude_items
8. **Ranking**: Sort by predicted rating, return top-k
9. **ID Conversion**: Convert matrix indices back to movie_ids

---

## Integrity Constraints

### Training Data Constraints

- User IDs must be integers
- Movie IDs must be integers
- Ratings must be in range [1, 5]
- No duplicate (user_id, movie_id) pairs
- No null values in any column

### Matrix Constraints

- Matrices must maintain sparsity (>90%)
- Matrix dimensions must be consistent with mappings
- No negative values in user-item matrix
- Similarity matrix must be symmetric

### Recommendation Constraints

- Must return exactly k recommendations (or fewer if insufficient candidates)
- Recommendations must exclude already-rated items
- Recommendations must respect exclude_items parameter
- Cold-start users must receive fallback recommendations
- No NaN or infinite values in predictions

---

## Performance Considerations

### Memory Optimization

- Use CSR format for row-oriented operations
- Cache similarity matrix after computation
- Use sparse operations throughout pipeline
- Avoid dense matrix conversions

### Computation Optimization

- Precompute similarity during training
- Use efficient sklearn implementation
- Cache similar user indices for repeated calls
- Minimize matrix copies during operations

### Scalability Constraints

- Target dataset: MovieLens small (100k ratings, ~10k users, ~10k movies)
- Memory limit: <100MB for matrices
- Recommendation time: <100ms per request
- Similarity computation: <5 seconds total

---

## Error Handling

### Training Errors

- **Empty Training Data**: Raise ValueError with descriptive message
- **Invalid Ratings**: Raise ValueError for ratings outside [1,5]
- **Duplicate Entries**: Raise ValueError for duplicate (user_id, movie_id)
- **Memory Error**: Raise MemoryError with dataset size guidance

### Recommendation Errors

- **Unfitted Model**: Raise RuntimeError if recommend() called before fit()
- **Invalid User ID**: Raise KeyError for user_id not in training data
- **Invalid k Value**: Raise ValueError for k ≤ 0
- **Computation Failure**: Raise RuntimeError with diagnostic information

### Cold-Start Errors

- **ContentModel Failure**: Propagate ContentModel exceptions
- **No Similar Users**: Fall back to ContentModel gracefully
- **Threshold Issues**: Log warning and adjust threshold