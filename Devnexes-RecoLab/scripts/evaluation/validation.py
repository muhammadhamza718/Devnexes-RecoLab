"""Data and parameter validation for evaluation framework.

Validates test data, model availability, and evaluation parameters before
running evaluation to fail fast with clear error messages.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import pandas as pd

from config import (
    K_VALUES,
    MODEL_NAMES,
    MOVIES_CSV,
    TEST_CSV,
    TRAIN_CSV,
)


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, message: str, details: list[str] | None = None) -> None:
        super().__init__(message)
        self.details = details or []


def validate_test_data(test_path: Path | None = None) -> pd.DataFrame:
    """Validate test dataset structure and load it.

    Args:
        test_path: Path to test CSV (defaults to TEST_CSV).

    Returns:
        Loaded test DataFrame.

    Raises:
        ValidationError: If validation fails.
    """
    path = test_path or TEST_CSV
    errors: list[str] = []

    if not path.exists():
        raise ValidationError(f"Test data not found: {path}")

    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise ValidationError(f"Failed to load test data: {e}")

    # Check required columns
    required = {"userId", "movieId", "rating"}
    missing = required - set(df.columns)
    if missing:
        errors.append(f"Missing columns: {missing}")

    # Check for empty data
    if df.empty:
        errors.append("Test data is empty")

    # Check for null values in key columns
    for col in ["userId", "movieId", "rating"]:
        if col in df.columns and df[col].isna().any():
            errors.append(f"Null values found in column: {col}")

    if errors:
        raise ValidationError("Test data validation failed", errors)

    return df


def validate_train_data(train_path: Path | None = None) -> pd.DataFrame:
    """Validate train dataset structure and load it.

    Args:
        train_path: Path to train CSV (defaults to TRAIN_CSV).

    Returns:
        Loaded train DataFrame.

    Raises:
        ValidationError: If validation fails.
    """
    path = train_path or TRAIN_CSV
    errors: list[str] = []

    if not path.exists():
        raise ValidationError(f"Train data not found: {path}")

    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise ValidationError(f"Failed to load train data: {e}")

    # Check required columns
    required = {"userId", "movieId", "rating"}
    missing = required - set(df.columns)
    if missing:
        errors.append(f"Missing columns: {missing}")

    # Check for empty data
    if df.empty:
        errors.append("Train data is empty")

    if errors:
        raise ValidationError("Train data validation failed", errors)

    return df


def validate_movies_data(movies_path: Path | None = None) -> pd.DataFrame:
    """Validate movies catalog structure and load it.

    Args:
        movies_path: Path to movies CSV (defaults to MOVIES_CSV).

    Returns:
        Loaded movies DataFrame.

    Raises:
        ValidationError: If validation fails.
    """
    path = movies_path or MOVIES_CSV
    errors: list[str] = []

    if not path.exists():
        raise ValidationError(f"Movies data not found: {path}")

    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise ValidationError(f"Failed to load movies data: {e}")

    # Check required columns
    required = {"movieId", "title", "genres"}
    missing = required - set(df.columns)
    if missing:
        errors.append(f"Missing columns: {missing}")

    if errors:
        raise ValidationError("Movies data validation failed", errors)

    return df


def validate_model_availability(
    model_manager: Any,
    model_names: list[str] | None = None,
) -> list[str]:
    """Check which models are available for evaluation.

    Args:
        model_manager: ModelManager instance.
        model_names: List of model names to check (defaults to MODEL_NAMES).

    Returns:
        List of available model names.

    Raises:
        ValidationError: If no models are available.
    """
    names = model_names or MODEL_NAMES
    available: list[str] = []

    for name in names:
        try:
            model, _ = model_manager.get_model(name)
            if model is not None and hasattr(model, "recommend"):
                available.append(name)
        except Exception:
            continue

    if not available:
        raise ValidationError(
            "No models available for evaluation",
            [f"Checked: {names}"],
        )

    return available


def validate_evaluation_parameters(
    k_values: list[int] | None = None,
) -> list[int]:
    """Validate evaluation parameters.

    Args:
        k_values: List of K values (defaults to K_VALUES).

    Returns:
        Validated K values.

    Raises:
        ValidationError: If validation fails.
    """
    ks = k_values or K_VALUES
    errors: list[str] = []

    if not ks:
        errors.append("K values list is empty")

    for k in ks:
        if not isinstance(k, int):
            errors.append(f"Invalid K value type: {k} ({type(k)})")
        elif k <= 0:
            errors.append(f"K value must be positive: {k}")

    if errors:
        raise ValidationError("Parameter validation failed", errors)

    return ks


def validate_result_format(results: dict[str, Any]) -> list[str]:
    """Validate evaluation result format.

    Args:
        results: Evaluation results dict.

    Returns:
        List of validation errors (empty if valid).
    """
    errors: list[str] = []

    if not isinstance(results, dict):
        return [f"Results must be dict, got {type(results)}"]

    # Check for required keys
    if "model_name" not in results:
        errors.append("Missing 'model_name' in results")

    # Check metric values
    for key, value in results.items():
        if key.startswith("mean_") and isinstance(value, (int, float)):
            if not (0.0 <= value <= 1.0):
                errors.append(f"Metric {key} out of range [0,1]: {value}")

    return errors


__all__ = [
    "ValidationError",
    "validate_test_data",
    "validate_train_data",
    "validate_movies_data",
    "validate_model_availability",
    "validate_evaluation_parameters",
    "validate_result_format",
]
