# Data Flow & Pipeline Architecture

## Pipeline Overview

```
 [Raw Ratings & Movies CSVs]
             │
             ▼
 ┌──────────────────────┐
 │ Data Loading & Clean │  --> Standardizes schemas, validates rating ranges [0.5, 5.0]
 └───────────┬──────────┘
             │
             ▼
 ┌──────────────────────┐
 │ train_test_split_user│  --> 80% train / 20% test split per user
 └───────────┬──────────┘
             │
      ┌──────┴─────────────────────┐
      │                            │
      ▼                            ▼
┌───────────┐                ┌───────────┐
│ Train Set │                │ Test Set  │
└─────┬─────┘                └─────┬─────┘
      │                            │
      ▼                            │
┌───────────┐                      │
│ Model.fit │                      │
└─────┬─────┘                      │
      │                            │
      ▼                            ▼
 ┌──────────────────────────────────────┐
 │  evaluate_recommender(model, test)   │ --> Computes P@10, R@10, NDCG@10, Coverage
 └──────────────────────────────────────┘
```

## Matrix Representations
- **Ratings Matrix**: Represented as `scipy.sparse.csr_matrix` of shape $(U \times I)$.
- **Item Feature Matrix**: Represented as TF-IDF sparse matrix of shape $(I \times M)$ where $M$ is number of genre terms.
