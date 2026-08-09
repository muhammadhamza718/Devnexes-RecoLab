"""Unit tests for UserBasedCF and ItemBasedCF recommenders."""

from __future__ import annotations

import time
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from recolab.collaborative import ItemBasedCF, UserBasedCF
from recolab.content import ContentModel
from recolab.interfaces import Recommender


@pytest.fixture
def sample_ratings() -> pd.DataFrame:
    """Sample ratings DataFrame for testing collaborative filtering."""
    return pd.DataFrame({
        "userId": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4],
        "movieId": [10, 20, 30, 10, 20, 40, 20, 30, 40, 50, 60],
        "rating": [5.0, 4.0, 3.0, 5.0, 4.0, 2.0, 4.0, 3.0, 5.0, 5.0, 4.0],
        "timestamp": [1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
    })


@pytest.fixture
def sample_movies() -> pd.DataFrame:
    """Sample movies DataFrame for ContentModel integration."""
    return pd.DataFrame({
        "movieId": [10, 20, 30, 40, 50, 60],
        "title": ["Movie A", "Movie B", "Movie C", "Movie D", "Movie E", "Movie F"],
        "genres": ["Action", "Action|Sci-Fi", "Drama", "Action|Comedy", "Drama", "Sci-Fi"],
    })


class TestUserBasedCFInitialization:
    """Task T008: Test UserBasedCF initialization and hyper-parameter validation."""

    def test_default_initialization(self) -> None:
        """Verify default hyper-parameter values and initial un-fitted state."""
        model = UserBasedCF()
        assert model.k_similar_users == 50
        assert model.min_similarity == 0.1
        assert model.cold_start_threshold == 5
        assert model.user_item_matrix is None
        assert model.similarity_matrix is None
        assert model.user_mapping == {}
        assert model.movie_mapping == {}
        assert model.is_fitted is False
        assert isinstance(model, Recommender)

    def test_custom_initialization(self) -> None:
        """Verify custom hyper-parameters."""
        model = UserBasedCF(k_similar_users=10, min_similarity=0.2, cold_start_threshold=3)
        assert model.k_similar_users == 10
        assert model.min_similarity == 0.2
        assert model.cold_start_threshold == 3

    def test_invalid_initialization_params(self) -> None:
        """Verify validation errors for invalid hyper-parameters."""
        with pytest.raises(ValueError, match="k_similar_users must be a positive integer"):
            UserBasedCF(k_similar_users=0)

        with pytest.raises(ValueError, match="min_similarity must be between 0.0 and 1.0"):
            UserBasedCF(min_similarity=-0.5)


class TestUserItemMatrixBuilding:
    """Task T009: Test user-item matrix building and index mappings."""

    def test_build_user_item_matrix(self, sample_ratings: pd.DataFrame) -> None:
        """Verify CSR matrix shape, non-zero entries, and mappings."""
        model = UserBasedCF(cold_start_threshold=0)
        model.fit(sample_ratings)

        assert model.is_fitted is True
        assert model.user_item_matrix is not None
        # 4 unique users (1, 2, 3, 4), 6 unique movies (10, 20, 30, 40, 50, 60)
        assert model.user_item_matrix.shape == (4, 6)
        assert len(model.user_mapping) == 4
        assert len(model.movie_mapping) == 6
        assert len(model.reverse_user_mapping) == 4
        assert len(model.reverse_movie_mapping) == 6

        # Check mapping bidirectionality
        for raw_uid, idx in model.user_mapping.items():
            assert model.reverse_user_mapping[idx] == raw_uid

        for raw_mid, idx in model.movie_mapping.items():
            assert model.reverse_movie_mapping[idx] == raw_mid

        # Verify rating value in matrix
        u1_idx = model.user_mapping[1]
        m10_idx = model.movie_mapping[10]
        assert model.user_item_matrix[u1_idx, m10_idx] == 5.0


class TestCosineSimilarityComputation:
    """Task T010: Test cosine similarity computation between users."""

    def test_compute_similarity_matrix(self, sample_ratings: pd.DataFrame) -> None:
        """Verify similarity matrix dimensions, bounds, and self-similarity."""
        model = UserBasedCF(cold_start_threshold=0)
        model.fit(sample_ratings)

        assert model.similarity_matrix is not None
        assert model.similarity_matrix.shape == (4, 4)

        # Self-similarity on diagonal must be ~1.0
        np.testing.assert_allclose(np.diag(model.similarity_matrix), 1.0, atol=1e-5)

        # User 1 and User 2 share movies 10 & 20 with matching high ratings
        u1_idx = model.user_mapping[1]
        u2_idx = model.user_mapping[2]
        sim_1_2 = model.similarity_matrix[u1_idx, u2_idx]
        assert sim_1_2 > 0.5


class TestFindSimilarUsers:
    """Task T011: Test finding nearest similar users for a target user."""

    def test_find_similar_users(self, sample_ratings: pd.DataFrame) -> None:
        """Verify top similar users filtering and sorting."""
        model = UserBasedCF(k_similar_users=2, min_similarity=0.1, cold_start_threshold=0)
        model.fit(sample_ratings)

        similar_users = model._find_similar_users(user_id=1)
        assert len(similar_users) <= 2
        # Target user 1 should NOT be in similar users list
        sim_uids = [uid for uid, _ in similar_users]
        assert 1 not in sim_uids

        # Similar users list should be sorted by similarity descending
        if len(similar_users) > 1:
            assert similar_users[0][1] >= similar_users[1][1]


class TestRecommendationAggregation:
    """Task T012: Test predicted rating aggregation logic."""

    def test_aggregate_predictions(self, sample_ratings: pd.DataFrame) -> None:
        """Verify weighted average prediction calculation for candidate items."""
        model = UserBasedCF(min_similarity=0.1, cold_start_threshold=0)
        model.fit(sample_ratings)

        similar_users = model._find_similar_users(user_id=1)
        predictions = model._aggregate_predictions(similar_users, target_user_id=1)
        assert isinstance(predictions, dict)
        # User 1 hasn't rated movie 40 (rated by user 2 & user 3), so movie 40 should be predicted
        assert 40 in predictions
        assert predictions[40] > 0.0


class TestConsumedItemFiltering:
    """Task T013: Test consumed-item filtering in recommendations."""

    def test_recommend_excludes_consumed_items(self, sample_ratings: pd.DataFrame) -> None:
        """Verify recommend does not include items already rated by target user."""
        model = UserBasedCF(min_similarity=0.1, cold_start_threshold=0)
        model.fit(sample_ratings)

        # User 1 has rated movies 10, 20, 30
        recs = model.recommend(user_id=1, k=5)
        assert 10 not in recs
        assert 20 not in recs
        assert 30 not in recs
        assert len(recs) > 0


class TestExcludeItemsParameter:
    """Task T014: Test exclude_items parameter handling."""

    def test_recommend_handles_exclude_items(self, sample_ratings: pd.DataFrame) -> None:
        """Verify recommend excludes items specified in exclude_items set."""
        model = UserBasedCF(min_similarity=0.1, cold_start_threshold=0)
        model.fit(sample_ratings)

        # Movie 40 would be recommended to user 1. Explicitly exclude movie 40.
        recs = model.recommend(user_id=1, k=5, exclude_items={40})
        assert 40 not in recs


class TestEdgeCaseNoSimilarUsers:
    """Task T015: Test edge case when user has no similar users above threshold."""

    def test_user_no_similar_users(self, sample_ratings: pd.DataFrame) -> None:
        """Verify graceful empty list or fallback when min_similarity is high."""
        # Set min_similarity unnaturally high so no users meet threshold
        model = UserBasedCF(min_similarity=0.999, cold_start_threshold=0)
        model.fit(sample_ratings)

        similar_users = model._find_similar_users(user_id=1)
        assert len(similar_users) == 0

        recs = model.recommend(user_id=1, k=5)
        assert isinstance(recs, list)


class TestRecommendationPerformance:
    """Task T016: Test performance benchmark (<100ms recommendation generation)."""

    def test_recommendation_latency_under_100ms(self, sample_ratings: pd.DataFrame) -> None:
        """Verify recommendation latency is under 100ms."""
        model = UserBasedCF(cold_start_threshold=0)
        model.fit(sample_ratings)

        start_time = time.perf_counter()
        recs = model.recommend(user_id=1, k=5)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        assert elapsed_ms < 100.0, f"Recommendation took {elapsed_ms:.2f}ms, target is <100ms"


class TestColdStartFallback:
    """Task T041-T045: Test cold-start detection and ContentModel fallback integration."""

    def test_cold_start_detection(self, sample_ratings: pd.DataFrame) -> None:
        """Verify user with <= 5 ratings is flagged as cold-start."""
        model = UserBasedCF(cold_start_threshold=5)
        model.fit(sample_ratings)

        # User 1 has 3 ratings (<= 5), so cold_start is True
        assert model._is_cold_start(user_id=1) is True
        # Non-existent user is cold-start
        assert model._is_cold_start(user_id=999) is True

    def test_cold_start_fallback_to_content_model(
        self, sample_ratings: pd.DataFrame, sample_movies: pd.DataFrame
    ) -> None:
        """Verify recommendations fall back to ContentModel for cold-start users."""
        content_model = ContentModel()
        content_model.fit(sample_ratings, sample_movies)

        model = UserBasedCF(cold_start_threshold=5, content_model=content_model)
        model.fit(sample_ratings)

        recs = model.recommend(user_id=1, k=3)
        assert isinstance(recs, list)
        assert len(recs) > 0


# =====================================================================
# Item-Based Collaborative Filtering (ItemBasedCF) Test Suite
# =====================================================================


class TestItemBasedCFInitialization:
    """Task T008 [001-collaborative-filtering]: Test ItemBasedCF initialization."""

    def test_default_initialization(self) -> None:
        """Verify default hyper-parameters and Recommender protocol implementation."""
        model = ItemBasedCF()
        assert model.k_similar_items == 50
        assert model.min_similarity == 0.1
        assert model.user_item_matrix is None
        assert model.item_item_matrix is None
        assert model.is_fitted is False
        assert isinstance(model, Recommender)

    def test_custom_initialization(self) -> None:
        """Verify custom hyper-parameters initialization."""
        model = ItemBasedCF(k_similar_items=15, min_similarity=0.25)
        assert model.k_similar_items == 15
        assert model.min_similarity == 0.25

    def test_invalid_initialization_params(self) -> None:
        """Verify validation errors for invalid hyper-parameters."""
        with pytest.raises(ValueError, match="k_similar_items must be a positive integer"):
            ItemBasedCF(k_similar_items=0)

        with pytest.raises(ValueError, match="min_similarity must be between 0.0 and 1.0"):
            ItemBasedCF(min_similarity=1.5)


class TestUserItemMatrixBuildingIBCF:
    """Task T009 [001-collaborative-filtering]: Test matrix building for item-based CF."""

    def test_build_user_item_matrix(self, sample_ratings: pd.DataFrame) -> None:
        """Verify matrix dimensions, user/movie index mappings, and rating data."""
        model = ItemBasedCF()
        model.fit(sample_ratings)

        assert model.is_fitted is True
        assert model.user_item_matrix is not None
        assert model.user_item_matrix.shape == (4, 6)
        assert len(model.movie_mapping) == 6
        assert len(model.user_mapping) == 4


class TestItemItemSimilarityComputation:
    """Task T010 [001-collaborative-filtering]: Test item-item similarity computation."""

    def test_compute_item_similarity(self, sample_ratings: pd.DataFrame) -> None:
        """Verify item-item matrix dimensions (n_items x n_items) and similarity scores."""
        model = ItemBasedCF()
        model.fit(sample_ratings)

        assert model.item_item_matrix is not None
        assert model.item_item_matrix.shape == (6, 6)

        # Diagonal values should be ~1.0 (self-similarity)
        np.testing.assert_allclose(np.diag(model.item_item_matrix), 1.0, atol=1e-5)

        # Movie 10 and Movie 20 both rated high by user 1 and user 2 -> high similarity
        m10_idx = model.movie_mapping[10]
        m20_idx = model.movie_mapping[20]
        sim_10_20 = model.item_item_matrix[m10_idx, m20_idx]
        assert sim_10_20 > 0.5


class TestFindSimilarItemsIBCF:
    """Task T011 [001-collaborative-filtering]: Test finding nearest similar items."""

    def test_find_similar_items(self, sample_ratings: pd.DataFrame) -> None:
        """Verify top similar items sorted descending, self excluded."""
        model = ItemBasedCF(k_similar_items=3, min_similarity=0.1)
        model.fit(sample_ratings)

        similar_items = model._find_similar_items(movie_id=10)
        assert len(similar_items) <= 3

        sim_mids = [mid for mid, _ in similar_items]
        assert 10 not in sim_mids

        if len(similar_items) > 1:
            assert similar_items[0][1] >= similar_items[1][1]


class TestAggregationIBCF:
    """Task T012 [001-collaborative-filtering]: Test predicted item aggregation."""

    def test_aggregate_predictions(self, sample_ratings: pd.DataFrame) -> None:
        """Verify item-based weighted rating prediction for unconsumed movies."""
        model = ItemBasedCF(min_similarity=0.1)
        model.fit(sample_ratings)

        # User 1 has rated movies 10, 20, 30
        user_rated_items = [(10, 5.0), (20, 4.0), (30, 3.0)]
        predictions = model._aggregate_predictions(user_id=1, user_rated_items=user_rated_items)

        assert isinstance(predictions, dict)
        # Movie 40 is similar to movie 20 (rated by User 2 & 3), so movie 40 should be predicted
        assert 40 in predictions
        assert predictions[40] > 0.0


class TestConsumedItemFilteringIBCF:
    """Task T013 [001-collaborative-filtering]: Test consumed-item filtering."""

    def test_recommend_excludes_consumed_items(self, sample_ratings: pd.DataFrame) -> None:
        """Verify recommend does not return movies already rated by user."""
        model = ItemBasedCF(min_similarity=0.1)
        model.fit(sample_ratings)

        recs = model.recommend(user_id=1, k=5)
        # User 1 has rated 10, 20, 30
        assert 10 not in recs
        assert 20 not in recs
        assert 30 not in recs
        assert len(recs) > 0


class TestExcludeItemsParameterIBCF:
    """Task T014 [001-collaborative-filtering]: Test exclude_items handling."""

    def test_recommend_handles_exclude_items(self, sample_ratings: pd.DataFrame) -> None:
        """Verify explicit exclude_items parameter set is excluded."""
        model = ItemBasedCF(min_similarity=0.1)
        model.fit(sample_ratings)

        recs = model.recommend(user_id=1, k=5, exclude_items={40})
        assert 40 not in recs


class TestLowRatedItemEdgeCaseIBCF:
    """Task T015 [001-collaborative-filtering]: Test edge case for user with ratings."""

    def test_recommend_low_rated_items(self, sample_ratings: pd.DataFrame) -> None:
        """Verify system handles users with low ratings gracefully."""
        model = ItemBasedCF(min_similarity=0.1)
        model.fit(sample_ratings)

        recs = model.recommend(user_id=2, k=5)
        assert isinstance(recs, list)


class TestRecommendationPerformanceIBCF:
    """Task T016 [001-collaborative-filtering]: Test recommendation latency."""

    def test_recommendation_latency_under_100ms(self, sample_ratings: pd.DataFrame) -> None:
        """Verify item-based recommendation generation latency is under 100ms."""
        model = ItemBasedCF()
        model.fit(sample_ratings)

        start_time = time.perf_counter()
        recs = model.recommend(user_id=1, k=5)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        assert elapsed_ms < 100.0, f"Item-based recommendation took {elapsed_ms:.2f}ms"


class TestNewItemFallback:
    """Task T041-T045 [001-collaborative-filtering]: Test new item detection and ContentModel fallback."""

    def test_new_item_detection(self, sample_ratings: pd.DataFrame) -> None:
        """Verify new item with 0 training ratings is detected by _is_new_item."""
        model = ItemBasedCF()
        model.fit(sample_ratings)

        # Movie 10 is in sample ratings -> False
        assert model._is_new_item(movie_id=10) is False
        # Movie 9999 was not in sample ratings -> True (new item)
        assert model._is_new_item(movie_id=9999) is True

    def test_unknown_user_fallback_to_content_model(
        self, sample_ratings: pd.DataFrame, sample_movies: pd.DataFrame
    ) -> None:
        """Verify recommendation for unknown user falls back to ContentModel."""
        content_model = ContentModel()
        content_model.fit(sample_ratings, sample_movies)

        model = ItemBasedCF(content_model=content_model)
        model.fit(sample_ratings)

        recs = model.recommend(user_id=999, k=3)
        assert isinstance(recs, list)
        assert len(recs) > 0


class TestCFPersistence:
    """Test model persistence (save/load/to_bundle/from_bundle) for UserBasedCF and ItemBasedCF (REQ-012)."""

    def test_user_based_cf_persistence(
        self, sample_ratings: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify UserBasedCF to_bundle, from_bundle, save, and load roundtrip."""
        model = UserBasedCF(k_similar_users=5, cold_start_threshold=1)
        model.fit(sample_ratings)

        bundle = model.to_bundle()
        assert bundle["is_fitted"] is True
        assert bundle["k_similar_users"] == 5

        restored = UserBasedCF.from_bundle(bundle)
        assert restored.is_fitted is True
        assert restored.k_similar_users == 5
        assert restored.recommend(user_id=1, k=3) == model.recommend(user_id=1, k=3)

        save_file = tmp_path / "ubcf.pkl"
        model.save(save_file)
        loaded = UserBasedCF.load(save_file)
        assert loaded.is_fitted is True
        assert loaded.recommend(user_id=1, k=3) == model.recommend(user_id=1, k=3)

    def test_item_based_cf_persistence(
        self, sample_ratings: pd.DataFrame, tmp_path: Path
    ) -> None:
        """Verify ItemBasedCF to_bundle, from_bundle, save, and load roundtrip."""
        model = ItemBasedCF(k_similar_items=5)
        model.fit(sample_ratings)

        bundle = model.to_bundle()
        assert bundle["is_fitted"] is True
        assert bundle["k_similar_items"] == 5

        restored = ItemBasedCF.from_bundle(bundle)
        assert restored.is_fitted is True
        assert restored.k_similar_items == 5
        assert restored.recommend(user_id=1, k=3) == model.recommend(user_id=1, k=3)

        save_file = tmp_path / "ibcf.pkl"
        model.save(save_file)
        loaded = ItemBasedCF.load(save_file)
        assert loaded.is_fitted is True
        assert loaded.recommend(user_id=1, k=3) == model.recommend(user_id=1, k=3)


class TestCFExplanations:
    """Test model explanation generation (explain()) for REQ-004."""

    def test_user_based_cf_explanations(
        self, sample_ratings: pd.DataFrame, sample_movies: pd.DataFrame
    ) -> None:
        """Verify UserBasedCF explain() returns truthful explanations for normal and cold-start users."""
        content_model = ContentModel()
        content_model.fit(sample_ratings, sample_movies)

        model = UserBasedCF(cold_start_threshold=1, content_model=content_model)
        model.fit(sample_ratings)

        # Standard user with > 1 rating (User 1 has 3 ratings)
        exp_normal = model.explain(user_id=1, movie_id=40)
        assert "similar taste" in exp_normal.lower()

        # Cold start user with 0 ratings
        exp_cold = model.explain(user_id=999, movie_id=10)
        assert len(exp_cold) > 0

    def test_item_based_cf_explanations(
        self, sample_ratings: pd.DataFrame, sample_movies: pd.DataFrame
    ) -> None:
        """Verify ItemBasedCF explain() returns truthful explanations for standard and new items."""
        content_model = ContentModel()
        content_model.fit(sample_ratings, sample_movies)

        model = ItemBasedCF(content_model=content_model)
        model.fit(sample_ratings)

        # Standard item
        exp_item = model.explain(user_id=1, movie_id=40)
        assert "similar movies" in exp_item.lower()

        # New item not in training set
        exp_new = model.explain(user_id=1, movie_id=9999)
        assert len(exp_new) > 0

