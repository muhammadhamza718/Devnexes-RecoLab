"""Model loading for the RecoLab Streamlit app (Task-003).

Loads pre-trained model bundles from the project ``models/`` directory (the
REQ-012 persistence convention) when present, and otherwise falls back to
fitting the model on the chronological train split at runtime.

Models are loaded lazily and cached per server run (``st.cache_resource``):
the first time a model is requested it is loaded/fitted (showing a spinner in
the caller), and every subsequent rerun reuses the same instance.
"""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

MODELS_DIR = PROJECT_ROOT / "models"

from recolab import (  # noqa: E402  (after sys.path bootstrap)
    ContentModel,
    HybridRecommender,
    ItemBasedCF,
    PopularityModel,
    UserBasedCF,
    load_artifact,
    load_model_bundle,
)

# Canonical model names as shown in the UI.
MODEL_NAMES: list[str] = [
    "Popularity",
    "Content",
    "User-Based CF",
    "Item-Based CF",
    "Hybrid",
]

# Keywords used to match persisted bundle filenames to canonical names.
_BUNDLE_KEYWORDS: dict[str, list[str]] = {
    "Popularity": ["popularity", "popular"],
    "Content": ["content"],
    "User-Based CF": ["user_based", "usercf", "user-based", "user"],
    "Item-Based CF": ["item_based", "itemcf", "item-based", "item"],
    "Hybrid": ["hybrid"],
}


# ---------------------------------------------------------------------------
# Loading / fitting
# ---------------------------------------------------------------------------


def _discover_bundle_files() -> dict[str, Path]:
    """Map canonical model name -> matching bundle file in models/."""
    found: dict[str, Path] = {}
    if not MODELS_DIR.exists():
        return found
    for path in sorted(MODELS_DIR.iterdir()):
        if path.suffix.lower() not in (".pkl", ".pickle", ".bundle", ".p"):
            continue
        stem = path.stem.lower()
        for name, keywords in _BUNDLE_KEYWORDS.items():
            if name in found:
                continue
            if any(keyword in stem for keyword in keywords):
                found[name] = path
                break
    return found


def _is_recommender(obj: Any) -> bool:
    """Best-effort check that an object satisfies the Recommender protocol."""
    return hasattr(obj, "recommend") and callable(getattr(obj, "recommend", None))


def _try_load_bundle(path: Path) -> Any | None:
    """Load a persisted model bundle; returns None when incompatible."""
    try:
        bundle = load_model_bundle(path)
        model = getattr(bundle, "model", None)
        if _is_recommender(model):
            return model
    except Exception:
        pass
    # Fallback: raw pickled artifact (bundle dict or model object).
    try:
        obj = load_artifact(path)
    except Exception:
        return None
    if _is_recommender(obj):
        return obj
    return None


def _fit_model(name: str, train: Any, movies: Any) -> Any:
    """Fit a model on the train split (fallback when no bundle is available)."""
    if name == "Popularity":
        return PopularityModel().fit(train)
    if name == "Content":
        return ContentModel().fit(train, movies)
    # Note: the CF and Hybrid fit() methods return None (not self), so the
    # model instance must be returned explicitly rather than chaining.
    if name == "User-Based CF":
        user_cf_model: Any = UserBasedCF()
        user_cf_model.fit(train)
        return user_cf_model
    if name == "Item-Based CF":
        item_cf_model: Any = ItemBasedCF()
        item_cf_model.fit(train)
        return item_cf_model
    if name == "Hybrid":
        hybrid_model: Any = HybridRecommender(alpha=0.5)
        hybrid_model.fit(train, movies)
        return hybrid_model
    raise ValueError(f"Unknown model name: {name}")


@st.cache_resource(show_spinner=False)
def _get_model(name: str) -> tuple[Any, str]:
    """Load or fit one model, returning (model, provenance). Cached per run."""
    from ui.data_provider import load_movies, load_train

    bundle_files = _discover_bundle_files()
    if name in bundle_files:
        model = _try_load_bundle(bundle_files[name])
        if model is not None:
            return model, f"Loaded from {bundle_files[name].name}"

    train = load_train()
    movies = load_movies()
    model = _fit_model(name, train, movies)
    return model, "Fitted at startup on the train split"


class ModelManager:
    """Facade over the cached per-name model loaders."""

    def get_model(self, name: str) -> tuple[Any, str]:
        """Return (model, provenance) for a canonical model name."""
        if name not in MODEL_NAMES:
            raise ValueError(f"Unknown model name: {name}")
        return _get_model(name)

    def get_available_models(self) -> list[str]:
        """Canonical names of all five models selectable in the UI."""
        return list(MODEL_NAMES)

    def is_ready(self, model: Any) -> bool:
        """True when a model reports itself fitted/ready."""
        return bool(
            getattr(model, "is_fitted", None)
            or getattr(model, "fitted", None)
            or getattr(model, "is_ready", None)
        )

    def apply_params(self, model: Any, name: str, params: dict[str, Any]) -> None:
        """Apply live-adjustable model parameters (alpha / CF neighbourhood k)."""
        if name == "Hybrid" and hasattr(model, "alpha"):
            model.alpha = float(params.get("alpha", 0.5))
        elif name == "User-Based CF" and hasattr(model, "k_similar_users"):
            model.k_similar_users = int(params.get("k", 10))
        elif name == "Item-Based CF" and hasattr(model, "k_similar_items"):
            model.k_similar_items = int(params.get("k", 10))
