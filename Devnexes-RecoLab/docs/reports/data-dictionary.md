# Data Dictionary

## 1. Overview

This document details the schema of the datasets utilized by the RecoLab system for model training and evaluation. The primary dataset is based on the MovieLens dataset structures.

---

## 2. Source Files

### 2.1 `ratings.csv`
Provides explicit feedback interactions between users and items.

| Column | Data Type | Description | Range / Constraints |
|--------|----------|-------------|--------------------|
| `userId` | Integer | Unique identifier for a user | Minimum: 1 |
| `movieId` | Integer | Unique identifier for an item (movie) | Minimum: 1 |
| `rating` | Float | Explicit preference score given by the user | $0.5 \le x \le 5.0$ (0.5 increments) |
| `timestamp` | Integer | Unix epoch timestamp of the interaction | Valid positive integer |

**Integrity Constraints:**
- A `(userId, movieId)` combination must be unique (deduplicated by keeping the most recent timestamp).
- Every user must have at least one interaction to be included.

### 2.2 `movies.csv`
Provides metadata and content attributes for items.

| Column | Data Type | Description | Example |
|--------|----------|-------------|---------|
| `movieId` | Integer | Unique identifier for an item | 1 |
| `title` | String | Title of the movie, including release year | "Toy Story (1995)" |
| `genres` | String | Pipe-separated (`\|`) list of genres | "Adventure\|Animation\|Children\|Comedy" |

**Integrity Constraints:**
- `movieId` acts as the primary key.
- Items lacking genre data are marked as `(no genres listed)`.

---

## 3. Manufactured / Transformed Artifacts

### 3.1 Sparse Ratings Matrix
Generated during model `fit()` and pipeline steps.

- **Type**: `scipy.sparse.csr_matrix` (Compressed Sparse Row).
- **Dimensions**: $U \times I$ ($U$ = total distinct users, $I$ = total distinct items).
- **Values**: Floating point `rating` values; missing interactions are implicit $0.0$.

### 3.2 Content TF-IDF Matrix
Created via `TfidfVectorizer` mapping genre text into sparse vectors.

- **Type**: `scipy.sparse.csr_matrix`.
- **Dimensions**: $I \times F$ ($I$ = items, $F$ = distinct genre vocabulary terms).
- **Values**: Frequency/Importance scores normalized to unit length.

### 3.3 Evaluation Results Artifacts (`results.json`)
The output schema for `evaluate_recommender()` serializations.

| Field | Type | Description |
|-------|------|-------------|
| `model` | String | Name of the evaluated algorithm |
| `precision@K` | Float | Evaluation score (K=5,10,20) |
| `recall@K` | Float | Evaluation score (K=5,10,20) |
| `ndcg@K` | Float | Evaluation score (K=5,10,20) |
| `catalog_coverage` | Float | Percentage of catalog recommended |
| `mean_popularity_decile` | Float | Average popularity bin (1=highly popular, 10=obscure) |
