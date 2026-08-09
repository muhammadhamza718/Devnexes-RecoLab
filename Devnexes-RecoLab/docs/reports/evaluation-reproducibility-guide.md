# Evaluation Reproducibility Guide

## 1. Goal

This guide outlines the exact, deterministic steps required to reproduce the Day 5 offline evaluation metrics synthesized in the Technical Evaluation Report. The system guarantees exact numerical reproducibility provided the starting dataset and environment are identical.

---

## 2. Prerequisites

### Environment Setup

Ensure you are using the precise dependency tree defined for the project.

```bash
# Verify Python version (must be >= 3.9)
python --version 

# Activate virtual environment
source venv/Scripts/activate  # (Windows)
# or
source venv/bin/activate      # (Unix)

# Install strict dependency versions
pip install -r requirements.txt
```

### Dataset

The evaluation pipeline relies on `ratings.csv` and `movies.csv` present in `data/raw/`.

**Expected Checksums/Shapes**:
- If using a standard test harness, `ratings.csv` should match the expected initial load size. The evaluation script operates defensively against data mutations but assumes stability of the raw inputs.

---

## 3. Running the Pipeline

To run the complete benchmark suite mapping across all models and K-values, execute the main analysis controller:

```bash
# Run from the repository root
PYTHONPATH=. python scripts/run_evaluation.py
```

### What this script does implicitly:
1. **Data Load**: Ingests raw CSVs via `src.recolab.data_loader`
2. **Stratification**: Performs a user-based temporal holdout slice (`test_size=0.2`) anchored with `random_state=42`.
3. **Execution**: Initializes all 5 `Recommender` protocol implementations sequentially.
4. **Metrics**: For every user in the holdout, calculates $P@K, R@K, NDCG@K$ against predictions.
5. **Persistence**: Saves raw metrics, significance distributions, and MD summaries to `data/evaluation/`.

---

## 4. Manual Verification / Debugging

If comparing differences manually inside a REPL or Jupyter notebook, ensure you mimic the temporal split exactly:

```python
from src.recolab.data_loader import RecoDataLoader
from src.recolab.split import train_test_split_by_user

# 1. Load Data
loader = RecoDataLoader(ratings_path="data/raw/ratings.csv", movies_path="data/raw/movies.csv")
ratings, movies = loader.load_data()

# 2. Strict Temporal Split - Random State 42 is REQUIRED for reproducibility
train_df, test_df = train_test_split_by_user(ratings, test_size=0.2, random_state=42)

print(f"Train size: {len(train_df)} | Test size: {len(test_df)}")
```

### Seed Control
RecoLab does not heavily rely on stochastic model initializations (e.g., pure SGD or deep learning dropouts). The algorithms (Item CF, User CF, TF-IDF, Popularity) are deterministic linear algebra calculations. Therefore, reproducibility hinges purely on the training/test partition determinism (`random_state=42`).

---

## 5. Artifact Inspection

After a successful run, the following directory tree is synchronized with the new outputs:

```
data/evaluation/
├── comparison/
│   └── comparison_<TIMESTAMP>.json
├── results/
│   ├── evaluation_summary.md
│   ├── hybrid_results_<TIMESTAMP>.json
│   ├── item_based_cf_results_<TIMESTAMP>.json
│   ├── popularity_results_<TIMESTAMP>.json
│   └── ...
└── segmented/
    ├── content_active_users_<TIMESTAMP>.json
    ├── hybrid_cold_start_users_<TIMESTAMP>.json
    └── ...
```

Check `evaluation_summary.md` generated in `data/evaluation/results/` to confirm metrics match the published Technical Report.
