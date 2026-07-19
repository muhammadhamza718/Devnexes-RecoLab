"""RecoLab hybrid recommender prototype — Day 1 data processing foundation.

Public surface for the data-splitting utilities introduced on Day 1.
"""

from recolab.baseline import (
    PopularityModel,
    compute_popularity,
)
from recolab.metrics import (
    evaluate_all,
    evaluate_user,
    ndcg_at_k,
    precision_at_k,
    recall_at_k,
)
from recolab.persistence import (
    ARTIFACT_PROTOCOL,
    MODELS_DIRNAME,
    ModelBundle,
    PersistError,
    load_artifact,
    load_model_bundle,
    save_artifact,
    save_model_bundle,
)
from recolab.split import chronological_split, load_ratings, save_split

__all__ = [
    "load_ratings",
    "chronological_split",
    "save_split",
    "PopularityModel",
    "compute_popularity",
    "ARTIFACT_PROTOCOL",
    "MODELS_DIRNAME",
    "PersistError",
    "ModelBundle",
    "save_artifact",
    "load_artifact",
    "save_model_bundle",
    "load_model_bundle",
    "precision_at_k",
    "recall_at_k",
    "ndcg_at_k",
    "evaluate_user",
    "evaluate_all",
]
