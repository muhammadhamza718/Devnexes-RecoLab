"""Unit and integration tests for HybridRecommender module."""

from __future__ import annotations

import pathlib
import time

import pandas as pd
import pytest

from recolab.content import ContentModel
from recolab.hybrid import (
    EnhancedColdStartHandler,
    FallbackManager,
    HybridRecommender,
    NewItemDetector,
    ParameterOptimizer,
    PerformanceMonitor,
    UserProfile,
)
from recolab.interfaces import ColdStartHandler, Recommender
from recolab.persistence import ModelBundle


@pytest.fixture
def sample_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Fixture providing small synthetic ratings and movies DataFrames."""
    movies = pd.DataFrame(
        {
            "movieId": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10],
            "title": [f"Movie {i}" for i in range(1, 11)],
            "genres": [
                "Action|Sci-Fi",
                "Action|Adventure",
                "Comedy|Romance",
                "Comedy",
                "Drama",
                "Action|Thriller",
                "Drama|Romance",
                "Animation|Children",
                "Sci-Fi|Thriller",
                "Documentary",
            ],
        }
    )

    ratings = pd.DataFrame(
        {
            "userId": [1] * 3 + [2] * 20 + [3] * 5 + [4] * 6,
            "movieId": [1, 2, 3] + list(range(1, 11)) * 2 + [1, 5, 6, 7, 8] + [1, 2, 3, 4, 5, 6],
            "rating": [5.0, 4.0, 3.0] + [4.5] * 20 + [4.0] * 5 + [5.0] * 6,
        }
    )
    return ratings, movies


def test_hybrid_init() -> None:
    """Test HybridRecommender initialization with valid parameters."""
    hybrid = HybridRecommender(
        alpha=0.6,
        cold_start_threshold=5,
        active_threshold=20,
    )
    assert hybrid.alpha == 0.6
    assert hybrid.cold_start_threshold == 5
    assert hybrid.active_threshold == 20
    assert not hybrid.is_fitted
    assert isinstance(hybrid, Recommender)
    assert isinstance(hybrid, ColdStartHandler)


def test_alpha_validation() -> None:
    """Test parameter validation for alpha and thresholds."""
    with pytest.raises(ValueError, match="alpha"):
        HybridRecommender(alpha=-0.1)

    with pytest.raises(ValueError, match="alpha"):
        HybridRecommender(alpha=1.5)

    with pytest.raises(ValueError, match="cold_start_threshold"):
        HybridRecommender(cold_start_threshold=0)

    with pytest.raises(ValueError, match="active_threshold"):
        HybridRecommender(cold_start_threshold=25, active_threshold=20)


def test_score_normalization() -> None:
    """Test score normalization method."""
    hybrid = HybridRecommender()
    raw_scores = [(1, 10.0), (2, 20.0), (3, 30.0)]
    normalized = hybrid._normalize_scores(raw_scores)

    assert len(normalized) == 3
    scores_dict = dict(normalized)
    assert pytest.approx(scores_dict[1]) == 0.0
    assert pytest.approx(scores_dict[2]) == 0.5
    assert pytest.approx(scores_dict[3]) == 1.0


def test_weighted_score_combination() -> None:
    """Test weighted score combination of content and collaborative scores."""
    hybrid = HybridRecommender(alpha=0.5)
    content_scores = [(10, 1.0), (20, 0.0)]
    cf_scores = [(10, 0.0), (20, 1.0)]

    combined = hybrid._combine_weighted_scores(content_scores, cf_scores, k=2)
    assert len(combined) == 2
    assert pytest.approx(dict(combined)[10]) == 0.5
    assert pytest.approx(dict(combined)[20]) == 0.5


def test_missing_score_handling() -> None:
    """Test score combination when an item exists in only one model."""
    hybrid = HybridRecommender(alpha=0.6)
    content_scores = [(10, 1.0)]  # item 10 only in content
    cf_scores = [(20, 1.0)]       # item 20 only in CF

    combined = hybrid._combine_weighted_scores(content_scores, cf_scores, k=2)
    combined_dict = dict(combined)
    assert pytest.approx(combined_dict[10]) == 0.6
    assert pytest.approx(combined_dict[20]) == 0.4


def test_different_alpha_values() -> None:
    """Test score combination with different alpha values (0.2, 0.5, 0.8)."""
    content_scores = [(10, 1.0), (20, 0.0)]
    cf_scores = [(10, 0.0), (20, 1.0)]

    for alpha, expected_10 in [(0.2, 0.2), (0.5, 0.5), (0.8, 0.8)]:
        hybrid = HybridRecommender(alpha=alpha)
        combined = dict(hybrid._combine_weighted_scores(content_scores, cf_scores, k=2))
        assert pytest.approx(combined[10]) == expected_10
        assert pytest.approx(combined[20]) == pytest.approx(1.0 - expected_10)


def test_cold_start_user_detection() -> None:
    """Test cold-start user detection (<=5 ratings)."""
    hybrid = HybridRecommender(cold_start_threshold=5, active_threshold=20)
    hybrid.user_rating_counts = {101: 3, 102: 5}

    assert hybrid._get_user_rating_count(101) == 3
    assert hybrid._get_user_rating_count(999) == 0

    _, model_name, reason = hybrid._select_model(101)
    assert model_name == "content"
    assert "Cold-start" in reason or "<=" in reason


def test_active_user_detection() -> None:
    """Test active user detection (>20 ratings)."""
    hybrid = HybridRecommender(cold_start_threshold=5, active_threshold=20)
    hybrid.user_rating_counts = {201: 25}

    _, model_name, reason = hybrid._select_model(201)
    assert model_name == "collaborative"
    assert "Active" in reason or ">=" in reason


def test_intermediate_user_detection() -> None:
    """Test intermediate user detection (5-20 ratings)."""
    hybrid = HybridRecommender(cold_start_threshold=5, active_threshold=20)
    hybrid.user_rating_counts = {301: 12}

    _, model_name, reason = hybrid._select_model(301)
    assert model_name == "hybrid"
    assert "Intermediate" in reason or "hybrid" in reason.lower()


def test_threshold_boundary_cases() -> None:
    """Test boundary threshold values (exactly 5, 20 ratings)."""
    hybrid = HybridRecommender(cold_start_threshold=5, active_threshold=20)
    hybrid.user_rating_counts = {1: 5, 2: 20}

    _, model_1, _ = hybrid._select_model(1)
    assert model_1 == "content"

    _, model_2, _ = hybrid._select_model(2)
    assert model_2 == "collaborative"


# --- User Story 3 Tests ---

def test_activity_confidence() -> None:
    """Test activity confidence score calculation."""
    hybrid = HybridRecommender(cold_start_threshold=5, active_threshold=20)
    hybrid.user_rating_counts = {1: 3, 2: 25, 3: 125}

    assert hybrid._compute_activity_confidence(1) == 0.0
    assert hybrid._compute_activity_confidence(2) == 1.0
    # For count=125, capped at 1.0
    assert hybrid._compute_activity_confidence(3) == 1.0


def test_popularity_confidence() -> None:
    """Test popularity confidence score calculation."""
    hybrid = HybridRecommender()
    hybrid.item_rating_counts = {1: 10, 2: 50, 3: 100}

    assert pytest.approx(hybrid._compute_popularity_confidence(1)) == 0.2
    assert pytest.approx(hybrid._compute_popularity_confidence(2)) == 1.0
    assert pytest.approx(hybrid._compute_popularity_confidence(3)) == 1.0


def test_agreement_confidence() -> None:
    """Test agreement confidence score calculation between candidate lists."""
    hybrid = HybridRecommender()
    c_items = [1, 2, 3, 4]
    cf_items = [3, 4, 5, 6]

    # Intersection: {3, 4} (size 2), Union: {1, 2, 3, 4, 5, 6} (size 6) -> 2/6 = 0.3333
    agr = hybrid._compute_agreement_confidence(c_items, cf_items)
    assert pytest.approx(agr) == 2.0 / 6.0


def test_composite_confidence_and_range() -> None:
    """Test composite confidence score calculation and range [0, 1]."""
    hybrid = HybridRecommender(cold_start_threshold=5, active_threshold=20)
    hybrid.user_rating_counts = {1: 25}
    hybrid.item_rating_counts = {10: 50}

    conf = hybrid.get_confidence(user_id=1, movie_id=10)
    assert 0.0 <= conf <= 1.0


# --- User Story 4 Tests ---

def test_explanation_delegation_and_fallback(sample_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    """Test explanation delegation to underlying models and fallback behavior."""
    ratings, movies = sample_data
    hybrid = HybridRecommender()
    hybrid.fit(ratings, movies)

    hybrid.recommend(user_id=2, k=3)  # Active user -> collaborative
    exp_collab = hybrid.explain(2, 1)
    assert isinstance(exp_collab, str)
    assert len(exp_collab) > 0

    hybrid.recommend(user_id=1, k=3)  # Cold start user -> content
    exp_content = hybrid.explain(1, 1)
    assert isinstance(exp_content, str)
    assert len(exp_content) > 0


# --- User Story 5 Tests ---

def test_to_bundle_and_from_bundle(sample_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    """Test to_bundle() and from_bundle() methods."""
    ratings, movies = sample_data
    hybrid = HybridRecommender(alpha=0.7)
    hybrid.fit(ratings, movies)

    bundle = hybrid.to_bundle()
    assert isinstance(bundle, ModelBundle)
    assert bundle.metadata["alpha"] == 0.7
    assert bundle.metadata["is_fitted"] is True

    restored = HybridRecommender.from_bundle(bundle)
    assert restored.alpha == 0.7
    assert restored.is_fitted is True


def test_save_load_persistence_roundtrip(tmp_path: pathlib.Path, sample_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    """Test full save and load persistence roundtrip."""
    ratings, movies = sample_data
    hybrid = HybridRecommender(alpha=0.4, cold_start_threshold=5, active_threshold=20)
    hybrid.fit(ratings, movies)

    save_path = tmp_path / "hybrid_model.pkl"
    written_path = hybrid.save(save_path)
    assert written_path.exists()

    loaded = HybridRecommender.load(written_path)
    assert loaded.alpha == 0.4
    assert loaded.is_fitted is True

    # Compare recommendations from original and loaded models
    recs_orig = hybrid.recommend(user_id=2, k=3)
    recs_loaded = loaded.recommend(user_id=2, k=3)
    assert recs_orig == recs_loaded


# --- Phase 8 Integration & End-to-End Tests ---

def test_fit_and_recommend_end_to_end(sample_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    """Test complete end-to-end fit and recommendation flow."""
    ratings, movies = sample_data
    hybrid = HybridRecommender(alpha=0.5)
    hybrid.fit(ratings, movies)

    assert hybrid.is_fitted

    recs = hybrid.recommend(user_id=2, k=5)
    assert len(recs) <= 5
    assert len(recs) == len(set(recs))  # unique item IDs


def test_recommend_cold_start(sample_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    """Test cold-start recommendation flow."""
    ratings, movies = sample_data
    hybrid = HybridRecommender()
    hybrid.fit(ratings, movies)

    recs = hybrid.recommend_cold_start(genres=["Action", "Sci-Fi"], liked_movie_ids=[1], k=3)
    assert isinstance(recs, list)
    assert 1 not in recs  # liked movie excluded


def test_get_model_selection_info(sample_data: tuple[pd.DataFrame, pd.DataFrame]) -> None:
    """Test get_model_selection_info diagnostic utility."""
    ratings, movies = sample_data
    hybrid = HybridRecommender()
    hybrid.fit(ratings, movies)

    info = hybrid.get_model_selection_info(user_id=2)
    assert info["user_id"] == 2
    assert "rating_count" in info
    assert "selected_model" in info
    assert "reason" in info


def test_unfitted_model_raises_runtime_error() -> None:
    """Test that calling recommend before fit raises RuntimeError."""
    hybrid = HybridRecommender()
    with pytest.raises(RuntimeError, match="fitted"):
        hybrid.recommend(user_id=1, k=5)


# --- 004 Cold-Start Optimization & Parameter Tuning Tests ---


def test_user_profile_creation_and_weights() -> None:
    """Test UserProfile initialization, weight normalization, and preferred genres."""
    profile = UserProfile(
        user_id=101,
        genre_weights={"Action": 2.0, "Sci-Fi": 1.0, "Comedy": 0.0},
        liked_movie_ids=[1, 2],
    )
    assert profile.user_id == 101
    assert profile.get_preferred_genres(top_n=2) == ["Action", "Sci-Fi"]

    profile.update_genre_weights(["Drama"], weight=1.5)
    assert "Drama" in profile.genre_weights


def test_user_profile_bundle_persistence() -> None:
    """Test UserProfile bundle serialization and deserialization."""
    profile = UserProfile(
        user_id=42,
        genre_weights={"Action": 0.6, "Drama": 0.4},
        liked_movie_ids=[5, 10],
    )
    bundle = profile.to_bundle()
    restored = UserProfile.from_bundle(bundle)
    assert restored.user_id == 42
    assert restored.genre_weights == profile.genre_weights
    assert restored.liked_movie_ids == [5, 10]


def test_enhanced_cold_start_handler_profile_building(
    sample_data: tuple[pd.DataFrame, pd.DataFrame],
) -> None:
    """Test EnhancedColdStartHandler profile building and recommendations."""
    ratings, movies = sample_data
    content_model = ContentModel()
    content_model.fit(ratings, movies)

    handler = EnhancedColdStartHandler(content_model=content_model)
    profile = handler.build_user_profile(
        genres=["Action", "Sci-Fi"], liked_movie_ids=[1], movies_df=movies
    )
    assert isinstance(profile, UserProfile)
    assert "Action" in profile.genre_weights

    recs = handler.recommend_cold_start(
        genres=["Action", "Sci-Fi"], liked_movie_ids=[1], k=3
    )
    assert isinstance(recs, list)
    assert len(recs) <= 3
    assert 1 not in recs


def test_enhanced_cold_start_explanation(
    sample_data: tuple[pd.DataFrame, pd.DataFrame],
) -> None:
    """Test EnhancedColdStartHandler explanation generation."""
    ratings, movies = sample_data
    content_model = ContentModel()
    content_model.fit(ratings, movies)

    handler = EnhancedColdStartHandler(content_model=content_model)
    exp = handler.explain(user_id=999, movie_id=2, genres=["Action"], liked_movie_ids=[1])
    assert isinstance(exp, str)
    assert len(exp) > 0


def test_new_item_detector_and_boost() -> None:
    """Test NewItemDetector detection, boost logic, and flagging."""
    detector = NewItemDetector(rating_count_threshold=5, boost_weight=0.3)
    assert detector.detect_new_items(movie_id=10, rating_count=3) is True
    assert detector.detect_new_items(movie_id=20, rating_count=15) is False

    boosted = detector.apply_popularity_boost(score=1.0, is_new=True)
    assert pytest.approx(boosted) == 1.3
    unboosted = detector.apply_popularity_boost(score=1.0, is_new=False)
    assert pytest.approx(unboosted) == 1.0

    # Test time decay with item_id
    detector.item_timestamps[10] = time.time() - (25 * 24 * 3600)  # 25 days ago
    decayed_boost = detector.apply_popularity_boost(score=1.0, is_new=True, item_id=10)
    # After 25 days with 30-day decay, boost should be reduced: 0.3 * (1 - 25/30) = 0.3 * 0.167 = 0.05
    # Total boost: 1.0 * (1.0 + 0.05) = 1.05
    assert pytest.approx(decayed_boost, rel=0.1) == 1.05

    flags = detector.flag_new_items([10, 20], {10: 2, 20: 100})
    assert flags[10] is True
    assert flags[20] is False


def test_parameter_optimizer_grid_search(
    sample_data: tuple[pd.DataFrame, pd.DataFrame],
) -> None:
    """Test ParameterOptimizer alpha and threshold grid search optimization."""
    ratings, movies = sample_data
    hybrid = HybridRecommender(alpha=0.5)
    hybrid.fit(ratings, movies)

    optimizer = ParameterOptimizer(hybrid_recommender=hybrid, validation_data=ratings)
    best_alpha = optimizer.grid_search_alpha(alpha_values=[0.2, 0.5, 0.8])
    assert "best_alpha" in best_alpha
    assert 0.0 <= best_alpha["best_alpha"] <= 1.0

    best_thresh = optimizer.grid_search_thresholds(threshold_candidates=[3, 5, 10])
    assert "best_cold_start_threshold" in best_thresh

    all_opt = optimizer.optimize_all_parameters()
    assert "alpha" in all_opt
    assert "cold_start_threshold" in all_opt

    bundle = optimizer.get_optimized_params_bundle()
    assert isinstance(bundle, dict)


def test_fallback_manager_execution_and_monitoring(
    sample_data: tuple[pd.DataFrame, pd.DataFrame],
) -> None:
    """Test FallbackManager fallback chain execution and monitoring."""
    ratings, movies = sample_data
    hybrid = HybridRecommender()
    hybrid.fit(ratings, movies)

    manager = FallbackManager(hybrid_recommender=hybrid)
    recs, mode = manager.execute_fallback_chain(user_id=2, k=3)
    assert isinstance(recs, list)
    assert isinstance(mode, str)

    metrics = manager.monitor_fallback_performance()
    assert "total_invocations" in metrics
    assert "fallback_rate" in metrics


def test_performance_monitor() -> None:
    """Test PerformanceMonitor recording and metrics calculation."""
    monitor = PerformanceMonitor()
    monitor.record_recommendation(latency_ms=12.5, fallback_mode="hybrid", count=5)
    monitor.record_recommendation(latency_ms=15.0, fallback_mode="content", count=5)

    metrics = monitor.get_metrics()
    assert metrics["total_requests"] == 2
    assert pytest.approx(metrics["avg_latency_ms"]) == 13.75
    assert metrics["p95_latency_ms"] > 0.0

