# Day 6 Morning: Deployment Setup - Specification

**Feature ID:** 010-day6-deployment  
**Date:** 2026-08-08  
**Status:** Draft  
**Effort:** 4 hours (Day 6 Morning)

---

## Overview

This specification defines the deployment setup for the Devnexes RecoLab application to Streamlit Cloud. The deployment setup includes application packaging, infrastructure configuration, environment setup, and deployment validation to ensure the application runs correctly in production.

## Scope

### In Scope
- Streamlit Cloud deployment configuration
- Application packaging with proper dependencies
- Environment variable configuration
- Data file inclusion and model artifact loading
- Infrastructure configuration (memory, timeout, caching)
- Deployment testing in staging environment
- Production deployment and monitoring setup
- Custom domain and SSL configuration (optional)

### Out of Scope
- Custom domain registration (if desired)
- Advanced SSL configuration (beyond Streamlit Cloud defaults)
- Multi-region deployment
- Advanced monitoring beyond Streamlit Cloud defaults
- Load balancing or scaling beyond Streamlit Cloud capabilities

---

## Implementation Guidelines (MUST DO / MUST NOT DO)

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

### ARCHITECTURAL CONSTRAINTS
- Deployment must use Streamlit Cloud platform
- Application must run as Streamlit app (app.py)
- Model loading must work without Streamlit dependency for evaluation
- Session state must use namespacing for deployment keys
- Environment variables must have sensible defaults
- Caching must work consistently across environments
- Error handling must be production-friendly
- Data files must be included in deployment package
- Deployment must not break existing functionality

---

## Functional Requirements

### FR-001: Streamlit Cloud Configuration
The system shall provide Streamlit Cloud deployment configuration with:
- Streamlit Cloud account setup and project configuration
- requirements.txt with all production dependencies
- .streamlit/config.toml for app configuration
- .env.example for environment variable documentation
- Proper file structure for deployment

### FR-002: Application Packaging
The system shall package the application for deployment with:
- All source code files included
- All data files (ml-latest-small, split_datasets)
- All model artifacts (if pre-bundled)
- Configuration files (.streamlit/config.toml)
- Documentation files (README.md)
- Proper Python package structure

### FR-003: Environment Configuration
The system shall configure production environment with:
- Environment variable detection and validation
- Sensible defaults for all environment variables
- Production logging configuration
- Error handling configuration
- Caching configuration
- Model loading configuration

### FR-004: Infrastructure Configuration
The system shall configure infrastructure with:
- Memory limits configuration (1GB minimum)
- Timeout parameters configuration
- Caching strategy setup
- Logging setup
- Monitoring configuration
- Health check endpoints

### FR-005: Model Artifact Loading
The system shall ensure model loading works in production with:
- Model bundle loading from models/ directory
- Fallback to fitting if bundles not available
- Environment-aware model loading
- Cache versioning for model updates
- Model loading validation

### FR-006: Deployment Testing
The system shall test deployment with:
- Staging environment deployment
- End-to-end functionality testing
- Performance testing
- Error scenario testing
- Model loading validation
- Data file validation

### FR-007: Production Deployment
The system shall deploy to production with:
- Production environment deployment
- Custom domain configuration (optional)
- SSL configuration (optional)
- Monitoring setup
- Error reporting setup
- Health monitoring

---

## Non-Functional Requirements

### NFR-001: Performance
- Deployment package size: < 500MB
- Initial application load time: < 30 seconds
- Model loading time: < 20 seconds per model
- API response time: < 5 seconds for recommendations
- Memory usage: < 1GB during normal operation

### NFR-002: Reliability
- Application uptime: > 99% (Streamlit Cloud SLA)
- Error rate: < 1% for successful deployments
- Model loading success rate: 100%
- Data file loading success rate: 100%
- Graceful degradation on errors

### NFR-003: Security
- No sensitive data in repository
- Environment variables for secrets
- Proper error messages (no stack traces in production)
- Input validation for all user inputs
- Safe model loading with validation

### NFR-004: Maintainability
- Clear deployment documentation
- Automated deployment process
- Version tracking for deployments
- Rollback capability
- Troubleshooting guide

---

## Data Model

### Deployment Configuration
```yaml
# .streamlit/config.toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"

[client]
showErrorDetails = false
maxUploadSize = 200

[logger]
level = "info"
```

### Environment Variables
```bash
# .env.example
RECOLAB_MODEL_PATH=models
RECOLAB_DATA_PATH=data
RECOLAB_LOG_LEVEL=INFO
RECOLAB_CACHE_TTL=3600
STREAMLIT_RUNTIME=true
PRODUCTION=false
```

### Session State (Deployment Keys)
```python
# Namespaced deployment state
deployment_status: str  # "local" | "staging" | "production"
deployment_health: dict  # Health check results
deployment_metrics: dict  # Performance metrics
deployment_logs: list  # Deployment event logs
production_mode: bool  # Production feature toggles
deployment_version: str  # Deployed version info
```

---

## Acceptance Criteria

### AC-001: Streamlit Cloud Configuration
- [ ] requirements.txt created with all dependencies
- [ ] .streamlit/config.toml configured with app settings
- [ ] .env.example created with all environment variables
- [ ] Streamlit Cloud project created and configured
- [ ] Git repository connected to Streamlit Cloud

### AC-002: Application Packaging
- [ ] All source code files included in deployment
- [ ] All data files included in deployment
- [ ] Model artifacts included (if pre-bundled)
- [ ] Configuration files included
- [ ] Documentation files included
- [ ] Package size < 500MB

### AC-003: Environment Configuration
- [ ] Environment variable detection implemented
- [ ] All environment variables have sensible defaults
- [ ] Production logging configured
- [ ] Error handling configured
- [ ] Caching configured

### AC-004: Infrastructure Configuration
- [ ] Memory limits configured (1GB minimum)
- [ ] Timeout parameters configured
- [ ] Caching strategy set up
- [ ] Logging set up
- [ ] Monitoring configured

### AC-005: Model Artifact Loading
- [ ] Model loading works in production environment
- [ ] Fallback to fitting works if bundles not available
- [ ] Environment-aware model loading implemented
- [ ] Cache versioning implemented
- [ ] Model loading validation works

### AC-006: Deployment Testing
- [ ] Staging deployment successful
- [ ] End-to-end functionality tests pass
- [ ] Performance tests pass
- [ ] Error scenario tests pass
- [ ] Model loading validation passes
- [ ] Data file validation passes

### AC-007: Production Deployment
- [ ] Production deployment successful
- [ ] Application accessible at production URL
- [ ] Custom domain configured (if applicable)
- [ ] SSL configured (if applicable)
- [ ] Monitoring set up
- [ ] Error reporting set up

---

## Technical Implementation Details

### Deployment Architecture
```
Development → Git Push → Streamlit Cloud → Production App
                ↓
            CI/CD Pipeline
                ↓
            Staging Environment
                ↓
            Production Environment
```

### File Structure for Deployment
```
Devnexes-RecoLab/
├── .streamlit/
│   └── config.toml              # Streamlit Cloud configuration
├── data/
│   ├── ml-latest-small/          # MovieLens dataset
│   ├── split_datasets/           # Train/test splits
│   └── evaluation/               # Day 5 evaluation results
├── models/                       # Model artifacts (optional)
├── src/recolab/                  # Source code
├── ui/                           # Streamlit UI
├── tests/                        # Test files
├── docs/                         # Documentation
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
├── README.md                     # Project documentation
└── app.py                        # Streamlit app entry point
```

### Environment Detection Logic
```python
def _detect_deployment_environment() -> str:
    """Detect current deployment environment."""
    if os.getenv("STREAMLIT_RUNTIME"):
        return "streamlit_cloud"
    elif os.getenv("PRODUCTION"):
        return "production"
    else:
        return "local"
```

### Model Loading Strategy
```python
# Dual-path model loading
if _detect_deployment_environment() == "streamlit_cloud":
    @st.cache_resource
    def load_model_with_cache(name):
        return _fit_model(name, train, movies)
else:
    def load_model_direct(name):
        return _fit_model(name, train, movies)
```

---

## Risk Analysis

### Risk-001: Deployment Package Size
**Probability**: Medium  
**Impact**: High  
**Mitigation**: Optimize data files, use efficient model bundling, monitor package size

### Risk-002: Model Loading Failure
**Probability**: Low  
**Impact**: High  
**Mitigation**: Fallback to fitting, model loading validation, health checks

### Risk-003: Environment Variable Issues
**Probability**: Medium  
**Impact**: Medium  
**Mitigation**: Sensible defaults, validation, documentation

### Risk-004: Performance Degradation
**Probability**: Medium  
**Impact**: Medium  
**Mitigation**: Performance testing, caching, optimization

### Risk-005: Streamlit Cloud Limits
**Probability**: Low  
**Impact**: High  
**Mitigation**: Monitor resource usage, optimize memory, stay within limits

---

## Dependencies

### External Dependencies
- Streamlit Cloud platform
- Git repository (GitHub)
- Python 3.14+
- MovieLens dataset (included in deployment)

### Internal Dependencies
- Day 1-4 UI implementation (session_manager.py, model_manager.py)
- Day 5 evaluation scripts (must work in production)
- Model artifacts (if pre-bundled)
- Data files (ml-latest-small, split_datasets)

---

## Success Metrics

### Deployment Success
- Application deploys successfully to Streamlit Cloud
- All functionality works in production
- Model loading works correctly
- Data files load correctly
- Error handling works in production

### Performance Metrics
- Initial load time < 30 seconds
- Model loading time < 20 seconds per model
- API response time < 5 seconds
- Memory usage < 1GB

### Quality Metrics
- No runtime errors in production
- Error rate < 1%
- Model loading success rate 100%
- User satisfaction (manual testing)

---

## Timeline Estimate

- Streamlit Cloud Configuration: 1 hour
- Application Packaging: 1 hour
- Environment Configuration: 30 minutes
- Infrastructure Configuration: 30 minutes
- Deployment Testing: 1 hour
- Production Deployment: 30 minutes

**Total**: 4 hours (Day 6 Morning)
