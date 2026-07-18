---
id: 001
title: Week 1 Technical Acquisition Record (DEPRECATED — see 002)
stage: plan
date: 2026-07-18
surface: agent
model: claude-sonnet-4
feature: week-1
branch: main
user: Muhammad Hamza
command: Week 1 technical learning documentation
labels: [week-1, technical-acquisition, data-processing, evaluation]
links:
  spec: specs/week-1/spec.md
  ticket: null
  adr: history/adr/001-data-technology-stack-week-1.md, history/adr/002-evaluation-methodology-week-1.md, history/adr/003-model-persistence-and-testing-week-1.md
  pr: null
files:
  - specs/week-1/spec.md
  - specs/week-1/plan.md
  - specs/week-1/tasks.md
  - history/adr/001-data-technology-stack-week-1.md
  - history/adr/002-evaluation-methodology-week-1.md
  - history/adr/003-model-persistence-and-testing-week-1.md
tests:
  - None (planning phase)
---

# Week 1 Technical Acquisition Record

> ## ⚠️ DEPRECATED — READ `technical-acquisition-record-day2.md` (id 002) INSTEAD
> This file (id 001) was written before Day 2 was implemented and contains **two factual errors** that were corrected in id 002. **Do not treat this file as authoritative.**
> 1. **Python version is wrong.** The project runs on **Python 3.14**, not 3.12. (`pyproject.toml` pins `>=3.14`; venv is 3.14.0.) The "3.12" mentions below are stale.
> 2. **The ranking-metric guidance is wrong.** `top_k_accuracy_score` is a **multiclass-label ranking** metric, **not** a Top-N recommender metric, and `sklearn.metrics` has **no** `precision_at_k`/`recall_at_k` (they don't exist) and **no NDCG@K**. Day 2 hand-implements P@K/R@K/NDCG@K in `metrics.py`. The `top_k_accuracy_score` usage and the `from sklearn.metrics import precision_at_k, recall_at_k` lines in §14/§15 are **incorrect** and must not be copied.
> The remaining "kitchen analogy" background is kept for context only. For the correct, complete Week 1 + Day 2 record, use **`technical-acquisition-record-day2.md`**.

## Executive Summary
Week 1 establishes the data processing and evaluation foundation for the RecoLab recommendation system prototype. This document provides deep technical understanding of the tools and technologies used: Python (3.14 — see banner), pandas, numpy, and scikit-learn. Each tool is examined in detail - understanding the tools, their purposes, how they work, and how we use them to build our recommendation system recipe.

> **Correction:** Python version is **3.14**, not 3.12 as stated in the original summary above. See the deprecation banner.

## 1. Python 3.14 - The Kitchen Foundation  *(correction: id 001 originally titled this "3.12"; project pins >=3.14)*

### Tool Name
Python 3.14+ (project pin: `requires-python = ">=3.14"`; venv is 3.14.0) — *correction: id 001 originally said 3.12*

### Version
Python 3.14.x (latest stable as of 2026-07-18) — *correction: id 001 originally said 3.12*

### Primary Purpose
Python serves as the foundational programming language and execution environment for the entire RecoLab project. It's the "kitchen" where all other tools (pandas, numpy, scikit-learn) operate together to process data and build recommendation models.

### Core Functionality
Python 3.12 provides:
- **Enhanced f-strings**: Arbitrary nesting, backslash support, same quote reuse within expressions
- **Performance improvements**: Faster execution, better memory management
- **Modern random number generation**: `numpy.random.default_rng()` for reproducibility
- **Type hints and static typing**: Better code quality and IDE support
- **Async/await patterns**: Future extensibility for concurrent operations

### How It Works Internally
Python 3.12 uses:
- **CPython interpreter**: Compiles Python bytecode to machine code
- **Memory management**: Automatic garbage collection with reference counting
- **Dynamic typing**: Variables can hold any type, checked at runtime
- **GIL (Global Interpreter Lock)**: Thread safety mechanism (one thread executes Python bytecode at a time)
- **Import system**: Module loading and dependency resolution

### Key Components and Architecture
- **Interpreter**: Reads and executes Python code
- **Standard Library**: Built-in modules (os, sys, json, etc.)
- **Package Manager (pip)**: Installs third-party libraries
- **Virtual Environment**: Isolated Python environments for dependency management
- **Type System**: Dynamic typing with optional static type hints

### Data Flow and Processing
Python code execution flow:
1. **Parsing**: Python source code → Abstract Syntax Tree (AST)
2. **Compilation**: AST → Python bytecode
3. **Execution**: Bytecode interpreter → Machine code
4. **Memory Management**: Reference counting + garbage collection

### Performance Characteristics
- **Interpreted language**: Slower than compiled languages (C++, Rust)
- **GIL limitation**: Limits true parallelism for CPU-bound tasks
- **I/O performance**: Excellent for I/O-bound tasks (network, disk operations)
- **Memory overhead**: Higher memory usage compared to lower-level languages

## 2. Project Integration

### How We're Using It
Python 3.12 serves as the primary development environment:
- **Script execution**: Running data processing and model training scripts
- **Package management**: Installing pandas, numpy, scikit-learn via pip
- **Virtual environment**: Creating isolated environment for project dependencies
- **Type hints**: Adding type annotations for better code quality
- **Jupyter integration**: Running exploratory data analysis notebooks

### Integration Points
- **pandas**: Data manipulation library built on Python
- **numpy**: Numerical computing foundation for Python scientific computing
- **scikit-learn**: Machine learning library using Python and numpy
- **pytest**: Testing framework for Python
- **pickle**: Python's built-in serialization module

### Configuration and Setup
```python
# Virtual environment creation
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Dependencies installation
pip install pandas numpy scikit-learn pytest jupyter

# requirements.txt for reproducibility
pandas>=2.0.0
numpy>=1.24.0
scikit-learn>=1.3.0
pytest>=7.0.0
jupyter>=1.0.0
```

### Data Structures Used
- **Lists**: Ordered collections for storing ratings and movie IDs
- **Dictionaries**: Key-value pairs for movie metadata and user preferences
- **DataFrames**: (from pandas) Tabular data structures for ratings and movies
- **Arrays**: (from numpy) Multi-dimensional arrays for numerical computations
- **Sets**: Unordered collections for unique values (genres, tags)

## 3. Implementation Details

### Code Patterns and Best Practices
```python
# Modern random number generation (Python 3.12)
import numpy as np
rng = np.random.default_rng(42)  # Fixed seed for reproducibility
random_data = rng.random((3, 4))  # Deterministic random array

# Type hints for better code quality
from typing import List, Dict, Tuple
def process_ratings(ratings: List[Dict]) -> pd.DataFrame:
    """Process raw ratings into structured DataFrame."""
    pass

# Context managers for resource management
with open('data/ratings.csv', 'r') as f:
    data = pd.read_csv(f)
```

### Key Functions and Methods
- **`default_rng(seed)`**: Creates reproducible random number generator
- **`open()` with context managers**: Safe file handling
- **Type hints**: `List[str]`, `Dict[str, int]`, `Tuple[int, int]`
- **f-strings**: String formatting with expressions: `f"User {user_id} has {count} ratings"`

### Error Handling and Edge Cases
```python
try:
    data = pd.read_csv('data/ratings.csv')
except FileNotFoundError:
    print("Dataset file not found. Please download MovieLens dataset.")
except pd.errors.EmptyDataError:
    print("Dataset file is empty. Please verify download.")
```

### Performance Optimizations
- **Use list comprehensions** instead of loops for simple transformations
- **Use generators** for large datasets to reduce memory usage
- **Vectorized operations** via numpy instead of Python loops
- **Avoid global variables** for better function performance

## 4. Conceptual Understanding

### Key Concepts and Terminology
- **Interpreted vs Compiled**: Python is interpreted (code executed line-by-line)
- **GIL (Global Interpreter Lock)**: Thread safety mechanism limiting true parallelism
- **Dynamic Typing**: Variable types determined at runtime, not compile time
- **Virtual Environment**: Isolated Python environment for dependency management
- **Bytecode**: Intermediate representation between source code and machine code

### Why This Tool/Technology
- **Ecosystem**: Unmatched library ecosystem for data science and ML
- **Readability**: Clean syntax that's easy to write and maintain
- **Community**: Large community, extensive documentation, many learning resources
- **Prototyping**: Rapid development cycle ideal for prototype projects
- **Integration**: Seamless integration with data science libraries

### Alternatives Considered
- **Python 3.11**: Stable but lacks latest performance improvements
- **Python 3.13**: Beta version, potential stability issues
- **R**: Excellent for statistics but steeper learning curve for web integration
- **Julia**: High performance but smaller ecosystem and community

### Trade-offs and Limitations
- **Performance**: Slower than compiled languages (C++, Rust)
- **Parallelism**: GIL limits true parallelism for CPU-bound tasks
- **Memory**: Higher memory overhead compared to lower-level languages
- **Deployment**: Requires runtime environment (not standalone executable)

## 5. pandas - The Data Processing Workhorse

### Tool Name
pandas (latest stable version)

### Version
pandas 2.0+ (latest stable as of 2026-07-18)

### Primary Purpose
pandas is the primary data manipulation library for loading, cleaning, transforming, and analyzing structured data. It's the "prep station" in our kitchen where raw ingredients (MovieLens dataset) are cleaned, organized, and prepared for cooking (model training).

### Core Functionality
pandas provides:
- **DataFrame**: 2D tabular data structure (like Excel spreadsheets programmatically)
- **Series**: 1D labeled array (like a single column with row labels)
- **Time series functionality**: Native support for datetime operations
- **Data I/O**: Read/write CSV, JSON, SQL, Excel, and many other formats
- **Data cleaning**: Handle missing values, duplicates, data type conversions
- **Grouping and aggregation**: Split-apply-combine operations for data analysis
- **Merging and joining**: Combine multiple datasets like SQL JOINs

### How It Works Internally
pandas is built on top of numpy:
- **DataFrame**: 2D numpy array with row/column labels and metadata
- **Series**: 1D numpy array with index labels
- **Cython optimization**: Performance-critical code written in C for speed
- **Memory management**: Efficient memory handling for large datasets
- **Block operations**: Processes data in chunks for memory efficiency

### Key Components and Architecture
- **DataFrame**: 2D labeled data structure with rows (index) and columns
- **Series**: 1D labeled data structure (single column)
- **Index**: Row labels for DataFrames and Series
- **GroupBy**: Split-apply-combine pattern for grouped operations
- **MultiIndex**: Hierarchical indexing for complex data organization
- **TimeSeries**: DatetimeIndex with time-specific operations

### Data Flow and Processing
pandas data processing pipeline:
1. **Loading**: `pd.read_csv()` → DataFrame in memory
2. **Cleaning**: `dropna()`, `fillna()`, `drop_duplicates()`
3. **Transformation**: `groupby()`, `agg()`, `apply()`
4. **Analysis**: Filtering, sorting, statistical operations
5. **Exporting**: `to_csv()`, `to_json()`, `to_excel()`

### Performance Characteristics
- **Memory intensive**: Loads entire dataset into memory
- **Vectorized operations**: Fast for large datasets using numpy backend
- **Chunk processing**: Can process large files in chunks for memory efficiency
- **I/O bottleneck**: File reading/writing can be slow for very large datasets

## 6. Project Integration

### How We're Using It
pandas handles all data operations in Week 1:
- **Dataset loading**: `pd.read_csv('ratings.csv')` loads MovieLens data
- **Data validation**: Checking data types, missing values, data integrity
- **Chronological splitting**: Time series sorting and per-user splitting
- **Popularity calculation**: `groupby('movie_id').count()` for baseline
- **Sparsity analysis**: Matrix density calculations and statistics

### Integration Points
- **numpy**: pandas uses numpy arrays for efficient numerical operations
- **scikit-learn**: pandas DataFrames can be converted to numpy arrays for ML
- **Python**: pandas is a Python library, uses Python's object system
- **pickle**: pandas DataFrames can be serialized for persistence

### Configuration and Setup
```python
import pandas as pd

# Load dataset with datetime parsing
ratings = pd.read_csv('data/ratings.csv', parse_dates=['timestamp'])

# Sort by timestamp for chronological split
ratings = ratings.sort_values(['userId', 'timestamp'])

# Group by user for per-user operations
user_groups = ratings.groupby('userId')

# Calculate popularity
popularity = ratings.groupby('movie_id').agg({'rating': 'count'}).sort_values('rating', ascending=False)
```

### Data Structures Used
- **DataFrame**: 2D data structure for ratings (userId, movieId, rating, timestamp)
- **Series**: 1D data structure for single columns (ratings, timestamps)
- **DatetimeIndex**: Time-based index for chronological operations
- **GroupBy**: Grouped data structure for per-user operations

## 7. Implementation Details

### Code Patterns and Best Practices
```python
# Modern pandas time series handling
ratings = pd.read_csv('ratings.csv', parse_dates=['timestamp'])
ratings = ratings.sort_values(['userId', 'timestamp'])

# Per-user chronological split
def split_user_ratings(group):
    split_point = int(len(group) * 0.8)
    return group.iloc[:split_point], group.iloc[split_point:]

train_test = ratings.groupby('userId').apply(split_user_rating)
```

### Key Functions and Methods
- **`read_csv()`**: Load CSV files into DataFrame
- **`groupby()`**: Group data by column(s) for aggregation
- **`sort_values()`**: Sort DataFrame by column(s)
- **`apply()`**: Apply function to each group/element
- **`agg()`**: Aggregate functions (sum, mean, count, etc.)

### Error Handling and Edge Cases
```python
# Handle missing data
ratings = ratings.dropna(subset=['userId', 'movieId', 'rating'])

# Handle duplicate entries
ratings = ratings.drop_duplicates()

# Handle edge case: user with single rating
def safe_split(group):
    if len(group) < 2:
        return group, pd.DataFrame()  # All to train, empty test
    split_point = int(len(group) * 0.8)
    return group.iloc[:split_point], group.iloc[split_point:]
```

### Performance Optimizations
- **Use categorical data types** for repeated string values (movie IDs, genres)
- **Use `chunksize` parameter** for reading large files in chunks
- **Vectorized operations** instead of loops where possible
- **Avoid `.apply()` with Python functions** on large DataFrames

## 8. Conceptual Understanding

### Key Concepts and Terminology
- **DataFrame**: 2D labeled data structure (rows + columns)
- **Series**: 1D labeled data structure (single column)
- **Index**: Row labels that enable fast lookups and alignment
- **GroupBy**: Split-apply-combine pattern for grouped operations
- **TimeSeries**: Data indexed by timestamps with time-specific operations
- **Vectorization**: Applying operations to entire arrays at once (not loops)

### Why This Tool/Technology
- **Data manipulation excellence**: Unmatched for structured data operations
- **Time series support**: Native datetime handling for chronological data
- **Integration**: Seamless integration with numpy and scikit-learn
- **Productivity**: High-level API reduces development time significantly
- **Community**: Extensive documentation and community support

### Alternatives Considered
- **Polars**: Faster but smaller ecosystem and less mature
- **Dask**: Better for very large datasets but overkill for MovieLens
- **Pure Python**: Too slow and verbose for data manipulation
- **SQL databases**: Overkill for prototype, pandas CSV processing sufficient

### Trade-offs and Limitations
- **Memory usage**: Loads entire dataset into memory (not suitable for TB-scale data)
- **Learning curve**: Complex API with many methods to learn
- **Performance**: Slower than optimized databases for very large datasets
- **File formats**: Limited support for some exotic file formats

## 9. numpy - The Numerical Computing Foundation

### Tool Name
numpy (latest stable version)

### Version
numpy 1.24+ (latest stable as of 2026-07-18)

### Primary Purpose
numpy provides the foundation for numerical computing in Python. It's the "knife set" in our kitchen - the fundamental tools for precise numerical operations, mathematical calculations, and efficient array manipulations that underpin all data science operations.

### Core Functionality
numpy provides:
- **ndarray**: Multi-dimensional array object for efficient numerical operations
- **Mathematical functions**: Trigonometry, logarithms, exponential, linear algebra
- **Random number generation**: Modern `default_rng()` for reproducibility
- **Broadcasting**: Efficient operations on arrays of different shapes
- **Linear algebra**: Matrix operations, eigenvalues, decompositions
- **Fourier transforms**: Signal processing capabilities

### How It Works Internally
numpy uses:
- **C arrays**: Contiguous memory blocks for efficient storage
- **Vectorized operations**: Apply operations to entire arrays at once (no Python loops)
- **SIMD instructions**: CPU-level parallelism for numerical calculations
- **Memory layout**: Contiguous memory for cache efficiency
- **Type system**: Fixed data types for performance (int32, float64, etc.)

### Key Components and Architecture
- **ndarray**: N-dimensional array object with fixed data type
- **dtype**: Data type specification (int32, float64, bool, etc.)
- **shape**: Array dimensions (rows, columns, depth)
- **strides**: Memory layout for efficient slicing
- **ufunc**: Universal functions for element-wise operations
- **random**: Modern random number generation with PCG64 algorithm

### Data Flow and Processing
numpy array operations:
1. **Creation**: `np.array()`, `np.zeros()`, `np.ones()`, `np.random()`
2. **Operations**: Vectorized arithmetic, mathematical functions
3. **Indexing**: Fancy indexing, boolean indexing, slicing
4. **Aggregation**: `sum()`, `mean()`, `std()`, `min()`, `max()`
5. **Linear algebra**: `dot()`, `matmul()`, `eig()`, `svd()`

### Performance Characteristics
- **Vectorized operations**: Orders of magnitude faster than Python loops
- **Memory efficient**: Contiguous memory layout, fixed data types
- **Cache friendly**: Memory layout optimized for CPU cache
- **SIMD acceleration**: CPU-level parallelism for numerical calculations

## 10. Project Integration

### How We're Using It
numpy provides the numerical foundation for Week 1:
- **Reproducibility**: `np.random.default_rng(42)` for deterministic random operations
- **Array operations**: Efficient numerical calculations for metrics
- **Data type handling**: Fixed data types for memory efficiency
- **Integration**: Underpins pandas and scikit-learn operations

### Integration Points
- **pandas**: Uses numpy arrays internally for DataFrame operations
- **scikit-learn**: Uses numpy arrays for ML model inputs
- **Python**: numpy is a Python library, extends Python with numerical capabilities
- **Metrics**: Custom metric calculations using numpy operations

### Configuration and Setup
```python
import numpy as np

# Modern reproducible random number generation
rng = np.random.default_rng(42)

# Generate random data
random_data = rng.random((3, 4))  # Deterministic 3x4 array

# Array operations
array_a = np.array([1, 2, 3, 4, 5])
array_b = np.array([10, 20, 30, 40, 50])
result = array_a + array_b  # Element-wise addition

# Aggregation operations
mean_value = np.mean(array_a)
sum_value = np.sum(array_a)
```

### Data Structures Used
- **ndarray**: N-dimensional arrays for numerical data
- **dtype**: Data type objects (int32, float64, bool, etc.)
- **Generator**: Random number generator for reproducibility

## 11. Implementation Details

### Code Patterns and Best Practices
```python
# Modern reproducible random number generation
import numpy as np
rng = np.random.default_rng(42)  # Always use seed for reproducibility

# Vectorized operations (fast)
squared_values = np.array([1, 2, 3, 4, 5]) ** 2

# Boolean indexing (efficient filtering)
condition = np.array([1, 2, 3, 4, 5]) > 3
filtered = np.array([1, 2, 3, 4, 5])[condition]

# Reshaping for different operations
matrix = np.array([[1, 2], [3, 4]])
flattened = matrix.flatten()  # [1, 2, 3, 4]
```

### Key Functions and Methods
- **`default_rng(seed)`**: Create reproducible random number generator
- **`array()`**: Create numpy arrays from Python lists
- **`mean()`, `sum()`, `std()`**: Statistical aggregation functions
- **`dot()`, `matmul()`**: Matrix multiplication operations
- **`zeros()`, `ones()`, `random()`: Array creation functions

### Error Handling and Edge Cases
```python
# Handle shape mismatches
try:
    result = np.array([1, 2, 3]) + np.array([10, 20])
except ValueError:
    print("Shape mismatch for array operation")

# Handle division by zero
array = np.array([1, 2, 0, 4])
with np.errstate(divide='ignore'):
    result = 10 / array  # inf for division by zero
```

### Performance Optimizations
- **Vectorized operations**: Always prefer over Python loops
- **In-place operations**: Use `+=` instead of `array = array + value`
- **Pre-allocation**: Pre-allocate arrays instead of growing in loops
- **Data types**: Use appropriate data types (float32 vs float64) for memory efficiency

## 12. Conceptual Understanding

### Key Concepts and Terminology
- **Vectorization**: Applying operations to entire arrays at once (no loops)
- **Broadcasting**: Operating on arrays of different shapes automatically
- **Memory layout**: How arrays are stored in memory (row-major vs column-major)
- **dtype**: Data type specification for memory efficiency
- **SIMD**: Single Instruction, Multiple Data (CPU-level parallelism)

### Why This Tool/Technology
- **Performance**: Orders of magnitude faster than Python loops for numerical operations
- **Foundation**: Underpins pandas and scikit-learn operations
- **Reproducibility**: Modern random number generation with guaranteed reproducibility
- **Community**: Industry standard for numerical computing in Python
- **Documentation**: Extensive documentation and community support

### Alternatives Considered
- **Pure Python**: Too slow for numerical operations
- **Julia**: Faster performance but smaller ecosystem
- **C/C++**: High performance but much more complex development
- **TensorFlow/PyTorch**: Overkill for simple numerical operations in Week 1

### Trade-offs and Limitations
- **Learning curve**: Requires understanding of array operations and broadcasting
- **Memory usage**: Can be memory-intensive for very large arrays
- **GIL limitation**: Still subject to Python's GIL for CPU-bound operations
- **Data types**: Fixed data types can be less flexible than Python objects

## 13. scikit-learn - The Machine Learning Toolkit

### Tool Name
scikit-learn (latest stable version)

### Version
scikit-learn 1.3+ (latest stable as of 2026-07-18)

### Primary Purpose
scikit-learn provides machine learning algorithms and evaluation metrics. It's the "specialized appliances" in our kitchen - the blender, food processor, and measuring tools that enable us to transform ingredients (data) into finished dishes (recommendations) and assess their quality.

### Core Functionality
scikit-learn provides:
- **Machine learning algorithms**: Classification, regression, clustering, dimensionality reduction
- **Model evaluation**: Metrics for accuracy, precision, recall, F1-score, AUC, etc.
- **Ranking metrics**: top_k_accuracy_score, label_ranking_average_precision_score
  > **Correction (id 002):** `top_k_accuracy_score` is **multiclass-label ranking**, NOT a Top-N recommender metric, and scikit-learn ships **no NDCG@K** and **no** `precision_at_k`/`recall_at_k`. RecoLab hand-implements P@K/R@K/NDCG@K in `metrics.py`.
- **Data preprocessing**: Scaling, encoding, feature extraction
- **Model selection**: Cross-validation, hyperparameter tuning
- **Pipeline**: Data preprocessing and model training workflow orchestration

### How It Works Internally
scikit-learn uses:
- **numpy arrays**: All inputs must be numpy arrays or array-like structures
- **Consistent API**: `.fit()`, `.predict()`, `.transform()` pattern across all algorithms
- **Type checking**: Input validation and type conversion
- **Optimized algorithms**: C/Cython implementations for performance
- **Cross-validation**: Built-in support for model evaluation

### Key Components and Architecture
- **Estimators**: Objects implementing `.fit()`, `.predict()`, `.transform()` pattern
- **Transformers**: Data preprocessing objects (StandardScaler, LabelEncoder)
- **Metrics**: Evaluation functions for model performance
- **Model selection**: Cross-validation and hyperparameter tuning tools
- **Pipeline**: Sequential transformation and modeling workflow

### Data Flow and Processing
scikit-learn machine learning pipeline:
1. **Data preparation**: numpy arrays as input
2. **Training**: `.fit(X_train, y_train)` learns model parameters
3. **Prediction**: `.predict(X_test)` generates predictions
4. **Evaluation**: Metrics compare predictions against ground truth
5. **Transformation**: `.transform(X)` applies learned transformations

### Performance Characteristics
- **CPU-bound**: Most algorithms are CPU-intensive
- **Memory efficient**: Designed for memory-constrained environments
- **Scalability**: Some algorithms support out-of-core processing
- **Batch processing**: Designed for batch training and prediction

## 14. Project Integration

### How We're Using It
scikit-learn provides the ML *framework* (split helpers, pipeline API) for Week 1:
- **Evaluation metrics**: **NOT** for Top-N ranking — see correction below.
- **Custom metrics**: Precision@K, Recall@K, NDCG@K are **hand-implemented** in `metrics.py` (numpy), because scikit-learn has no NDCG@K and `top_k_accuracy_score` is the wrong semantic.
- **Future weeks**: Will provide collaborative filtering and content-based algorithms.

> **Correction (id 002 — IMPORTANT):** Do **not** use `top_k_accuracy_score` for recommendation evaluation. It scores a single multiclass prediction (true label within top-k score positions), which is semantically different from Top-N hit-rate over a relevance set. And `sklearn.metrics.precision_at_k` / `recall_at_k` **do not exist**. The original §15 import `from sklearn.metrics import precision_at_k, recall_at_k` would raise `ImportError`. RecSys metrics are hand-written in `metrics.py`.

### Integration Points
- **numpy**: scikit-learn uses numpy arrays for all inputs/outputs
- **pandas**: pandas DataFrames can be converted to numpy arrays
- **Python**: scikit-learn is a Python library with consistent API
- **Model training**: Future weeks will use scikit-learn for ML algorithms

### Configuration and Setup
```python
# Correct approach (id 002): hand-implement Top-N metrics with numpy.
# scikit-learn provides NO NDCG@K and NO precision_at_k / recall_at_k.
# top_k_accuracy_score is multiclass-label ranking — NOT a recsys metric.
from recolab.metrics import precision_at_k, recall_at_k, ndcg_at_k  # our hand-written module
```

### Data Structures Used
- **numpy arrays**: All inputs and outputs are numpy arrays
- **Arrays of predictions**: Score arrays for ranking evaluation
- **Binary indicator matrices**: Multi-label classification representation

## 15. Implementation Details

### Code Patterns and Best Practices
```python
# CORRECTED (id 002): the import below does NOT exist in scikit-learn and
# top_k_accuracy_score is the wrong metric for Top-N recsys. Use our hand-written
# metrics in metrics.py instead.
from recolab.metrics import precision_at_k, recall_at_k, ndcg_at_k
```

### Key Functions and Methods
- **`top_k_accuracy_score()`**: Multiclass-label ranking metric — **NOT for Top-N recsys** (see id 002 correction).
- **`label_ranking_average_precision_score()`**: Average precision for multi-label ranking
- **`precision_score()`**: Standard precision for binary/multiclass classification
- **`recall_score()`**: Standard recall for binary/multiclass classification
- **RecoLab Top-N metrics (hand-written)**: `recolab.metrics.precision_at_k`, `.recall_at_k`, `.ndcg_at_k` — the correct tools for this project.

### Error Handling and Edge Cases
```python
# Handle edge case: k larger than number of predictions
def safe_precision_at_k(y_true, y_score, k=10):
    k = min(k, len(y_score))
    if k == 0:
        return 0.0
    return precision_at_k(y_true, y_score, k=k)

# Handle empty predictions
if len(y_score) == 0:
    return 0.0
```

### Performance Optimizations
- **Vectorized operations**: Use numpy operations instead of loops
- **Batch processing**: Process multiple users simultaneously
- **Memory efficiency**: Use appropriate data types (float32 vs float64)

## 16. Conceptual Understanding

### Key Concepts and Terminology
- **Estimator API**: `.fit()`, `.predict()`, `.transform()` pattern
- **Ranking metrics**: Metrics that evaluate ordering quality (not just accuracy)
- **Top-K accuracy**: Fraction of true labels in top-k predictions
- **NDCG**: Normalized Discounted Cumulative Gain (accounts for ranking position)
- **Multi-label ranking**: Evaluating ranking when items can have multiple labels

### Why This Tool/Technology
- **Comprehensive metrics**: Provides extensive evaluation metrics
- **Consistent API**: Unified interface across all algorithms
- **Performance optimization**: C/Cython implementations for speed
- **Community standard**: Industry standard for ML evaluation
- **Extensive documentation**: Well-documented with many examples

### Alternatives Considered
- **Custom metric implementation**: More control but development time
- **TensorFlow/PyTorch metrics**: Overkill for prototype evaluation
- **LightFM**: Specialized for recommendation systems but less general
- **Surprise**: Specialized for collaborative filtering but narrower scope

### Trade-offs and Limitations
- **CPU-only**: No GPU acceleration for most algorithms
- **Limited deep learning**: Not designed for neural networks
- **Memory constraints**: Some algorithms require significant memory
- **Batch processing**: Not designed for streaming/online learning

## 17. Learning Outcomes

### What I Learned
- **Python 3.12 features**: Enhanced f-strings, performance improvements, modern random generation
- **pandas mastery**: Time series data handling, chronological splitting, groupby operations
- **numpy fundamentals**: Vectorized operations, reproducibility with `default_rng()`
- **scikit-learn metrics**: Ranking metrics for recommendation evaluation
- **Integration patterns**: How these tools work together in a data pipeline

### Skills Developed
- **Modern Python practices**: Using latest stable versions, reproducibility patterns
- **Data manipulation**: pandas for data cleaning, transformation, analysis
- **Numerical computing**: numpy for efficient array operations
- **Machine learning evaluation**: Ranking metrics for recommendation systems
- **Technical documentation**: Understanding internal workings of each tool

### Challenges Overcome
- **Timeline constraint**: Prioritized essential features while maintaining quality
- **Prototype scope understanding**: Clarified this is a portfolio-grade prototype, not production
- **Complex metric implementation**: NDCG@K implementation complexity balanced with timeline
- **Testing strategy**: Basic automated testing foundation within time constraints

### Connections to Other Technologies
- **pandas ↔ numpy**: pandas uses numpy arrays internally
- **numpy ↔ scikit-learn**: scikit-learn uses numpy arrays for ML operations
- **Python ↔ all tools**: Python provides the execution environment
- **All tools ↔ evaluation**: Combined to create evaluation framework

## 18. Interview Preparation

### Technical Discussion Points
- **Python 3.14 choice**: The project pins `>=3.14` (venv is 3.14.0). **Correction:** id 001 originally said 3.12 — see deprecation banner.
- **pandas time series**: Why chronological splitting requires time series functionality
- **numpy reproducibility**: Why `default_rng()` is preferred over legacy `seed()`
- **Ranking metrics**: Why P@K, R@K, NDCG@K are essential for recommendation evaluation
- **Prototype scope**: Understanding this is a portfolio-grade prototype, not production system

### Decision-Making Examples
- **Technology stack**: Chose Python **3.14** (correction: id 001 said 3.12 — see banner) for modern features and ecosystem
- **Chronological split**: Chose over random split to prevent data leakage
- **Ranking metrics**: Chose over accuracy for recommendation quality evaluation
- **Baseline first**: Implemented popularity baseline to establish performance floor

### Problem-Solving Examples
- **Data sparsity**: Handled by documenting characteristics and using ranking metrics
- **Reproducibility**: Solved using modern random number generation with fixed seed
- **Timeline constraints**: Addressed by prioritizing essential features and documenting trade-offs
- **Prototype requirements**: Clarified scope boundaries and quality expectations

### Key Takeaways for Explanation
- **Python 3.14** (not 3.12 — see banner): Foundation with modern features and performance improvements
- **pandas**: Data manipulation workhorse with time series support for chronological data
- **numpy**: Numerical foundation with vectorized operations and reproducibility
- **scikit-learn**: ML framework; but Top-N ranking metrics are hand-written in `recolab.metrics` (sklearn has no NDCG@K / precision_at_k / recall_at_k)
- **Integration**: All tools work together in a cohesive data pipeline for evaluation

## 19. References and Resources
- **Python 3.12 docs**: https://docs.python.org/3.12/whatsnew.html
- **pandas docs**: https://pandas.pydata.org/docs/
- **numpy docs**: https://numpy.org/doc/
- **scikit-learn docs**: https://scikit-learn.org/stable/
- **Context7 research**: Latest documentation and best practices for all tools
- **Master files**: spec-architecture-recolab-hybrid-recommender.md, Devnexes_AI_ML_Individual_Project_Plans.pdf

---
## Prompt
User requested comprehensive SDD document refinement and detailed technical learning documentation following the "kitchen analogy" - deep understanding of tools, their purposes, internal workings, and integration in the recommendation system recipe. Addressed IVP validation findings and created detailed technical acquisition record.

## Response Snapshot
Refined Week 1 SDD documents to address all IVP findings, added prototype context, NDCG@K metric, model persistence, sparsity documentation, comprehensive README, and testing strategy. Created detailed technical acquisition record explaining Python 3.12, pandas, numpy, and scikit-learn with deep technical understanding following kitchen analogy.

## Outcome
- ✅ Impact: Week 1 SDD documents now fully compliant with master project requirements
- 🧪 Tests: None (planning phase)
- 📁 Files: Updated 4 SDD documents, added 1 ADR, updated 2 ADRs, created 1 template, created 1 technical record
- 🔁 Next prompts: Begin Day 1 implementation tasks
- 🧠 Reflection: Deep technical understanding established for all Week 1 technologies