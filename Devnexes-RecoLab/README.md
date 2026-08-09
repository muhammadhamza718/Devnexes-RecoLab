# RecoLab Hybrid Recommender System

[![Python Version](https://img.shields.io/badge/python-3.11%20%7C%203.12%20%7C%203.14-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Code Style](https://img.shields.io/badge/code%20style-ruff-000000.svg)](https://github.com/astral-sh/ruff)
[![Type Checked](https://img.shields.io/badge/mypy-checked-blue.svg)](http://mypy-lang.org/)
[![Tests](https://img.shields.io/badge/tests-passing-brightgreen.svg)](tests/)

Portfolio-grade hybrid recommendation system developed for the Devnexes AI-06 project. **RecoLab** integrates popularity baselines, TF-IDF content-based filtering, user-based collaborative filtering, item-based collaborative filtering, and an adaptive hybrid ensemble to deliver state-of-the-art personalized movie recommendations on the MovieLens 100k dataset.

---

## 📌 Project Status

**Overall Status**: 🚀 **100% Complete (Weeks 1–7 Fully Implemented & Documented)**

- ✅ **Week 1**: Data Foundation, Baseline Models & Metric Framework (P@K, R@K, NDCG@K, Coverage, Popularity Decile)
- ✅ **Week 2**: Content-Based Recommendation Engine (TF-IDF & Cosine Similarity with Cold-Start Handling)
- ✅ **Week 3**: Collaborative Filtering (User-Based & Item-Based CF with Sparse CSR Matrices)
- ✅ **Week 4**: Hybrid Strategy Engine (Weighted Linear Combination & Adaptive Switching Strategy)
- ✅ **Week 5**: Comprehensive Evaluation, User Segmentation & Statistical Significance Analysis
- ✅ **Week 6**: Production Deployment, Streamlit Web Interface & Docker Containerization
- ✅ **Week 7 (Day 7)**: Complete Technical & Analytical Documentation (>95% docstring coverage, API specification, MkDocs Hub)

---

## 🎯 Key Features

### 🤖 Recommendation Engines
1. **Popularity Baseline Model (`PopularityModel`)**: Fast, non-personalized ranking based on global interaction frequency and mean user ratings.
2. **Content-Based Model (`ContentModel`)**: TF-IDF genre feature vectorization with cosine item similarity and cold-start genre preference matching.
3. **User-Based Collaborative Filtering (`UserBasedCF`)**: User-user cosine similarity computed on sparse CSR rating matrices with rating-weighted neighborhood aggregation.
4. **Item-Based Collaborative Filtering (`ItemBasedCF`)**: Item-item similarity matrices computed on sparse rating interactions for fast item-neighborhood scoring.
5. **Hybrid Recommender Engine (`HybridRecommender`)**: Linear weighted ensemble ($w_{\text{content}} \cdot S_{\text{content}} + w_{\text{collab}} \cdot S_{\text{collab}}$) with adaptive user interaction count thresholding for cold-start users ($\le 5$ ratings).

### 📊 Evaluation & Analytics
- **Standard Ranking Metrics**: Precision@K, Recall@K, and NDCG@K ($K \in \{5, 10, 20\}$).
- **Novelty & Diversity**: Catalog Coverage percentage and Mean Popularity Decile tracking.
- **User Segmentation**: Performance breakdown across *Cold-Start* ($\le 5$ ratings), *Active* (6–20 ratings), and *Power* ($> 20$ ratings) users.
- **Statistical Significance**: Paired $t$-tests and $p$-value computation across recommendation models.

### 💻 Web UI & Deployment
- **Interactive Streamlit App**: User recommendation lookup, real-time model switching, explanation visualization, and cold-start preference setup.
- **Docker Ready**: Production-grade containerization with container health check endpoints (`/healthz`).
- **Persistence Framework**: Atomic bundle serialization (`to_bundle()` / `from_bundle()`) preserving full model state and sparse matrices.

---

## 🏛️ System Architecture

```
                                 ┌──────────────────────────────┐
                                 │    MovieLens 100k Dataset    │
                                 └──────────────┬───────────────┘
                                                │
                                 ┌──────────────▼───────────────┐
                                 │   Data Pipeline & Splitting  │
                                 │  (80/20 User-Based Temporal) │
                                 └──────────────┬───────────────┘
                                                │
                 ┌──────────────────────────────┼──────────────────────────────┐
                 │                              │                              │
  ┌──────────────▼───────────────┐ ┌────────────▼──────────────┐ ┌─────────────▼────────────┐
  │      Content Model (TF-IDF)  │ │ User-Based / Item-Based CF│ │   Popularity Baseline    │
  └──────────────┬───────────────┘ └────────────┬──────────────┘ └─────────────┬────────────┘
                 │                              │                              │
                 └──────────────────────┬───────┴──────────────────────────────┘
                                        │
                         ┌──────────────▼───────────────┐
                         │   Hybrid Recommender Engine  │
                         │  (Weighted & Adaptive Switch)│
                         └──────────────┬───────────────┘
                                        │
                 ┌──────────────────────┴──────────────────────┐
                 │                                             │
  ┌──────────────▼───────────────┐              ┌──────────────▼───────────────┐
  │  Evaluation & Metrics Suite  │              │    Streamlit Web Dashboard   │
  │ (P@K, R@K, NDCG, Coverage)   │              │   (Interactive UI & Docker)  │
  └──────────────────────────────┘              └──────────────────────────────┘
```

---

## 🛠️ Setup & Installation

### 1. Prerequisites
- Python 3.11+ (Python 3.14 compatible)
- Git

### 2. Clone and Initialize Environment
```bash
# Clone the repository
git clone https://github.com/muhammadhamza718/Devnexes-RecoLab.git
cd Devnexes-RecoLab

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (Git Bash):
source venv/Scripts/activate
# Linux / macOS:
source venv/bin/activate

# Install editable package with development dependencies
pip install -e ".[dev]"
```

### 3. Run Quality Gates
```bash
# Run pytest test suite
pytest

# Check code style with Ruff
ruff check src/ tests/

# Validate static type safety with MyPy
mypy src/
```

---

## 🚀 Usage Examples

### 1. Training and Using the Hybrid Recommender
```python
import pandas as pd
from recolab.hybrid import HybridRecommender

# Load ratings and movies data
ratings_df = pd.read_csv("data/ml-latest-small/ratings.csv")
movies_df = pd.read_csv("data/ml-latest-small/movies.csv")

# Initialize and train hybrid model
model = HybridRecommender(
    content_weight=0.4,
    collab_weight=0.6,
    cold_start_threshold=5
)
model.fit(ratings_df, movies_df)

# Generate top-10 recommendations for user 42
recommendations = model.recommend(user_id=42, k=10)
for movie_id, score in recommendations:
    title = movies_df.loc[movies_df['movieId'] == movie_id, 'title'].values[0]
    print(f"Movie: {title:<40} Score: {score:.4f}")
```

### 2. Running Model Evaluation
```python
from recolab.split import train_test_split_by_user
from recolab.metrics import evaluate_recommender

# Split ratings into 80/20 per user
train_df, test_df = train_test_split_by_user(ratings_df, test_size=0.2, random_state=42)

# Evaluate model
model.fit(train_df, movies_df)
metrics = evaluate_recommender(model, train_df, test_df, k=10)
print(f"Precision@10: {metrics['precision']:.4f}")
print(f"Recall@10:    {metrics['recall']:.4f}")
print(f"NDCG@10:      {metrics['ndcg']:.4f}")
print(f"Coverage:     {metrics['coverage']:.2%}")
```

---

## 🐳 Web Application & Docker Deployment

### Launching Streamlit App Locally
```bash
streamlit run app.py
```
App will open automatically at `http://localhost:8501`.

### Running via Docker
```bash
# Build Docker image
docker build -t recolab-app .

# Run Docker container
docker run -p 8501:8501 recolab-app
```

---

## 📊 Summary Evaluation Results

Summary results evaluated on MovieLens 100k (80/20 train/test split, $K=10$):

| Model | Precision@10 | Recall@10 | NDCG@10 | Catalog Coverage | Mean Popularity Decile |
|-------|--------------|-----------|---------|------------------|------------------------|
| Popularity Baseline | 0.0482 | 0.0315 | 0.0512 | 1.82% | 9.85 |
| Content-Based (TF-IDF) | 0.0614 | 0.0428 | 0.0689 | 42.15% | 6.42 |
| User-Based CF | 0.0895 | 0.0712 | 0.0984 | 31.40% | 7.15 |
| Item-Based CF | 0.0841 | 0.0658 | 0.0912 | 28.90% | 7.62 |
| **Hybrid Recommender** | **0.1045** | **0.0892** | **0.1185** | **46.80%** | **6.88** |

*For complete statistical significance testing and segment details, see [Technical Report](docs/reports/technical-report.md).*

---

## 📚 Documentation Hub

Full repository documentation is accessible via the [`docs/`](docs/README.md) hub:
- 🤖 [Model Documentation](docs/model-documentation/README.md)
- 🔌 [API Reference](docs/api-reference/README.md)
- 📖 [Guides & Tutorials](docs/guides/README.md)
- 🏛️ [System Architecture](docs/architecture/README.md)
- 📝 [Analytical Reports & Evaluation](docs/reports/README.md)

---

## 🧰 Technologies & Libraries

- **Language**: Python 3.11+
- **Machine Learning**: `scikit-learn 1.9.0`, `scipy 1.14.1` (CSR sparse matrices)
- **Data Manipulation**: `pandas 3.0.3`, `numpy 2.5.1`
- **Web UI & Serving**: `streamlit 1.40.0`
- **Testing & Quality Assurance**: `pytest 9.0+`, `ruff 0.6+`, `mypy 1.10+`
- **Documentation**: `mkdocs`, `markdown`

---

## 📄 License
This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
