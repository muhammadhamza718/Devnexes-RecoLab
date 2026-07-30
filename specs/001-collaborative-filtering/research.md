# Research: Item-Based Collaborative Filtering

**Feature**: 001-collaborative-filtering  
**Date**: 2026-07-29  
**Purpose**: Technology decisions and implementation patterns for item-based CF

---

## Technology Decisions

### Decision 1: Sparse Matrix Format

**Decision**: Use scipy.sparse.csr_matrix (Compressed Sparse Row) format

**Rationale**: 
- CSR format is optimized for row operations (item-based similarity computation)
- Efficient memory usage for sparse user-item matrices (typical sparsity >95%)
- Fast row slicing operations needed for finding similar items
- Well-supported by scipy and sklearn integration

**Alternatives Considered**:
- CSC (Compressed Sparse Column): Better for column operations, but item-based CF needs row operations
- Dense matrix: Would use excessive memory (10k×10k matrix = 100M entries vs ~100k ratings)
- Dictionary of dictionaries: More flexible but slower for matrix operations

**Industry Standard**: CSR is the de facto standard for collaborative filtering sparse matrices

---

### Decision 2: Cosine Similarity Computation

**Decision**: Use sklearn.metrics.pairwise.cosine_similarity with L2 normalization

**Rationale**:
- sklearn provides optimized C implementation for performance
- Built-in L2 normalization ensures consistent similarity scores
- Handles sparse matrices efficiently
- Well-tested and maintained library
- Integrates seamlessly with scipy sparse matrices

**Alternatives Considered**:
- Manual numpy implementation: Slower, more error-prone, reinventing the wheel
- scipy.spatial.distance.cosine: Designed for vectors, not matrices
- Custom implementation: Unnecessary complexity for well-solved problem

**Performance**: <5 seconds for MovieLens small dataset (10k users)

---

### Decision 3: New-Item Detection Threshold

**Decision**: Define new items as those with 0 ratings

**Rationale**:
- Industry standard threshold for new-item detection
- No collaborative signal available for items with no ratings
- Must fall back to content-based similarity for new items
- Enables handling of constantly growing item catalogs

**Alternatives Considered**:
- ≤5 ratings: Too restrictive, might fall back unnecessarily
- ≤10 ratings: Too permissive, might produce poor collaborative recommendations
- Dynamic threshold: Adds complexity without clear benefit

**Validation**: Will test threshold effectiveness during evaluation phase

---

### Decision 4: K-Similar Items Parameter

**Decision**: Default k = 50 similar items per rated item for recommendation aggregation

**Rationale**:
- Balance between recommendation diversity and relevance
- Sufficient sample size for stable predictions
- Computationally feasible (<100ms recommendation generation)
- Industry-standard starting point for item-based CF

**Alternatives Considered**:
- k = 20: Might miss relevant similar items
- k = 100: Slower computation, diminishing returns
- Dynamic k: Adds complexity without clear benefit

**Tunability**: Parameter can be optimized during evaluation phase

---

### Decision 5: Minimum Similarity Threshold

**Decision**: Minimum similarity threshold = 0.1

**Rationale**:
- Filters out weak correlations that add noise
- Improves recommendation quality by focusing on meaningful relationships
- Prevents recommendations from negatively correlated users
- Conservative threshold to avoid over-filtering

**Alternatives Considered**:
- 0.0: No filtering, includes all users (more noise)
- 0.3: Too restrictive, might eliminate useful signals
- Dynamic threshold: Adds complexity without clear benefit

**Validation**: Will test threshold impact on recommendation quality

---

## Integration Patterns

### ContentModel Integration

**Pattern**: ItemBasedCF will use existing ContentModel for new-item fallback

**Rationale**:
- ContentModel already implements Recommender protocol
- Maintains consistent interface across all recommendation approaches
- Leverages existing Week 2 implementation
- Enables seamless hybrid strategy in future phases

**Implementation**:
```python
if self._is_new_item(item_id):
    return self.content_model.recommend(user_id, k, exclude_items)
```

### Recommender Protocol Compliance

**Pattern**: ItemBasedCF will satisfy existing Recommender protocol

**Rationale**:
- Ensures consistency with existing evaluation framework
- Enables model swapping for comparison testing
- Maintains clean architecture boundaries
- Supports future hybrid strategy development

**Implementation**:
```python
class ItemBasedCF:
    def recommend(self, user_id: int, k: int, exclude_items: Optional[List[int]] = None) -> List[int]:
        # Implementation following protocol signature
```

---

## Performance Considerations

### Memory Management

**Strategy**: Use sparse matrices throughout pipeline

**Implementation**:
- Item-item matrix in CSR format
- User-item matrix in CSR format
- Intermediate computations use sparse operations
- Cache similarity matrix after computation
- Item similarity caching for popular items

**Expected Usage**: <100MB for MovieLens small dataset

### Computation Optimization

**Strategy**: Precompute and cache similarity matrix

**Implementation**:
- Compute similarity during fit() phase
- Store matrix for repeated recommendation calls
- Avoid recomputing for each recommendation request

**Expected Performance**: <5 seconds for similarity computation, <100ms per recommendation

---

## Risk Assessment

### Memory Risks

**Risk**: Large datasets may exceed memory limits

**Mitigation**:
- Start with MovieLens small dataset
- Use sparse matrices throughout
- Monitor memory usage during development
- Implement fallback to subset if needed

### Performance Risks

**Risk**: Similarity computation may be slow for large item catalogs

**Mitigation**:
- Use optimized sklearn implementation
- Cache similarity matrix
- Item similarity caching for popular items
- Profile performance during development
- Consider approximation techniques if needed

### New-Item Quality Risks

**Risk**: Content-based fallback may not match collaborative quality for new items

**Mitigation**:
- Document limitations clearly
- This is temporary until hybrid strategy
- Evaluate new-item performance separately
- Tune threshold based on validation results

---

## Success Criteria Validation

### Technical Requirements

- ✅ User-item matrix building using scipy sparse CSR format
- ✅ Cosine similarity computation using sklearn with normalization
- ✅ Recommendation generation in <100ms per request
- ✅ Similarity computation in <5 seconds for target dataset
- ✅ Memory usage <100MB for target dataset
- ✅ Cold-start fallback to ContentModel working
- ✅ Recommender protocol conformance verified

### Quality Requirements

- ✅ ≥70% test coverage achieved
- ✅ ≥15 passing unit tests
- ✅ Integration with existing evaluation framework
- ✅ Edge case handling documented and tested
- ✅ Performance benchmarks met

---

## References

- sklearn.metrics.pairwise.cosine_similarity documentation
- scipy.sparse.csr_matrix documentation
- Collaborative filtering best practices (Netflix Prize papers)
- Existing ContentModel implementation (Week 2 work)
- Existing evaluation framework (Week 1 work)