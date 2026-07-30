# Implementation Plan: Item-Based Collaborative Filtering

**Branch**: `001-collaborative-filtering` | **Date**: 2026-07-29 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/001-collaborative-filtering/spec.md`

## Summary

Implement item-based collaborative filtering for movie recommendations using cosine similarity on item-item rating matrices. The system will find similar items to the user's previously rated items, aggregate ratings from those similar items using weighted averages, handle new-item cold-start scenarios with content-based fallback, and integrate with the existing Recommender protocol and evaluation framework.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: scipy (sparse matrices), sklearn (cosine similarity), pandas (data manipulation), numpy (numerical operations)  
**Storage**: Sparse matrices (CSR format) + Model artifact persistence  
**Testing**: pytest with ≥70% coverage requirement  
**Target Platform**: Linux/Windows local development environment  
**Project Type**: Single project (Python recommendation system)  
**Performance Goals**: <100ms recommendation generation, <5s similarity computation  
**Constraints**: <100MB memory usage for matrices, existing ContentModel integration  
**Scale/Scope**: MovieLens small dataset (100k ratings, ~10k users, ~10k movies)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Quality-First Development**: ✅ PASS - Implementation will follow TDD with tests written before code
**Spec-Driven Development**: ✅ PASS - This plan follows approved specification  
**Blast-Radius Awareness**: ✅ PASS - New collaborative.py file, no existing code modifications  
**Security & Performance**: ✅ PASS - No security concerns, performance targets defined  
**Incremental Delivery**: ✅ PASS - Small, testable increments with clear acceptance criteria  
**IVP Validation**: ✅ PASS - Multi-perspective validation planned after each phase  
**Permission Gates**: ✅ PASS - User approval required before phase progression  

## Project Structure

### Documentation (this feature)

```text
specs/001-collaborative-filtering/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (research decisions)
├── data-model.md        # Phase 1 output (entity definitions)
├── quickstart.md        # Phase 1 output (development setup)
├── contracts/           # Phase 1 output (API contracts if needed)
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
src/recolab/
├── collaborative.py          # NEW: Item-based collaborative filtering
│   ├── ItemBasedCF            # Main class implementing Recommender protocol
│   ├── matrix_operations     # Utility functions for matrix building
│   └── similarity_compute   # Cosine similarity computation functions
├── content.py               # EXISTING: Content model (for new-item fallback)
├── interfaces.py            # EXISTING: Recommender protocol
└── __init__.py              # UPDATE: Export collaborative classes

tests/
├── test_collaborative.py     # NEW: Collaborative filtering tests
│   ├── test_matrix_ops      # Matrix building tests
│   ├── test_similarity      # Similarity computation tests
│   ├── test_recommendations # Recommendation logic tests
│   └── test_cold_start      # New-item fallback tests
└── fixtures/                # EXISTING: Test fixtures
```

**Structure Decision**: Single project structure following existing RecoLab patterns. New collaborative.py file alongside existing content.py, maintaining clean separation of concerns and following established architecture from Week 1-2 work.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

---

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **Sparse Matrix Implementation**: Research scipy sparse matrix formats (CSR vs CSC) for item-item matrices
2. **Cosine Similarity Optimization**: Research sklearn cosine_similarity performance characteristics and normalization requirements
3. **New-Item Detection**: Research best practices for new-item cold-start handling thresholds
4. **Integration Patterns**: Research existing ContentModel integration patterns from Week 2

### Technology Decisions

- **Sparse Matrix Format**: CSR (Compressed Sparse Row) - efficient for row operations (item-based similarity)
- **Similarity Computation**: sklearn.metrics.pairwise.cosine_similarity with L2 normalization
- **New-Item Threshold**: 0 ratings (industry standard for new-item detection)
- **K-Similar Items**: 50 (balance between relevance and performance)
- **Minimum Similarity**: 0.1 (filter out weak correlations)
- **Item Similarity Caching**: Cache top-K similar items for popular items to improve performance

---

## Phase 1: Design & Contracts

### Data Model

**ItemBasedCF Class**:
- `item_item_matrix`: scipy.sparse.csr_matrix - item-item similarity matrix
- `user_item_matrix`: scipy.sparse.csr_matrix - user ratings matrix
- `user_mapping`: dict - user_id to matrix index mapping
- `movie_mapping`: dict - movie_id to matrix column mapping
- `k_similar_items`: int - number of similar items to consider per rated item
- `min_similarity`: float - minimum similarity threshold

**Key Entities**:
- Item-Item Matrix: Sparse representation of item-item similarities
- User-Item Matrix: Sparse representation of user ratings
- Index Mappings: Efficient lookup between IDs and matrix indices

### API Contracts

**Recommender Protocol Compliance**:
```python
class Recommender(Protocol):
    def recommend(self, user_id: int, k: int, exclude_items: Optional[List[int]] = None) -> List[int]:
        """Return k movie IDs for user, excluding specified items"""
```

**ItemBasedCF Methods**:
- `fit(ratings_df: pd.DataFrame) -> None`: Train model on rating data
- `recommend(user_id: int, k: int, exclude_items: Optional[List[int]] = None) -> List[int]`: Generate recommendations
- `_build_user_item_matrix(ratings_df: pd.DataFrame) -> csr_matrix`: Build sparse matrix
- `_compute_item_similarity(matrix: csr_matrix) -> csr_matrix`: Compute item-item cosine similarity
- `_find_similar_items(item_idx: int) -> List[int]`: Find k most similar items
- `_aggregate_predictions(user_idx: int, similar_items: List[int]) -> Dict[int, float]`: Aggregate ratings
- `_is_new_item(item_id: int) -> bool`: Detect new items

### Quickstart Guide

**Development Setup**:
1. Ensure virtual environment with dependencies: scipy, sklearn, pandas, numpy, pytest
2. Place MovieLens training data in expected location
3. Run `pytest tests/test_collaborative.py` to verify setup
4. Implement ItemBasedCF class following the interface above
5. Target ≥70% test coverage before integration

---

## Implementation Strategy

### Phase Sequence

1. **Phase 0**: Research - Complete technology decisions and integration patterns
2. **Phase 1**: Design - Define data model, contracts, and quickstart guide
3. **Phase 2**: Implementation - Build ItemBasedCF with TDD approach
4. **Phase 3**: Integration - Connect with ContentModel and evaluation framework
5. **Phase 4**: Validation - Performance testing and cold-start verification

### Testing Strategy

- **Unit Tests**: Test matrix operations, similarity computation, recommendation logic
- **Integration Tests**: Test cold-start fallback, ContentModel integration
- **Performance Tests**: Verify <100ms recommendation generation, <5s similarity computation
- **Edge Case Tests**: New items, low-rated items, memory constraints

### Risk Mitigation

- **Memory Usage**: Use sparse matrices, test with MovieLens small first
- **Performance**: Cache similarity matrix, use efficient sklearn implementation
- **New-Item Quality**: Document limitations, hybrid strategy in future phases
- **Integration**: Follow existing ContentModel patterns from Week 2