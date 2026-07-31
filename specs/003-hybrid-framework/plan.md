# Implementation Plan: Hybrid Recommendation Framework

**Branch**: `003-hybrid-framework` | **Date**: 2026-07-30 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/003-hybrid-framework/spec.md`

## Summary

Implement a hybrid recommendation framework that combines content-based and collaborative filtering approaches using weighted scoring, adaptive model selection, and confidence scoring. The system will automatically select the best recommendation approach based on user activity levels, provide confidence indicators, and maintain fallback chains for graceful degradation.

## Technical Context

**Language/Version**: Python 3.11+  
**Primary Dependencies**: existing ContentModel, UserBasedCF, ItemBasedCF, numpy (score combination), pandas (data handling)  
**Storage**: No new storage requirements (uses existing model artifacts)  
**Testing**: pytest with ≥70% coverage requirement  
**Target Platform**: Linux/Windows local development environment  
**Project Type**: Single project (Python recommendation system)  
**Performance Goals**: <100ms recommendation generation (same as individual models)  
**Constraints**: Must maintain compatibility with existing Recommender protocol, integrate with three existing models  
**Scale/Scope**: MovieLens small dataset (100k ratings, ~10k users, ~10k movies)

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**Quality-First Development**: ✅ PASS - Implementation will follow TDD with tests written before code
**Spec-Driven Development**: ✅ PASS - This plan follows approved specification  
**Blast-Radius Awareness**: ✅ PASS - New hybrid.py file, minimal modifications to existing models  
**Security & Performance**: ✅ PASS - No security concerns, performance targets defined  
**Incremental Delivery**: ✅ PASS - Small, testable increments with clear acceptance criteria  
**IVP Validation**: ✅ PASS - Multi-perspective validation planned after each phase  
**Permission Gates**: ✅ PASS - User approval required before phase progression  

## Project Structure

### Documentation (this feature)

```text
specs/003-hybrid-framework/
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
├── hybrid.py                # NEW: Hybrid recommendation framework
│   ├── HybridRecommender     # Main class implementing Recommender + ColdStartHandler protocols
│   ├── score_combination     # Weighted scoring logic
│   ├── model_selection       # Adaptive model selection logic
│   ├── confidence_scoring    # Confidence computation
│   └── fallback_chain        # Fallback strategy implementation
├── content.py               # EXISTING: Content model (from Week 2)
├── collaborative.py          # EXISTING: User-based and Item-based CF (from Day 1)
├── interfaces.py            # EXISTING: Recommender protocol
└── __init__.py              # UPDATE: Export hybrid class

tests/
├── test_hybrid.py            # NEW: Hybrid framework tests
│   ├── test_score_combination   # Weighted scoring tests
│   ├── test_model_selection     # Adaptive selection tests
│   ├── test_confidence_scoring  # Confidence computation tests
│   └── test_fallback_chain      # Fallback strategy tests
└── fixtures/                # EXISTING: Test fixtures
```

**Structure Decision**: Single project structure following existing RecoLab patterns. New hybrid.py file alongside existing content.py and collaborative.py, maintaining clean separation of concerns and following established architecture from Week 1-2 work.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| None | N/A | N/A |

---

## Phase 0: Research & Technology Decisions

### Research Tasks

1. **Hybrid Scoring Methods**: Research weighted averaging vs. other combination methods (rank fusion, stacking)
2. **Score Normalization**: Research normalization techniques for combining different score ranges (min-max, z-score, percentile)
3. **Adaptive Thresholds**: Research optimal activity level thresholds for model selection (5, 20 ratings)
4. **Confidence Metrics**: Research confidence scoring approaches for recommendation systems
5. **Fallback Strategies**: Research graceful degradation patterns in recommendation systems

### Technology Decisions

- **Scoring Method**: Weighted averaging with configurable α parameter (simple, interpretable, tunable)
- **Normalization**: Min-max normalization per model to ensure fair weighting
- **Activity Thresholds**: Cold-start ≤5 ratings, active >20 ratings (based on dataset analysis)
- **Confidence Scoring**: Composite score based on activity level (0.4), item popularity (0.3), model agreement (0.3)
- **Fallback Chain**: Hybrid → Content → Collaborative → Popularity (ordered by reliability)
- **Alpha Default**: 0.5 (equal weighting between content and collaborative)
- **Persistence Strategy**: Use existing recolab.persistence module with to_bundle()/from_bundle() methods (consistent with Day 1 pattern)
- **Explanation Generation**: Delegate to underlying model's explain() method (ContentModel, UserBasedCF, or ItemBasedCF)

---

## Phase 1: Design & Contracts

### API Contract Design

#### HybridRecommender Class

```python
class HybridRecommender:
    def __init__(
        self,
        alpha: float = 0.5,
        cold_start_threshold: int = 5,
        active_threshold: int = 20,
        content_model: Optional[ContentModel] = None,
        user_based_cf: Optional[UserBasedCF] = None,
        item_based_cf: Optional[ItemBasedCF] = None
    ) -> None
        """Initialize hybrid recommender with configurable parameters."""
    
    def fit(self, ratings_df: pd.DataFrame, movies_df: pd.DataFrame) -> None
        """Train all underlying models on provided data."""
    
    def recommend(
        self,
        user_id: int,
        k: int,
        exclude_items: Optional[Set[int]] = None
    ) -> List[int]
        """Generate recommendations using adaptive model selection."""
    
    def recommend_cold_start(
        self,
        genres: List[str],
        liked_movie_ids: List[int],
        k: int
    ) -> List[int]
        """Generate recommendations for cold-start users."""
    
    def get_confidence(self, user_id: int, movie_id: int) -> float
        """Return confidence score for a specific recommendation."""
    
    def get_model_selection_info(self, user_id: int) -> Dict[str, Any]
        """Return information about which model was selected and why."""
    
    def explain(self, user_id: int, movie_id: int) -> str
        """Generate human-readable explanation by delegating to selected underlying model."""
    
    def to_bundle(self) -> ModelBundle
        """Create ModelBundle for persistence using existing persistence.py module."""
    
    @classmethod
    def from_bundle(cls, bundle: ModelBundle) -> "HybridRecommender"
        """Restore HybridRecommender from ModelBundle using existing persistence.py module."""
    
    def save(self, path: Path) -> None
        """Save model artifact using existing persistence.py save_artifact function."""
    
    @classmethod
    def load(cls, path: Path) -> "HybridRecommender"
        """Load model artifact using existing persistence.py load_artifact function."""
```

#### Protocol Compliance

- **Recommender Protocol**: ✅ recommend(user_id, k, exclude_items) method
- **ColdStartHandler Protocol**: ✅ recommend_cold_start(genres, liked_movie_ids, k) method

### Data Model Design

#### Confidence Score Composition

```python
confidence_score = (
    0.4 * activity_confidence +  # Based on user rating count
    0.3 * popularity_confidence +  # Based on item popularity
    0.3 * agreement_confidence     # Based on model agreement
)
```

#### Model Selection Logic

```python
if user_rating_count <= cold_start_threshold:
    selected_model = "content"
elif user_rating_count >= active_threshold:
    selected_model = "collaborative"  # or user-based/item-based
else:
    selected_model = "hybrid"
```

---

## Phase 2: Implementation Strategy

### Module Breakdown

#### 1. Core HybridRecommender Class (P1)
- **Responsibility**: Orchestrate model selection and recommendation generation
- **Dependencies**: ContentModel, UserBasedCF, ItemBasedCF
- **Key Methods**: __init__, fit, recommend, recommend_cold_start

#### 2. Score Combination Module (P1)
- **Responsibility**: Combine normalized scores from multiple models
- **Dependencies**: numpy, model outputs
- **Key Functions**: normalize_scores, combine_weighted_scores, handle_missing_scores

#### 3. Model Selection Module (P1)
- **Responsibility**: Select optimal model based on user activity
- **Dependencies**: user rating data, thresholds
- **Key Functions**: select_model, evaluate_user_activity, apply_adaptive_logic

#### 4. Confidence Scoring Module (P2)
- **Responsibility**: Compute confidence scores for recommendations
- **Dependencies**: user data, item data, model outputs
- **Key Functions**: compute_activity_confidence, compute_popularity_confidence, compute_agreement_confidence

#### 5. Fallback Chain Module (P2)
- **Responsibility**: Implement graceful degradation when models fail
- **Dependencies**: All models, error handling
- **Key Functions**: execute_fallback_chain, handle_model_failure, log_fallback_events

#### 6. Persistence Module (P1)
- **Responsibility**: Save and load hybrid model artifacts using existing persistence.py module
- **Dependencies**: existing recolab.persistence module, ModelBundle, save_artifact, load_artifact
- **Key Functions**: to_bundle(), from_bundle(), save(), load()
- **Rationale**: Follows Day 1 pattern where UserBasedCF and ItemBasedCF persistence was added via to_bundle()/from_bundle() methods

### Implementation Order

1. **Phase 2a**: Core HybridRecommender class skeleton with protocol compliance
2. **Phase 2b**: Score combination module with normalization and weighted averaging
3. **Phase 2c**: Model selection module with adaptive thresholds
4. **Phase 2d**: Integration with existing models (ContentModel, UserBasedCF, ItemBasedCF)
5. **Phase 2e**: Confidence scoring module
6. **Phase 2f**: Fallback chain implementation
7. **Phase 2g**: Persistence module with to_bundle()/from_bundle() methods
8. **Phase 2h**: Explanation generation delegation to underlying models
9. **Phase 2i**: Comprehensive testing and validation

---

## Phase 3: Quality Assurance

### Testing Strategy

#### Unit Tests (Target: 20+ tests)
- Score combination tests (5 tests)
- Model selection tests (5 tests)
- Confidence scoring tests (5 tests)
- Fallback chain tests (3 tests)
- Persistence tests (2 tests) - to_bundle()/from_bundle() roundtrip
- Explanation generation tests (2 tests) - delegation to underlying models
- Integration tests (2 tests)

#### Performance Tests
- Recommendation latency <100ms (all model selection paths)
- Memory usage monitoring (multiple models loaded)
- Score combination efficiency

#### Integration Tests
- Protocol compliance verification
- Existing model integration (ContentModel, UserBasedCF, ItemBasedCF)
- End-to-end recommendation flow

### Code Quality Standards
- Type hints on all functions and methods
- Comprehensive docstrings
- Error handling with meaningful messages
- No code duplication (DRY principle)
- Coverage ≥70%

---

## Phase 4: Deployment & Operations

### Deployment Considerations
- No new dependencies required
- Backward compatible with existing Recommender protocol
- Can be tested alongside existing models
- Gradual rollout possible through α parameter tuning

### Monitoring Requirements
- Model selection distribution logging
- Confidence score distribution monitoring
- Fallback chain activation frequency
- Performance metrics (latency, error rates)

### Rollback Strategy
- Revert to individual models if hybrid underperforms
- α parameter can be adjusted without code changes
- Fallback to content model if hybrid fails

---

## Risk Analysis

### Top 3 Risks

1. **Performance Degradation Risk**: Added complexity may increase latency beyond 100ms target
   - **Mitigation**: Lazy model loading, score caching, efficient normalization
   - **Blast Radius**: Limited to hybrid.py, individual models unaffected

2. **Model Selection Inaccuracy Risk**: Activity thresholds may not match actual optimal split points
   - **Mitigation**: Empirical validation on dataset, configurable thresholds
   - **Blast Radius**: Can be adjusted via parameters without code changes

3. **Integration Complexity Risk**: Coordinating three existing models may introduce bugs
   - **Mitigation**: Comprehensive integration tests, fallback chain for failures
   - **Blast Radius**: Isolated to hybrid.py, existing models remain functional

---

## Success Criteria Validation

### Functional Requirements Coverage
- ✅ FR-001 to FR-012 covered in implementation phases
- ✅ All user stories have corresponding test scenarios
- ✅ Edge cases identified and addressed

### Success Criteria Coverage
- ✅ SC-001 to SC-010 measurable and testable
- ✅ Performance targets defined and achievable
- ✅ Integration success criteria established

### Definition of Done
- All functional requirements implemented
- ≥20 unit tests passing
- ≥70% code coverage achieved
- Protocol compliance verified
- Performance targets met (<100ms)
- Integration with existing models successful
- Documentation updated

---

## Architectural Decision Records

### ADR-001: Weighted Averaging vs. Advanced Ensemble Methods
**Decision**: Use weighted averaging for score combination rather than advanced ensemble methods (stacking, rank fusion)

**Rationale**: 
- Weighted averaging is interpretable and tunable via α parameter
- Simpler to implement and debug
- Sufficient for Week 3 scope (advanced ensembles can be future work)
- Lower computational overhead

**Trade-offs**: 
- May not capture complex non-linear relationships between models
- Manual parameter tuning required

### ADR-002: Activity Threshold Selection (5 and 20 ratings)
**Decision**: Use 5 ratings for cold-start threshold and 20 ratings for active user threshold

**Rationale**:
- 5 ratings is industry standard for minimal interaction
- 20 ratings provides sufficient data for collaborative filtering reliability
- Creates three distinct user segments (cold-start, intermediate, active)
- Balances granularity with sufficient data per segment

**Trade-offs**:
- Thresholds may not be optimal for all datasets
- May need adjustment based on empirical validation

### ADR-003: Persistence Strategy Using Existing Module
**Decision**: Use existing recolab.persistence module with to_bundle()/from_bundle() methods for hybrid model persistence

**Rationale**:
- Follows established pattern from Day 1 (UserBasedCF and ItemBasedCF persistence)
- Maintains consistency with existing codebase architecture
- Leverages existing infrastructure (ModelBundle, save_artifact, load_artifact)
- Satisfies REQ-012 and AC-005 for evaluation reproducibility
- No new dependencies or infrastructure required

**Trade-offs**:
- Must include references to underlying models (ContentModel, UserBasedCF, ItemBasedCF)
- Cannot persist full model states, only configuration and references
- Dependent on existing persistence module stability

### ADR-004: Explanation Generation via Model Delegation
**Decision**: Delegate explanation generation to selected underlying model's explain() method

**Rationale**:
- ContentModel, UserBasedCF, and ItemBasedCF already have explain() methods from Day 1 IVP fixes
- Maintains consistency with existing model behavior
- Leverages existing work (no new implementation needed)
- Satisfies REQ-004 and GUD-002 for truthful explanations
- Reduces complexity and maintenance burden

**Trade-offs**:
- Hybrid explanations depend on individual model implementations
- Must handle cases where selected model's explain() method fails
- Less control over explanation format compared to custom implementation

---

## Next Steps

1. **Immediate**: Create research.md with detailed technology research
2. **Follow-up**: Create data-model.md with entity definitions
3. **Then**: Create quickstart.md with development setup instructions
4. **Finally**: Create tasks.md with detailed implementation tasks