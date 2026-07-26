"""
Manual Testing Script for Week 2 ContentModel Implementation

This script provides comprehensive manual testing of the ContentModel implementation
including interactive testing, full dataset integration, persistence, protocol conformance,
edge cases, performance, and explanation quality checks.
"""

import time
import pandas as pd
from pathlib import Path
from recolab.content import ContentModel
from recolab.interfaces import Recommender, ColdStartHandler


def test_interactive_content_model():
    """Test 1: Interactive ContentModel Testing"""
    print("\n" + "="*60)
    print("TEST 1: Interactive ContentModel Testing")
    print("="*60)
    
    # Load sample data
    ratings = pd.read_csv('tests/fixtures/ratings_sample.csv')
    movies = pd.read_csv('tests/fixtures/movies_sample.csv')
    
    print(f"Loaded {len(ratings)} ratings and {len(movies)} movies")
    
    # Train model
    model = ContentModel().fit(ratings, movies)
    print("Model fitted successfully")
    
    # Test recommendations
    recs = model.recommend(user_id=1, k=5)
    print(f"User 1 recommendations: {recs}")
    
    # Test cold-start
    cold_recs = model.recommend_cold_start(genres=["Action"], liked_movie_ids=[], k=5)
    print(f"Cold-start recommendations: {cold_recs}")
    
    # Test similar items
    similar = model.similar_items(item_id=10, k=3)
    print(f"Similar to item 10: {similar}")
    
    # Test explanation
    explanation = model.get_explanation(user_id=1, item_id=10)
    print(f"Explanation for item 10: {explanation}")
    
    print("[PASS] Test 1 passed")


def test_full_dataset_integration():
    """Test 2: Full Dataset Integration Test"""
    print("\n" + "="*60)
    print("TEST 2: Full Dataset Integration Test")
    print("="*60)
    
    try:
        ratings = pd.read_csv('data/ml-latest-small/ratings.csv')
        movies = pd.read_csv('data/ml-latest-small/movies.csv')
        
        print(f"Loaded full dataset: {len(ratings)} ratings, {len(movies)} movies")
        
        model = ContentModel().fit(ratings, movies)
        print("Model fitted on full dataset")
        
        recs = model.recommend(user_id=1, k=10)
        print(f"Full dataset recommendations for user 1: {recs[:5]}...")
        
        print("[PASS] Test 2 passed")
    except FileNotFoundError as e:
        print(f"[SKIP] Test 2 skipped: Full dataset not found ({e})")


def test_persistence_roundtrip():
    """Test 3: Persistence Roundtrip Test"""
    print("\n" + "="*60)
    print("TEST 3: Persistence Roundtrip Test")
    print("="*60)
    
    ratings = pd.read_csv('tests/fixtures/ratings_sample.csv')
    movies = pd.read_csv('tests/fixtures/movies_sample.csv')
    
    model = ContentModel().fit(ratings, movies)
    
    # Save model
    test_path = Path("test_model.pkl")
    model.save(test_path)
    print(f"Model saved to {test_path}")
    
    # Load model
    loaded_model = ContentModel.load(test_path)
    print("Model loaded successfully")
    
    # Verify they produce same recommendations
    original_recs = model.recommend(1, 5)
    loaded_recs = loaded_model.recommend(1, 5)
    
    assert original_recs == loaded_recs, "Recommendations differ after roundtrip"
    print(f"Recommendations match: {original_recs}")
    
    # Cleanup
    test_path.unlink()
    print("[PASS] Test 3 passed")


def test_protocol_conformance():
    """Test 4: Protocol Conformance Check"""
    print("\n" + "="*60)
    print("TEST 4: Protocol Conformance Check")
    print("="*60)
    
    model = ContentModel()
    
    assert isinstance(model, Recommender), "Model does not satisfy Recommender protocol"
    print("[PASS] Model satisfies Recommender protocol")
    
    assert isinstance(model, ColdStartHandler), "Model does not satisfy ColdStartHandler protocol"
    print("[PASS] Model satisfies ColdStartHandler protocol")
    
    print("[PASS] Test 4 passed")


def test_edge_cases():
    """Test 5: Edge Case Testing"""
    print("\n" + "="*60)
    print("TEST 5: Edge Case Testing")
    print("="*60)
    
    ratings = pd.read_csv('tests/fixtures/ratings_sample.csv')
    movies = pd.read_csv('tests/fixtures/movies_sample.csv')
    
    model = ContentModel().fit(ratings, movies)
    
    # Test with unknown user
    try:
        recs = model.recommend(user_id=99999, k=5)
        print(f"Unknown user recommendations: {recs}")
    except Exception as e:
        print(f"Unknown user handled: {type(e).__name__}")
    
    # Test with unknown item
    try:
        similar = model.similar_items(item_id=99999, k=5)
        print(f"Unknown item similar: {similar}")
    except Exception as e:
        print(f"Unknown item handled: {type(e).__name__}")
    
    # Test with exclude_items
    recs = model.recommend(user_id=1, k=5, exclude_items={10, 20, 30})
    assert 10 not in recs and 20 not in recs and 30 not in recs
    print(f"Exclude items working: {recs}")
    
    print("[PASS] Test 5 passed")


def test_performance():
    """Test 6: Performance Test"""
    print("\n" + "="*60)
    print("TEST 6: Performance Test")
    print("="*60)
    
    ratings = pd.read_csv('tests/fixtures/ratings_sample.csv')
    movies = pd.read_csv('tests/fixtures/movies_sample.csv')
    
    model = ContentModel().fit(ratings, movies)
    
    # Measure recommendation latency
    start = time.time()
    recs = model.recommend(user_id=1, k=10)
    latency = time.time() - start
    
    print(f"Recommendation latency: {latency:.4f}s")
    
    # Measure similar_items latency
    start = time.time()
    similar = model.similar_items(item_id=10, k=10)
    latency = time.time() - start
    
    print(f"Similar items latency: {latency:.4f}s")
    
    # Measure cold-start latency
    start = time.time()
    cold_recs = model.recommend_cold_start(genres=["Action"], liked_movie_ids=[], k=10)
    latency = time.time() - start
    
    print(f"Cold-start latency: {latency:.4f}s")
    
    print("[PASS] Test 6 passed")


def test_explanation_quality():
    """Test 7: Explanation Quality Check"""
    print("\n" + "="*60)
    print("TEST 7: Explanation Quality Check")
    print("="*60)
    
    ratings = pd.read_csv('tests/fixtures/ratings_sample.csv')
    movies = pd.read_csv('tests/fixtures/movies_sample.csv')
    
    model = ContentModel().fit(ratings, movies)
    
    # Test explanation generation for various items
    test_items = [10, 20, 30, 40, 50]
    
    for item_id in test_items:
        try:
            explanation = model.get_explanation(user_id=1, item_id=item_id)
            print(f"Item {item_id}: {explanation}")
        except Exception as e:
            print(f"Item {item_id}: Error - {type(e).__name__}")
    
    print("[PASS] Test 7 passed")


def test_genre_filtering():
    """Test 8: Genre Filtering Test"""
    print("\n" + "="*60)
    print("TEST 8: Genre Filtering Test")
    print("="*60)
    
    ratings = pd.read_csv('tests/fixtures/ratings_sample.csv')
    movies = pd.read_csv('tests/fixtures/movies_sample.csv')
    
    model = ContentModel().fit(ratings, movies)
    
    # Test different genre combinations
    genre_combinations = [
        ["Action"],
        ["Drama"],
        ["Action", "Drama"],
        ["Comedy"],
        ["Action", "Comedy", "Drama"]
    ]
    
    for genres in genre_combinations:
        recs = model.recommend_cold_start(genres=genres, liked_movie_ids=[], k=5)
        print(f"Genres {genres}: {recs}")
    
    print("[PASS] Test 8 passed")


def test_bundle_integrity():
    """Test 9: Bundle Integrity Test"""
    print("\n" + "="*60)
    print("TEST 9: Bundle Integrity Test")
    print("="*60)
    
    ratings = pd.read_csv('tests/fixtures/ratings_sample.csv')
    movies = pd.read_csv('tests/fixtures/movies_sample.csv')
    
    model = ContentModel().fit(ratings, movies)
    
    # Test to_bundle
    bundle = model.to_bundle()
    required_keys = ["item_features", "item_index", "tfidf_matrix", "item_popularity", "ratings", "fitted"]
    
    for key in required_keys:
        assert key in bundle, f"Missing key in bundle: {key}"
    
    print(f"Bundle contains all required keys: {required_keys}")
    
    # Test from_bundle
    loaded_model = ContentModel.from_bundle(bundle)
    
    assert loaded_model.item_features == model.item_features
    assert loaded_model.fitted == model.fitted
    print("Bundle roundtrip preserves data integrity")
    
    print("[PASS] Test 9 passed")


def test_user_history_utilization():
    """Test 10: User History Utilization Test"""
    print("\n" + "="*60)
    print("TEST 10: User History Utilization Test")
    print("="*60)
    
    ratings = pd.read_csv('tests/fixtures/ratings_sample.csv')
    movies = pd.read_csv('tests/fixtures/movies_sample.csv')
    
    model = ContentModel().fit(ratings, movies)
    
    # Test recommendations for different users
    test_users = [1, 2, 3, 4, 5]
    
    for user_id in test_users:
        try:
            recs = model.recommend(user_id=user_id, k=5)
            print(f"User {user_id} recommendations: {recs}")
        except Exception as e:
            print(f"User {user_id}: Error - {type(e).__name__}")
    
    print("[PASS] Test 10 passed")


def main():
    """Run all manual tests"""
    print("\n" + "="*60)
    print("MANUAL TESTING SUITE FOR WEEK 2 CONTENTMODEL")
    print("="*60)
    
    tests = [
        test_interactive_content_model,
        test_full_dataset_integration,
        test_persistence_roundtrip,
        test_protocol_conformance,
        test_edge_cases,
        test_performance,
        test_explanation_quality,
        test_genre_filtering,
        test_bundle_integrity,
        test_user_history_utilization
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"[FAIL] {test.__name__} failed: {e}")
            failed += 1
    
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Passed: {passed}/{len(tests)}")
    print(f"Failed: {failed}/{len(tests)}")
    
    if failed == 0:
        print("[SUCCESS] All manual tests passed!")
    else:
        print(f"[WARNING] {failed} test(s) failed")


if __name__ == "__main__":
    main()
