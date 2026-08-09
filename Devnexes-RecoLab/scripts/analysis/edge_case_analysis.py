"""Edge Case Analysis Engine for Day 5 Afternoon.

Evaluates recommender performance on extreme edge cases:
- Sparse users (<= 3 ratings) vs Power users (> 50 ratings)
- New items (<= 5 ratings) vs Popular items (> 100 ratings)
- Genre-specific recommendation quality
- Temporal drift analysis across early/late rating splits
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Add scripts directory to path for path_utils import
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from path_utils import get_validated_project_root

PROJECT_ROOT = get_validated_project_root()
SRC_DIR = PROJECT_ROOT / "src"
EVAL_SCRIPTS = PROJECT_ROOT / "scripts" / "evaluation"
ANALYSIS_SCRIPTS = PROJECT_ROOT / "scripts" / "analysis"
for path_item in [SRC_DIR, EVAL_SCRIPTS, ANALYSIS_SCRIPTS]:
    if str(path_item) not in sys.path:
        sys.path.insert(0, str(path_item))

from analysis_storage import AnalysisStorage
from result_loader import EvaluationResultLoader
from run_evaluation import OfflineModelManager


class EdgeCaseAnalyzer:
    """Engine for performing edge-case performance evaluations."""

    def __init__(
        self,
        loader: EvaluationResultLoader | None = None,
        storage: AnalysisStorage | None = None,
    ) -> None:
        """Initialize EdgeCaseAnalyzer."""
        self.loader = loader or EvaluationResultLoader()
        self.storage = storage or AnalysisStorage()

        # Load dataset splits
        self.train_df = pd.read_csv(PROJECT_ROOT / "data" / "split_datasets" / "train.csv")
        self.test_df = pd.read_csv(PROJECT_ROOT / "data" / "split_datasets" / "test.csv")
        self.movies_df = pd.read_csv(PROJECT_ROOT / "data" / "ml-latest-small" / "movies.csv")

        # Counts
        self.user_counts = self.train_df.groupby("userId").size()
        self.item_counts = self.train_df.groupby("movieId").size()
        self.model_manager = OfflineModelManager()

    def analyze_edge_cases(
        self, model_names: list[str] | None = None
    ) -> dict[str, Any]:
        """Run edge case analysis across all requested models."""
        if model_names is None:
            model_names = self.model_manager.get_available_models()

        morning_results = self.loader.load_model_results(model_names)
        edge_results: dict[str, Any] = {}

        # Segment definitions
        sparse_users = set(self.user_counts[self.user_counts <= 3].index)
        power_users = set(self.user_counts[self.user_counts > 50].index)
        new_items = set(self.item_counts[self.item_counts <= 5].index)
        popular_items = set(self.item_counts[self.item_counts > 100].index)

        for model_name in model_names:
            print(f"Running edge case analysis for model: {model_name}...")
            model, _ = self.model_manager.get_model(model_name)
            morning = morning_results.get(model_name, {})

            res = {
                "model_name": model_name,
                "sparse_users": self._analyze_user_group(model, sparse_users, "sparse_users (<=3)"),
                "power_users": self._analyze_user_group(model, power_users, "power_users (>50)"),
                "new_items": self._analyze_item_group(model, new_items, "new_items (<=5)"),
                "popular_items": self._analyze_item_group(model, popular_items, "popular_items (>100)"),
                "genre_performance": self._analyze_genre_specific(model),
                "temporal_drift": self._analyze_temporal_drift(model),
                "baseline_comparison": {
                    "overall_p10": morning.get("k_metrics", {}).get("10", {}).get("precision", morning.get("precision", 0.05)),
                    "overall_r10": morning.get("k_metrics", {}).get("10", {}).get("recall", morning.get("recall", 0.03)),
                    "overall_ndcg10": morning.get("k_metrics", {}).get("10", {}).get("ndcg", morning.get("ndcg", 0.05)),
                },
            }

            edge_results[model_name] = res

        # Save to disk
        self.storage.save_result(
            category="edge_case_analysis",
            name="edge_case_summary",
            data=edge_results,
            add_timestamp=True,
        )

        return edge_results

    def _analyze_user_group(
        self, model: Any, target_users: set[int], group_label: str
    ) -> dict[str, float]:
        """Analyze Precision/Recall for a specific user subgroup."""
        pos_test = self.test_df[self.test_df["rating"] >= 3.0]
        test_by_user = pos_test.groupby("userId")["movieId"].apply(set).to_dict()

        eval_users = [u for u in self.test_df["userId"].unique() if u in target_users][:100]

        if not eval_users:
            return {"precision@10": 0.0, "recall@10": 0.0, "ndcg@10": 0.0, "count": 0}

        precisions, recalls, ndcgs = [], [], []

        for u in eval_users:
            relevant = test_by_user.get(u, set())
            if not relevant:
                continue

            try:
                recs = model.recommend(u, top_n=10)
                rec_ids = recs["movieId"].tolist() if isinstance(recs, pd.DataFrame) and "movieId" in recs else recs
            except Exception:
                rec_ids = []

            k = len(rec_ids)
            if k == 0:
                precisions.append(0.0)
                recalls.append(0.0)
                ndcgs.append(0.0)
                continue

            hits = len(set(rec_ids).intersection(relevant))
            p = hits / k
            r = hits / len(relevant)

            # DCG / NDCG
            dcg = sum(1.0 / np.log2(idx + 2) for idx, item in enumerate(rec_ids) if item in relevant)
            idcg = sum(1.0 / np.log2(idx + 2) for idx in range(min(k, len(relevant))))
            ndcg = dcg / idcg if idcg > 0 else 0.0

            precisions.append(p)
            recalls.append(r)
            ndcgs.append(ndcg)

        return {
            "precision@10": float(np.mean(precisions)) if precisions else 0.0,
            "recall@10": float(np.mean(recalls)) if recalls else 0.0,
            "ndcg@10": float(np.mean(ndcgs)) if ndcgs else 0.0,
            "count": len(eval_users),
        }

    def _analyze_item_group(
        self, model: Any, target_items: set[int], group_label: str
    ) -> dict[str, float]:
        """Analyze recommendation frequency and accuracy for item subgroup."""
        test_users = self.test_df["userId"].unique()[:100]

        recommended_count = 0
        total_recommendations = 0

        for u in test_users:
            try:
                recs = model.recommend(u, top_n=10)
                rec_ids = recs["movieId"].tolist() if isinstance(recs, pd.DataFrame) and "movieId" in recs else recs
            except Exception:
                rec_ids = []

            total_recommendations += len(rec_ids)
            recommended_count += len(set(rec_ids).intersection(target_items))

        share = float(recommended_count / total_recommendations) if total_recommendations > 0 else 0.0
        return {
            "recommendation_share": share,
            "recommended_target_items": recommended_count,
            "total_items_in_group": len(target_items),
        }

    def _analyze_genre_specific(self, model: Any) -> dict[str, float]:
        """Analyze recommendation precision by movie genre."""
        # Top 6 popular genres in MovieLens
        target_genres = ["Action", "Comedy", "Drama", "Sci-Fi", "Thriller", "Romance"]

        movie_genres = {}
        for _, row in self.movies_df.iterrows():
            genres = str(row["genres"]).split("|")
            movie_genres[row["movieId"]] = genres

        pos_test = self.test_df[self.test_df["rating"] >= 3.0]
        test_by_user = pos_test.groupby("userId")["movieId"].apply(set).to_dict()

        test_users = self.test_df["userId"].unique()[:100]
        genre_hits = {g: 0 for g in target_genres}
        genre_recs = {g: 0 for g in target_genres}

        for u in test_users:
            relevant = test_by_user.get(u, set())
            try:
                recs = model.recommend(u, top_n=10)
                rec_ids = recs["movieId"].tolist() if isinstance(recs, pd.DataFrame) and "movieId" in recs else recs
            except Exception:
                rec_ids = []

            for item_id in rec_ids:
                genres = movie_genres.get(item_id, [])
                for g in target_genres:
                    if g in genres:
                        genre_recs[g] += 1
                        if item_id in relevant:
                            genre_hits[g] += 1

        res = {}
        for g in target_genres:
            res[g] = float(genre_hits[g] / genre_recs[g]) if genre_recs[g] > 0 else 0.0
        return res

    def _analyze_temporal_drift(self, model: Any) -> dict[str, Any]:
        """Analyze temporal drift in recommendation quality between early and late test ratings."""
        median_ts = pd.to_numeric(self.test_df["timestamp"], errors='coerce').median()

        early_test = self.test_df[(self.test_df["timestamp"] <= median_ts) & (self.test_df["rating"] >= 3.0)]
        late_test = self.test_df[(self.test_df["timestamp"] > median_ts) & (self.test_df["rating"] >= 3.0)]

        early_by_user = early_test.groupby("userId")["movieId"].apply(set).to_dict()
        late_by_user = late_test.groupby("userId")["movieId"].apply(set).to_dict()

        sample_users = self.test_df["userId"].unique()[:100]

        early_precisions, late_precisions = [], []

        for u in sample_users:
            try:
                recs = model.recommend(u, top_n=10)
                rec_ids = recs["movieId"].tolist() if isinstance(recs, pd.DataFrame) and "movieId" in recs else recs
            except Exception:
                rec_ids = []

            k = len(rec_ids)
            if k == 0:
                continue

            # Early precision
            e_rel = early_by_user.get(u, set())
            if e_rel:
                early_precisions.append(len(set(rec_ids).intersection(e_rel)) / k)

            # Late precision
            l_rel = late_by_user.get(u, set())
            if l_rel:
                late_precisions.append(len(set(rec_ids).intersection(l_rel)) / k)

        e_mean = float(np.mean(early_precisions)) if early_precisions else 0.0
        l_mean = float(np.mean(late_precisions)) if late_precisions else 0.0

        return {
            "early_period_precision": e_mean,
            "late_period_precision": l_mean,
            "temporal_drift": float(l_mean - e_mean),
            "stable": abs(l_mean - e_mean) < 0.02,
        }
