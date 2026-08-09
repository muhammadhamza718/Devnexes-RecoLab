# Model Documentation Index

This directory contains comprehensive technical documentation, mathematical foundations, and implementation details for all recommendation models implemented in RecoLab.

---

## 📑 Model Index

| Model Name | Type | Key Features | Primary File |
|------------|------|--------------|--------------|
| [Popularity Baseline](popularity-baseline.md) | Heuristic / Non-Personalized | Global rating count & mean rating ranking, fast fallback | `src/recolab/baseline.py` |
| [Content-Based Model](content-based-model.md) | Content / TF-IDF | Genre TF-IDF vectors, cosine similarity, genre cold-start fallback | `src/recolab/content.py` |
| [User-Based CF](user-based-cf.md) | Collaborative Filtering | Cosine user-user similarity matrix, weighted rating aggregation | `src/recolab/collaborative.py` |
| [Item-Based CF](item-based-cf.md) | Collaborative Filtering | Cosine item-item similarity matrix, item-neighborhood scoring | `src/recolab/collaborative.py` |
| [Hybrid Recommender](hybrid-model.md) | Ensemble / Adaptive | Linear weighted ensemble, adaptive user activity threshold switching | `src/recolab/hybrid.py` |

---

## 🛠️ Shared Model Protocols
All recommendation models implement the standard [`Recommender`](../api-reference/interfaces.md) protocol:
- `fit(ratings_df, movies_df=None)`
- `recommend(user_id, k=10, exclude_items=None)`
- `explain(user_id, movie_id)`
- `to_bundle()` / `from_bundle(bundle)`
