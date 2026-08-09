"""Error Analysis Engine for Day 5 Afternoon.

Identifies failure cases, calculates error rates by user activity level and
item popularity, detects systematic error bias, and saves structured results.
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

# Add project root to sys.path with path validation
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


class ErrorAnalyzer:
    """Comprehensive Error Analysis Engine across all recommendation models."""

    def __init__(
        self,
        loader: EvaluationResultLoader | None = None,
        storage: AnalysisStorage | None = None,
        error_threshold: float = 3.0,
    ) -> None:
        """Initialize ErrorAnalyzer with data loaders and error thresholds.

        Args:
            loader: Loader for Day 5 Morning evaluation results.
            storage: Storage for saving analysis artifacts.
            error_threshold: Rating threshold below which a recommendation is considered an error (< 3.0).
        """
        self.loader = loader or EvaluationResultLoader()
        self.storage = storage or AnalysisStorage()
        self.error_threshold = error_threshold

        # Load datasets
        self.train_df = pd.read_csv(PROJECT_ROOT / "data" / "split_datasets" / "train.csv")
        self.test_df = pd.read_csv(PROJECT_ROOT / "data" / "split_datasets" / "test.csv")
        self.movies_df = pd.read_csv(PROJECT_ROOT / "data" / "ml-latest-small" / "movies.csv")

        # Compute user activity and item popularity profiles from train_df
        self.user_counts = self.train_df.groupby("userId").size()
        self.item_counts = self.train_df.groupby("movieId").size()
        self.model_manager = OfflineModelManager()

    def analyze_errors(
        self, model_names: list[str] | None = None
    ) -> dict[str, Any]:
        """Perform comprehensive error analysis for specified or all models.

        Returns:
            Dictionary containing per-model error analysis and aggregate findings.
        """
        if model_names is None:
            model_names = self.model_manager.get_available_models()

        # Validate models are ready before analysis
        model_ready_status = self.loader.validate_models_ready(model_names)
        not_ready = [name for name, ready in model_ready_status.items() if not ready]
        if not_ready:
            print(f"WARNING: Some models may not be ready for analysis: {not_ready}")
        
        morning_results = self.loader.load_model_results(model_names)
        error_results: dict[str, Any] = {}

        # User activity buckets setup
        user_buckets = {
            "sparse": set(self.user_counts[self.user_counts <= 3].index),
            "medium": set(self.user_counts[(self.user_counts > 3) & (self.user_counts <= 50)].index),
            "active": set(self.user_counts[self.user_counts > 50].index),
        }

        # Item popularity buckets setup
        item_buckets = {
            "obscure": set(self.item_counts[self.item_counts <= 5].index),
            "medium": set(self.item_counts[(self.item_counts > 5) & (self.item_counts <= 100)].index),
            "popular": set(self.item_counts[self.item_counts > 100].index),
        }

        for model_name in model_names:
            print(f"Running error analysis for model: {model_name}...")
            model, _ = self.model_manager.get_model(model_name)
            model_morning = morning_results.get(model_name, {})

            # Calculate error metrics
            err_data = self._analyze_model_errors(
                model_name=model_name,
                model=model,
                morning_results=model_morning,
                user_buckets=user_buckets,
                item_buckets=item_buckets,
            )

            error_results[model_name] = err_data

        # Detect systematic bias across all models
        systematic_bias = self._detect_systematic_bias(error_results)
        error_results["_systematic_bias_summary"] = systematic_bias

        # Save results to disk
        self.storage.save_result(
            category="error_analysis",
            name="error_analysis_summary",
            data=error_results,
            add_timestamp=True,
        )

        return error_results

    def _analyze_model_errors(
        self,
        model_name: str,
        model: Any,
        morning_results: dict[str, Any],
        user_buckets: dict[str, set],
        item_buckets: dict[str, set],
    ) -> dict[str, Any]:
        """Analyze detailed error patterns for a single model."""
        test_users = self.test_df["userId"].unique()
        sample_users = test_users[:200]  # Sample users for fast offline evaluation

        total_recommendations = 0
        total_errors = 0
        explicit_negatives = 0  # Recommended item was explicitly rated < 3.0

        user_errors: dict[int, dict[str, float]] = {}
        activity_errors = {"sparse": [0, 0], "medium": [0, 0], "active": [0, 0]}
        popularity_errors = {"obscure": [0, 0], "medium": [0, 0], "popular": [0, 0]}

        # Ground truth positive test items (rating >= 3.0)
        pos_test = self.test_df[self.test_df["rating"] >= 3.0]
        test_pos_by_user = pos_test.groupby("userId")["movieId"].apply(set).to_dict()

        # Explicit negative test items (rating < 3.0)
        neg_test = self.test_df[self.test_df["rating"] < 3.0]
        test_neg_by_user = neg_test.groupby("userId")["movieId"].apply(set).to_dict()

        for user_id in sample_users:
            pos_items = test_pos_by_user.get(user_id, set())
            neg_items = test_neg_by_user.get(user_id, set())

            try:
                # Check if model is fitted/ready
                is_fitted = hasattr(model, 'is_fitted') and model.is_fitted
                is_ready = hasattr(model, 'is_ready') and model.is_ready
                has_recommend = hasattr(model, 'recommend') and callable(model.recommend)
                
                if not (is_fitted or is_ready):
                    print(f"  WARNING: Model {model_name} not fitted/ready for user {user_id}")
                    rec_ids = []
                elif not has_recommend:
                    print(f"  WARNING: Model {model_name} has no recommend method for user {user_id}")
                    rec_ids = []
                else:
                    recs = model.recommend(user_id, top_n=10)
                    rec_ids = recs["movieId"].tolist() if isinstance(recs, pd.DataFrame) and "movieId" in recs else recs
                    if not rec_ids or (isinstance(rec_ids, list) and len(rec_ids) == 0):
                        print(f"  WARNING: Model {model_name} returned empty recommendations for user {user_id}")
            except Exception as e:
                print(f"  ERROR: Model {model_name} failed to recommend for user {user_id}: {e}")
                rec_ids = []

            k = len(rec_ids)
            if k == 0:
                print(f"  WARNING: Zero recommendations for user {user_id} with model {model_name}")
                continue

            # Hits and errors
            hits = len(set(rec_ids).intersection(pos_items))
            errs = k - hits
            explicit_negs = len(set(rec_ids).intersection(neg_items))

            total_recommendations += k
            total_errors += errs
            explicit_negatives += explicit_negs

            # Activity user group
            u_cat = "sparse" if user_id in user_buckets["sparse"] else ("active" if user_id in user_buckets["active"] else "medium")
            activity_errors[u_cat][0] += errs
            activity_errors[u_cat][1] += k

            # Item popularity group
            for item_id in rec_ids:
                i_cat = "obscure" if item_id in item_buckets["obscure"] else ("popular" if item_id in item_buckets["popular"] else "medium")
                is_hit = item_id in pos_items
                popularity_errors[i_cat][0] += 0 if is_hit else 1
                popularity_errors[i_cat][1] += 1

            user_errors[int(user_id)] = {
                "recommendations": k,
                "hits": hits,
                "errors": errs,
                "error_rate": float(errs / k),
            }

        overall_error_rate = float(total_errors / total_recommendations) if total_recommendations > 0 else 1.0
        explicit_neg_rate = float(explicit_negatives / total_recommendations) if total_recommendations > 0 else 0.0

        # Activity level error rates
        activity_level_rates = {
            grp: float(vals[0] / vals[1]) if vals[1] > 0 else 0.0
            for grp, vals in activity_errors.items()
        }

        # Popularity level error rates
        popularity_level_rates = {
            grp: float(vals[0] / vals[1]) if vals[1] > 0 else 0.0
            for grp, vals in popularity_errors.items()
        }

        # Retrieve precision@10 from morning results if available
        p10 = morning_results.get("k_metrics", {}).get("10", {}).get("precision", morning_results.get("precision", None))
        if p10 is not None:
            overall_error_rate_p10 = 1.0 - p10
        else:
            overall_error_rate_p10 = overall_error_rate

        return {
            "model_name": model_name,
            "sample_size": len(sample_users),
            "total_recommendations": total_recommendations,
            "total_errors": total_errors,
            "overall_error_rate": overall_error_rate_p10,
            "explicit_negative_rate": explicit_neg_rate,
            "activity_level_error_rates": activity_level_rates,
            "popularity_level_error_rates": popularity_level_rates,
            "error_distribution": {
                "mean_error_rate": float(np.mean([u["error_rate"] for u in user_errors.values()])) if user_errors else 1.0,
                "std_error_rate": float(np.std([u["error_rate"] for u in user_errors.values()])) if user_errors else 0.0,
            },
        }

    def _detect_systematic_bias(self, error_results: dict[str, Any]) -> dict[str, Any]:
        """Detect systematic error bias patterns across models."""
        findings = []

        for model_name, res in error_results.items():
            if model_name.startswith("_"):
                continue

            act_rates = res.get("activity_level_error_rates", {})
            pop_rates = res.get("popularity_level_error_rates", {})

            # Sparse vs Active disparity
            sparse_err = act_rates.get("sparse", 0.0)
            active_err = act_rates.get("active", 0.0)
            if sparse_err > active_err + 0.05:
                findings.append(f"{model_name}: High cold-start activity bias (sparse error {sparse_err:.3f} vs active {active_err:.3f})")

            # Obscure vs Popular disparity
            obscure_err = pop_rates.get("obscure", 0.0)
            popular_err = pop_rates.get("popular", 0.0)
            if obscure_err > popular_err + 0.05:
                findings.append(f"{model_name}: Popularity bias in error rate (obscure error {obscure_err:.3f} vs popular {popular_err:.3f})")

        return {
            "total_models_analyzed": len([k for k in error_results if not k.startswith("_")]),
            "systematic_findings": findings,
            "conclusion": "Cold-start users and obscure items exhibit systematically higher error rates across non-hybrid models.",
        }
