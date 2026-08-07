"""Onboarding wizard controller managing step state and navigation (Task-001)."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ui.session_manager import SessionManager
from ui.onboarding.preference_validator import PreferenceValidator

DEFAULT_SKIP_GENRES = ["Action", "Comedy", "Drama"]


class OnboardingWizard:
    """Controls wizard step navigation, validation, and completion state."""

    TOTAL_STEPS = 3  # Step 0: Genres, Step 1: Liked Movies, Step 2: Confirmation

    def __init__(self, session_manager: type[SessionManager] | None = None) -> None:
        self.sm = session_manager or SessionManager

    def get_current_step(self) -> int:
        """Return the current step index (0-based)."""
        return self.sm.get_onboarding_step()

    def can_proceed(self) -> tuple[bool, str | None]:
        """Validate if the current step can advance to the next step."""
        step = self.get_current_step()
        if step == 0:
            genres = self.sm.get_onboarding_selected_genres()
            # On step 0, allow proceeding if at least 1 genre is selected, or if they want to skip
            if not genres:
                return True, None  # User can proceed without genres (they might add liked movies on step 1)
            return PreferenceValidator.validate_genres(genres)
        elif step == 1:
            liked = self.sm.get_onboarding_liked_movies()
            return PreferenceValidator.validate_liked_movies(liked)
        elif step == 2:
            prefs = self.get_preferences()
            return PreferenceValidator.validate_preferences(prefs)
        return True, None

    def next_step(self) -> bool:
        """Advance to the next wizard step if current step is valid."""
        can_do, _ = self.can_proceed()
        if not can_do:
            return False

        curr = self.get_current_step()
        if curr < self.TOTAL_STEPS - 1:
            self.sm.set_onboarding_step(curr + 1)
            return True
        return False

    def previous_step(self) -> bool:
        """Go back to the previous wizard step."""
        curr = self.get_current_step()
        if curr > 0:
            self.sm.set_onboarding_step(curr - 1)
            return True
        return False

    def set_step(self, step: int) -> bool:
        """Jump to a specific step if valid."""
        if 0 <= step < self.TOTAL_STEPS:
            self.sm.set_onboarding_step(step)
            return True
        return False

    def skip_onboarding(self) -> dict[str, Any]:
        """Skip onboarding wizard using default genres ['Action', 'Comedy', 'Drama']."""
        self.sm.set_onboarding_selected_genres(list(DEFAULT_SKIP_GENRES))
        self.sm.set_onboarding_liked_movies([])
        self.sm.set_onboarding_preference_weights({g: 1.0 for g in DEFAULT_SKIP_GENRES})

        now_iso = datetime.now(timezone.utc).isoformat()
        prefs = {
            "genres": list(DEFAULT_SKIP_GENRES),
            "liked_movies": [],
            "preference_weights": {g: 1.0 for g in DEFAULT_SKIP_GENRES},
            "is_skip": True,
            "completed_at": now_iso,
        }

        self.sm.set_onboarding_preferences(prefs)
        self.sm.set_onboarding_complete(True)
        self.sm.set_onboarding_timestamp(now_iso)
        self.sm.set_onboarding_active(False)
        self.sm.set_current_view("recommendations")
        return prefs

    def get_preferences(self) -> dict[str, Any]:
        """Collect current selections into a preference dict."""
        genres = self.sm.get_onboarding_selected_genres()
        liked = self.sm.get_onboarding_liked_movies()
        weights = self.sm.get_onboarding_preference_weights()
        if not weights and genres:
            weights = {g: 1.0 for g in genres}

        return {
            "genres": genres,
            "liked_movies": liked,
            "preference_weights": weights,
            "is_skip": False,
        }

    def complete_onboarding(self) -> dict[str, Any]:
        """Finalize onboarding with user selections."""
        prefs = self.get_preferences()

        # If empty preferences on completion, apply defaults
        if not prefs["genres"] and not prefs["liked_movies"]:
            return self.skip_onboarding()

        now_iso = datetime.now(timezone.utc).isoformat()
        prefs["completed_at"] = now_iso

        self.sm.set_onboarding_preferences(prefs)
        self.sm.set_onboarding_complete(True)
        self.sm.set_onboarding_timestamp(now_iso)
        self.sm.set_onboarding_active(False)
        self.sm.set_current_view("recommendations")
        return prefs
