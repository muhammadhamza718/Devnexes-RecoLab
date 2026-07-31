# Quickstart Guide: Hybrid Recommendation Framework

**Feature**: 003-hybrid-framework  
**Date**: 2026-07-30  
**Purpose**: Development setup and initial implementation guidance

---

## Prerequisites

### Environment Setup

**Required Dependencies**:
```bash
# Core dependencies (already installed from Week 1-2 and Day 1)
# No new dependencies required for hybrid framework
# Existing models provide all needed functionality
```

**Model Requirements**:
- ContentModel from Week 2 work (content-based recommendations)
- UserBasedCF from Day 1 work (user-based collaborative filtering)
- ItemBasedCF from Day 1 work (item-based collaborative filtering)
- All models must satisfy Recommender protocol
- ContentModel must satisfy ColdStartHandler protocol

**Data Requirements**:
- MovieLens small dataset (ml-latest-small)
- Training data in expected format: user_id, movie_id, rating columns
- Movies data with genre information for content-based fallback

### Development Environment

**Virtual Environment**:
```bash
# Activate existing virtual environment
cd F:\Courses\Hamza\Devnexes-Internship-Projects
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate  # Windows
```

**Project Structure**:
```bash
# Verify existing structure
ls src/recolab/
# Expected: content.py, collaborative.py, interfaces.py, __init__.py
ls tests/
# Expected: fixtures/, test_collaborative.py, test_content.py, etc.
```

---

## Initial Implementation Steps

### Step 1: Create File Structure

```bash
# Create new hybrid.py file
touch src/recolab/hybrid.py

# Create test file
touch tests/test_hybrid.py
```

### Step 2: Implement Basic HybridRecommender Skeleton

```python
# src/recolab/hybrid.py
from typing import List, Optional, Dict, Set, Any
import pandas as pd
import numpy as np

from recolab.content import ContentModel
from recolab.collaborative import UserBasedCF, ItemBasedCF
from recolab.interfaces import Recommender, ColdStartHandler

class HybridRecommender(Recommender, ColdStartHandler):
    def __init__(
        self,
        alpha: float = 0.5,
        cold_start_threshold: int = 5,
        active_threshold: int = 20,
        content_model: Optional[ContentModel] = None,
        user_based_cf: Optional[UserBasedCF] = None,
        item_based_cf: Optional[ItemBasedCF] = None
    ) -> None:
        """Initialize hybrid recommender with configurable parameters"""
        self.alpha = alpha
        self.cold_start_threshold = cold_start_threshold
        self.active_threshold = active_threshold
        self.content_model = content_model
        self.user_based_cf = user_based_cf
        self.item_based_cf = item_based_cf
        self.normalization_params = {}
        self.model_selection_log = []
        self.is_fitted = False
    
    def fit(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame) -> None:
        """Train all underlying models on provided data"""
        pass  # Implementation to follow
    
    def recommend(
        self,
        user_id: int,
        k: int,
        exclude_items: Optional[Set[int]] = None
    ) -> List[int]:
        """Generate recommendations using adaptive model selection"""
        pass  # Implementation to follow
    
    def recommend_cold_start(
        self,
        genres: List[str],
        liked_movie_ids: List[int],
        k: int
    ) -> List[int]:
        """Generate recommendations for cold-start users"""
        pass  # Implementation to follow
    
    def get_confidence(self, user_id: int, movie_id: int) -> float:
        """Return confidence score for a specific recommendation"""
        pass  # Implementation to follow
    
    def get_model_selection_info(self, user_id: int) -> Dict[str, Any]:
        """Return information about which model was selected and why"""
        pass  # Implementation to follow
```

### Step 3: Write First Test

```python
# tests/test_hybrid.py
import pytest
import pandas as pd
import numpy as np
from src.recolab.hybrid import HybridRecommender
from src.recolab.content import ContentModel
from src.recolab.collaborative import UserBasedCF, ItemBasedCF

@pytest.fixture
def sample_ratings() -> pd.DataFrame:
    """Sample ratings DataFrame for testing"""
    return pd.DataFrame({
        "userId": [1, 1, 1, 2, 2, 2, 3, 3, 3, 4, 4],
        "movieId": [10, 20, 30, 10, 20, 40, 20, 30, 40, 50, 60],
        "rating": [5.0, 4.0, 3.0, 5.0, 4.0, 2.0, 4.0, 3.0, 5.0, 5.0, 4.0],
        "timestamp": [1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007, 1008, 1009, 1010],
    })

@pytest.fixture
def sample_movies() -> pd.DataFrame:
    """Sample movies DataFrame for testing"""
    return pd.DataFrame({
        "movieId": [10, 20, 30, 40, 50, 60],
        "title": ["Movie A", "Movie B", "Movie C", "Movie D", "Movie E", "Movie F"],
        "genres": ["Action", "Action|Sci-Fi", "Drama", "Action|Comedy", "Drama", "Sci-Fi"],
    })

class TestHybridRecommenderInitialization:
    """Test hybrid recommender initialization and parameter validation"""
    
    def test_default_initialization(self):
        """Verify default parameters and initial state"""
        hybrid = HybridRecommender()
        assert hybrid.alpha == 0.5
        assert hybrid.cold_start_threshold == 5
        assert hybrid.active_threshold == 20
        assert hybrid.is_fitted is False
    
    def test_custom_initialization(self):
        """Verify custom parameter values"""
        hybrid = HybridRecommender(alpha=0.7, cold_start_threshold=3, active_threshold=15)
        assert hybrid.alpha == 0.7
        assert hybrid.cold_start_threshold == 3
        assert hybrid.active_threshold == 15
```

### Step 4: Run Initial Test

```bash
# Run the first test to verify setup
pytest tests/test_hybrid.py::TestHybridRecommenderInitialization::test_default_initialization -v
```

---

## Development Workflow

### Phase 1: Core Implementation

1. **Implement Model Selection Logic**
   - Add user activity evaluation
   - Implement adaptive selection based on rating count
   - Add selection logging

2. **Implement Score Combination**
   - Add normalization functions
   - Implement weighted averaging with alpha parameter
   - Handle missing scores gracefully

3. **Implement Confidence Scoring**
   - Add activity confidence computation
   - Add popularity confidence computation
   - Add model agreement confidence
   - Combine into composite confidence score

### Phase 2: Integration

1. **Integrate Existing Models**
   - Load ContentModel, UserBasedCF, ItemBasedCF
   - Train all models on same data
   - Compute normalization parameters

2. **Implement Fallback Chain**
   - Add fallback logic for model failures
   - Implement fallback chain ordering
   - Add fallback event logging

3. **Protocol Compliance**
   - Verify Recommender protocol compliance
   - Verify ColdStartHandler protocol compliance
   - Test both recommend methods

### Phase 3: Testing

1. **Unit Tests**
   - Score combination tests
   - Model selection tests
   - Confidence scoring tests
   - Fallback chain tests

2. **Integration Tests**
   - End-to-end recommendation flow
   - Protocol compliance verification
   - Multi-model coordination tests

3. **Performance Tests**
   - Latency benchmarks (<100ms target)
   - Memory usage monitoring
   - Model selection overhead measurement

---

## Common Patterns

### Model Selection Pattern

```python
def _select_model(self, user_id: int) -> str:
    """Select optimal model based on user activity level"""
    rating_count = self._get_user_rating_count(user_id)
    
    if rating_count <= self.cold_start_threshold:
        return "content"
    elif rating_count >= self.active_threshold:
        return "collaborative"  # or user-based/item-based
    else:
        return "hybrid"
```

### Score Combination Pattern

```python
def _combine_scores(
    self,
    content_scores: Dict[int, float],
    collaborative_scores: Dict[int, float]
) -> Dict[int, float]:
    """Combine normalized scores using weighted averaging"""
    combined = {}
    
    for item_id in set(content_scores.keys()) | set(collaborative_scores.keys()):
        content_score = content_scores.get(item_id, 0.0)
        collab_score = collaborative_scores.get(item_id, 0.0)
        
        combined[item_id] = (
            self.alpha * content_score + 
            (1 - self.alpha) * collab_score
        )
    
    return combined
```

### Confidence Scoring Pattern

```python
def _compute_confidence(
    self,
    user_id: int,
    movie_id: int,
    activity_level: int
) -> float:
    """Compute composite confidence score"""
    activity_conf = self._compute_activity_confidence(activity_level)
    popularity_conf = self._compute_popularity_confidence(movie_id)
    agreement_conf = self._compute_agreement_confidence(user_id, movie_id)
    
    return (
        0.4 * activity_conf +
        0.3 * popularity_conf +
        0.3 * agreement_conf
    )
```

---

## Testing Checklist

### Unit Tests
- [ ] Initialization tests (default and custom parameters)
- [ ] Model selection tests (cold-start, intermediate, active users)
- [ ] Score combination tests (normalization, weighted averaging)
- [ ] Confidence scoring tests (activity, popularity, agreement)
- [ ] Fallback chain tests (model failures, graceful degradation)

### Integration Tests
- [ ] End-to-end recommendation flow
- [ ] Protocol compliance (Recommender, ColdStartHandler)
- [ ] Multi-model coordination
- [ ] Existing model integration (ContentModel, UserBasedCF, ItemBasedCF)

### Performance Tests
- [ ] Recommendation latency <100ms
- [ ] Model selection overhead <10ms
- [ ] Confidence computation overhead <5ms
- [ ] Memory usage within limits

---

## Troubleshooting

### Common Issues

**Import Errors**: Ensure all existing models are properly exported in `__init__.py`

**Model Training Failures**: Verify all models can be trained on the same data split

**Normalization Issues**: Check that score ranges are consistent across models

**Performance Degradation**: Profile score combination operations and optimize hot paths

**Fallback Loops**: Ensure fallback limit prevents infinite retry loops

### Debugging Tips

1. **Enable Model Selection Logging**: Check which model is selected for different users
2. **Score Inspection**: Examine normalized scores before and after combination
3. **Confidence Analysis**: Verify confidence scores reflect expected factors
4. **Fallback Monitoring**: Track fallback frequency and reasons

---

## Next Steps

1. Complete the implementation following the task breakdown in tasks.md
2. Run comprehensive test suite to verify all functionality
3. Perform IVP validation to ensure quality standards
4. Update README.md with hybrid framework information
5. Proceed to Day 2 afternoon work (advanced cold-start and parameter tuning)