"""Model comparison engine for the RecoLab dashboard (Feature 008, Task-005).

Generates side-by-side comparison data: per-model recommendation outputs for a
user, pair-wise agreement analysis (Jaccard similarity on the recommendation
sets), and the performance comparison table from :class:`MetricsProvider`.
Also derives a model-selection recommendation (Task-008) that blends offline
metrics with the user's activity level.
"""

from __future__ import annotations

from typing import Any

from ui.dashboard.metrics_provider import MODEL_NAMES, MetricsProvider
from ui.model_manager import ModelManager


class ModelComparisonEngine:
    """Compares models on recommendation output and offline performance."""

    def __init__(
        self,
        model_manager: ModelManager,
        metrics_provider: MetricsProvider,
    ) -> None:
        self._model_manager = model_manager
        self._metrics_provider = metrics_provider
        self._cache: dict[str, dict[str, Any]] = {}

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def compare_models(
        self,
        user_id: int,
        k: int = 10,
        models: list[str] | None = None,
        exclude_items: set[int] | None = None,
    ) -> dict[str, Any]:
        """Build the full comparison payload for one user at cut-off ``k``."""
        cache_key = f"{user_id}:{k}:{','.join(models or MODEL_NAMES)}"
        if cache_key in self._cache:
            return self._cache[cache_key]

        model_outputs: dict[str, list[int]] = {}
        for name in models or MODEL_NAMES:
            model, _ = self._model_manager.get_model(name)
            model_outputs[name] = list(
                model.recommend(
                    user_id=user_id,
                    k=k,
                    exclude_items=exclude_items,
                )
                or []
            )

        payload = {
            "user_id": user_id,
            "k": k,
            "model_outputs": model_outputs,
            "agreement_analysis": self._analyze_agreement(model_outputs),
            "performance_comparison": self._metrics_provider.get_comparison_metrics(k),
        }
        self._cache[cache_key] = payload
        return payload

    def recommend_models(
        self,
        k: int = 10,
        rating_count: int | None = None,
    ) -> dict[str, Any]:
        """Suggest a primary model plus rationale from metrics and activity.

        Cold-start users (fewer than 5 ratings) are steered to the Hybrid
        model because it blends content and collaborative signals; otherwise
        the best-performing model at cut-off ``k`` is recommended.
        """
        summary = self._metrics_provider.get_metric_summary(k, metric="ndcg")
        best = summary[0] if summary else {"model": "Hybrid", "value": 0.0}
        runner_up = summary[1] if len(summary) > 1 else None

        if rating_count is not None and rating_count < 5:
            primary = "Hybrid"
            rationale = (
                f"With only {rating_count} rating(s) you're a cold-start user; "
                "Hybrid blends content and collaborative signals, which gives "
                "more stable recommendations from sparse history."
            )
        else:
            primary = str(best.get("model", "Hybrid"))
            rationale = (
                f"Best offline NDCG@{k} ({best.get('value', 0.0):.3f}) on the held-out "
                "test split, so it is the most likely to surface relevant titles."
            )

        return {
            "primary_model": primary,
            "rationale": rationale,
            "alternatives": [
                {"model": row["model"], "ndcg": row["value"]}
                for row in (summary[1:4] if summary else [])
            ],
            "runner_up": runner_up["model"] if runner_up else None,
        }

    # ------------------------------------------------------------------
    # Agreement analysis
    # ------------------------------------------------------------------

    @staticmethod
    def _analyze_agreement(
        model_outputs: dict[str, list[int]],
    ) -> dict[str, dict[str, Any]]:
        """Pair-wise Jaccard similarity and overlap between model outputs.

        Each pair ``A_vs_B`` reports the overlap count and Jaccard similarity
        (intersection / union) of the two recommendation sets, both as a raw
        fraction and as a percentage.
        """
        names = list(model_outputs)
        agreements: dict[str, dict[str, Any]] = {}
        for i, model_a in enumerate(names):
            set_a = set(model_outputs[model_a])
            for model_b in names[i + 1 :]:
                set_b = set(model_outputs[model_b])
                intersection = set_a & set_b
                union = set_a | set_b
                jaccard = len(intersection) / len(union) if union else 0.0
                agreements[f"{model_a}_vs_{model_b}"] = {
                    "model_a": model_a,
                    "model_b": model_b,
                    "overlap_count": len(intersection),
                    "jaccard_similarity": round(jaccard, 4),
                    "agreement_percentage": round(jaccard * 100, 1),
                }
        return agreements
