# Week 2 Learning Notes - Content-Based Recommendation Model

## Implementation Summary
Week 2 implemented a content-based recommendation model using TF-IDF feature extraction and cosine similarity. The model addresses the cold-start problem identified in Week 1 by recommending items based on genre preferences rather than user history.

## Key Technical Decisions

### 1. Protocol-Oriented Design
**Decision**: Use Python protocols (structural subtyping) instead of abstract base classes

**Rationale**:
- Protocols enable duck-typing without requiring inheritance
- Models can satisfy multiple protocols simultaneously (ContentModel implements both Recommender and ColdStartHandler)
- Runtime protocol checking via `isinstance(model, Protocol)` works
- Type annotations improve IDE support and mypy checking

**Implementation**:
```python
@runtime_checkable
class Recommender(Protocol):
    def fit(self, ratings: pd.DataFrame, movies: pd.DataFrame | None = None) -> Recommender: ...
    def recommend(self, user_id: int, k: int, exclude_items: set[int] | None = None) -> list[int]: ...

@runtime_checkable
class ColdStartHandler(Protocol):
    def recommend_cold_start(self, genres: list[str], liked_movie_ids: list[int], k: int) -> list[int]: ...
```

**Learnings**:
- Protocols require `@runtime_checkable` decorator for `isinstance()` checks
- Protocol methods must use `...` ellipsis for abstract methods
- Protocol conformance is structural, not nominal
- Type hints are essential for protocol compliance

### 2. TF-IDF Feature Extraction
**Decision**: Use scikit-learn's TfidfVectorizer for genre feature extraction

**Rationale**:
- TF-IDF captures genre importance across the catalog
- Handles multi-label genre strings (e.g., "Action|Adventure|Sci-Fi")
- Sparse matrix representation is memory-efficient
- Cosine similarity works naturally with TF-IDF vectors

**Implementation**:
```python
from sklearn.feature_extraction.text import TfidfVectorizer

# Preprocess genres: replace "|" with spaces
genres_text = item_features["genres"].str.replace("|", " ")

# Fit TF-IDF vectorizer
vectorizer = TfidfVectorizer(tokenizer=lambda x: x.split())
tfidf_matrix = vectorizer.fit_transform(genres_text)
```

**Learnings**:
- TF-IDF reduces common genres (Drama, Comedy) weight relative to rare genres
- Tokenizer must handle multi-label strings (space-separated works well)
- Sparse matrix operations are efficient for large catalogs
- Cosine similarity on TF-IDF vectors is domain-agnostic (works for any text features)

### 3. Cold-Start Handling
**Decision**: Implement genre-based filtering for users without history

**Rationale**:
- New users have no rating history for collaborative filtering
- Genre preferences are easy to collect during onboarding
- Content-based filtering works without user-item interactions
- Provides meaningful recommendations from day one

**Implementation**:
```python
def recommend_cold_start(self, genres: list[str], liked_movie_ids: list[int], k: int) -> list[int]:
    # Filter items by preferred genres
    candidate_items = []
    for item_id, item_genres in self.item_features.items():
        if any(genre in item_genres for genre in genres):
            candidate_items.append(item_id)
    
    # Rank by popularity (fallback for content model)
    ranked = sorted(candidate_items, key=lambda x: self.item_popularity.get(x, 0), reverse=True)
    return ranked[:k]
```

**Learnings**:
- Cold-start recommendations must exclude already-liked items
- Genre matching is fuzzy (partial matches acceptable)
- Popularity fallback provides reasonable ordering when similarity scores are unavailable
- Onboarding UX should collect genre preferences for new users

### 4. CI-Safe Test Fixtures
**Decision**: Create sample fixtures (50 users, 5858 ratings) for CI testing

**Rationale**:
- Full MovieLens dataset (100k+ ratings) is too large for CI
- Sample fixtures maintain data structure consistency
- CI tests run in seconds instead of minutes
- Integration tests with full dataset run locally or in nightly builds

**Implementation**:
```python
# tests/fixtures/ratings_sample.csv (50 users, 5858 ratings)
# tests/fixtures/movies_sample.csv (reduced catalog)
# tests/conftest.py marks tests with @pytest.mark.full_dataset
```

**Learnings**:
- Sample fixtures must preserve column names and data types
- Statistical properties (sparsity, distribution) should mirror full dataset
- pytest markers enable selective test execution
- GitHub Actions needs `pytest -m "not full_dataset"` for CI speed

### 5. Persistence Strategy
**Decision**: Bundle pattern (to_bundle/from_bundle) for model serialization

**Rationale**:
- Explicit bundle structure is more maintainable than raw pickle
- Enables version control of serialization format
- Allows partial deserialization for large models
- Type annotations improve deserialization safety

**Implementation**:
```python
def to_bundle(self) -> dict[str, Any]:
    return {
        "item_features": self.item_features,
        "item_index": self.item_index,
        "tfidf_matrix": self.tfidf_matrix,
        "item_popularity": self.item_popularity,
        "ratings": self._ratings,
        "fitted": self.fitted,
    }

@classmethod
def from_bundle(cls, bundle: dict[str, Any]) -> ContentModel:
    model = cls()
    model.item_features = bundle["item_features"]
    model.item_index = bundle["item_index"]
    model.tfidf_matrix = bundle["tfidf_matrix"]
    model.item_popularity = bundle["item_popularity"]
    model._ratings = bundle["ratings"]
    model.fitted = bundle["fitted"]
    return model
```

**Learnings**:
- Include all state (including sparse matrices) for roundtrip safety
- Sparse matrices (CSR format) serialize well with pickle
- Ratings data needed for user-based similarity computation
- Version field should be added for future compatibility

## Testing Strategy

### Test Coverage
- **34 tests** for ContentModel (target: 25+ exceeded)
- **92% coverage** for content.py
- Protocol conformance tests for Recommender and ColdStartHandler
- Persistence roundtrip tests
- Edge case tests (empty data, unknown items, etc.)

### Test Organization
- **TestContentModelInit**: Initialization parameters
- **TestContentModelFit**: Training behavior and validation
- **TestContentModelRecommenderProtocol**: Recommender protocol conformance
- **TestContentModelColdStartHandlerProtocol**: ColdStartHandler protocol conformance
- **TestContentModelSimilarItems**: Item similarity computation
- **TestContentModelRecommendEnhanced**: User-based recommendations
- **TestContentModelColdStartEnhanced**: Cold-start recommendation logic
- **TestContentModelExplanation**: Explanation generation
- **TestContentModelPersistence**: Serialization roundtrip

### Key Testing Learnings
- Protocol conformance tests prevent interface drift
- Sample fixtures enable reproducible CI tests
- Parametrized tests reduce code duplication
- Coverage reporting identifies untested edge cases
- mypy type checking catches annotation errors

## Type Checking Configuration

### MyPy Challenges
- scikit-learn lacks official type stubs
- Configured `ignore_missing_imports = true` in pyproject.toml
- Removed unused `# type: ignore` comments (warn_unused_ignores)
- Result: `Success: no issues found in 7 source files`

### Learnings
- Third-party libraries without stubs require mypy configuration
- `warn_unused_ignores` helps clean up type comments
- Type annotations improve code maintainability
- mypy catches real bugs (e.g., missing imports, wrong types)

## Performance Considerations

### TF-IDF Computation
- TF-IDF matrix is sparse (most genre combinations don't exist)
- Cosine similarity is O(n²) for all item pairs
- For large catalogs, consider approximate nearest neighbors (ANN)
- Caching similarity scores for frequently-accessed items

### Recommendation Generation
- User-based similarity requires computing item similarity to all user-rated items
- Aggregating similarity scores across user history can be expensive
- Consider caching user-specific similarity matrices
- Popular items can be pre-computed and ranked

### Cold-Start Performance
- Genre filtering is O(n) over catalog
- Popularity ranking is O(n log n) for sorting
- Consider maintaining genre-indexed item lists
- Pre-compute genre-to-items mapping for faster filtering

## Future Improvements

### Model Enhancements
- Add item-to-item similarity caching
- Implement hybrid scoring (content + collaborative)
- Add explanations with confidence scores
- Support more item features (year, director, actors)

### Performance Optimizations
- Use approximate nearest neighbors for large catalogs
- Implement batch recommendation API
- Add incremental model updates (online learning)
- Consider GPU acceleration for similarity computation

### Feature Engineering
- Incorporate temporal dynamics (recent ratings weighted higher)
- Add user demographic features
- Implement content-aware collaborative filtering
- Support clickstream/view history as features

## Week 2 Success Metrics
- ✅ 34 tests passing (target: 25+)
- ✅ 92% coverage for content.py
- ✅ Protocol conformance verified
- ✅ CI-safe fixtures implemented
- ✅ All linting and type checking passing
- ✅ Cold-start handling implemented
- ✅ Documentation updated (README + learning notes)

## References
- TF-IDF: "A Survey of Text Similarity Approaches" (2023)
- Recommendation Systems: "Recommender Systems Handbook" (Ricci et al., 2022)
- Protocols: PEP 544 - Structural Subtyping (Static and Runtime)
- scikit-learn: https://scikit-learn.org/stable/modules/feature_extraction.html
