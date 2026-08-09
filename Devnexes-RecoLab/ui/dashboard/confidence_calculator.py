"""Confidence calculator for recommendation confidence scoring (Task-013).

Computes confidence scores for recommendations by combining multiple factors:
- User activity level (more ratings = higher confidence)
- Item popularity (more ratings for the item = higher confidence)
- Model agreement (multiple models agreeing = higher confidence)
- Model-specific confidence (e.g. HybridRecommender.get_confidence)
- Data quality (coverage of the user/item in training data)

Scores are normalized to [0.0, 1.0] and categorized as high / medium / low.
"""

from __future__ import annotations

import statistics
from typing import Any

from ui.data_provider import DataProvider
from ui.model_manager import ModelManager

# Category boundaries.
_HIGH_THRESHOLD = 0.66
_MEDIUM_THRESHOLD = 0.33

# Activity thresholds (mirror DataProvider / HybridRecommender).
_COLD_START_MAX = 5
_ACTIVE_MIN = 20
_MAX_ACTIVITY_RATINGS = 100  # cap for normalization

# Confidence category labels.
HIGH = "high"
MEDIUM = "medium"
LOW = "low"


def _clamp(value: float, lo: float = 0.0, hi: float = 1.0) -> float:
    return max(lo, min(hi, value))


class ConfidenceCalculator:
    """Compute per-recommendation confidence scores.

    Parameters
    ----------
    model_manager : ModelManager
        Provides access to loaded models (for model-specific confidence).
    provider : DataProvider
        Movie catalog and user statistics.
    """

    def __init__(self, model_manager: ModelManager, provider: DataProvider) -> None:
        self._model_manager = model_manager
        self._provider = provider

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate_confidence(
        self,
        user_id: int,
        movie_id: int,
        model_name: str,
        all_models_agreement: dict[str, list[int]] | None = None,
    ) -> dict[str, Any]:
        """Return a full confidence payload for one (user, item) pair.

        Keys in the returned dict:
            overall_score  : float in [0, 1]
            category       : "high" | "medium" | "low"
            factors        : dict[str, float] — per-factor breakdown
            uncertainty    : float in [0, 1]
            reliability    : float in [0, 1]
        """
        factors: dict[str, float] = {}

        # 1. User activity factor
        factors["user_activity"] = self._user_activity_factor(user_id)

        # 2. Item popularity factor
        factors["item_popularity"] = self._item_popularity_factor(movie_id)

        # 3. Model-specific confidence (best-effort)
        factors["model_specific"] = self._model_specific_factor(
            user_id, movie_id, model_name
        )

        # 4. Model agreement factor
        if all_models_agreement:
            factors["model_agreement"] = self._agreement_factor(
                movie_id, all_models_agreement
            )
        else:
            factors["model_agreement"] = 0.5  # neutral when unknown

        # 5. Data quality factor
        factors["data_quality"] = self._data_quality_factor(user_id, movie_id)

        # Weighted combination.
        weights = {
            "user_activity": 0.20,
            "item_popularity": 0.15,
            "model_specific": 0.30,
            "model_agreement": 0.20,
            "data_quality": 0.15,
        }
        overall = sum(
            factors[k] * weights.get(k, 0) for k in factors
        )
        overall = _clamp(overall)

        uncertainty = _clamp(1.0 - overall)
        reliability = _clamp(overall * 0.9 + 0.05)  # slight optimism floor

        return {
            "overall_score": round(overall, 4),
            "category": self._categorize(overall),
            "factors": {k: round(v, 4) for k, v in factors.items()},
            "uncertainty": round(uncertainty, 4),
            "reliability": round(reliability, 4),
        }

    def categorize(self, score: float) -> str:
        """Public accessor for score-to-category mapping."""
        return self._categorize(score)

    # ------------------------------------------------------------------
    # Factor helpers
    # ------------------------------------------------------------------

    def _user_activity_factor(self, user_id: int) -> float:
        """More ratings → higher confidence.  Caps at _MAX_ACTIVITY_RATINGS."""
        count = self._provider.get_user_rating_count(user_id)
        return _clamp(count / _MAX_ACTIVITY_RATINGS)

    def _item_popularity_factor(self, movie_id: int) -> float:
        """More community ratings for the item → higher confidence."""
        import math
        stats = self._provider.get_movie_stats(movie_id)
        rc = stats.get("rating_count", 0)
        # Log-ish scaling: 1 rating ≈ 0.1, 10 ≈ 0.5, 100+ ≈ 1.0
        return _clamp(math.log1p(rc) / math.log1p(100))

    def _model_specific_factor(
        self, user_id: int, movie_id: int, model_name: str
    ) -> float:
        """Use model-native confidence when available (HybridRecommender)."""
        try:
            model, _ = self._model_manager.get_model(model_name)
            if hasattr(model, "get_confidence") and callable(model.get_confidence):
                raw = float(model.get_confidence(user_id, movie_id))
                return _clamp(raw)
        except Exception:
            pass
        return 0.5  # neutral fallback

    def _agreement_factor(
        self, movie_id: int, all_models_agreement: dict[str, list[int]]
    ) -> float:
        """Fraction of models that include this movie in their top-K."""
        if not all_models_agreement:
            return 0.5
        total = len(all_models_agreement)
        if total == 0:
            return 0.5
        count = sum(
            1 for recs in all_models_agreement.values() if movie_id in recs
        )
        return _clamp(count / total)

    def _data_quality_factor(self, user_id: int, movie_id: int) -> float:
        """Heuristic: both user and item present in training data → higher."""
        user_count = self._provider.get_user_rating_count(user_id)
        movie_stats = self._provider.get_movie_stats(movie_id)
        movie_count = movie_stats.get("rating_count", 0)
        # Both present?
        user_ok = min(user_count / _COLD_START_MAX, 1.0) if user_count > 0 else 0.0
        item_ok = min(movie_count / 10, 1.0) if movie_count > 0 else 0.0
        return _clamp((user_ok + item_ok) / 2)

    @staticmethod
    def _categorize(score: float) -> str:
        if score >= _HIGH_THRESHOLD:
            return HIGH
        if score >= _MEDIUM_THRESHOLD:
            return MEDIUM
        return LOW
