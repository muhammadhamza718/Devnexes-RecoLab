# API Reference Index

This section provides complete Python API documentation, class definitions, function signatures, typing annotations, and usage examples for RecoLab modules.

---

## 🔌 API Modules

1. **[Core Interfaces & Protocols](interfaces.md)**
   - `Recommender` (Protocol)
   - `ColdStartHandler` (Protocol)
   - `FeatureError` & Custom Exceptions

2. **[Recommendation Models API](models.md)**
   - `PopularityModel` (`src/recolab/baseline.py`)
   - `ContentModel` (`src/recolab/content.py`)
   - `UserBasedCF` (`src/recolab/collaborative.py`)
   - `ItemBasedCF` (`src/recolab/collaborative.py`)
   - `HybridRecommender` (`src/recolab/hybrid.py`)

3. **[Evaluation & Ranking Metrics API](metrics.md)**
   - `precision_at_k`, `recall_at_k`, `ndcg_at_k`
   - `catalog_coverage`, `mean_popularity_decile`
   - `evaluate_recommender`

4. **[Persistence & Data Utilities API](persistence.md)**
   - `ModelBundle`, `save_bundle`, `load_bundle`
   - `train_test_split_by_user` (`src/recolab/split.py`)
