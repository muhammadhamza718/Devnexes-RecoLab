"""Pytest configuration and shared fixtures for RecoLab tests."""

from pathlib import Path

import pandas as pd
import pytest


def get_sample_ratings_path() -> Path:
    """Get path to sample ratings fixture, fallback to full dataset."""
    fixture_path = Path(__file__).parent / "fixtures" / "ratings_sample.csv"
    if fixture_path.exists():
        return fixture_path
    # Fallback to full dataset
    return Path(__file__).parent.parent / "data" / "ml-latest-small" / "ratings.csv"


def get_sample_movies_path() -> Path:
    """Get path to sample movies fixture, fallback to full dataset."""
    fixture_path = Path(__file__).parent / "fixtures" / "movies_sample.csv"
    if fixture_path.exists():
        return fixture_path
    # Fallback to full dataset
    return Path(__file__).parent.parent / "data" / "ml-latest-small" / "movies.csv"


@pytest.fixture
def sample_ratings_df() -> pd.DataFrame:
    """Load sample ratings as DataFrame."""
    return pd.read_csv(get_sample_ratings_path())


@pytest.fixture
def sample_movies_df() -> pd.DataFrame:
    """Load sample movies as DataFrame."""
    return pd.read_csv(get_sample_movies_path())


@pytest.fixture
def sample_ratings_path() -> Path:
    """Get path to sample ratings file."""
    return get_sample_ratings_path()


@pytest.fixture
def sample_movies_path() -> Path:
    """Get path to sample movies file."""
    return get_sample_movies_path()
