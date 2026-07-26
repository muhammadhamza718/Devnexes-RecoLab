"""Tests for recolab.persistence (REQ-012).

Covers save/load round-trips for generic artifacts and structured bundles,
plus explicit error handling for missing/corrupt files. Persistence is kept
generic: this module does NOT import baseline.py/metrics.py internals.
"""

from __future__ import annotations

import pathlib
from dataclasses import dataclass

import pytest

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


@dataclass
class _SampleModel:
    name: str
    weights: dict[str, float]
    top_items: list[int]


def _sample_model() -> _SampleModel:
    return _SampleModel(
        name="popularity_v1",
        weights={"a": 0.5, "b": 1.0, "c": -0.25},
        top_items=[1, 7, 42, 99],
    )


# --- Round-trip: generic object preserves state EXACTLY ----------------------


def test_save_load_roundtrip_dataclass(tmp_path: pathlib.Path) -> None:
    obj = _sample_model()
    path = tmp_path / "model.pkl"
    saved = save_artifact(obj, path)
    assert saved == path.resolve()
    loaded = load_artifact(path)
    assert loaded == obj
    assert loaded.name == "popularity_v1"
    assert loaded.weights == {"a": 0.5, "b": 1.0, "c": -0.25}
    assert loaded.top_items == [1, 7, 42, 99]


def test_save_load_roundtrip_nested_dict(tmp_path: pathlib.Path) -> None:
    obj = {
        "popularity": {"1": 12, "2": 9},
        "params": {"k": 5, "seed": 42},
        "nested": {"deep": {"vals": [1, 2, 3]}},
    }
    path = tmp_path / "dict.pkl"
    save_artifact(obj, path)
    loaded = load_artifact(path)
    assert loaded == obj


# --- Resolved-vs-relative path convention ------------------------------------


def test_relative_path_resolves_into_models_dir(tmp_path: pathlib.Path) -> None:
    # A relative name must land inside the given root's models/ directory.
    saved = save_artifact(_sample_model(), "artifacts/model.pkl", root=tmp_path)
    expected = (tmp_path / MODELS_DIRNAME / "model.pkl").resolve()
    assert saved == expected
    assert expected.exists()
    # And reloading with the same relative name + root works.
    loaded = load_artifact("artifacts/model.pkl", root=tmp_path)
    assert loaded == _sample_model()


# --- Error handling: no silent failures --------------------------------------


def test_load_missing_file_raises(tmp_path: pathlib.Path) -> None:
    with pytest.raises(PersistError, match="not found"):
        load_artifact(tmp_path / "does_not_exist.pkl")


def test_load_corrupt_file_raises(tmp_path: pathlib.Path) -> None:
    bad = tmp_path / "corrupt.pkl"
    bad.write_bytes(b"\x80\x05not a valid pickle stream??????")
    with pytest.raises(PersistError, match="corrupt"):
        load_artifact(bad)


def test_save_rejects_directory_path(tmp_path: pathlib.Path) -> None:
    with pytest.raises(PersistError):
        save_artifact(_sample_model(), tmp_path)  # tmp_path is a directory


# --- Bundle: model + metrics + metadata --------------------------------------


def test_bundle_roundtrip_preserves_nested_structure(tmp_path: pathlib.Path) -> None:
    bundle = ModelBundle(
        model=_sample_model(),
        metrics={
            "precision@5": 0.123,
            "recall@5": 0.087,
            "per_user": {"u1": 0.2, "u2": 0.0},
        },
        metadata={
            "version": "1.0.0",
            "trained_on": "train.csv",
            "params": {"weight_by_rating": True, "seed": 42},
        },
    )
    path = tmp_path / "bundle.pkl"
    save_model_bundle(bundle, path)
    loaded = load_model_bundle(path)

    assert isinstance(loaded, ModelBundle)
    assert loaded.model == bundle.model
    assert loaded.metrics == bundle.metrics
    assert loaded.metadata == bundle.metadata
    # Deep equality, including nested dicts inside metrics/metadata.
    assert loaded.metrics["per_user"] == {"u1": 0.2, "u2": 0.0}
    assert loaded.metadata["params"]["seed"] == 42


def test_load_artifact_into_bundle_type_mismatch_raises(tmp_path: pathlib.Path) -> None:
    # Persist a plain dict, then try to read it as a bundle.
    save_artifact({"not": "a bundle"}, tmp_path / "plain.pkl")
    with pytest.raises(PersistError, match="not a ModelBundle"):
        load_model_bundle(tmp_path / "plain.pkl")


def test_save_model_bundle_rejects_non_bundle(tmp_path: pathlib.Path) -> None:
    with pytest.raises(PersistError):
        save_model_bundle({"model": "x"}, tmp_path / "bad.pkl")  # type: ignore[arg-type]


def test_artifact_protocol_is_stable() -> None:
    # Documented contract: we always write with protocol 5.
    assert ARTIFACT_PROTOCOL == 5
