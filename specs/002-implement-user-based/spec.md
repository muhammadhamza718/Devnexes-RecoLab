# Feature Specification: User-Based Collaborative Filtering

**Feature Branch**: `002-implement-user-based`  
**Created**: 2026-07-29  
**Status**: IMPLEMENTED (Day 1 AM) — IVP audit pending fixes  
**IVP Status**: ❌ FAIL — 2 critical gaps (persistence, explanation missing)  
**Input**: User description: "Implement user-based collaborative filtering model with cosine similarity, cold-start fallback, and comprehensive testing"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - User-Based Collaborative Filtering Recommendations (Priority: P1)

The system provides movie recommendations to users based on similar users' preferences using user-based collaborative filtering with cosine similarity. When a user requests recommendations, the system finds the most similar users, aggregates their ratings, and returns personalized movie suggestions while excluding movies the user has already rated.

**Why this priority**: This is the core functionality for Week 3 of the project and a critical component of the hybrid recommendation system. Without user-based CF, the system lacks collaborative filtering capabilities that are essential for the complete hybrid approach.

**Independent Test**: Can be fully tested by generating recommendations for existing users and verifying that recommendations exclude consumed items, are based on similar users' preferences, and fall back gracefully for cold-start users.

**Acceptance Scenarios**:

1. **Given** an existing user with rating history, **When** the user requests k recommendations, **Then** the system returns k movie IDs excluding movies the user has already rated, based on the most similar users' preferences
2. **Given** a new user with ≤5 ratings, **When** the user requests recommendations, **Then** the system falls back to content-based recommendations from the existing ContentModel
3. **Given** a user with no similar users, **When** the user requests recommendations, **Then** the system falls back to content-based recommendations without errors
4. **Given** an exclude_items parameter, **When** the user requests recommendations, **Then** the system excludes both already-rated items and items in the exclude_items list

---

### User Story 2 - User-Based CF Model Training and Persistence (Priority: P2)

The system can be trained on rating data to build user-user similarity matrices and persist the trained model for later use. When training completes, the model artifact is saved and can be loaded for generating recommendations without retraining.

**Why this priority**: Model persistence is essential for production deployment and integration with the existing evaluation framework. Without persistence, the model would need to be retrained on every request, which is inefficient.

**Independent Test**: Can be fully tested by training the model on training data, verifying similarity matrix computation, saving the model artifact, loading it back, and confirming it produces the same recommendations.

**Acceptance Scenarios**:

1. **Given** training data with user ratings, **When** the model is trained, **Then** the system builds a user-item matrix and computes user-user cosine similarity matrix
2. **Given** a trained model, **When** the model is saved, **Then** the model artifact persists and can be loaded for later use
3. **Given** a loaded model artifact, **When** recommendations are generated, **Then** the model produces consistent results without retraining

---

### Edge Cases

- What happens when a user has rated all available movies? The system should return an empty list or appropriate error message
- How does system handle users with no similar users below the minimum similarity threshold? Fall back to content-based recommendations
- What happens when the training data is empty or malformed? The system should handle this gracefully with appropriate error messages
- How does system handle memory constraints with large user-item matrices? Use sparse matrix operations to manage memory efficiently
- What happens when k is larger than the number of available unrated movies? Return as many recommendations as possible
- How does system handle duplicate user IDs or movie IDs in training data? Deduplicate and handle appropriately

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST build a user-item rating matrix from training data using sparse matrix representation
- **FR-002**: System MUST compute user-user cosine similarity using normalized vectors and efficient matrix operations
- **FR-003**: System MUST find the k most similar users for a target user based on cosine similarity scores
- **FR-004**: System MUST aggregate ratings from similar users using weighted average by similarity score
- **FR-005**: System MUST filter out movies the user has already rated from recommendations
- **FR-006**: System MUST respect exclude_items parameter to filter specified movies from recommendations
- **FR-007**: System MUST detect cold-start users (≤5 ratings or no similar users) and fall back to content-based recommendations
- **FR-008**: System MUST satisfy the Recommender protocol with recommend(user_id, k, exclude_items) method signature
- **FR-009**: System MUST return exactly k recommendations or fewer if insufficient candidates are available
- **FR-010**: System MUST handle edge cases gracefully with appropriate error messages and fallback behavior
- **FR-011**: System MUST persist trained model artifacts for later loading and reuse
- **FR-012**: System MUST use sparse matrix operations to optimize memory usage for large datasets

### Key Entities

- **User-Item Matrix**: Sparse matrix representing user ratings where rows are users, columns are movies, and values are ratings (0 for missing/unrated)
- **User-User Similarity Matrix**: Matrix storing cosine similarity scores between all pairs of users, used for finding similar users
- **User Mapping**: Mapping between user IDs and matrix row indices for efficient lookup
- **Movie Mapping**: Mapping between movie IDs and matrix column indices for efficient lookup
- **Similarity Threshold**: Minimum similarity score required for considering users as similar (default: 0.1)
- **K-Similar Users**: Number of similar users to consider for recommendation aggregation (default: 50)

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: User-based CF generates recommendations for existing users in under 100ms per request
- **SC-002**: System handles users with no similar users with 100% fallback success rate
- **SC-003**: Similarity matrix computation completes in under 5 seconds for MovieLens small dataset
- **SC-004**: Memory usage for matrices stays under 100MB for MovieLens small dataset
- **SC-005**: Unit test coverage reaches ≥70% for user-based CF code
- **SC-006**: System achieves ≥15 passing unit tests covering all major functionality
- **SC-007**: Cold-start fallback activates correctly for 100% of users with ≤5 ratings
- **SC-008**: Recommendations exclude consumed items with 100% accuracy
- **SC-009**: Model persistence and loading cycle completes without data loss
- **SC-010**: Integration with existing evaluation framework succeeds without errors

## Assumptions

- Training data is available in the expected format (user_id, movie_id, rating columns)
- Existing ContentModel is available for cold-start fallback
- MovieLens small dataset serves as the primary test dataset
- System has sufficient memory to handle sparse matrices for the target dataset size
- sklearn and scipy libraries are available in the development environment
- Existing Recommender protocol is defined and must be satisfied
- Evaluation framework is already implemented from Week 1-2 work

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

> Generated by IVP Agent after Day 1 AM session. These findings amend the spec.

### Critical Gaps (Must Fix Before Day 2 Closes)

**GAP-001 — Model Persistence Missing (FR-011, REQ-012)**
- `UserBasedCF` has no `to_bundle()` or `from_bundle()` methods.
- `persistence.py` exists but is never called from `collaborative.py`.
- Fix: Implement `to_bundle()` → `save_artifact()` and classmethod `from_bundle()` → `load_artifact()` matching `ContentModel` pattern.
- Task: T054 (002-user-based tasks.md)

**GAP-002 — No Explanation Output (REQ-004, AC-004, GUD-002)**
- `recommend()` returns bare `List[int]` with no score, reason, or source.
- API response schema requires `{movie_id, score, reason, source}` per item.
- Fix: Add `explain(user_id: int, movie_id: int) -> str` method returning a truthful, grounded explanation string.
- Task: T055 (002-user-based tasks.md)

### Warning Gaps (Fix During Day 2)

**WARN-001 — DRY Violation**: `_build_user_item_matrix` is duplicated verbatim in both `UserBasedCF` and `ItemBasedCF`. Extract to module-level function.

**WARN-002 — Protocol Type Divergence**: `exclude_items: Optional[Set[int] | List[int]]` vs protocol's `set[int] | None`. Align to protocol.

**WARN-003 — Cold-Start Attribute Check**: The cold-start guard uses `getattr(self.content_model, "fitted", False)`. Relying on a string attribute name directly is fragile. Validate content model interface explicitly.

**WARN-004 — Scale Documentation**: `UserBasedCF.similarity_matrix` is dense user×user matrix. Document scale limit (<5000 users) and log a warning if exceeded.