# Manual Testing Guide - Day 1 Implementation

## Quick Test Verification

### Test 1: Environment Setup Verification
```bash
cd recolab-hybrid-recommender
.\venv\Scripts\python.exe --version
```
**Expected**: Python 3.14.x

### Test 2: Dataset Loading Test
```bash
.\venv\Scripts\python.exe -c "import pandas as pd; ratings = pd.read_csv('data/ml-latest-small/ratings.csv'); print(f'Loaded {len(ratings)} ratings')"
```
**Expected**: `Loaded 100836 ratings`

### Test 3: Data Quality Test
```bash
.\venv\Scripts\python.exe -c "import pandas as pd; ratings = pd.read_csv('data/ml-latest-small/ratings.csv'); print(f'Missing: {ratings.isnull().sum().sum()}'); print(f'Duplicates: {ratings.duplicated().sum()}')"
```
**Expected**: `Missing: 0, Duplicates: 0`

### Test 4: Run Full Data Analysis
```bash
.\venv\Scripts\python.exe notebooks/data_analysis.py
```
**Expected**: Complete analysis output with no errors

### Test 5: Verify Output Files
```bash
dir data\analysis
```
**Expected**: 4 files (3 PNG images + 1 text summary)

### Test 6: Check Analysis Summary
```bash
type data\analysis\data_analysis_summary.txt
```
**Expected**: Comprehensive summary with sparsity (98.30%), user stats, movie stats

## Project Structure Verification

```bash
dir
```
**Expected Structure**:
```
recolab-hybrid-recommender/
├── data/              ✓
├── notebooks/         ✓
├── src/               ✓
├── tests/             ✓
├── venv/              ✓
├── pyproject.toml     ✓
└── README.md          ✓
```

## Key Metrics Verification

### Sparsity Analysis
- **Total Possible Ratings**: 610 users × 9,724 movies = 5,931,640
- **Actual Ratings**: 100,836
- **Sparsity**: 98.30% (should be >95%)

### Data Quality
- **Missing Values**: 0 (should be 0)
- **Duplicates**: 0 (should be 0)
- **Data Types**: int64 for IDs, float64 for ratings (should match)

### Cold Start Analysis
- **Cold Users (≤5 ratings)**: 0 (good - no cold users)
- **Cold Items (≤5 ratings)**: 6,456 (66.39% - significant challenge)

## Visual Verification

### Rating Distribution
- **File**: `data/analysis/rating_distribution.png`
- **Expected**: Bar chart showing ratings 0.5-5.0, highest bars at 3.0-4.0

### User Activity Distribution  
- **File**: `data/analysis/user_activity_distribution.png`
- **Expected**: Histogram showing user rating counts, right-skewed distribution

### Item Popularity Distribution
- **File**: `data/analysis/item_popularity_distribution.png`
- **Expected**: Histogram showing movie rating counts, long-tail distribution

## Troubleshooting

### Issue: Images show errors
**Solution**: Fixed by using `matplotlib.use('Agg')` non-interactive backend

### Issue: Dataset not found
**Solution**: Ensure `data/ml-latest-small/` directory exists with all CSV files

### Issue: Virtual environment not working
**Solution**: Recreate with `python -m venv venv` and reinstall dependencies

### Issue: Import errors
**Solution**: Ensure virtual environment is activated and dependencies installed

## Success Criteria
✅ All 6 manual tests pass
✅ Project structure is clean and organized
✅ Analysis outputs are generated correctly
✅ Visualizations are viewable PNG files
✅ Data quality metrics meet expectations
✅ No errors or warnings in analysis output

## Manual Test Results Summary
```
Test 1 (Python Version): PASS
Test 2 (Dataset Loading): PASS
Test 3 (Data Quality): PASS
Test 4 (Full Analysis): PASS
Test 5 (Output Files): PASS
Test 6 (Summary Check): PASS
```