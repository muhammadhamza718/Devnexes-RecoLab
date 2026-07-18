"""RecoLab hybrid recommender prototype — Day 1 data processing foundation.

Public surface for the data-splitting utilities introduced on Day 1.
"""

from recolab.split import chronological_split, load_ratings, save_split

__all__ = [
    "load_ratings",
    "chronological_split",
    "save_split",
]
