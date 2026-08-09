# System Architecture Overview

## 1. Design Philosophy
RecoLab is architected around **clean interface boundaries**, **duck-typed runtime protocols**, **high computational efficiency**, and **tiered fallback mechanisms**.

```
                           ┌───────────────────────────────┐
                           │      Recommender Protocol     │
                           └───────────────┬───────────────┘
                                           │
       ┌───────────────────┬───────────────┼───────────────┬───────────────────┐
       │                   │               │               │                   │
┌──────▼──────┐     ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐     ┌──────▼──────┐
│ Popularity  │     │   Content   │ │ User-Based  │ │ Item-Based  │     │   Hybrid    │
│  Baseline   │     │ (TF-IDF)    │ │ Collaborative││ Collaborative│    │  Recommender│
└─────────────┘     └─────────────┘ └─────────────┘ └─────────────┘     └─────────────┘
```

## 2. Architectural Layers

1. **Interface Layer (`interfaces.py`)**: Defines standard protocols (`Recommender`, `ColdStartHandler`) and custom exceptions (`FeatureError`).
2. **Model Layer (`baseline.py`, `content.py`, `collaborative.py`, `hybrid.py`)**: Implements concrete recommendation algorithms with uniform `fit()` and `recommend()` interfaces.
3. **Persistence Layer (`persistence.py`)**: Handles atomic state serialization using `ModelBundle` artifacts.
4. **Evaluation & Analytics Layer (`metrics.py`, `split.py`)**: Provides offline split logic and ranking metrics ($P@K, R@K, NDCG@K$).
5. **Presentation Layer (`app.py`, Streamlit UI)**: Provides interactive web application serving.
