"""Bias Quantification & Diversity Analysis Framework for Day 5 Afternoon.

Quantifies model bias across multiple measurable dimensions:
- Popularity bias (mean popularity decile)
- Catalog coverage (unique items recommended / total catalog)
- Intra-list diversity (genre distance within recommended list)
- Inter-list diversity (uniqueness across different user recommendation lists)
- Novelty score (-log2(item_popularity_fraction))
- Serendipity (unexpected recommendation relevance)
- Fairness evaluation across user activity quintiles
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


class BiasAnalyzer:
    """Bias Analysis Framework for recommender evaluation."""

    def __init__(
        self,
        loader: EvaluationResultLoader | None = None,
        storage: AnalysisStorage | None = None,
    ) -> None:
        """Initialize BiasAnalyzer."""
        self.loader = loader or EvaluationResultLoader()
        self.storage = storage or AnalysisStorage()

        self.train_df = pd.read_csv(PROJECT_ROOT / "data" / "split_datasets" / "train.csv")
        self.test_df = pd.read_csv(PROJECT_ROOT / "data" / "split_datasets" / "test.csv")
        self.movies_df = pd.read_csv(PROJECT_ROOT / "data" / "ml-latest-small" / "movies.csv")

        # Total catalog count and item counts
        self.total_catalog_size = len(self.movies_df["movieId"].unique())
        self.user_counts = self.train_df.groupby("userId").size()
        self.item_counts = self.train_df.groupby("movieId").size()
        self.total_train_interactions = len(self.train_df)

        # Precompute item popularity deciles (1 = least popular, 10 = most popular)
        item_pop = self.item_counts.reindex(self.movies_df["movieId"], fill_value=0)
        pop_ranks = pd.qcut(item_pop.rank(method="first"), 10, labels=list(range(1, 11)))
        self.item_pop_deciles = dict(zip(self.movies_df["movieId"], pop_ranks))

        # Precompute genre sets per item
        self.item_genres = {}
        for _, row in self.movies_df.iterrows():
            g_set = set(str(row["genres"]).split("|"))
            if "(no genres listed)" in g_set:
                g_set = set()
            self.item_genres[row["movieId"]] = g_set

        self.model_manager = OfflineModelManager()

    def analyze_bias(
        self, model_names: list[str] | None = None
    ) -> dict[str, Any]:
        """Quantify and compare bias across all specified models."""
        if model_names is None:
            model_names = self.model_manager.get_available_models()

        bias_results: dict[str, Any] = {}
        test_users = self.test_df["userId"].unique()[:100]

        pos_test = self.test_df[self.test_df["rating"] >= 3.0]
        test_by_user = pos_test.groupby("userId")["movieId"].apply(set).to_dict()

        for model_name in model_names:
            print(f"Running bias analysis for model: {model_name}...")
            model, _ = self.model_manager.get_model(model_name)

            # Generate top-10 recs for test users
            user_recs: dict[int, list[int]] = {}
            all_recommended_items: set[int] = set()

            for u in test_users:
                try:
                    recs = model.recommend(u, top_n=10)
                    rec_ids = recs["movieId"].tolist() if isinstance(recs, pd.DataFrame) and "movieId" in recs else recs
                except Exception:
                    rec_ids = []

                if rec_ids:
                    user_recs[int(u)] = rec_ids
                    all_recommended_items.update(rec_ids)

            # Calculate individual bias metrics
            pop_bias = self._calculate_popularity_bias(user_recs)
            coverage = self._calculate_catalog_coverage(all_recommended_items)
            div_metrics = self._calculate_diversity_metrics(user_recs)
            novelty = self._calculate_novelty_score(user_recs)
            serendipity = self._calculate_serendipity(user_recs, test_by_user)
            fairness = self._evaluate_fairness(model, test_users, test_by_user)

            bias_results[model_name] = {
                "model_name": model_name,
                "popularity_bias": pop_bias,
                "catalog_coverage": coverage,
                "diversity": div_metrics,
                "novelty_score": novelty,
                "serendipity": serendipity,
                "fairness": fairness,
            }

        # Model comparison matrix
        comparison_matrix = self._compare_bias_across_models(bias_results)
        bias_results["_bias_comparison_matrix"] = comparison_matrix

        # Save to disk
        self.storage.save_result(
            category="bias_analysis",
            name="bias_analysis_summary",
            data=bias_results,
            add_timestamp=True,
        )

        return bias_results

    def _calculate_popularity_bias(self, user_recs: dict[int, list[int]]) -> dict[str, float]:
        """Calculate mean popularity decile of recommended items (1=niche, 10=popular)."""
        deciles = []
        for rec_list in user_recs.values():
            for item in rec_list:
                d = self.item_pop_deciles.get(item, 1)
                deciles.append(int(d))

        mean_decile = float(np.mean(deciles)) if deciles else 0.0
        return {
            "mean_popularity_decile": mean_decile,
            "pop_decile_10_share": float(np.mean([d == 10 for d in deciles])) if deciles else 0.0,
        }

    def _calculate_catalog_coverage(self, recommended_items: set[int]) -> dict[str, float]:
        """Calculate percentage of catalog items recommended."""
        num_recommended = len(recommended_items)
        coverage_pct = float(num_recommended / self.total_catalog_size) if self.total_catalog_size > 0 else 0.0
        return {
            "unique_items_recommended": num_recommended,
            "total_catalog_items": self.total_catalog_size,
            "catalog_coverage_pct": coverage_pct,
        }

    def _calculate_diversity_metrics(self, user_recs: dict[int, list[int]]) -> dict[str, float]:
        """Calculate intra-list (genre Jaccard distance) and inter-list diversity."""
        # 1. Intra-list diversity (ILD)
        ild_scores = []
        for rec_list in user_recs.values():
            k = len(rec_list)
            if k <= 1:
                continue

            dissimilarities = []
            for i in range(k):
                for j in range(i + 1, k):
                    g1 = self.item_genres.get(rec_list[i], set())
                    g2 = self.item_genres.get(rec_list[j], set())

                    union = len(g1.union(g2))
                    if union == 0:
                        jaccard_sim = 1.0
                    else:
                        jaccard_sim = len(g1.intersection(g2)) / union

                    dissimilarity = 1.0 - jaccard_sim
                    dissimilarities.append(dissimilarity)

            if dissimilarities:
                ild_scores.append(np.mean(dissimilarities))

        mean_ild = float(np.mean(ild_scores)) if ild_scores else 0.0

        # 2. Inter-list diversity (uniqueness across user lists)
        users = list(user_recs.keys())
        inter_sims = []
        for i in range(min(50, len(users))):
            for j in range(i + 1, min(50, len(users))):
                s1 = set(user_recs[users[i]])
                s2 = set(user_recs[users[j]])
                u = len(s1.union(s2))
                sim = len(s1.intersection(s2)) / u if u > 0 else 0.0
                inter_sims.append(1.0 - sim)

        inter_diversity = float(np.mean(inter_sims)) if inter_sims else 1.0

        return {
            "intra_list_diversity": mean_ild,
            "inter_list_diversity": inter_diversity,
        }

    def _calculate_novelty_score(self, user_recs: dict[int, list[int]]) -> dict[str, float]:
        """Calculate self-information novelty score: -log2(p(i))."""
        novelty_scores = []
        for rec_list in user_recs.values():
            for item in rec_list:
                pop_count = self.item_counts.get(item, 1)
                p_i = pop_count / self.total_train_interactions
                self_info = -np.log2(p_i)
                novelty_scores.append(self_info)

        mean_novelty = float(np.mean(novelty_scores)) if novelty_scores else 0.0
        return {
            "mean_novelty_score": mean_novelty,
            "novelty_std": float(np.std(novelty_scores)) if novelty_scores else 0.0,
        }

    def _calculate_serendipity(
        self, user_recs: dict[int, list[int]], test_by_user: dict[int, set[int]]
    ) -> dict[str, float]:
        """Assess serendipity: unexpectedness x hit relevance."""
        # Baseline expectations from popular items
        popular_items_top50 = set(self.item_counts.nlargest(50).index)

        serendipity_scores = []
        for u, rec_list in user_recs.items():
            hits = set(rec_list).intersection(test_by_user.get(u, set()))
            if not hits:
                serendipity_scores.append(0.0)
                continue

            # Unexpected hits = hits that are not top-50 popular items
            unexpected_hits = [item for item in hits if item not in popular_items_top50]
            serendipity_scores.append(len(unexpected_hits) / len(rec_list))

        mean_serendipity = float(np.mean(serendipity_scores)) if serendipity_scores else 0.0
        return {"mean_serendipity_score": mean_serendipity}

    def _evaluate_fairness(
        self, model: Any, test_users: list[int], test_by_user: dict[int, set[int]]
    ) -> dict[str, float]:
        """Evaluate Gini inequality of precision across user activity quintiles."""
        user_counts = self.user_counts.reindex(test_users, fill_value=0)
        quintiles = pd.qcut(user_counts.rank(method="first"), 5, labels=False)

        q_precisions = {i: [] for i in range(5)}

        for idx, u in enumerate(test_users):
            q = quintiles.iloc[idx]
            relevant = test_by_user.get(u, set())
            if not relevant:
                continue

            try:
                recs = model.recommend(u, top_n=10)
                rec_ids = recs["movieId"].tolist() if isinstance(recs, pd.DataFrame) and "movieId" in recs else recs
            except Exception:
                rec_ids = []

            k = len(rec_ids)
            p = len(set(rec_ids).intersection(relevant)) / k if k > 0 else 0.0
            q_precisions[q].append(p)

        mean_q_prec = [float(np.mean(q_precisions[i])) if q_precisions[i] else 0.0 for i in range(5)]

        # Gini coefficient of performance across quintiles
        array = np.array(mean_q_prec)
        if np.amin(array) < 0:
            array -= np.amin(array)
        array += 0.0000001
        array = np.sort(array)
        index = np.arange(1, array.shape[0] + 1)
        n = array.shape[0]
        gini = float((np.sum((2 * index - n - 1) * array)) / (n * np.sum(array)))

        return {
            "quintile_precisions": mean_q_prec,
            "performance_gini_coefficient": gini,
            "fairness_rating": "High" if gini < 0.15 else ("Moderate" if gini < 0.30 else "Low"),
        }

    def _compare_bias_across_models(
        self, bias_results: dict[str, Any]
    ) -> dict[str, dict[str, float]]:
        """Create structured comparison matrix of bias metrics across models."""
        matrix = {}
        for m_name, res in bias_results.items():
            if m_name.startswith("_"):
                continue
            matrix[m_name] = {
                "popularity_decile": res["popularity_bias"]["mean_popularity_decile"],
                "catalog_coverage_pct": res["catalog_coverage"]["catalog_coverage_pct"],
                "intra_list_diversity": res["diversity"]["intra_list_diversity"],
                "novelty_score": res["novelty_score"]["mean_novelty_score"],
                "serendipity": res["serendipity"]["mean_serendipity_score"],
                "fairness_gini": res["fairness"]["performance_gini_coefficient"],
            }
        return matrix
