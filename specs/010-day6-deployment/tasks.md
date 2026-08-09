# Day 6 Morning: Deployment Setup - Tasks

**Feature ID:** 010-day6-deployment  
**Date:** 2026-08-08  
**Status:** Draft  
**Effort**: 4 hours (Day 6 Morning)

---

## Implementation Constraints (MUST DO / MUST NOT DO)

### MUST DO
- **MUST** use Streamlit Cloud as deployment platform
- **MUST** create requirements.txt with all dependencies
- **MUST** configure environment variables for production
- **MUST** include all data files in deployment package
- **MUST** configure model artifact loading for production
- **MUST** set up proper error handling for production
- **MUST** configure memory limits and timeout parameters
- **MUST** set up caching strategy for production
- **MUST** configure logging for production monitoring
- **MUST** test deployment in staging before production
- **MUST** implement deployment validation checks
- **MUST** use namespacing for deployment session state keys (`deployment_*` prefix)
- **MUST** detect deployment environment for conditional behavior
- **MUST** maintain dual model loading paths (Streamlit + offline)
- **MUST** document deployment process and troubleshooting

### MUST NOT DO
- **MUST NOT** hardcode sensitive information (API keys, passwords)
- **MUST NOT** include development-only dependencies in production
- **MUST NOT** break existing UI functionality during deployment
- **MUST NOT** modify existing session state keys from Days 3-4
- **MUST NOT** interfere with Day 5 evaluation scripts
- **MUST NOT** deploy without testing in staging environment
- **MUST NOT** break model loading in production environment
- **MUST NOT** commit sensitive environment files (.env) to repository
- **MUST NOT** modify development dataset structure
- **MUST NOT** remove existing error handling in UI components

---

## Task Breakdown

### Phase 1: Streamlit Cloud Configuration (1 hour)

#### Task-001: Streamlit Cloud Account Setup
**Description**: Create and configure Streamlit Cloud account and project

**Acceptance Criteria**:
- [ ] Streamlit Cloud account created
- [ ] New project created in Streamlit Cloud
- [ ] Project settings configured (name, description)
- [ ] Git repository connected to Streamlit Cloud
- [ ] Deployment permissions configured

**Test Cases**:
- Test: Can access Streamlit Cloud dashboard
- Test: Project shows in Streamlit Cloud dashboard
- Test: Git repository successfully connected
- Test: Deployment settings are accessible

**Dependencies**: Streamlit Cloud account, Git repository

**Time Estimate**: 15 minutes

---

#### Task-002: Requirements.txt Creation
**Description**: Create requirements.txt with all production dependencies

**Acceptance Criteria**:
- [ ] requirements.txt created in project root
- [ ] All required dependencies listed
- [ ] Python version specified (>=3.14)
- [ ] Dependencies pinned to compatible versions
- [ ] No development-only dependencies included
- [ ] Dependencies validated for Streamlit Cloud compatibility

**Test Cases**:
- Test: pip install -r requirements.txt succeeds
- Test: All imports work without errors
- Test: No version conflicts
- Test: Streamlit Cloud accepts requirements.txt

**Dependencies**: Existing pyproject.toml, dependency list from project

**Time Estimate**: 15 minutes

---

#### Task-003: Streamlit Configuration File
**Description**: Create .streamlit/config.toml for app configuration

**Acceptance Criteria**:
- [ ] .streamlit directory created
- [ ] config.toml created with app settings
- [ ] Theme configuration set (primaryColor, backgroundColor)
- [ ] Client configuration set (showErrorDetails, maxUploadSize)
- [ ] Logger configuration set (level)
- [ ] Configuration validated against Streamlit Cloud specs

**Test Cases**:
- Test: Configuration file syntax is valid
- Test: Theme colors work correctly
- Test: Error details hidden in production
- Test: Logger level is appropriate

**Dependencies**: Streamlit Cloud documentation, design specifications

**Time Estimate**: 10 minutes

---

#### Task-004: Environment Variables Template
**Description**: Create .env.example with all environment variables

**Acceptance Criteria**:
- [ ] .env.example created in project root
- [ ] All RECOLAB_ environment variables documented
- [ ] Default values provided for all variables
- [ ] Variable descriptions included
- [ ] Sensitive variables noted (if any)
- [ ] Documentation included in README

**Test Cases**:
- Test: .env.example is well-formatted
- Test: All variables have defaults
- Test: Variables are properly documented
- Test: No sensitive information in .env.example

**Dependencies**: Environment variable requirements from plan

**Time Estimate**: 10 minutes

---

#### Task-005: Git Repository Connection
**Description**: Connect Git repository to Streamlit Cloud

**Acceptance Criteria**:
- [ ] Git repository connected to Streamlit Cloud
- [ ] Branch configuration set (main branch)
- [ ] Auto-deployment enabled
- [ ] Repository permissions configured
- [ ] Connection tested with sample deployment

**Test Cases**:
- Test: Git push triggers Streamlit Cloud deployment
- Test: Deployment builds successfully
- Test: Application accessible at Streamlit Cloud URL
- Test: Branch configuration works correctly

**Dependencies**: Streamlit Cloud account, Git repository

**Time Estimate**: 10 minutes

---

### Phase 2: Application Packaging (1 hour)

#### Task-006: Source Code Verification
**Description**: Verify all source code files are included in deployment

**Acceptance Criteria**:
- [ ] All src/recolab/ files present
- [ ] All ui/ files present
- [ ] All scripts/ files present
- [ ] All required __init__.py files present
- [ ] No unnecessary files included
- [ ] Package structure validated

**Test Cases**:
- Test: All imports work in deployment environment
- Test: No missing module errors
- Test: Package structure is correct
- Test: No duplicate files

**Dependencies**: Complete source code from Days 1-5

**Time Estimate**: 15 minutes

---

#### Task-007: Data File Verification
**Description**: Verify all data files are included in deployment

**Acceptance Criteria**:
- [ ] data/ml-latest-small/ directory present
- [ ] data/split_datasets/ directory present
- [ ] data/evaluation/ directory present (Day 5 results)
- [ ] All required CSV files present
- [ ] File sizes within limits
- [ ] No corrupted data files

**Test Cases**:
- Test: Data files load correctly
- Test: No missing data errors
- Test: File sizes are reasonable
- Test: Data integrity validated

**Dependencies**: Data files from Days 1-5

**Time Estimate**: 15 minutes

---

#### Task-008: Model Artifact Verification
**Description**: Verify model artifacts (if present) are included

**Acceptance Criteria**:
- [ ] models/ directory present (if pre-bundled)
- [ ] Model bundle files present (if pre-bundled)
- [ ] Model bundle format validated
- [ ] No corrupted model files
- [ ] Model loading tested

**Test Cases**:
- Test: Model bundles load correctly
- Test: No corrupted model errors
- Test: Model format is correct
- Test: Fallback to fitting works if bundles missing

**Dependencies**: Model artifacts (optional), Day 1-4 model implementations

**Time Estimate**: 10 minutes

---

#### Task-009: Package Size Optimization
**Description**: Optimize deployment package size

**Acceptance Criteria**:
- [ ] Package size < 500MB
- [ ] Unnecessary files removed
- [ ] Data files optimized
- [ ] Large files identified and handled
- [ ] Package size validated

**Test Cases**:
- Test: Package size measured
- Test: Package size within limits
- Test: No critical files removed
- Test: Functionality still works after optimization

**Dependencies**: All project files

**Time Estimate**: 10 minutes

---

#### Task-010: Local Deployment Test
**Description**: Test deployment locally before Streamlit Cloud

**Acceptance Criteria**:
- [ ] Application runs locally with production config
- [ ] All functionality works locally
- [ ] Model loading works locally
- [ ] Data files load locally
- [ ] No errors in local deployment

**Test Cases**:
- Test: Streamlit app starts locally
- Test: All models load locally
- Test: All features work locally
- Test: No runtime errors

**Dependencies**: Complete application, configuration files

**Time Estimate**: 10 minutes

---

### Phase 3: Environment Configuration (30 minutes)

#### Task-011: Environment Detection Implementation
**Description**: Implement environment detection logic

**Acceptance Criteria**:
- [ ] _detect_deployment_environment() function implemented
- [ ] Detects local, staging, production environments
- [ ] Uses STREAMLIT_RUNTIME environment variable
- [ ] Uses PRODUCTION environment variable
- [ ] Returns correct environment string
- [ ] Fallback to local if no environment detected

**Test Cases**:
- Test: Returns "local" in development
- Test: Returns "streamlit_cloud" on Streamlit Cloud
- Test: Returns "production" when PRODUCTION set
- Test: Fallback works correctly

**Dependencies**: scripts/path_utils.py (from Day 5 fixes)

**Time Estimate**: 10 minutes

---

#### Task-012: Environment Variable Validation
**Description**: Implement environment variable validation

**Acceptance Criteria**:
- [ ] validate_environment() function implemented
- [ ] All RECOLAB_ variables validated
- [ ] Defaults applied for missing variables
- [ ] Validation errors handled gracefully
- [ ] Environment configuration returned
- [ ] Validation logged

**Test Cases**:
- Test: Valid environment variables accepted
- Test: Missing variables use defaults
- Test: Invalid variables handled gracefully
- Test: Validation errors logged

**Dependencies**: .env.example, environment variable requirements

**Time Estimate**: 10 minutes

---

#### Task-013: Production Logging Configuration
**Description**: Configure production logging using scripts/logging_config.py

**Acceptance Criteria**:
- [ ] configure_production_logging() function implemented
- [ ] Log level set based on environment
- [ ] Production uses WARNING level
- [ ] Development uses INFO level
- [ ] Structured logging configured
- [ ] Logging tested in both environments

**Test Cases**:
- Test: Logging works in development
- Test: Logging works in production
- Test: Log levels are appropriate
- Test: Structured logging works

**Dependencies**: scripts/logging_config.py (from Day 5 fixes)

**Time Estimate**: 5 minutes

---

#### Task-014: Error Handling Configuration
**Description**: Configure production error handling

**Acceptance Criteria**:
- [ ] production_error_handler decorator implemented
- [ ] Production shows user-friendly errors
- [ ] Development shows full stack traces
- [ ] Errors logged in production
- [ ] Error handling tested
- [ ] Existing UI error handling preserved

**Test Cases**:
- Test: Errors are user-friendly in production
- Test: Stack traces hidden in production
- Test: Errors show full details in development
- Test: Existing error handling still works

**Dependencies**: Existing error handling in UI components

**Time Estimate**: 5 minutes

---

### Phase 4: Infrastructure Configuration (30 minutes)

#### Task-015: Memory and Timeout Configuration
**Description**: Configure memory limits and timeout parameters

**Acceptance Criteria**:
- [ ] Memory limit configured (1GB minimum)
- [ ] Timeout parameters configured
- [ ] Configuration documented
- [ ] Resource usage monitored
- [ ] Configuration validated

**Test Cases**:
- Test: Application stays within memory limits
- Test: Timeouts are appropriate
- Test: No memory errors
- Test: Resource usage acceptable

**Dependencies**: Streamlit Cloud infrastructure capabilities

**Time Estimate**: 10 minutes

---

#### Task-016: Caching Strategy Setup
**Description**: Set up caching strategy for production

**Acceptance Criteria**:
- [ ] Cache versioning implemented
- [ ] Cache TTL configured
- [ ] Model caching with st.cache_resource
- [ ] Cache warming script created
- [ ] Cache invalidation strategy defined
- [ ] Caching tested

**Test Cases**:
- Test: Model caching works in production
- Test: Cache versioning works
- Test: Cache invalidation works
- Test: Cache warming works

**Dependencies**: ui/model_manager.py, existing caching

**Time Estimate**: 10 minutes

---

#### Task-017: Logging and Monitoring Setup
**Description**: Set up logging and monitoring for production

**Acceptance Criteria**:
- [ ] Logging configured for production
- [ ] Streamlit Cloud logging integrated
- [ ] Monitoring metrics configured
- [ ] Health check endpoints added
- [ ] Monitoring tested
- [ ] Logging validated

**Test Cases**:
- Test: Logs appear in Streamlit Cloud
- Test: Metrics are collected
- Test: Health checks work
- Test: Monitoring is functional

**Dependencies**: scripts/logging_config.py, Streamlit Cloud monitoring

**Time Estimate**: 10 minutes

---

### Phase 5: Deployment Testing (1 hour)

#### Task-018: Staging Deployment
**Description**: Deploy application to staging environment

**Acceptance Criteria**:
- [ ] Application deployed to staging
- [ ] Staging URL accessible
- [ ] Deployment successful
- [ ] No deployment errors
- [ ] Staging environment validated

**Test Cases**:
- Test: Staging deployment succeeds
- Test: Staging URL works
- Test: No deployment errors
- Test: Staging environment is functional

**Dependencies**: Streamlit Cloud account, complete application

**Time Estimate**: 15 minutes

---

#### Task-019: End-to-End Functionality Testing
**Description**: Run end-to-end functionality tests in staging

**Acceptance Criteria**:
- [ ] All UI features work in staging
- [ ] Model selection works
- [ ] User selection works
- [ ] Recommendations work
- [ ] All features tested
- [ ] No functionality errors

**Test Cases**:
- Test: User can select model
- Test: User can select user
- Test: Recommendations display correctly
- Test: Similar items work
- Test: Dashboard works
- Test: Onboarding works

**Dependencies**: Complete application, staging deployment

**Time Estimate**: 20 minutes

---

#### Task-020: Performance Testing
**Description**: Run performance tests in staging

**Acceptance Criteria**:
- [ ] Initial load time < 30 seconds
- [ ] Model loading time < 20 seconds per model
- [ ] API response time < 5 seconds
- [ ] Memory usage < 1GB
- [ ] Performance metrics validated
- [ ] Performance within NFRs

**Test Cases**:
- Test: Load time measured
- Test: Model loading time measured
- Test: Response time measured
- Test: Memory usage measured
- Test: All metrics within budgets

**Dependencies**: Staging deployment, performance testing tools

**Time Estimate**: 10 minutes

---

#### Task-021: Error Scenario Testing
**Description**: Test error scenarios in staging

**Acceptance Criteria**:
- [ ] Model loading errors handled gracefully
- [ ] Data loading errors handled gracefully
- [ ] User input errors handled gracefully
- [ ] Network errors handled gracefully
- [ ] Error messages are user-friendly
- [ ] Error handling validated

**Test Cases**:
- Test: Invalid user ID handled
- Test: Invalid model selection handled
- Test: Data loading errors handled
- Test: Model loading errors handled
- Test: Error messages are appropriate

**Dependencies**: Staging deployment, error handling implementation

**Time Estimate**: 10 minutes

---

#### Task-022: Model Loading Validation
**Description**: Validate model loading in staging

**Acceptance Criteria**:
- [ ] All 5 models load successfully
- [ ] Model loading time < 20 seconds
- [ ] Model loading errors handled
- [ ] Fallback to fitting works
- [ ] Model loading validated
- [ ] No model loading errors

**Test Cases**:
- Test: Popularity model loads
- Test: Content model loads
- Test: User-Based CF loads
- Test: Item-Based CF loads
- Test: Hybrid model loads
- Test: Fallback works

**Dependencies**: Staging deployment, model artifacts

**Time Estimate**: 5 minutes

---

### Phase 6: Production Deployment (30 minutes)

#### Task-023: Production Deployment
**Description**: Deploy application to production environment

**Acceptance Criteria**:
- [ ] Application deployed to production
- [ ] Production URL accessible
- [ ] Deployment successful
- [ ] No deployment errors
- [ ] Production environment validated
- [ ] Production mode enabled

**Test Cases**:
- Test: Production deployment succeeds
- Test: Production URL works
- Test: No deployment errors
- Test: Production environment is functional
- Test: Production mode works

**Dependencies**: Staging deployment validated, Streamlit Cloud account

**Time Estimate**: 10 minutes

---

#### Task-024: Custom Domain Configuration (Optional)
**Description**: Configure custom domain for production (if desired)

**Acceptance Criteria**:
- [ ] Custom domain configured (if applicable)
- [ ] DNS settings configured
- [ ] SSL certificate configured
- [ ] Domain accessible
- [ ] SSL valid
- [ ] Configuration validated

**Test Cases**:
- Test: Custom domain works
- Test: SSL is valid
- Test: DNS resolves correctly
- Test: Domain is accessible

**Dependencies**: Custom domain (optional), DNS provider

**Time Estimate**: 10 minutes (optional)

---

#### Task-025: Monitoring Setup
**Description**: Set up monitoring for production

**Acceptance Criteria**:
- [ ] Monitoring configured in Streamlit Cloud
- [ ] Health checks enabled
- [ ] Error reporting enabled
- [ ] Metrics collection enabled
- [ ] Monitoring validated
- [ ] Alerts configured (if needed)

**Test Cases**:
- Test: Monitoring is active
- Test: Health checks work
- Test: Error reporting works
- Test: Metrics are collected
- Test: Alerts work (if configured)

**Dependencies**: Streamlit Cloud monitoring, production deployment

**Time Estimate**: 5 minutes

---

#### Task-026: Final Validation
**Description**: Perform final validation of production deployment

**Acceptance Criteria**:
- [ ] All functionality works in production
- [ ] Performance meets NFRs
- [ ] Error handling works correctly
- [ ] Monitoring is functional
- [ ] Documentation is complete
- [ ] Deployment validated

**Test Cases**:
- Test: Complete user flow works
- Test: Performance metrics within budgets
- Test: Error handling is production-friendly
- Test: Monitoring is functional
- Test: Documentation is complete

**Dependencies**: Complete production deployment

**Time Estimate**: 5 minutes

---

## Validation Checklist

### Configuration Validation
- [ ] requirements.txt is correct
- [ ] .streamlit/config.toml is valid
- [ ] .env.example is complete
- [ ] Git repository is connected
- [ ] Environment variables are validated

### Packaging Validation
- [ ] All source files included
- [ ] All data files included
- [ ] Model artifacts included (if present)
- [ ] Package size < 500MB
- [ ] No corrupted files

### Environment Validation
- [ ] Environment detection works
- [ ] Environment variables validated
- [ ] Logging configured correctly
- [ ] Error handling configured
- [ ] Caching configured

### Infrastructure Validation
- [ ] Memory limits configured
- [ ] Timeout parameters configured
- [ ] Caching strategy set up
- [ ] Logging set up
- [ ] Monitoring configured

### Deployment Validation
- [ ] Staging deployment successful
- [ ] End-to-end tests pass
- [ ] Performance tests pass
- [ ] Error scenario tests pass
- [ ] Model loading validated
- [ ] Production deployment successful
- [ ] Monitoring is functional
- [ ] Documentation is complete

---

## Success Criteria

### Deployment Success
- [ ] Application deploys successfully to Streamlit Cloud
- [ ] All functionality works in production
- [ ] Model loading works correctly
- [ ] Data files load correctly
- [ ] Error handling works in production

### Performance Success
- [ ] Initial load time < 30 seconds
- [ ] Model loading time < 20 seconds per model
- [ ] API response time < 5 seconds
- [ ] Memory usage < 1GB

### Quality Success
- [ ] No runtime errors in production
- [ ] Error rate < 1%
- [ ] Model loading success rate 100%
- [ ] Documentation is complete
- [ ] Troubleshooting guide is available
