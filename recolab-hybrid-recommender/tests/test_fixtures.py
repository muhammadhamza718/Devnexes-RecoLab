"""Tests for CI-safe fixtures and full dataset availability.

This module verifies that:
1. Sample fixtures exist and can be loaded
2. Full MovieLens dataset is available when needed
3. Fixture data is representative
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from conftest import get_sample_movies_path, get_sample_ratings_path


def test_sample_fixtures_exist():
    """Verify sample fixtures are available for CI."""
    ratings_path = get_sample_ratings_path()
    movies_path = get_sample_movies_path()
    
    assert ratings_path.exists(), f"Sample ratings not found at {ratings_path}"
    assert movies_path.exists(), f"Sample movies not found at {movies_path}"


def test_sample_fixtures_loadable():
    """Verify sample fixtures can be loaded as DataFrames."""
    ratings = pd.read_csv(get_sample_ratings_path())
    movies = pd.read_csv(get_sample_movies_path())
    
    assert len(ratings) > 0, "Sample ratings empty"
    assert len(movies) > 0, "Sample movies empty"
    assert "userId" in ratings.columns
    assert "movieId" in ratings.columns
    assert "rating" in ratings.columns
    assert "movieId" in movies.columns
    assert "title" in movies.columns


def test_sample_fixtures_representative():
    """Verify sample fixtures are representative of full dataset."""
    ratings = pd.read_csv(get_sample_ratings_path())
    movies = pd.read_csv(get_sample_movies_path())
    
    # Check we have multiple users and movies
    assert ratings["userId"].nunique() >= 10, "Sample needs >= 10 users"
    assert ratings["movieId"].nunique() >= 100, "Sample needs >= 100 movies"
    
    # Check rating distribution is reasonable
    assert ratings["rating"].between(0.5, 5.0).all(), "Ratings must be 0.5-5.0"
    
    # Check movies have genres
    assert movies["genres"].notna().any(), "Movies should have genres"


@pytest.mark.full_dataset
def test_full_dataset_available():
    """Verify full MovieLens dataset is available when needed."""
    full_ratings = Path(__file__).parent.parent / "data" / "ml-latest-small" / "ratings.csv"
    full_movies = Path(__file__).parent.parent / "data" / "ml-latest-small" / "movies.csv"
    
    assert full_ratings.exists(), f"Full dataset not found at {full_ratings}"
    assert full_movies.exists(), f"Full dataset not found at {full_movies}"


@pytest.mark.full_dataset
def test_full_dataset_size():
    """Verify full dataset is the expected size."""
    ratings = pd.read_csv(
        Path(__file__).parent.parent / "data" / "ml-latest-small" / "ratings.csv"
    )
    movies = pd.read_csv(
        Path(__file__).parent.parent / "data" / "ml-latest-small" / "movies.csv"
    )
    
    # ml-latest-small has ~100k ratings and ~9700 movies
    assert len(ratings) >= 80000, f"Full dataset too small: {len(ratings)} ratings"
    assert len(movies) >= 9000, f"Full dataset too small: {len(movies)} movies"
    assert ratings["userId"].nunique() >= 600, "Full dataset should have 600+ users"