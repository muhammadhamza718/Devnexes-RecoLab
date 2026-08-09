"""Segmented evaluation for analyzing model performance on user/item subgroups.

Segments include:
- Cold-start users (≤5 ratings)
- Active users (>20 ratings)
- New items (≤10 ratings)
- Genre-based segments
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

# Add scripts directory to path for path_utils import
sys.path.insert(0, str(Path(__file__).resolve().parent))
from path_utils import get_validated_project_root

PROJECT_ROOT = get_validated_project_root()
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from recolab.metrics import evaluate_all

from config import (
    ACTIVE_MIN_RATINGS,
    COLD_START_MAX_RATINGS,
    K_VALUES,
    MODEL_NAMES,
    NEW_ITEM_MAX_RATINGS,
    RANDOM_SEED,
    TEST_CSV,
    TRAIN_CSV,
)
from result_storage import ResultStorage


class SegmentedEvaluation:
    """Performs segmented evaluation to analyze performance on subgroups.

    Identifies performance gaps for:
    - Cold-start vs active users
    - New vs established items
    - Different genres
    """

    def __init__(
        self,
        model_manager: Any,
        storage: ResultStorage | None = None,
        k_values: list[int] | None = None,
        random_seed: int = RANDOM_SEED,
    ) -> None:
        """Initialize segmented evaluation.

        Args:
            model_manager: ModelManager instance.
            storage: ResultStorage instance.
            k_values: K values for evaluation.
            random_seed: Random seed for reproducibility.
        """
        self.model_manager = model_manager
        self.storage = storage or ResultStorage()
        self.k_values = k_values or K_VALUES
        self.random_seed = random_seed

        np.random.seed(random_seed)

        # Load data
        self.train_df = pd.read_csv(TRAIN_CSV)
        self.test_df = pd.read_csv(TEST_CSV)

        # Build segment indices
        self._build_segment_indices()

    def _build_segment_indices(self) -> None:
        """Build indices for user and item segments."""
        # User rating counts in train
        self.user_rating_counts = self.train_df.groupby("userId").size()

        # Item rating counts in train
        self.item_rating_counts = self.train_df.groupby("movieId").size()

        # User segments
        self.cold_start_users = set(
            self.user_rating_counts[
                self.user_rating_counts <= COLD_START_MAX_RATINGS
            ].index.astype(int)
        )
        self.active_users = set(
            self.user_rating_counts[
                self.user_rating_counts >= ACTIVE_MIN_RATINGS
            ].index.astype(int)
        )

        # Item segments
        self.new_items = set(
            self.item_rating_counts[
                self.item_rating_counts <= NEW_ITEM_MAX_RATINGS
            ].index.astype(int)
        )
        self.established_items = set(
            self.item_rating_counts[
                self.item_rating_counts > NEW_ITEM_MAX_RATINGS
            ].index.astype(int)
        )

        # Genre segments (parse from movies.csv)
        movies_df = pd.read_csv(PROJECT_ROOT / "data" / "ml-latest-small" / "movies.csv")
        self.item_genres: dict[int, list[str]] = {}
        self.genre_items: dict[str, set[int]] = {}

        for _, row in movies_df.iterrows():
            movie_id = int(row["movieId"])
            genres_str = str(row.get("genres", ""))
            genres = [g.strip() for g in genres_str.split("|") if g.strip()]
            self.item_genres[movie_id] = genres
            for genre in genres:
                if genre not in self.genre_items:
                    self.genre_items[genre] = set()
                self.genre_items[genre].add(movie_id)

    def run_segmented_evaluation(
        self,
        model_names: list[str] | None = None,
        segments: list[str] | None = None,
        save_results: bool = True,
    ) -> dict[str, dict[str, dict[str, Any]]]:
        """Run segmented evaluation for all models.

        Args:
            model_names: Models to evaluate.
            segments: Segments to evaluate (default: all).
            save_results: Whether to save results.

        Returns:
            Nested dict: model_name -> segment_name -> results.
        """
        models = model_names or MODEL_NAMES
        all_segments = segments or [
            "cold_start_users",
            "active_users",
            "new_items",
            "established_items",
            "genre_based",  # Added genre-based segmentation
        ]

        print(f"\n{'='*60}")
        print(f"Segmented Evaluation — Day 5 Morning")
        print(f"{'='*60}")
        print(f"Models: {models}")
        print(f"Segments: {all_segments}")
        print(f"Cold-start users: {len(self.cold_start_users)}")
        print(f"Active users: {len(self.active_users)}")
        print(f"New items: {len(self.new_items)}")
        print(f"Established items: {len(self.established_items)}")
        print(f"{'='*60}\n")

        results: dict[str, dict[str, dict[str, Any]]] = {}

        for model_name in models:
            print(f"\n{'='*40}")
            print(f"Model: {model_name}")
            print(f"{'='*40}")
            results[model_name] = {}

            try:
                model, _ = self.model_manager.get_model(model_name)

                for segment_name in all_segments:
                    print(f"\n  Segment: {segment_name}")
                    try:
                        segment_results = self._evaluate_on_segment(
                            model, model_name, segment_name
                        )
                        results[model_name][segment_name] = segment_results

                        if save_results:
                            self.storage.save_segmented_results(
                                model_name,
                                segment_name,
                                segment_results,
                            )

                        print(f"    P@10: {segment_results.get('mean_precision@10', 0):.4f}")
                        print(f"    R@10: {segment_results.get('mean_recall@10', 0):.4f}")

                    except Exception as e:
                        print(f"    ERROR: {e}")
                        results[model_name][segment_name] = {"error": str(e)}

            except Exception as e:
                print(f"  ERROR loading model: {e}")
                results[model_name] = {"error": str(e)}

        return results

    def _evaluate_on_segment(
        self,
        model: Any,
        model_name: str,
        segment_name: str,
    ) -> dict[str, Any]:
        """Evaluate model on a specific segment.

        Args:
            model: Model instance.
            model_name: Model name.
            segment_name: Segment name.

        Returns:
            Evaluation results for segment.
        """
        # Determine segment filter
        if segment_name == "cold_start_users":
            target_users = self.cold_start_users
        elif segment_name == "active_users":
            target_users = self.active_users
        elif segment_name == "new_items":
            target_users = set(self.test_df["userId"].unique())  # All users
        elif segment_name == "established_items":
            target_users = set(self.test_df["userId"].unique())  # All users
        elif segment_name == "genre_based":
            # For genre-based, we evaluate all users but analyze by genre of recommended items
            target_users = set(self.test_df["userId"].unique())
        else:
            target_users = set(self.test_df["userId"].unique())

        # Filter test data by segment
        if segment_name in ["cold_start_users", "active_users"]:
            segment_test_df = self.test_df[
                self.test_df["userId"].astype(int).isin(target_users)
            ]
        elif segment_name == "new_items":
            segment_test_df = self.test_df[
                self.test_df["movieId"].astype(int).isin(self.new_items)
            ]
        elif segment_name == "established_items":
            segment_test_df = self.test_df[
                self.test_df["movieId"].astype(int).isin(self.established_items)
            ]
        elif segment_name == "genre_based":
            # For genre-based, we use all test data but will analyze genre-specific performance
            segment_test_df = self.test_df
        else:
            segment_test_df = self.test_df

        if segment_test_df.empty:
            return {"error": "No test data for segment", "n_users": 0}

        # Build recommendations function
        def recommendations_fn(user_id: int, train_items: set[int]) -> list[int]:
            try:
                recs = list(model.recommend(user_id, k=20, exclude_items=train_items))
                return recs
            except Exception:
                return []

        # Run evaluation
        results = evaluate_all(
            test_df=segment_test_df,
            recommendations_fn=recommendations_fn,
            train_df=self.train_df,
            ks=self.k_values,
        )

        results["segment_name"] = segment_name
        results["n_test_users"] = int(segment_test_df["userId"].nunique())
        
        # For genre-based analysis, calculate genre-specific metrics
        if segment_name == "genre_based":
            results["genre_metrics"] = self._calculate_genre_metrics(model, results, segment_test_df)

        return results
    
    def _calculate_genre_metrics(self, model: Any, evaluation_results: dict, test_df: pd.DataFrame) -> dict[str, dict]:
        """Calculate genre-specific performance metrics.
        
        Args:
            model: Model instance.
            evaluation_results: Base evaluation results.
            test_df: Test data for this segment.
            
        Returns:
            Dictionary mapping genre to performance metrics.
        """
        genre_metrics: dict[str, dict] = {}
        
        # Collect recommendations for all users
        all_recommendations = []
        for user_id in test_df["userId"].unique():
            try:
                recs = list(model.recommend(user_id, k=20, exclude_items=set()))
                all_recommendations.extend(recs)
            except Exception:
                continue
        
        # Calculate metrics per genre
        for genre, genre_items in self.genre_items.items():
            genre_rec_items = [item for item in all_recommendations if item in genre_items]
            
            if genre_rec_items:
                # Calculate genre-specific precision/recall
                genre_precision = len(genre_rec_items) / len(all_recommendations) if all_recommendations else 0.0
                
                # Simple genre metric for now
                genre_metrics[genre] = {
                    "genre_coverage": len(genre_rec_items) / len(genre_items) if genre_items else 0.0,
                    "precision": genre_precision,
                    "recommended_count": len(genre_rec_items),
                }
            else:
                genre_metrics[genre] = {
                    "genre_coverage": 0.0,
                    "precision": 0.0,
                    "recommended_count": 0,
                }
        
        return genre_metrics


__all__ = ["SegmentedEvaluation"]
