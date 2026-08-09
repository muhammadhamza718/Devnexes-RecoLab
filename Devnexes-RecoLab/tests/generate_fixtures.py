"""Generate test fixtures from MovieLens data for CI-safe testing.

This script creates a small sample dataset (50 users) that can be committed
to the repository so CI can run tests without requiring the full MovieLens
dataset to be present.
"""

import numpy as np
import pandas as pd

# Set random seed for reproducibility
rng = np.random.default_rng(42)

# Load the full datasets
ratings = pd.read_csv("data/ml-latest-small/ratings.csv")
movies = pd.read_csv("data/ml-latest-small/movies.csv")

# Select 50 random users
uids = rng.choice(ratings["userId"].unique(), 50, replace=False)
sub_ratings = ratings[ratings["userId"].isin(uids)]

# Get corresponding movies
sub_movies = movies[movies["movieId"].isin(sub_ratings["movieId"].unique())]

# Save fixtures
sub_ratings.to_csv("tests/fixtures/ratings_sample.csv", index=False)
sub_movies.to_csv("tests/fixtures/movies_sample.csv", index=False)

print("Generated fixtures:")
print(f"  - ratings_sample.csv: {len(sub_ratings)} ratings for {len(uids)} users")
print(f"  - movies_sample.csv: {len(sub_movies)} movies")
print(f"  - Users: {sorted(uids)}")
print(f"  - Movies: {sorted(sub_movies['movieId'].unique())}")
