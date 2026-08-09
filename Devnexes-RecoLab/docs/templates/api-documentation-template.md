# API Reference: [Module Name]

## 1. Module Overview
- **Module Path**: `src/recolab/[module].py`
- **Description**: Summary of module responsibilities.

## 2. Class Definitions

### `[ClassName]`
```python
class ClassName(Recommender):
    """Short description of ClassName."""
```

#### Initialization Parameters
- `param1` (*type*): Description of param1. Default: `value`.

#### Public Methods

##### `fit(ratings_df: pd.DataFrame, movies_df: Optional[pd.DataFrame] = None) -> ClassName`
Trains model on input DataFrame.

##### `recommend(user_id: int, k: int = 10, exclude_items: Optional[List[int]] = None) -> List[Tuple[int, float]]`
Generates top-K recommendations for target user.

## 3. Exceptions & Error Handling
- `FeatureError`: Raised when...
