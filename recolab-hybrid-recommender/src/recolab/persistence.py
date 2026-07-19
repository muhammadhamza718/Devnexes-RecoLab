"""Model artifact persistence for RecoLab (REQ-012).

Provides a small, typed serialization layer built on :mod:`pickle` so that
trained model artifacts (popularity tables, fitted arrays, metric bundles)
can be saved and reloaded **exactly** for reproducible evaluation.

Design notes
------------
* Protocol 5 is used for all writes (supports out-of-band buffers / large
  NumPy arrays while staying broadly readable back to Python 3.8+).
* All path inputs are validated up front; missing or corrupt files raise a
  clear, dedicated :class:`PersistError` rather than letting a raw
  ``FileNotFoundError`` / ``EOFError`` escape. No silent failures.
* The module is fully deterministic and import-clean: it depends only on the
  standard library, so it loads alongside ``split.py`` / ``baseline.py`` /
  ``metrics.py`` without import-order issues.
"""

from __future__ import annotations

import pathlib
import pickle
from dataclasses import dataclass, field
from typing import Any

# Stable, broadly-compatible pickle protocol. Protocol 5 adds support for
# out-of-band buffers (large NumPy arrays) without sacrificing readability.
ARTIFACT_PROTOCOL: int = 5

# Fixed artifact directory, relative to the project root (the
# recolab-hybrid-recommender/ folder that contains ``src/``).
MODELS_DIRNAME: str = "models"


class PersistError(Exception):
    """Raised for any artifact save/load failure (missing or corrupt file)."""


def _resolve_path(path: str | pathlib.Path) -> pathlib.Path:
    """Coerce *path* to a :class:`pathlib.Path` and reject non-files safely.

    Args:
        path: A file path (str or Path). Directories are not valid targets.

    Returns:
        The resolved :class:`pathlib.Path`.

    Raises:
        PersistError: If *path* is not a usable file path.
    """
    try:
        resolved = pathlib.Path(path)
    except (TypeError, ValueError) as exc:
        raise PersistError(f"Invalid artifact path: {path!r}") from exc
    if resolved.is_dir():
        raise PersistError(f"Artifact path is a directory, not a file: {resolved}")
    return resolved


def _models_dir(root: str | pathlib.Path | None = None) -> pathlib.Path:
    """Return the project ``models/`` directory, creating it if needed.

    Args:
        root: Optional project root. When ``None``, the directory is resolved
            relative to this file's grandparent (``recolab-hybrid-recommender/``).

    Returns:
        Absolute path to the ``models/`` directory.
    """
    if root is None:
        base = pathlib.Path(__file__).resolve().parents[2]
    else:
        # Env vars / user expansion for robustness in scripts.
        base = pathlib.Path(str(root)).expanduser().resolve()
    models_dir = base / MODELS_DIRNAME
    models_dir.mkdir(parents=True, exist_ok=True)
    return models_dir


def save_artifact(
    obj: Any,
    path: str | pathlib.Path,
    *,
    root: str | pathlib.Path | None = None,
) -> pathlib.Path:
    """Pickle *obj* to *path* and return the written path.

    Args:
        obj: Any picklable object (model, DataFrame, array, dict, dataclass).
        path: Destination file path. If it is not already absolute and a
            *root* is supplied (or the project models dir is implied), it is
            written inside the fixed ``models/`` convention.
        root: Optional explicit project root. When omitted, a relative *path*
            is resolved against the project ``models/`` directory.

    Returns:
        The absolute :class:`pathlib.Path` the artifact was written to.

    Raises:
        PersistError: On an invalid path or a serialization failure.
    """
    if root is not None or not pathlib.PurePath(path).is_absolute():
        target = _models_dir(root) / pathlib.PurePath(path).name
    else:
        target = _resolve_path(path)

    if target.is_dir():
        raise PersistError(f"Artifact path is a directory, not a file: {target}")

    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("wb") as fh:
            pickle.dump(obj, fh, protocol=ARTIFACT_PROTOCOL)
    except (OSError, pickle.PickleError) as exc:
        raise PersistError(f"Failed to save artifact to {target}: {exc}") from exc
    return target.resolve()


def load_artifact(
    path: str | pathlib.Path,
    *,
    root: str | pathlib.Path | None = None,
) -> Any:
    """Unpickle and return the object stored at *path*.

    Args:
        path: File path written by :func:`save_artifact`.
        root: Optional explicit project root used to resolve a relative path.

    Returns:
        The reconstructed object, exactly as serialized.

    Raises:
        PersistError: If the file is missing, is not a regular file, or cannot
            be unpickled (corrupt/truncated payload).
    """
    if root is not None:
        target = _models_dir(root) / pathlib.PurePath(path).name
    else:
        target = _resolve_path(path)

    if not target.exists():
        raise PersistError(f"Artifact not found: {target}")
    if not target.is_file():
        raise PersistError(f"Artifact path is not a file: {target}")

    try:
        with target.open("rb") as fh:
            return pickle.load(fh)
    except (pickle.UnpicklingError, EOFError, OSError) as exc:
        msg = f"Failed to load artifact from {target}: corrupt file"
        raise PersistError(msg) from exc


@dataclass(slots=True)
class ModelBundle:
    """Structured, self-describing container persisted as one file.

    Attributes:
        model: The trained model artifact (any picklable object).
        metrics: Evaluation metrics (e.g., ``{"precision@5": 0.12}``).
        metadata: Free-form reproducibility metadata (params, versions, seeds).
    """

    model: Any
    metrics: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


def save_model_bundle(
    bundle: ModelBundle,
    path: str | pathlib.Path,
    *,
    root: str | pathlib.Path | None = None,
) -> pathlib.Path:
    """Persist a :class:`ModelBundle` (model + metrics + metadata) in one file.

    Args:
        bundle: The bundle to persist.
        path: Destination file path (resolved via the ``models/`` convention
            for relative paths, like :func:`save_artifact`).
        root: Optional explicit project root.

    Returns:
        The absolute path the bundle was written to.

    Raises:
        PersistError: On invalid path or serialization failure.
    """
    if not isinstance(bundle, ModelBundle):
        raise PersistError(
            f"save_model_bundle expects a ModelBundle, got {type(bundle).__name__}"
        )
    return save_artifact(bundle, path, root=root)


def load_model_bundle(
    path: str | pathlib.Path,
    *,
    root: str | pathlib.Path | None = None,
) -> ModelBundle:
    """Load a :class:`ModelBundle` previously written by :func:`save_model_bundle`.

    Args:
        path: File path of the persisted bundle.
        root: Optional explicit project root.

    Returns:
        The reconstructed :class:`ModelBundle`.

    Raises:
        PersistError: If the file is missing, corrupt, or does not contain a
            :class:`ModelBundle` (wrong payload type).
    """
    loaded = load_artifact(path, root=root)
    if not isinstance(loaded, ModelBundle):
        raise PersistError(
            f"Artifact at {path} is not a ModelBundle "
            f"(got {type(loaded).__name__})"
        )
    return loaded


__all__ = [
    "ARTIFACT_PROTOCOL",
    "MODELS_DIRNAME",
    "PersistError",
    "ModelBundle",
    "save_artifact",
    "load_artifact",
    "save_model_bundle",
    "load_model_bundle",
]
