# API Reference: Persistence & Data Splitting (`src/recolab/`)

## 1. Model Persistence (`src/recolab/persistence.py`)

### `ModelBundle` (Dataclass)
Container dataclass for atomic model state serialization.

```python
@dataclass
class ModelBundle:
    model_type: str
    version: str
    metadata: Dict[str, Any]
    artifacts: Dict[str, Any]
```

### `save_bundle(bundle: ModelBundle, filepath: str) -> None`
Serializes `ModelBundle` to disk using pickle protocol 5.

### `load_bundle(filepath: str) -> ModelBundle`
Deserializes `ModelBundle` from disk file path.

---

## 2. Data Splitting (`src/recolab/split.py`)

### `train_test_split_by_user(ratings_df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42) -> Tuple[pd.DataFrame, pd.DataFrame]`
Performs user-based temporal/stratified split, holding back `test_size` fraction of latest ratings per user for the test set while ensuring every user in test set has training history.
