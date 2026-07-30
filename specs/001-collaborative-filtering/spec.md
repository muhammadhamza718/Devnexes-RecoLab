# Feature Specification: Item-Based Collaborative Filtering

**Feature Branch**: `001-collaborative-filtering`  
**Created**: 2026-07-29  
**Status**: IMPLEMENTED (Day 1 PM) — IVP audit pending fixes  
**IVP Status**: ❌ FAIL — 3 critical gaps (persistence, dense matrix OOM, explanation missing)  
**Input**: User description: "Implement item-based collaborative filtering model with cosine similarity, new-item cold-start handling, and comprehensive testing"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Item-Based Collaborative Filtering Recommendations (Priority: P1)

The system provides movie recommendations to users based on similar items' ratings using item-based collaborative filtering with cosine similarity. When a user requests recommendations, the system finds items similar to the user's previously rated items, aggregates ratings from those similar items, and returns personalized movie suggestions while excluding movies the user has already rated.

**Why this priority**: This is the core functionality for Day 1 afternoon and a critical component of the hybrid recommendation system. Item-based CF provides different recommendation patterns than user-based CF and is essential for the complete collaborative filtering implementation.

**Independent Test**: Can be fully tested by generating recommendations for existing users and verifying that recommendations exclude consumed items, are based on similar items' ratings, and handle new-item cold-start scenarios gracefully.

**Acceptance Scenarios**:

1. **Given** an existing user with rating history, **When** the user requests k recommendations, **Then** the system returns k movie IDs excluding movies the user has already rated, based on similar items to the user's rated items
2. **Given** a new item with no ratings, **When** the system encounters this item during recommendation, **Then** the system falls back to content-based similarity for new-item handling
3. **Given** a user with low-rated items, **When** the user requests recommendations, **Then** the system uses weighted aggregation based on user's rating values
4. **Given** an exclude_items parameter, **When** the user requests recommendations, **Then** the system excludes both already-rated items and items in the exclude_items list

---

### User Story 2 - Item-Based CF Model Training and Persistence (Priority: P2)

The system can be trained on rating data to build item-item similarity matrices and persist the trained model for later use. When training completes, the model artifact is saved and can be loaded for generating recommendations without retraining.

**Why this priority**: Model persistence is essential for production deployment and integration with the existing evaluation framework. Without persistence, the model would need to be retrained on every request, which is inefficient.

**Independent Test**: Can be fully tested by training the model on training data, verifying item-item similarity matrix computation, saving the model artifact, loading it back, and confirming it produces the same recommendations.

**Acceptance Scenarios**:

1. **Given** training data with user ratings, **When** the model is trained, **Then** the system builds an item-item matrix and computes item-item cosine similarity matrix
2. **Given** a trained model, **When** the model is saved, **Then** the model artifact persists and can be loaded for later use
3. **Given** a loaded model artifact, **When** recommendations are generated, **Then** the model produces consistent results without retraining

---

### Edge Cases

- What happens when a user has rated no items? The system should fall back to content-based recommendations
- How does system handle new items with no ratings? Fall back to content-based similarity for new-item recommendations
- What happens when the training data is empty or malformed? The system should handle this gracefully with appropriate error messages
- How does system handle memory constraints with large item-item matrices? Use sparse matrix operations and item similarity caching
- What happens when k is larger than the number of available unrated items? Return as many recommendations as possible
- How does system handle duplicate item IDs in training data? Deduplicate and handle appropriately
- What happens when all similar items have been rated by the user? Return fewer recommendations or suggest exploration

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST build an item-item rating matrix from training data using sparse matrix representation
- **FR-002**: System MUST compute item-item cosine similarity using normalized vectors and efficient matrix operations
- **FR-003**: System MUST find the k most similar items for each of the user's rated items based on cosine similarity scores
- **FR-004**: System MUST aggregate item similarities using weighted average by user's rating values
- **FR-005**: System MUST filter out movies the user has already rated from recommendations
- **FR-006**: System MUST respect exclude_items parameter to filter specified movies from recommendations
- **FR-007**: System MUST detect new items (no ratings) and fall back to content-based similarity for new-item handling
- **FR-008**: System MUST satisfy the Recommender protocol with recommend(user_id, k, exclude_items) method signature
- **FR-009**: System MUST return exactly k recommendations or fewer if insufficient candidates are available
- **FR-010**: System MUST handle edge cases gracefully with appropriate error messages and fallback behavior
- **FR-011**: System MUST persist trained model artifacts for later loading and reuse
- **FR-012**: System MUST use sparse matrix operations and item similarity caching to optimize memory usage for large datasets

### Key Entities

- **Item-Item Matrix**: Sparse matrix representing item-item similarities where rows and columns are movies, and values are cosine similarity scores
- **User-Item Matrix**: Sparse matrix representing user ratings where rows are users, columns are movies, and values are ratings (0 for missing/unrated)
- **User Mapping**: Mapping between user IDs and matrix row indices for efficient lookup
- **Movie Mapping**: Mapping between movie IDs and matrix column indices for efficient lookup
- **Reverse User Mapping**: Mapping between matrix row indices and user IDs for result conversion
- **Reverse Movie Mapping**: Mapping between matrix column indices and movie IDs for result conversion
- **Similarity Threshold**: Minimum similarity score required for considering items as similar (default: 0.1)
- **K-Similar Items**: Number of similar items to consider per rated item for recommendation aggregation (default: 50)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Item-based CF generates recommendations for existing users in under 100ms per request
- **SC-002**: System handles new items with no ratings with 100% fallback success rate
- **SC-003**: Item-item similarity matrix computation completes in under 5 seconds for MovieLens small dataset
- **SC-004**: Memory usage for matrices stays under 100MB for MovieLens small dataset
- **SC-005**: Unit test coverage reaches ≥70% for item-based CF code
- **SC-006**: System achieves ≥15 passing unit tests covering all major functionality
- **SC-007**: New-item fallback activates correctly for 100% of items with no ratings
- **SC-008**: Recommendations exclude consumed items with 100% accuracy
- **SC-009**: Model persistence and loading cycle completes without data loss
- **SC-010**: Integration with existing evaluation framework succeeds without errors

## Assumptions

- Training data is available in the expected format (user_id, movie_id, rating columns)
- Existing ContentModel is available for new-item fallback
- MovieLens small dataset serves as the primary test dataset
- System has sufficient memory to handle sparse matrices for the target dataset size
- sklearn and scipy libraries are available in the development environment
- Existing Recommender protocol is defined and must be satisfied
- Evaluation framework is already implemented from Week 1-2 work
- User-based CF from Day 1 morning is available for comparison and hybrid strategy

## Dependencies

- Existing ContentModel for cold-start fallback
- Existing Recommender protocol definition
- Training data pipeline from Week 1 work
- Evaluation framework from Week 1 work
- scipy library for sparse matrix operations
- sklearn library for cosine similarity computation
- pandas library for data manipulation
- numpy library for numerical operations

---

## IVP Audit Findings (2026-07-29)

> Generated by IVP Agent after Day 1 PM session. These findings amend the spec.

### Critical Gaps (Must Fix Before Day 2 Closes)

**GAP-001 — Model Persistence Missing (FR-011, REQ-012)**
- `ItemBasedCF` has no `to_bundle()` or `from_bundle()` methods.
- `persistence.py` exists but is never called from `collaborative.py`.
- Fix: Implement `to_bundle()` → `save_artifact()` and classmethod `from_bundle()` → `load_artifact()` matching `ContentModel` pattern.
- Task: T055 (001-CF tasks.md)

**GAP-002 — Dense item_item_matrix Violates SC-004 (<100MB) (FR-012)**
- `_compute_item_similarity` uses `cosine_similarity(item_user_matrix)` producing a full dense `n_items × n_items` matrix.
- On MovieLens-small (9,742 items): ~380 MB float32 — **3.8× over budget**.
- Fix: Replace with `NearestNeighbors(metric='cosine')` storing only top-K similar items per item in a sparse dict or CSR structure.
- Task: T054 (001-CF tasks.md)

**GAP-003 — No Explanation Output (REQ-004, AC-004, GUD-002)**
- `recommend()` returns bare `List[int]` with no score, reason, or source.
- API response schema requires `{movie_id, score, reason, source}` per item.
- Fix: Add `explain(user_id: int, movie_id: int) -> str` method returning a truthful, grounded explanation string.
- Task: T056 (001-CF tasks.md)

### Warning Gaps (Fix During Day 2)

**WARN-001 — Dead Parameter**: `_aggregate_predictions(self, user_id, user_rated_items)` — `user_id` is never used. Remove or document.

**WARN-002 — DRY Violation**: `_build_user_item_matrix` is duplicated verbatim in both `UserBasedCF` and `ItemBasedCF`. Extract to module-level function.

**WARN-003 — Protocol Type Divergence**: `exclude_items: Optional[Set[int] | List[int]]` vs protocol's `set[int] | None`. Align to protocol.

**WARN-004 — Fragile Test**: `TestAggregationIBCF.test_aggregate_predictions` asserts specific movie ID (40) is in predictions based on implicit cosine similarity assumption. Use structural assertions instead.