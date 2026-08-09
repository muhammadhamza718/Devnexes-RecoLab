# Evaluation Workflow & Analysis Guide

This guide describes how to run offline evaluations, generate comparative benchmarking metrics, perform user segmentation, and execute statistical significance tests on RecoLab models.

---

## 1. Overview of Evaluation Pipeline

```
  ┌─────────────────────────┐
  │  MovieLens Ratings Data │
  └────────────┬────────────┘
               │
  ┌────────────▼────────────┐
  │ train_test_split_user   │  <-- 80/20 User-Based Temporal Split
  └────────────┬────────────┘
               │
 ┌─────────────┴─────────────┐
 │                           │
┌▼─────────────────────────┐ ┌▼─────────────────────────┐
│     Train Models         │ │  Evaluate Test Set      │
│ (Baseline, Content, CF,  │ │ (Precision@K, Recall@K, │
│  Hybrid)                 │ │  NDCG@K, Coverage)      │
└──────────────────────────┘ └────────────┬────────────┘
                                          │
                             ┌────────────▼────────────┐
                             │ Export JSON & Charts    │
                             │ (data/evaluation/...)   │
                             └─────────────────────────┘
```

---

## 2. Executing Evaluation Pipeline

### Step 1: Run Full Evaluation Pipeline
To run evaluation across all 5 models and output result JSON files:
```bash
python -m scripts.evaluation.evaluate_all_models --k 10 --test-size 0.2
```

### Step 2: Run User Segmentation Analysis
Segment users into Cold Start ($\le 5$ ratings), Active (6–20 ratings), and Power ($> 20$ ratings):
```bash
python -m scripts.analysis.user_segmentation_analysis
```

### Step 3: Run Statistical Significance Tests
Compute paired $t$-tests and $p$-values across model pairs:
```bash
python -m scripts.analysis.statistical_significance_test
```

### Step 4: Render Visualizations
Generate metric comparison charts and radar plots:
```bash
python -m scripts.analysis.generate_evaluation_charts
```
Visualizations are saved to `data/evaluation/visualizations/`.
