# Troubleshooting & FAQ

Common issues, error messages, and solutions encountered when configuring, running, or testing RecoLab.

---

## ❓ Frequently Asked Questions & Solutions

### 1. `ModuleNotFoundError: No module named 'recolab'`
**Cause**: The package was not installed in editable mode or `PYTHONPATH` does not include the project root.  
**Fix**:
```bash
pip install -e ".[dev]"
# Or explicitly set PYTHONPATH
export PYTHONPATH=.  # Linux/macOS
set PYTHONPATH=.     # Windows CMD
$env:PYTHONPATH="."  # Windows PowerShell
```

---

### 2. `FeatureError: Movie ID [X] not found in TF-IDF matrix`
**Cause**: Candidate movie ID was not present in the training set movies metadata during `fit()`.  
**Fix**: Catch `FeatureError` in inference pipelines or ensure candidate items are validated against `movies_df['movieId']` prior to scoring.

---

### 3. Sparse Matrix Memory Overflow / High RAM Usage
**Cause**: Dense similarity computations performed on full rating matrix instead of sparse CSR representations.  
**Fix**: Ensure `scipy.sparse.csr_matrix` is used for user-item matrix representations and cosine similarity calculations.

---

### 4. Cold-Start Users Receiving Low-Quality Recommendations
**Cause**: Target user has $\le 5$ ratings and collaborative filtering neighbor similarity fails.  
**Fix**: Verify that `cold_start_threshold=5` is set in `HybridRecommender` or `UserBasedCF`, triggering automatic fallback to `ContentModel`.

---

### 5. Streamlit App Session State Reset
**Cause**: Rerunning UI script clears loaded model bundle.  
**Fix**: Models in `app.py` are decorated with `@st.cache_resource` to keep model state in memory across reruns.
