# RecoLab Hybrid Recommender - Week 1 Implementation

## Project Overview
Portfolio-grade prototype of a hybrid recommendation system for Devnexes AI-06 project. Week 1 focuses on data processing and evaluation foundation.

## Project Structure
```
recolab-hybrid-recommender/
├── data/                      # Dataset and analysis results
│   ├── ml-latest-small/      # MovieLens dataset
│   └── analysis/             # Analysis outputs and visualizations
├── notebooks/                # Data analysis scripts
│   └── data_analysis.py      # Exploratory data analysis
├── src/                      # Source code (future weeks)
├── tests/                    # Test files (future weeks)
├── venv/                     # Python virtual environment
└── pyproject.toml           # Project configuration
```

## Setup Instructions

### 1. Activate Virtual Environment
```bash
# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 2. Verify Dependencies
```bash
pip list
```
Expected packages:
- pandas>=2.0.0
- numpy>=1.24.0
- scikit-learn>=1.3.0
- pytest>=7.0.0
- matplotlib>=3.7.0
- seaborn>=0.12.0

## Manual Testing & Verification (Day 1)

### Test 1: Verify Dataset Loading
```bash
python -c "import pandas as pd; ratings = pd.read_csv('data/ml-latest-small/ratings.csv'); print(f'Loaded {len(ratings)} ratings')"
```
**Expected Output**: `Loaded 100836 ratings`

### Test 2: Run Data Analysis
```bash
python notebooks/data_analysis.py
```
**Expected Output**: 
- Data structure validation
- Sparsity analysis (98.30%)
- Cold start analysis
- Visualization generation

### Test 3: Verify Analysis Results
```bash
type data\analysis\data_analysis_summary.txt
```
**Expected Output**: 
```
=== MovieLens Data Analysis Summary ===

Number of Users: 610
Number of Movies: 9724
Number of Ratings: 100836
Sparsity: 0.9830 (98.30%)
...
```

### Test 4: Check Visualizations
```bash
dir data\analysis
```
**Expected Files**:
- rating_distribution.png
- user_activity_distribution.png  
- item_popularity_distribution.png
- data_analysis_summary.txt

### Test 5: Verify Data Quality
```bash
python -c "import pandas as pd; ratings = pd.read_csv('data/ml-latest-small/ratings.csv'); print(f'Missing: {ratings.isnull().sum().sum()}'); print(f'Duplicates: {ratings.duplicated().sum()}')"
```
**Expected Output**: `Missing: 0, Duplicates: 0`

## Key Findings (Day 1)

### Data Characteristics
- **Users**: 610 active users
- **Movies**: 9,742 movies in catalog
- **Ratings**: 100,836 total ratings
- **Sparsity**: 98.30% (extremely sparse matrix)

### Quality Metrics
- **Data Quality**: No missing values, no duplicates
- **Rating Distribution**: Skewed toward higher ratings (3.0-4.0 most common)
- **User Activity**: Mean 165.30 ratings/user, median 70.50
- **Item Popularity**: Mean 10.37 ratings/movie, median 3.00

### Challenges Identified
- **Cold Start**: 66.39% of movies have ≤5 ratings
- **Popularity Bias**: Strong long-tail distribution
- **Sparsity**: Extremely sparse user-item matrix

## Week 1 Technologies
- **Python 3.14**: Latest stable version with modern features
- **pandas 3.0.3**: Data manipulation and analysis
- **numpy 2.5.1**: Numerical computing foundation
- **scikit-learn 1.9.0**: Machine learning evaluation metrics
- **matplotlib 3.11.0**: Visualization
- **seaborn 0.13.2**: Statistical plotting

## Next Steps (Day 2)
- Implement popularity baseline model
- Create chronological train-test split
- Implement ranking metrics (P@K, R@K, NDCG@K)
- Run baseline evaluation
- Create automated tests

## Data Source
MovieLens dataset from GroupLens Research:
- Citation: F. Maxwell Harper and Joseph A. Konstan, 2015
- License: CC BY-4.0
- URL: https://grouplens.org/datasets/movielens/