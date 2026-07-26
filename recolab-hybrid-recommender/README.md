# RecoLab Hybrid Recommender - Week 2 Content Model Implementation

## Project Overview
Portfolio-grade prototype of a hybrid recommendation system for Devnexes AI-06 project. Week 2 implements the content-based recommendation model with cold-start handling.

## Week 2 Status
**Completion**: 83.3% (Phase 1-6 complete)

### Completed Components
- ✅ Phase 1: Setup & Hygiene - Dependencies updated, 32 baseline tests passing
- ✅ Phase 2: Interfaces - Shared protocols (Recommender, ColdStartHandler, FeatureError)
- ✅ Phase 3: Test Fixtures - CI-safe sample fixtures (50 users, 5858 ratings)
- ✅ Phase 4a-4f: ContentModel - Full implementation with TF-IDF + cosine similarity
- ✅ Phase 5: Test Suite - 34 tests (target: 25+ exceeded)
- ✅ Phase 6: Integration Gate - All checks pass (ruff, mypy, pytest)

### Remaining Work (Weeks 3-6)
- ⏳ Week 3: Collaborative filtering model
- ⏳ Week 4: Hybrid model (content + collaborative)
- ⏳ Week 5: UI development
- ⏳ Week 6: Deployment

## Project Structure
```
recolab-hybrid-recommender/
├── data/                      # Dataset and analysis results
│   ├── ml-latest-small/      # MovieLens dataset
│   └── analysis/             # Analysis outputs and visualizations
├── src/recolab/              # Source code
│   ├── __init__.py           # Public API
│   ├── baseline.py           # Popularity baseline (Week 1)
│   ├── content.py            # Content-based model (Week 2)
│   ├── interfaces.py         # Shared protocols (Week 2)
│   ├── metrics.py            # Ranking metrics (Week 1)
│   ├── persistence.py        # Model persistence (Week 1)
│   └── split.py              # Data splitting (Week 1)
├── tests/                    # Test files
│   ├── fixtures/             # CI-safe sample data
│   ├── conftest.py            # Pytest configuration
│   ├── test_baseline.py      # Baseline tests (Week 1)
│   ├── test_content.py       # ContentModel tests (Week 2)
│   ├── test_fixtures.py      # Fixture validation
│   ├── test_interfaces.py    # Protocol conformance tests
│   ├── test_metrics.py       # Metrics tests (Week 1)
│   └── test_persistence.py   # Persistence tests (Week 1)
├── .github/workflows/         # CI configuration
│   └── ci.yml                # GitHub Actions workflow
├── notebooks/                # Data analysis scripts
├── venv/                     # Python virtual environment
└── pyproject.toml           # Project configuration
```

## Week 2 Implementation

### ContentModel Features
- **TF-IDF Feature Extraction**: Converts movie genres to numerical features
- **Cosine Similarity**: Computes item-to-item similarity scores
- **User-Based Recommendations**: Uses user's rated items to find similar content
- **Cold-Start Handling**: Recommends based on genre preferences without history
- **Persistence**: Save/load models with pickle serialization
- **Protocol Conformance**: Satisfies both Recommender and ColdStartHandler protocols

### Key Methods
- `fit(ratings, movies)`: Train model on ratings and item metadata
- `recommend(user_id, k, exclude_items)`: Get personalized recommendations
- `similar_items(item_id, k)`: Find items similar to a given item
- `recommend_cold_start(genres, liked_movie_ids, k)`: Handle new users
- `get_explanation(user_id, item_id)`: Generate recommendation explanations
- `save(path) / load(path)`: Model persistence

## Setup Instructions

### 1. Activate Virtual Environment
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Install Dependencies
```bash
pip install -e ".[dev]"
```

### 3. Run Tests
```bash
# All tests (CI-safe, excludes full dataset)
pytest -m "not full_dataset"

# All tests including full dataset
pytest

# With coverage
pytest --cov=src/recolab --cov-report=html
```

### 4. Linting & Type Checking
```bash
# Ruff linting
ruff check src/

# Ruff formatting
ruff format src/

# MyPy type checking
mypy src/
```

## Test Results
- **Total Tests**: 73 passed, 1 skipped, 2 deselected
- **Coverage**: 84% overall, 92% for content.py
- **Protocol Conformance**: ✅ ContentModel satisfies both Recommender and ColdStartHandler
- **CI Safety**: ✅ All CI tests pass without full dataset

## Technologies (Week 2)
- **Python 3.14**: Latest stable version
- **scikit-learn 1.9.0**: TF-IDF vectorization and cosine similarity
- **pandas 3.0.3**: Data manipulation
- **numpy 2.5.1**: Numerical computing
- **pytest 9.1.1**: Testing framework
- **ruff 0.6.0**: Fast Python linter
- **mypy 1.10.0**: Static type checking

## Week 2 Learnings

### Content-Based Filtering
- TF-IDF effectively captures genre similarities
- Cosine similarity provides meaningful item-to-item relationships
- Cold-start handling is essential for user onboarding
- Genre-based recommendations work well for new users

### Protocol-Oriented Design
- Protocols enable duck-typing without inheritance
- Shared interfaces ensure consistency across models
- Runtime protocol checking enables type-safe code
- Protocol conformance tests prevent interface drift

### CI Safety
- Sample fixtures enable fast CI without large datasets
- Markers separate CI tests from integration tests
- GitHub Actions provides automated validation
- Coverage tracking ensures quality gates

### Persistence Strategy
- Bundle pattern (to_bundle/from_bundle) for serialization
- Include all state (features, matrix, ratings) for roundtrip safety
- Pickle format for simplicity (protocol 5)
- Type annotations improve deserialization safety

## Next Steps (Week 3)
- Implement collaborative filtering model (user-based, item-based)
- Add collaborative filtering to ColdStartHandler protocol
- Create hybrid model combining content + collaborative signals
- Compare model performance against baseline