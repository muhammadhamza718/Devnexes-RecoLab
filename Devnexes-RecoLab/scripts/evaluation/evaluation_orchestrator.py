"""Main evaluation orchestrator for Day 5 Morning.

Coordinates comprehensive evaluation of all 5 recommendation models on the
complete test set, generating metrics, comparisons, and segmented analysis.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

# Add project to path
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from recolab.metrics import evaluate_all, evaluate_user

from config import (
    K_VALUES,
    MODEL_NAMES,
    RANDOM_SEED,
    TEST_CSV,
    TRAIN_CSV,
)
from result_storage import ResultStorage
from validation import (
    validate_model_availability,
    validate_test_data,
    validate_train_data,
)


class EvaluationOrchestrator:
    """Orchestrates comprehensive evaluation of all recommendation models.

    Coordinates:
    - Per-model evaluation on complete test set
    - Metrics aggregation (P@K, R@K, NDCG@K, coverage, popularity bias)
    - Segmented evaluation by user activity and item characteristics
    - Result storage with validation
    """

    def __init__(
        self,
        model_manager: Any,
        storage: ResultStorage | None = None,
        k_values: list[int] | None = None,
        random_seed: int = RANDOM_SEED,
    ) -> None:
        """Initialize orchestrator.

        Args:
            model_manager: ModelManager instance for loading models.
            storage: ResultStorage instance (created if None).
            k_values: K values for evaluation (defaults to config.K_VALUES).
            random_seed: Random seed for reproducibility.
        """
        self.model_manager = model_manager
        self.storage = storage or ResultStorage()
        self.k_values = k_values or K_VALUES
        self.random_seed = random_seed

        # Set random seed for reproducibility
        np.random.seed(random_seed)

        # Load data
        self.train_df = validate_train_data()
        self.test_df = validate_test_data()

        # Build user/item indices
        self._build_indices()

    def _build_indices(self) -> None:
        """Build user and item indices from train/test data."""
        # Test items per user
        self.test_by_user: dict[int, set[int]] = {
            int(uid): set(items.astype(int).tolist())
            for uid, items in self.test_df.groupby("userId")["movieId"]
        }

        # Train items per user (for exclusion)
        self.train_by_user: dict[int, set[int]] = {
            int(uid): set(items.astype(int).tolist())
            for uid, items in self.train_df.groupby("userId")["movieId"]
        }

        # Train item popularity (for coverage)
        self.catalog_items: set[int] = set(
            self.train_df["movieId"].astype(int).tolist()
        )

    def run_full_evaluation(
        self,
        model_names: list[str] | None = None,
        save_results: bool = True,
    ) -> dict[str, dict[str, Any]]:
        """Run evaluation for all models.

        Args:
            model_names: Models to evaluate (defaults to all available).
            save_results: Whether to save results to storage.

        Returns:
            Dict mapping model name to evaluation results.
        """
        # Validate model availability
        available = validate_model_availability(
            self.model_manager,
            model_names or MODEL_NAMES,
        )

        print(f"\n{'='*60}")
        print(f"Evaluation Orchestrator — Day 5 Morning")
        print(f"{'='*60}")
        print(f"Models to evaluate: {available}")
        print(f"K values: {self.k_values}")
        print(f"Random seed: {self.random_seed}")
        print(f"Test users: {len(self.test_by_user)}")
        print(f"Catalog items: {len(self.catalog_items)}")
        print(f"{'='*60}\n")

        results: dict[str, dict[str, Any]] = {}

        for i, model_name in enumerate(available, 1):
            print(f"\n[{i}/{len(available)}] Evaluating: {model_name}")
            print("-" * 40)

            try:
                model_results = self._evaluate_model(model_name)
                results[model_name] = model_results

                if save_results:
                    self.storage.save_model_results(
                        model_name,
                        model_results,
                        metadata={
                            "random_seed": self.random_seed,
                            "k_values": self.k_values,
                            "n_test_users": len(self.test_by_user),
                        },
                    )

                # Print summary
                print(f"  P@10: {model_results.get('mean_precision@10', 0):.4f}")
                print(f"  R@10: {model_results.get('mean_recall@10', 0):.4f}")
                print(f"  NDCG@10: {model_results.get('mean_ndcg@10', 0):.4f}")
                print(f"  Coverage: {model_results.get('catalog_coverage', 0):.4f}")
                print(f"  Pop. Decile: {model_results.get('mean_popularity_decile', 0):.2f}")

            except Exception as e:
                print(f"  ERROR: {e}")
                results[model_name] = {"error": str(e)}

        return results

    def _evaluate_model(self, model_name: str) -> dict[str, Any]:
        """Evaluate a single model on the complete test set.

        Args:
            model_name: Name of model to evaluate.

        Returns:
            Evaluation results dict.
        """
        start_time = time.time()

        # Load model
        model, provenance = self.model_manager.get_model(model_name)
        print(f"  Provenance: {provenance}")

        # Build recommendations function
        def recommendations_fn(user_id: int, train_items: set[int]) -> list[int]:
            """Get recommendations for a user, excluding train items."""
            try:
                recs = list(model.recommend(user_id, k=20, exclude_items=train_items))
                return recs
            except Exception:
                return []

        # Run evaluation using existing metrics.py framework
        results = evaluate_all(
            test_df=self.test_df,
            recommendations_fn=recommendations_fn,
            train_df=self.train_df,
            ks=self.k_values,
        )

        elapsed = time.time() - start_time
        results["evaluation_time_seconds"] = elapsed
        results["model_provenance"] = provenance

        # Validate results
        errors = self.storage.validate_results(results)
        if errors:
            print(f"  Validation warnings: {errors}")

        return results

    def _calculate_coverage(self, all_recommendations: set[int]) -> float:
        """Calculate catalog coverage.

        Args:
            all_recommendations: Set of all recommended item IDs.

        Returns:
            Coverage fraction.
        """
        if not self.catalog_items:
            return 0.0
        return len(all_recommendations & self.catalog_items) / len(self.catalog_items)


__all__ = ["EvaluationOrchestrator"]
