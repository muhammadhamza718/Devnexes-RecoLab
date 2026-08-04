"""Smoke test for Day 4 Morning Cold-Start Onboarding functionality."""

import sys
from pathlib import Path

# Add src and project root to path
PROJECT_ROOT = Path(__file__).resolve().parent
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Mock streamlit session_state for headless test execution
import streamlit as st

if not hasattr(st, "session_state") or not isinstance(st.session_state, dict):
    st.session_state = {}

from ui.session_manager import SessionManager
from ui.onboarding.genre_provider import GenreProvider
from ui.onboarding.movie_search_provider import MovieSearchProvider
from ui.onboarding.preference_validator import PreferenceValidator
from ui.onboarding.wizard_controller import OnboardingWizard
from ui.onboarding.onboarding_recommender import OnboardingRecommender
from ui.data_provider import DataProvider


def test_session_manager_onboarding():
    print("Testing SessionManager onboarding keys...")
    SessionManager.ensure_initialized()
    assert SessionManager.is_onboarding_active() is False
    assert SessionManager.get_onboarding_step() == 0

    SessionManager.reset_onboarding_state()
    assert SessionManager.is_onboarding_active() is True
    assert SessionManager.get_selected_genres() == []
    assert SessionManager.get_liked_movies() == []

    SessionManager.set_selected_genres(["Action", "Comedy"])
    assert SessionManager.get_selected_genres() == ["Action", "Comedy"]
    print("  [OK] SessionManager onboarding state tests passed.")


def test_genre_provider():
    print("Testing GenreProvider...")
    gp = GenreProvider()
    all_genres = gp.get_all_genres()
    assert len(all_genres) > 0
    assert "Action" in all_genres

    popularity = gp.get_genre_popularity()
    assert isinstance(popularity, dict)
    assert popularity.get("Action", 0) > 0

    combos = gp.get_suggested_combinations()
    assert len(combos) >= 3
    print("  [OK] GenreProvider tests passed.")


def test_movie_search_provider():
    print("Testing MovieSearchProvider...")
    sp = MovieSearchProvider()
    popular = sp.search_movies("")
    assert len(popular) > 0

    matches = sp.search_movies("<script>Inception</script>")
    assert isinstance(matches, list)

    preview = sp.get_movie_preview(1)
    assert preview is not None
    assert preview["movieId"] == 1
    assert "Toy Story" in preview["title"]
    print("  [OK] MovieSearchProvider tests passed.")


def test_preference_validator():
    print("Testing PreferenceValidator...")
    valid, err = PreferenceValidator.validate_genres(["Action", "Drama"])
    assert valid is True
    assert err is None

    valid_over, err_over = PreferenceValidator.validate_genres(["G" + str(i) for i in range(15)])
    assert valid_over is False
    assert "up to 10" in err_over

    valid_prefs, err_prefs = PreferenceValidator.validate_preferences({"genres": ["Action"], "liked_movies": []})
    assert valid_prefs is True
    print("  [OK] PreferenceValidator tests passed.")


def test_wizard_controller():
    print("Testing OnboardingWizard controller...")
    SessionManager.reset_onboarding_state()
    wizard = OnboardingWizard()
    assert wizard.get_current_step() == 0

    # Advance to step 1
    SessionManager.set_selected_genres(["Action"])
    adv = wizard.next_step()
    assert adv is True
    assert wizard.get_current_step() == 1

    # Advance to step 2
    adv2 = wizard.next_step()
    assert adv2 is True
    assert wizard.get_current_step() == 2

    # Complete onboarding
    completed = wizard.complete_onboarding()
    assert completed["is_skip"] is False
    assert SessionManager.is_onboarding_complete() is True
    assert SessionManager.is_onboarding_active() is False

    # Test skip onboarding
    SessionManager.reset_onboarding_state()
    skipped = wizard.skip_onboarding()
    assert skipped["is_skip"] is True
    assert len(SessionManager.get_selected_genres()) > 0
    print("  [OK] OnboardingWizard tests passed.")


def test_onboarding_recommender():
    print("Testing OnboardingRecommender...")
    dp = DataProvider()
    rec = OnboardingRecommender(data_provider=dp)
    prefs = {"genres": ["Action", "Sci-Fi"], "liked_movies": [{"movieId": 2571, "title": "Matrix"}]}
    results = rec.get_preview_recommendations(prefs, top_n=5)
    assert len(results) > 0
    assert "movieId" in results[0]
    assert "title" in results[0]
    print("  [OK] OnboardingRecommender tests passed.")


if __name__ == "__main__":
    test_session_manager_onboarding()
    test_genre_provider()
    test_movie_search_provider()
    test_preference_validator()
    test_wizard_controller()
    test_onboarding_recommender()
    print("\nALL COLD-START ONBOARDING SMOKE TESTS PASSED SUCCESSFULLY!")
