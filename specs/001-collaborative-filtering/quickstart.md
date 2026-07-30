# Quickstart Guide: Item-Based Collaborative Filtering

**Feature**: 001-collaborative-filtering  
**Date**: 2026-07-29  
**Purpose**: Development setup and initial implementation guidance

---

## Prerequisites

### Environment Setup

**Required Dependencies**:
```bash
# Core dependencies (already installed from Week 1-2)
scipy>=1.11.0
scikit-learn>=1.3.0
pandas>=2.0.0
numpy>=1.24.0
pytest>=7.4.0
```

**Data Requirements**:
- MovieLens small dataset (ml-latest-small)
- Training data in expected format: user_id, movie_id, rating columns
- Existing ContentModel from Week 2 work

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
# Expected: content.py, interfaces.py, __init__.py
ls tests/
# Expected: fixtures/ and existing test files
```

---

## Initial Implementation Steps

### Step 1: Create File Structure

```bash
# Create new collaborative.py file
touch src/recolab/collaborative.py

# Create test file
touch tests/test_collaborative.py
```

### Step 2: Implement Basic ItemBasedCF Skeleton

```python
# src/recolab/collaborative.py
from typing import List, Optional, Dict
import scipy.sparse as sp
from sklearn.metrics.pairwise import cosine_similarity
import pandas as pd
import numpy as np

class ItemBasedCF:
    def __init__(self, k_similar_items: int = 50, min_similarity: float = 0.1):
        self.k_similar_items = k_similar_items
        self.min_similarity = min_similarity
        self.item_item_matrix = None
        self.user_item_matrix = None
        self.user_mapping = {}
        self.movie_mapping = {}
        self.reverse_user_mapping = {}
        self.reverse_movie_mapping = {}
        self.is_fitted = False
    
    def fit(self, ratings_df: pd.DataFrame) -> None:
        """Train model on rating data"""
        pass  # Implementation to follow
    
    def recommend(self, user_id: int, k: int, exclude_items: Optional[List[int]] = None) -> List[int]:
        """Generate recommendations for user"""
        pass  # Implementation to follow
```

### Step 3: Write First Test

```python
# tests/test_collaborative.py
import pytest
import pandas as pd
import numpy as np
from src.recolab.collaborative import ItemBasedCF

def test_item_based_cf_initialization():
    """Test that ItemBasedCF initializes correctly"""
    model = ItemBasedCF(k_similar_items=50, min_similarity=0.1)
    assert model.k_similar_items == 50
    assert model.min_similarity == 0.1
    assert model.is_fitted == False
```

### Step 4: Run Initial Test

```bash
# Run the test to verify setup
pytest tests/test_collaborative.py::test_item_based_cf_initialization -v
```

---

## Implementation Priority

### Phase 1: Matrix Building (Priority: P1)

**Tasks**:
1. Implement `_build_user_item_matrix()` method
2. Create user and movie index mappings
3. Handle missing values as zeros
4. Write matrix building tests

**Acceptance Criteria**:
- ✅ Matrix shape matches (n_users, n_items)
- ✅ Sparse format (CSR) used
- ✅ Mappings are consistent with matrix dimensions
- ✅ Tests pass for various input sizes

### Phase 2: Similarity Computation (Priority: P1)

**Tasks**:
1. Implement `_compute_item_similarity()` method
2. Use sklearn cosine_similarity with normalization
3. Store item-item similarity matrix efficiently
4. Write similarity computation tests

**Acceptance Criteria**:
- ✅ Similarity matrix shape matches (n_items, n_items)
- ✅ Diagonal values equal 1.0
- ✅ Similarity scores in range [-1, 1]
- ✅ Computation time <5 seconds for target dataset

### Phase 3: Recommendation Logic (Priority: P1)

**Tasks**:
1. Implement `_find_similar_items()` method
2. Implement `_aggregate_predictions()` method
3. Implement main `recommend()` method
4. Add consumed-item filtering
5. Write recommendation tests

**Acceptance Criteria**:
- ✅ Returns exactly k recommendations (or fewer)
- ✅ Excludes already-rated items
- ✅ Respects exclude_items parameter
- ✅ Recommendation time <100ms

### Phase 4: New-Item Handling (Priority: P2)

**Tasks**:
1. Implement `_is_new_item()` method
2. Integrate ContentModel fallback for new items
3. Write new-item scenario tests
4. Test fallback behavior

**Acceptance Criteria**:
- ✅ New items use content-based similarity
- ✅ No crashes for items with 0 ratings
- ✅ Seamless fallback with same interface

---

## Development Workflow

### Test-Driven Development Cycle

1. **Write Test**: Create failing test for specific functionality
2. **Run Test**: Confirm test fails
3. **Implement**: Write minimal code to pass test
4. **Run Test**: Confirm test passes
5. **Refactor**: Improve code while keeping tests passing
6. **Repeat**: Move to next functionality

### Continuous Testing

```bash
# Run all collaborative filtering tests
pytest tests/test_collaborative.py -v

# Run with coverage
pytest tests/test_collaborative.py --cov=src/recolab/collaborative --cov-report=term-missing

# Run specific test file
pytest tests/test_collaborative.py::test_matrix_building -v
```

### Integration Testing

```bash
# Test integration with existing ContentModel
pytest tests/test_collaborative.py::test_cold_start_fallback -v

# Test integration with evaluation framework
pytest tests/test_collaborative.py::test_evaluation_integration -v
```

---

## Common Issues and Solutions

### Issue 1: Memory Errors

**Symptom**: MemoryError during matrix building

**Solution**:
- Verify using sparse matrices (CSR format)
- Check dataset size is within limits
- Consider subset for testing

### Issue 2: Slow Similarity Computation

**Symptom**: Similarity computation takes >5 seconds

**Solution**:
- Verify using sklearn cosine_similarity
- Check if vectors are normalized
- Profile to identify bottlenecks

### Issue 3: Invalid User IDs

**Symptom**: KeyError for user_id not in training data

**Solution**:
- Implement proper error handling
- Add validation in recommend() method
- Provide helpful error messages

### Issue 4: Poor New-Item Quality

**Symptom**: New-item recommendations seem low quality

**Solution**:
- Verify ContentModel integration
- Check new-item threshold (0 ratings)
- Document limitations (temporary until hybrid)

---

## Performance Benchmarks

### Target Performance

- **Matrix Building**: <1 second for MovieLens small
- **Similarity Computation**: <5 seconds for MovieLens small
- **Recommendation Generation**: <100ms per request
- **Memory Usage**: <100MB for matrices

### Performance Testing

```bash
# Run performance tests
pytest tests/test_collaborative.py::test_performance -v

# Profile memory usage
python -m memory_profiler tests/test_collaborative.py::test_memory_usage
```

---

## Next Steps

### Immediate Actions

1. ✅ Create file structure (collaborative.py, test_collaborative.py)
2. ✅ Implement basic ItemBasedCF skeleton
3. ✅ Write first initialization test
4. ⏳ Implement matrix building with tests
5. ⏳ Implement similarity computation with tests
6. ⏳ Implement recommendation logic with tests
7. ⏳ Add new-item handling with tests
8. ⏳ Integrate with ContentModel and evaluation framework

### Validation Gates

- **Gate 1**: Matrix building complete with ≥3 passing tests
- **Gate 2**: Similarity computation complete with ≥3 passing tests
- **Gate 3**: Recommendation logic complete with ≥5 passing tests
- **Gate 4**: New-item handling complete with ≥4 passing tests
- **Final Gate**: ≥15 total tests, ≥70% coverage, integration verified

---

## Support and Resources

### Documentation

- scipy.sparse documentation: https://docs.scipy.org/doc/scipy/reference/sparse.html
- sklearn cosine_similarity: https://scikit-learn.org/stable/modules/generated/sklearn.metrics.pairwise.cosine_similarity.html
- Existing ContentModel: src/recolab/content.py
- Existing evaluation framework: Week 1 work

### Troubleshooting

- Check existing Week 2 ContentModel for integration patterns
- Review Week 1 evaluation framework for testing approach
- Consult constitution.md for coding standards
- Use pytest -v for detailed test output