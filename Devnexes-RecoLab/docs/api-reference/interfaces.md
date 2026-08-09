# API Reference: Core Interfaces & Protocols

## 1. Protocol Definitions (`src/recolab/interfaces.py`)

### `Recommender` (Protocol)
The baseline runtime protocol implemented by all recommendation models in RecoLab.

```python
from typing import Protocol, List, Tuple, Optional, Dict, Any
import pandas as pd

class Recommender(Protocol):
    """Duck-typed runtime protocol for recommendation models."""
    
    def fit(self, ratings_df: pd.DataFrame, movies_df: Optional[pd.DataFrame] = None) -> "Recommender":
        """Train recommendation model on interaction dataset."""
        ...
        
    def recommend(
        self, 
        user_id: int, 
        k: int = 10, 
        exclude_items: Optional[List[int]] = None
    ) -> List[Tuple[int, float]]:
        """Generate top-K recommended (movieId, score) pairs for target user."""
        ...

    def explain(self, user_id: int, movie_id: int) -> Dict[str, Any]:
        """Generate human-readable explanation payload for recommendation."""
        ...
```

---

### `ColdStartHandler` (Protocol)
Protocol for models capable of generating recommendations for unprofiled or low-interaction users based on explicit preference inputs.

```python
class ColdStartHandler(Protocol):
    """Protocol for models capable of handling cold-start preference inputs."""
    
    def recommend_cold_start(
        self, 
        genres: List[str], 
        liked_movie_ids: Optional[List[int]] = None, 
        k: int = 10
    ) -> List[Tuple[int, float]]:
        """Generate recommendations for new user based on preferred genres/movies."""
        ...
```

---

## 2. Exceptions

### `FeatureError`
Raised when requested item or feature vector is missing from feature matrix.

```python
class FeatureError(Exception):
    """Raised when item or feature is absent from model matrix."""
    def __init__(self, message: str, movie_id: Optional[int] = None):
        super().__init__(message)
        self.movie_id = movie_id
```
