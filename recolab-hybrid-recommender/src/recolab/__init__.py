"""RecoLab hybrid recommender prototype — data processing foundation + interfaces.

Public surface for data-splitting utilities (Week 1) and shared recommendation
model interfaces (Week 2).
"""

from recolab.baseline import (
    PopularityModel,
    compute_popularity,
)
from recolab.interfaces import (
    ColdStartHandler,
    FeatureError,
    Recommender,
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
    "Recommender",
    "ColdStartHandler",
    "FeatureError",
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
