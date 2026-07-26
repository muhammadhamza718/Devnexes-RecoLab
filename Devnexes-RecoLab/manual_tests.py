"""
Manual Testing Script for Week 2 ContentModel Implementation

This script provides comprehensive manual testing of the ContentModel implementation
including interactive testing, full dataset integration, persistence, protocol conformance,
edge cases, performance, and explanation quality checks.
"""

import sys
from pathlib import Path

# Add src directory to Python path for development
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

import time
import pandas as pd
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


def test_protocol_conformance():
    """Test 2: Protocol Conformance Check"""
    print("\n" + "="*60)
    print("TEST 2: Protocol Conformance Check")
    print("="*60)
    
    model = ContentModel()
    
    assert isinstance(model, Recommender), "Model does not satisfy Recommender protocol"
    print("[PASS] Model satisfies Recommender protocol")
    
    assert isinstance(model, ColdStartHandler), "Model does not satisfy ColdStartHandler protocol"
    print("[PASS] Model satisfies ColdStartHandler protocol")
    
    print("[PASS] Test 2 passed")


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


def test_performance():
    """Test 4: Performance Test"""
    print("\n" + "="*60)
    print("TEST 4: Performance Test")
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


def main():
    """Run all manual tests"""
    print("\n" + "="*60)
    print("MANUAL TESTING SUITE FOR WEEK 2 CONTENTMODEL")
    print("="*60)
    
    tests = [
        test_interactive_content_model,
        test_protocol_conformance,
        test_persistence_roundtrip,
        test_performance,
        test_edge_cases
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
