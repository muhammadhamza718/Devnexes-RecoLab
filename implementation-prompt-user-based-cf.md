# Implementation Prompt: User-Based Collaborative Filtering (Day 1 Morning)

**Project**: RecoLab Hybrid Recommendation Engine  
**Feature**: User-Based Collaborative Filtering  
**Specification Directory**: `specs/002-implement-user-based/`  
**Target Timeline**: Day 1 Morning (4 hours, MVP scope 26 tasks)

---

## 🎯 Implementation Context

You are implementing user-based collaborative filtering for the RecoLab Hybrid Recommendation Engine project. This is Day 1 morning work in an accelerated timeline compressing 4 weeks into 1.2 weeks. The specification, plan, research, data model, quickstart, and tasks have been completed and validated via IVP analysis.

### Prerequisites
- Week 1 (Data Foundation) and Week 2 (Content-Based Model) are completed
- Existing ContentModel and evaluation framework are available
- SDD documentation is complete and validated in `specs/002-implement-user-based/`

---

## 📋 Mandatory Development Methodology

### 1. Spec-Driven Development (SDD) - NON-NEGOTIABLE
- **STRICTLY FOLLOW**: Spec → Plan → Tasks → Implementation sequence
- **NO IMPLEMENTATION** without reviewing all SDD documents first
- **ALL CHANGES** must trace back to specific requirements in spec.md
- **DEVIATIONS** require explicit user approval before proceeding

### 2. Test-Driven Development (TDD) - NON-NEGOTIABLE
- **WRITE TESTS FIRST** for every component (Red-Green-Refactor cycle)
- **NO IMPLEMENTATION** without failing tests written first
- **EACH TASK** includes test writing before implementation
- **COVERAGE TARGET**: ≥70% for collaborative.py code
- **MINIMUM TESTS**: 15+ tests specified in tasks.md

### 3. Quality-First Development
- **TYPE HINTS**: All functions must have explicit return types and parameter types
- **ERROR HANDLING**: All operations must have try-catch blocks with meaningful error messages
- **DOCUMENTATION**: All complex logic requires inline comments
- **NAMING**: Descriptive names, no abbreviations unless widely understood
- **NO ANY TYPES**: Use proper typing throughout (Python typing with Optional, Union, etc.)

---

## 🏛️ Core Principles (Constitution Compliance)

### I. Quality-First Development
Every feature must meet strict quality standards before completion. Quality is not optional.

### II. Spec-Driven Development
Follow the SDD lifecycle strictly. Reference spec.md, plan.md, and tasks.md throughout implementation.

### III. Test-Driven Development
Tests before implementation. Red-Green-Refactor cycle enforced for all business logic.

### IV. Blast-Radius Awareness
Consider impact on existing codebase. Review ContentModel integration points before changes.

### V. Security & Performance Standards
- No secrets, credentials, or .env files in code
- Performance targets: <100ms recommendation generation, <5s similarity computation
- Memory target: <100MB for matrices
- Use sparse matrices (CSR format) for memory efficiency

### VI. Incremental Delivery
- One task = one commit
- Small, testable increments
- Changes must be revertable in isolation
- Regular git commits with professional messages

### VII. Independent Validation Perspective (IVP)
After implementation, your work must pass validation across 5 perspectives:
- **Security**: No vulnerabilities, proper data handling
- **Constitution**: Compliance with all project standards
- **Specification**: Alignment with spec.md requirements
- **Quality**: Code quality, best practices, bug detection
- **Conflict**: No integration conflicts with existing code

### VIII. Permission Gates
- **EXPLICIT PERMISSION** required before phase progression
- Present IVP validation results before proceeding
- Never automatically progress to next phase
- User testing results required before completion

---

## 🛠️ Project-Specific Standards (RecoLab)

### 12 RecoLab Principles
1. **README Requirements**: Comprehensive documentation (problem, objectives, features, architecture, tech stack, setup, env-vars, screenshots, testing, deployment)
2. **Security & Data Privacy**: No secrets committed, config via environment variables, gitignored
3. **User Experience Standards**: Loading, empty, and error states with meaningful feedback
4. **Commit Discipline**: Regular incremental progress with professional commit messages
5. **AI Review Protocol**: Review, understand, test, and improve all AI-generated code before submission
6. **Repository Naming**: Follow `Devnexes-ProjectName` convention
7. **Code Quality**: Clean architecture, reusable modules, no large files, no duplicated logic
8. **Data Usage Standards**: Public/licensed/synthetic datasets only (MovieLens small dataset)
9. **Ethical AI Usage**: Frame as decision support, not medical/legal/financial decisions
10. **Timeline Management**: Prioritize learning and portfolio quality over speed
11. **Evaluation Framework**: Engineering quality 25%, Functional completion 25%, Problem-solving depth 15%, Presentation 15%, Testing/evidence 10%, GitHub discipline 10%
12. **Scope Boundaries**: Focus on recommendation quality/evaluation/explanation only, not full e-commerce platform

### Latest & Stable Tech Stack Policy
- All package versions must be latest stable releases
- Version decisions must be documented with rationale if not latest stable
- Current target: Python 3.14, scipy>=1.11.0, scikit-learn>=1.3.0, pandas>=2.0.0, numpy>=1.24.0, pytest>=7.4.0

---

## 📂 Implementation Structure

### Files to Create/Modify
```
src/recolab/
├── collaborative.py          # NEW: User-based collaborative filtering
│   ├── UserBasedCF           # Main class implementing Recommender protocol
│   ├── matrix_operations     # Utility functions for matrix building
│   └── similarity_compute   # Cosine similarity computation functions
├── content.py               # EXISTING: Content model (for cold-start fallback)
├── interfaces.py            # EXISTING: Recommender protocol
└── __init__.py              # UPDATE: Export collaborative classes

tests/
├── test_collaborative.py     # NEW: Collaborative filtering tests
│   ├── test_matrix_ops      # Matrix building tests
│   ├── test_similarity      # Similarity computation tests
│   ├── test_recommendations # Recommendation logic tests
│   └── test_cold_start      # Cold-start fallback tests
└── fixtures/                # EXISTING: Test fixtures
```

### Key Integration Points
- **ContentModel**: Cold-start fallback for users with ≤5 ratings
- **Recommender Protocol**: Must satisfy `recommend(user_id, k, exclude_items)` interface
- **Evaluation Framework**: Compatible with existing Week 1-2 evaluation infrastructure

---

## 🎯 Implementation Tasks (MVP Scope - 26 Tasks)

### Phase 1: Setup (3 tasks)
- T001: Create collaborative.py file
- T002: Create test_collaborative.py file  
- T003: Add collaborative imports to __init__.py

### Phase 2: Foundational (4 tasks)
- T004: Implement UserBasedCF class skeleton with __init__ method
- T005: Implement Recommender protocol compliance stub
- T006: Add type hints for all UserBasedCF methods
- T007: Setup ContentModel integration stub

### Phase 3: User Story 1 - Core Recommendations (19 tasks)

**Tests FIRST (9 tests):**
- T008: Write test for UserBasedCF initialization
- T009: Write test for user-item matrix building
- T010: Write test for cosine similarity computation
- T011: Write test for similar user finding
- T012: Write test for recommendation aggregation
- T013: Write test for consumed-item filtering
- T014: Write test for exclude_items parameter
- T015: Write test for edge case: user with no similar users
- T016: Write test for performance: recommendation generation <100ms

**Implementation (10 tasks):**
- T017: Implement _build_user_item_matrix method
- T018: Implement user and movie index mappings
- T019: Implement _compute_similarity method with sklearn cosine_similarity
- T020: Implement _find_similar_users method
- T021: Implement _aggregate_predictions method with weighted averaging
- T022: Implement main recommend method with filtering logic
- T023: Add consumed-item filtering logic
- T024: Add exclude_items parameter handling
- T025: Add error handling for invalid user IDs
- T026: Add error handling for invalid k values

---

## 🔧 Technical Implementation Details

### Core Class Structure
```python
class UserBasedCF:
    def __init__(self, k_similar_users: int = 50, min_similarity: float = 0.1):
        self.k_similar_users = k_similar_users
        self.min_similarity = min_similarity
        self.user_item_matrix = None  # scipy.sparse.csr_matrix
        self.similarity_matrix = None  # scipy.sparse.csr_matrix
        self.user_mapping = {}  # Dict[int, int]
        self.movie_mapping = {}  # Dict[int, int]
        self.reverse_user_mapping = {}  # Dict[int, int]
        self.reverse_movie_mapping = {}  # Dict[int, int]
        self.content_model = None  # ContentModel for cold-start fallback
        self.is_fitted = False
    
    def fit(self, ratings_df: pd.DataFrame) -> None:
        """Train model on rating data"""
        pass
    
    def recommend(self, user_id: int, k: int, exclude_items: Optional[List[int]] = None) -> List[int]:
        """Generate recommendations for user"""
        pass
```

### Key Technology Decisions
- **Sparse Matrix Format**: scipy.sparse.csr_matrix (Compressed Sparse Row)
- **Similarity Computation**: sklearn.metrics.pairwise.cosine_similarity with L2 normalization
- **Cold-Start Threshold**: ≤5 ratings (industry standard)
- **K-Similar Users**: 50 (balance between relevance and performance)
- **Minimum Similarity**: 0.1 (filter out weak correlations)

### Performance Requirements
- **Matrix Building**: <1 second for MovieLens small dataset
- **Similarity Computation**: <5 seconds for MovieLens small dataset
- **Recommendation Generation**: <100ms per request
- **Memory Usage**: <100MB for matrices

---

## ✅ Quality Gates & Validation

### Checkpoint 1: Setup Completion
- ✅ collaborative.py file created
- ✅ test_collaborative.py file created
- ✅ __init__.py updated with imports
- ✅ All files compile without errors

### Checkpoint 2: Foundation Complete
- ✅ UserBasedCF class skeleton with proper type hints
- ✅ Recommender protocol compliance verified
- ✅ ContentModel integration stub ready
- ✅ Initialization tests pass

### Checkpoint 3: MVP Functionality (T001-T026)
- ✅ 9 tests written and failing (TDD approach)
- ✅ 9 tests passing after implementation
- ✅ User-item matrix building works correctly
- ✅ Cosine similarity computation complete
- ✅ Recommendation logic functional
- ✅ Cold-start fallback working
- ✅ Performance benchmarks met (<100ms recommendations)
- ✅ ≥70% code coverage achieved

### Final Validation Requirements
- ✅ IVP validation across 5 perspectives passes
- ✅ All functional requirements (FR-001 through FR-012) satisfied
- ✅ All success criteria (SC-001 through SC-010) met
- ✅ Integration with ContentModel verified
- ✅ Integration with evaluation framework verified
- ✅ Professional commit history maintained

---

## 🚨 Forbidden Patterns (NON-NEGOTIABLE)

### No Anti-Patterns
1. **No untyped functions** - All functions must have explicit return types
2. **No missing error handling** - All operations must have try-catch blocks
3. **No hardcoded values** - Use configuration and parameters
4. **No secrets in code** - Use environment variables only
5. **No synchronous blocking operations** - Use efficient algorithms
6. **No code duplication** - Reuse utility functions
7. **No abbreviations in naming** - Use descriptive names
8. **No magic numbers** - Use named constants
9. **No comments for obvious code** - Comment only complex logic
10. **No commits without tests** - One task = one commit with tests

---

## 📊 Expected Deliverables

### Code Deliverables
- **src/recolab/collaborative.py**: Complete UserBasedCF implementation
- **tests/test_collaborative.py**: 15+ comprehensive tests
- **src/recolab/__init__.py**: Updated exports
- **README.md**: Updated with collaborative filtering section

### Documentation Deliverables
- **Commit History**: Professional, incremental commits with descriptive messages
- **Code Coverage**: ≥70% coverage report
- **Performance Benchmarks**: <100ms recommendations, <5s similarity computation
- **Integration Evidence**: Screenshots/tests of ContentModel and evaluation framework integration

### Validation Deliverables
- **IVP Validation Report**: Multi-perspective validation results
- **Test Results**: All 15+ tests passing
- **Performance Report**: Memory usage and timing benchmarks
- **Integration Report**: Successful integration with existing components

---

## 🎯 Success Criteria

### Functional Requirements (FR-001 through FR-012)
- ✅ FR-001: User-item matrix building using sparse CSR format
- ✅ FR-002: Cosine similarity computation using sklearn with normalization
- ✅ FR-003: Find k most similar users
- ✅ FR-004: Aggregate weighted ratings from similar users
- ✅ FR-005: Filter out consumed items
- ✅ FR-006: Handle exclude_items parameter
- ✅ FR-007: Cold-start detection (≤5 ratings) with ContentModel fallback
- ✅ FR-008: Recommender protocol compliance
- ✅ FR-009: Return exactly k recommendations (or fewer)
- ✅ FR-010: Edge case handling with graceful errors
- ✅ FR-011: Model persistence for loading/reuse
- ✅ FR-012: Sparse matrix operations for memory efficiency

### Success Criteria (SC-001 through SC-010)
- ✅ SC-001: <100ms recommendation generation
- ✅ SC-002: 100% cold-start fallback success rate
- ✅ SC-003: <5s similarity computation
- ✅ SC-004: <100MB memory usage
- ✅ SC-005: ≥70% test coverage
- ✅ SC-006: ≥15 passing unit tests
- ✅ SC-007: Cold-start activation correctness
- ✅ SC-008: Consumed-item filtering accuracy
- ✅ SC-009: Model persistence without data loss
- ✅ SC-010: Evaluation framework integration

---

## 🚀 Implementation Workflow

### Step 1: Review SDD Documents
1. Read `specs/002-implement-user-based/spec.md` thoroughly
2. Read `specs/002-implement-user-based/plan.md` for architecture decisions
3. Read `specs/002-implement-user-based/tasks.md` for detailed tasks
4. Read `specs/002-implement-user-based/research.md` for technology decisions
5. Read `specs/002-implement-user-based/data-model.md` for entity definitions
6. Read `specs/002-implement-user-based/quickstart.md` for implementation guidance

### Step 2: Setup Phase (T001-T003)
1. Create file structure following project conventions
2. Set up test infrastructure
3. Verify environment and dependencies
4. Commit: "Setup: Create collaborative filtering file structure"

### Step 3: Foundation Phase (T004-T007)
1. Implement UserBasedCF class skeleton with proper typing
2. Set up Recommender protocol compliance
3. Configure ContentModel integration
4. Write and verify initialization tests
5. Commit: "Foundation: UserBasedCF class skeleton with type hints"

### Step 4: MVP Implementation (T008-T026)
1. **WRITE TESTS FIRST** for each component (TDD approach)
2. Implement matrix building with sparse operations
3. Implement cosine similarity computation
4. Implement recommendation logic with aggregation
5. Add filtering and error handling
6. Verify all tests pass
7. Commit: "Implementation: Core user-based CF with matrix operations"
8. Commit: "Implementation: Similarity computation and recommendations"
9. Commit: "Implementation: Filtering and error handling"

### Step 5: Validation Phase
1. Run comprehensive test suite
2. Measure performance benchmarks
3. Verify code coverage ≥70%
4. Test ContentModel integration
5. Test evaluation framework integration
6. Perform IVP validation across 5 perspectives
7. Address any validation findings

### Step 6: Final Deliverables
1. Update README.md with collaborative filtering section
2. Generate coverage report
3. Document performance benchmarks
4. Create integration evidence
5. Final commit: "Complete: User-based collaborative filtering MVP"

---

## 📞 Support & Resources

### Documentation References
- scipy.sparse.csr_matrix documentation
- sklearn.metrics.pairwise.cosine_similarity documentation
- Existing ContentModel implementation (Week 2 work)
- Existing evaluation framework (Week 1 work)
- Project constitution: `.specify/memory/constitution.md`

### Troubleshooting
- Memory errors: Verify sparse matrix usage, check dataset size
- Performance issues: Profile code, verify sklearn implementation, check similarity matrix caching
- Integration issues: Verify ContentModel interface, check Recommender protocol compliance
- Test failures: Review test logic, verify implementation matches spec requirements

---

## ⚠️ Critical Reminders

1. **TDD IS MANDATORY**: Write tests first, ensure they fail, then implement
2. **NO SHORTCUTS**: Every requirement in spec.md must be addressed
3. **TYPE SAFETY**: All functions must have explicit types
4. **ERROR HANDLING**: All operations must have try-catch blocks
5. **PERFORMANCE**: Must meet <100ms recommendation target
6. **MEMORY**: Must stay under 100MB for matrices
7. **COVERAGE**: Must achieve ≥70% code coverage
8. **INTEGRATION**: Must work with existing ContentModel and evaluation framework
9. **COMMIT DISCIPLINE**: Regular, professional commits with descriptive messages
10. **VALIDATION**: Must pass IVP validation before completion

---

**Implementation Authorization**: You are authorized to proceed with the implementation following these specifications, the SDD methodology, and all project constitution principles. Any deviations from these requirements must receive explicit user approval before proceeding.

**Start Point**: Begin with Step 1 (Review SDD Documents) and proceed through the implementation workflow systematically.