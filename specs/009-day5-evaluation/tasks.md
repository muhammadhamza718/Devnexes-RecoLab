# Day 5 Morning: Full Model Evaluation - Tasks

**Feature ID:** 009-day5-evaluation  
**Date:** 2026-08-08  
**Status:** Draft  
**Effort**: 4 hours (Day 5 Morning)

---

## Implementation Constraints (MUST DO / MUST NOT DO)

### MUST DO
- **MUST** use existing ModelManager for model access
- **MUST** use existing metrics.py framework for evaluation
- **MUST** write evaluation results to data/evaluation/ directory
- **MUST** separate evaluation from Streamlit UI (run as scripts)
- **MUST** evaluate all 5 models consistently
- **MUST** use test set (test.csv) for evaluation, not training data
- **MUST** store results in structured JSON format
- **MUST** implement proper error handling for evaluation failures
- **MUST** document evaluation methodology and parameters
- **MUST** ensure reproducibility with random seed control

### MUST NOT DO
- **MUST NOT** load models directly in evaluation code (use ModelManager)
- **MUST NOT** modify trained model parameters
- **MUST NOT** write evaluation results to source data directories
- **MUST NOT** interfere with Streamlit UI session state
- **MUST NOT** run evaluation within Streamlit app memory space
- **MUST NOT** use training data for evaluation metrics
- **MUST NOT** skip statistical significance testing
- **MUST NOT** hardcode model names or paths
- **MUST NOT** create conflicts with Day 3-4 session state keys
- **MUST NOT** modify existing evaluation framework in metrics.py

---

## Task Breakdown

### Phase 1: Foundation (1 hour)

#### Task-001: Evaluation Framework Setup
**Description**: Set up evaluation framework and result storage infrastructure

**Acceptance Criteria**:
- [ ] Create data/evaluation/ directory structure
- [ ] Create scripts/evaluation/ directory for evaluation scripts
- [ ] Create ResultStorage class for structured result storage
- [ ] Create data/evaluation/results/ subdirectory
- [ ] Create data/evaluation/comparison/ subdirectory
- [ ] Create data/evaluation/segmented/ subdirectory
- [ ] Create data/evaluation/visualizations/ subdirectory

**Test Cases**:
- Test: Directory structure created correctly
- Test: ResultStorage class can save and load results
- Test: Result validation works correctly
- Test: JSON serialization works correctly

**Dependencies**: Day 1-4 complete, data/ directory exists

**Time Estimate**: 15 minutes

---

#### Task-002: Main Evaluation Orchestrator
**Description**: Implement main evaluation orchestrator for full model evaluation

**Acceptance Criteria**:
- [ ] EvaluationOrchestrator class created in scripts/evaluation/evaluation_orchestrator.py
- [ ] run_full_evaluation() method works for all 5 models
- [ ] _evaluate_model() method evaluates single model correctly
- [ ] _generate_comparison() method creates comparison results
- [ ] Progress indicators print during evaluation
- [ ] Error handling for model loading failures

**Test Cases**:
- Test: All 5 models load successfully
- Test: Metrics calculated correctly for each model
- Test: Results stored correctly in data/evaluation/results/
- Test: Comparison results generated correctly
- Test: Progress indicators display correctly

**Dependencies**: Task-001, ModelManager accessible, metrics.py available

**Time Estimate**: 20 minutes

---

#### Task-003: Metrics Calculation Implementation
**Description**: Implement metrics calculation using existing metrics.py framework

**Acceptance Criteria**:
- [ ] _calculate_precision() method works correctly
- [ ] _calculate_recall() method works correctly
- [ ] _calculate_ndcg() method works correctly
- [ ] _calculate_coverage() method works correctly
- [ ] _calculate_popularity_decile() method works correctly
- [ ] All metrics validated against test cases
- [ ] Edge cases handled (empty data, division by zero)

**Test Cases**:
- Test: Precision@K matches expected values for known cases
- Test: Recall@K matches expected values for known cases
- Test: NDCG@K matches expected values for known cases
- Test: Coverage calculation works correctly
- Test: Popularity decile calculation works correctly

**Dependencies**: Task-002, metrics.py framework

**Time Estimate**: 15 minutes

---

#### Task-004: Data Validation Setup
**Description**: Implement data validation for test dataset and model artifacts

**Acceptance Criteria**:
- [ ] Test dataset validation function created
- [ ] Model artifact validation function created
- [ ] Evaluation parameter validation function created
- [ ] Result format validation function created
- [ ] Validation errors are user-friendly
- [ ] Validation failures prevent evaluation

**Test Cases**:
- Test: Test dataset validation identifies data quality issues
- Test: Model validation checks model availability
- Test: Parameter validation prevents invalid configurations
- Test: Result validation ensures correct format

**Dependencies**: Task-001, test.csv available

**Time Estimate**: 10 minutes

---

### Phase 2: Core Evaluation (1.5 hours)

#### Task-005: Model Evaluation Execution
**Description**: Execute comprehensive evaluation of all 5 models

**Acceptance Criteria**:
- [ ] All 5 models evaluated successfully
- [ ] Precision@K calculated for K=5,10,20
- [ ] Recall@K calculated for K=5,10,20
- [ ] NDCG@K calculated for K=5,10,20
- [ ] Catalog coverage calculated for each model
- [ ] Mean popularity decile calculated for each model
- [ ] Results stored in JSON format per model
- [ ] Evaluation completes within 10 minutes

**Test Cases**:
- Test: All 5 models produce results
- Test: Metrics are within expected ranges (0-1 for P/R/NDCG)
- Test: Results are stored in correct directory
- Test: JSON format is valid and parseable
- Test: Evaluation completes within time limit

**Dependencies**: Tasks 001-004, all models available

**Time Estimate**: 45 minutes

---

#### Task-006: Model Comparison Analysis
**Description**: Generate model comparison and statistical analysis

**Acceptance Criteria**:
- [ ] Model comparison table generated
- [ ] Performance ranking produced
- [ ] Statistical significance tests executed
- [ ] Paired t-tests between models performed
- [ ] Results stored in comparison file
- [ ] Statistical results are interpretable

**Test Cases**:
- Test: Comparison table includes all models and metrics
- Test: Ranking is consistent with performance
- Test: Statistical tests execute correctly
- Test: P-values are calculated correctly
- Test: Results indicate significant differences

**Dependencies**: Task-005, scipy available

**Time Estimate**: 20 minutes

---

#### Task-007: Segmented Evaluation
**Description**: Perform segmented evaluation by user activity and item characteristics

**Acceptance Criteria**:
- [ ] Cold-start user segmentation works
- [ ] Active user segmentation works
- [ ] New-item segmentation works
- [ ] Genre-based segmentation works
- [ ] Segmented metrics calculated for each segment
- [ ] Comparison to overall performance included
- [ ] Results stored in segmented/ directory

**Test Cases**:
- Test: Cold-start users identified correctly (≤5 ratings)
- Test: Active users identified correctly (>20 ratings)
- Test: New items identified correctly
- Test: Genre segmentation works correctly
- Test: Segmented metrics are reasonable

**Dependencies**: Task-005, SegmentedEvaluation class

**Time Estimate**: 25 minutes

---

### Phase 3: Visualization & Reporting (1.5 hours)

#### Task-008: Visualization Generation
**Description**: Generate performance comparison charts and visualizations

**Acceptance Criteria**:
- [ ] Model comparison bar chart generated
- [ ] Metric trends line chart generated
- [ ] Catalog coverage pie chart generated
- [ ] Statistical tests chart generated
- [ ] Charts saved in multiple formats (PNG, SVG)
- [ ] Charts are readable and labeled
- [ ] Color-blind friendly color schemes used

**Test Cases**:
- Test: Comparison bar chart displays correctly
- Test: Metric trends chart displays correctly
- Test: Coverage pie chart displays correctly
- Test: Statistical tests chart displays correctly
- Test: Charts are saved in correct directory

**Dependencies**: Task-006, matplotlib/seaborn available

**Time Estimate**: 30 minutes

---

#### Task-009: Evaluation Summary Report
**Description**: Generate comprehensive evaluation summary report

**Acceptance Criteria**:
- [ ] Evaluation summary includes all model results
- [ ] Performance ranking table included
- [ ] Statistical test results summarized
- [ ] Segmented analysis summary included
- [ ] Evaluation methodology documented
- [ ] Parameters and timestamp included
- [ ] Report saved in evaluation directory

**Test Cases**:
- Test: Summary includes all required sections
- Test: Performance table is accurate
- [ ] Statistical results are accurate
- Test: Methodology is clearly documented
- Test: Report is saved correctly

**Dependencies**: Tasks 005-008

**Time Estimate**: 20 minutes

---

#### Task-010: Reproducibility Validation
**Description**: Validate evaluation reproducibility with random seed control

**Acceptance Criteria**:
- [ ] Random seed control implemented
- [ ] Re-run evaluation produces identical results
- [ ] Results are consistent across runs
- [ ] Seed value documented in evaluation metadata
- [ ] Evaluation parameters are fixed and documented

**Test Cases**:
- Test: Seed control works correctly
- Test: Re-run produces identical JSON results
- Test: Metadata includes seed value
- Test: Parameters are documented

**Dependencies**: Task-005

**Time Estimate**: 10 minutes

---

## Total Time Estimate

- Phase 1: Foundation (1 hour)
- Phase 2: Core Evaluation (1.5 hours)
- Phase 3: Visualization & Reporting (1.5 hours)
- **Total: 4 hours**

---

## Success Criteria

Day 5 Morning is complete when:

- ✅ All 5 models evaluated with comprehensive metrics
- ✅ Model comparison and statistical analysis completed
- ✅ Segmented evaluation by user activity and item characteristics
- ✅ Performance visualizations generated
- ✅ Evaluation summary report created
- ✅ All results stored in data/evaluation/ directory
- ✅ Evaluation is reproducible with seed control
- ✅ Evaluation runs as separate scripts (not in Streamlit)
- ✅ No conflicts with Day 3-4 session state or functionality
