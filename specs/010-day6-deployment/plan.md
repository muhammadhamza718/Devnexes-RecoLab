# Day 6 Morning: Deployment Setup - Architecture Plan

**Feature ID:** 010-day6-deployment  
**Date:** 2026-08-08  
**Status:** Draft

---

## Overview

This architectural plan outlines the deployment strategy for the Devnexes RecoLab application to Streamlit Cloud. The plan addresses infrastructure configuration, application packaging, environment setup, and deployment validation.

---

## 1. Scope and Dependencies

### In Scope
- Streamlit Cloud deployment infrastructure
- Application packaging and dependency management
- Environment variable configuration
- Model artifact loading in production
- Infrastructure configuration (memory, timeout, caching)
- Deployment testing and validation
- Production deployment and monitoring

### Out of Scope
- Custom domain registration (optional add-on)
- Advanced SSL configuration (beyond Streamlit Cloud defaults)
- Multi-region deployment
- Advanced monitoring beyond Streamlit Cloud defaults
- Load balancing or scaling beyond Streamlit Cloud capabilities

### External Dependencies
- **Streamlit Cloud Platform**: Deployment hosting platform
- **GitHub**: Git repository for source control
- **Python 3.14+**: Runtime environment
- **MovieLens Dataset**: Included in deployment package

### Internal Dependencies
- **Day 1-4 UI Implementation**: session_manager.py, model_manager.py
- **Day 5 Evaluation Scripts**: Must work in production environment
- **Model Artifacts**: Optional pre-bundled models
- **Data Files**: ml-latest-small, split_datasets
- **Path Utils**: scripts/path_utils.py (from Day 5 fixes)

---

## 2. Key Decisions and Rationale

### Decision-001: Streamlit Cloud as Deployment Platform
**Options Considered**:
1. Streamlit Cloud (Chosen)
2. Heroku
3. AWS EC2
4. Docker container deployment

**Rationale**:
- Native support for Streamlit applications
- Zero-configuration deployment
- Built-in caching and resource management
- Free tier available for development
- Seamless integration with Git workflow
- Production-ready SSL and domain support

**Trade-offs**:
- Limited customization compared to cloud providers
- Resource limits on free tier
- Vendor lock-in to Streamlit Cloud

---

### Decision-002: Dual Model Loading Strategy
**Options Considered**:
1. Streamlit-only loading (Rejected - breaks Day 5 evaluation)
2. Offline-only loading (Rejected - breaks UI caching)
3. Dual-path loading with environment detection (Chosen)

**Rationale**:
- Maintains compatibility with Day 5 evaluation scripts
- Preserves Streamlit cache_resource benefits in UI
- Environment detection allows appropriate strategy
- Backward compatible with existing code

**Implementation**:
```python
def _detect_deployment_environment() -> str:
    """Detect current deployment environment."""
    if os.getenv("STREAMLIT_RUNTIME"):
        return "streamlit_cloud"
    elif os.getenv("PRODUCTION"):
        return "production"
    else:
        return "local"

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

### Decision-003: Session State Namespacing
**Options Considered**:
1. Add keys to existing session state (Rejected - conflicts with Days 3-4)
2. Separate session state for deployment (Rejected - complexity)
3. Namespacing with `deployment_*` prefix (Chosen)

**Rationale**:
- Maintains backward compatibility
- Clear separation of concerns
- Easy to identify deployment-specific state
- Follows existing pattern (onboarding_*, dashboard_*)

**Implementation**:
```python
DEFAULT_SESSION_STATE.update({
    # Day 6: deployment state (namespaced with deployment_)
    "deployment_status": "local",
    "deployment_health": {},
    "deployment_metrics": {},
    "deployment_logs": [],
    "production_mode": False,
    "deployment_version": None,
})
```

---

### Decision-004: Environment Variable Prefixing
**Options Considered**:
1. No prefix (Rejected - conflicts with system variables)
2. RECO prefix (Rejected - unclear meaning)
3. RECOLAB_ prefix (Chosen)

**Rationale**:
- Clear project identification
- Avoids conflicts with system variables
- Follows common practice (e.g., DATABASE_URL)
- Easy to identify project-specific variables

**Implementation**:
```python
optional_vars = {
    "RECOLAB_MODEL_PATH": "models",
    "RECOLAB_DATA_PATH": "data",
    "RECOLAB_LOG_LEVEL": "INFO",
    "RECOLAB_CACHE_TTL": "3600",
}
```

---

### Decision-005: Separate Production Data Directory
**Options Considered**:
1. Use existing data/ directory (Rejected - conflicts with development)
2. Inline production data in code (Rejected - bad practice)
3. Separate data/production/ directory (Chosen)

**Rationale**:
- Clear separation of development and production data
- Maintains development workflow
- Allows different datasets for different environments
- Follows common deployment patterns

**Implementation**:
```
data/
├── ml-latest-small/          # Development dataset
├── split_datasets/           # Development splits
├── evaluation/               # Evaluation results (Day 5)
└── production/               # Production data (Day 6)
    ├── models/               # Production model bundles
    ├── datasets/             # Production datasets
    └── metadata/             # Deployment metadata
```

---

## 3. Interfaces and API Contracts

### Interface-001: Deployment Configuration API
**Description**: External configuration interface for deployment

**Inputs**:
- Environment variables (RECOLAB_*)
- Configuration files (.streamlit/config.toml)
- Command-line arguments (if any)

**Outputs**:
- Deployment configuration dictionary
- Environment detection result
- Validation status

**Error Handling**:
- Invalid environment variables → use defaults
- Missing configuration files → use defaults
- Invalid configuration → raise ConfigurationError

**Idempotency**: Yes - configuration can be reloaded without side effects

---

### Interface-002: Model Loading API
**Description**: Enhanced model loading interface with environment awareness

**Inputs**:
- Model name (string)
- Environment context (optional, auto-detected)

**Outputs**:
- Model instance
- Provenance information
- Loading status

**Error Handling**:
- Model not found → try fallback to fitting
- Loading failure → raise ModelLoadError
- Bundle corruption → fall back to fitting

**Idempotency**: Yes - model loading is cached per environment

---

### Interface-003: Health Check API
**Description**: Health check interface for production monitoring

**Inputs**:
- Health check type (basic, detailed, model)
- Component to check (optional)

**Outputs**:
- Health status (healthy/unhealthy/degraded)
- Health metrics
- Timestamp
- Error details (if unhealthy)

**Error Handling**:
- Component not found → return unhealthy status
- Timeout → return degraded status
- Check failure → return unhealthy status

**Idempotency**: Yes - health checks can be repeated

---

## 4. Non-Functional Requirements and Budgets

### Performance Budgets
- **Deployment Package Size**: < 500MB
- **Initial Application Load Time**: < 30 seconds
- **Model Loading Time**: < 20 seconds per model
- **API Response Time**: < 5 seconds for recommendations
- **Memory Usage**: < 1GB during normal operation
- **CPU Usage**: < 50% during normal operation

### Reliability Budgets
- **Application Uptime**: > 99% (Streamlit Cloud SLA)
- **Error Rate**: < 1% for successful deployments
- **Model Loading Success Rate**: 100%
- **Data File Loading Success Rate**: 100%
- **Graceful Degradation**: 100% on errors

### Security Budgets
- **Secrets in Repository**: 0
- **Environment Variables for Secrets**: 100%
- **Input Validation Coverage**: 100%
- **Error Message Security**: Production-friendly (no stack traces)
- **File Access Validation**: 100% (using path_utils.py)

### Cost Budgets
- **Streamlit Cloud Free Tier**: $0/month
- **Streamlit Cloud Pro Tier**: $20/month (if needed)
- **Domain Registration**: $10-15/year (if custom domain)
- **SSL Certificate**: Free (Let's Encrypt via Streamlit Cloud)

---

## 5. Data Management and Migration

### Source of Truth
- **Git Repository**: Source code and configuration
- **Streamlit Cloud**: Production deployment state
- **Environment Variables**: Runtime configuration

### Schema Evolution
- **Session State Schema**: Version 1.0 (Day 6 addition)
- **Environment Variable Schema**: Version 1.0 (Day 6 addition)
- **Configuration File Schema**: Version 1.0 (Day 6 addition)

### Migration Strategy
- **Session State Migration**: Automatic via SessionManager.ensure_initialized()
- **Environment Variable Migration**: Graceful with defaults
- **Configuration File Migration**: New files, no migration needed

### Rollback Strategy
- **Git Rollback**: Revert to previous commit
- **Environment Rollback**: Restore previous environment variables
- **Configuration Rollback**: Restore previous config.toml

### Data Retention
- **Deployment Logs**: 30 days (Streamlit Cloud default)
- **Application Data**: Persistent in deployment package
- **User Data**: None (no user data persistence)

---

## 6. Operational Readiness

### Observability
**Logs**:
- Structured logging via scripts/logging_config.py
- Environment-based log level configuration
- Streamlit Cloud log integration
- Error logging for production monitoring

**Metrics**:
- Model loading time metrics
- API response time metrics
- Error rate metrics
- Resource usage metrics (memory, CPU)

**Traces**:
- Request tracing via Streamlit Cloud
- Model loading tracing
- Error tracing

### Alerting
**Thresholds**:
- Error rate > 5% → alert
- Model loading failure → alert
- Memory usage > 80% → alert
- API response time > 10 seconds → alert

**On-Call Owner**: Developer (project owner)

### Runbooks
**Common Tasks**:
- Deployment rollback procedure
- Model bundle update procedure
- Environment variable update procedure
- Configuration change procedure
- Troubleshooting guide

### Deployment Strategy
**Process**:
1. Test in staging environment
2. Validate all functionality
3. Deploy to production
4. Monitor initial load
5. Validate production functionality

**Rollback Strategy**:
- Git revert to previous commit
- Streamlit Cloud auto-deploys from Git
- Monitor rollback success

### Feature Flags
**Flags**:
- `production_mode`: Toggle production features
- `deployment_metrics`: Toggle detailed metrics
- `enhanced_logging`: Toggle detailed logging

**Compatibility**: All flags backward compatible

---

## 7. Risk Analysis and Mitigation

### Risk-001: Deployment Package Size
**Probability**: Medium  
**Impact**: High  
**Blast Radius**: Deployment failure  
**Mitigation**:
- Optimize data files (remove unnecessary data)
- Use efficient model bundling
- Monitor package size during development
- Streamlit Cloud limit is 1GB, target < 500MB

**Kill Switch**: Reduce data files, use smaller dataset

---

### Risk-002: Model Loading Failure
**Probability**: Low  
**Impact**: High  
**Blast Radius**: Application unusable  
**Mitigation**:
- Fallback to fitting if bundles not available
- Model loading validation
- Health checks on startup
- Error handling with user-friendly messages

**Kill Switch**: Fallback to fitting, disable affected models

---

### Risk-003: Environment Variable Issues
**Probability**: Medium  
**Impact**: Medium  
**Blast Radius**: Configuration errors  
**Mitigation**:
- Sensible defaults for all variables
- Environment variable validation
- Documentation of all variables
- .env.example for reference

**Kill Switch**: Use hardcoded defaults

---

### Risk-004: Performance Degradation
**Probability**: Medium  
**Impact**: Medium  
**Blast Radius**: Poor user experience  
**Mitigation**:
- Performance testing in staging
- Caching strategy optimization
- Memory usage monitoring
- Resource usage optimization

**Kill Switch**: Reduce caching, optimize memory

---

### Risk-005: Streamlit Cloud Limits
**Probability**: Low  
**Impact**: High  
**Blast Radius**: Deployment failure  
**Mitigation**:
- Monitor resource usage
- Optimize memory usage
- Stay within Streamlit Cloud limits
- Consider Pro tier if needed

**Kill Switch**: Upgrade to Pro tier

---

## 8. Evaluation and Validation

### Definition of Done
- [ ] Application deploys successfully to Streamlit Cloud
- [ ] All functionality works in production
- [ ] Model loading works correctly
- [ ] Data files load correctly
- [ ] Error handling works in production
- [ ] Performance meets NFRs
- [ ] Documentation is complete
- [ ] Troubleshooting guide is available

### Validation Approach
- **Unit Tests**: Environment detection, configuration loading
- **Integration Tests**: Model loading in production environment
- **End-to-End Tests**: Complete user flows in production
- **Performance Tests**: Load time, response time, memory usage
- **Security Tests**: No secrets in repository, input validation

### Output Validation
- **Format**: Deployment package structure validation
- **Requirements**: All files included, correct structure
- **Safety**: No sensitive data, proper file permissions
- **Functionality**: All features work in production

---

## 9. Implementation Sequence

### Phase 1: Streamlit Cloud Configuration (1 hour)
1. Create Streamlit Cloud account
2. Configure project settings
3. Create requirements.txt
4. Create .streamlit/config.toml
5. Create .env.example
6. Connect Git repository

### Phase 2: Application Packaging (1 hour)
1. Verify all source files included
2. Verify all data files included
3. Verify model artifacts (if present)
4. Optimize package size
5. Test local deployment
6. Validate package structure

### Phase 3: Environment Configuration (30 minutes)
1. Implement environment detection
2. Add environment variable validation
3. Configure production logging
4. Configure error handling
5. Configure caching
6. Test environment configuration

### Phase 4: Infrastructure Configuration (30 minutes)
1. Configure memory limits
2. Configure timeout parameters
3. Set up caching strategy
4. Configure logging
5. Configure monitoring
6. Add health checks

### Phase 5: Deployment Testing (1 hour)
1. Deploy to staging
2. Run end-to-end tests
3. Run performance tests
4. Test error scenarios
5. Validate model loading
6. Validate data files

### Phase 6: Production Deployment (30 minutes)
1. Deploy to production
2. Validate production URL
3. Configure custom domain (optional)
4. Configure SSL (optional)
5. Set up monitoring
6. Set up error reporting

---

## 10. Architectural Decision Records

### ADR-001: Streamlit Cloud Platform Selection
**Status**: Accepted  
**Context**: Need deployment platform for Streamlit application  
**Decision**: Use Streamlit Cloud as deployment platform  
**Consequences**: Native Streamlit support, vendor lock-in, resource limits

### ADR-002: Dual Model Loading Strategy
**Status**: Accepted  
**Context**: Need model loading that works in both UI and evaluation  
**Decision**: Implement dual-path loading with environment detection  
**Consequences**: Added complexity, maintained compatibility

### ADR-003: Session State Namespacing
**Status**: Accepted  
**Context**: Need deployment-specific session state without conflicts  
**Decision**: Use `deployment_*` prefix for deployment state keys  
**Consequences**: Clear separation, follows existing pattern

### ADR-004: Environment Variable Prefixing
**Status**: Accepted  
**Context**: Need environment variables without conflicts  
**Decision**: Use `RECOLAB_` prefix for project-specific variables  
**Consequences**: Clear identification, avoids conflicts

### ADR-005: Production Data Separation
**Status**: Accepted  
**Context**: Need production data without interfering with development  
**Decision**: Use separate `data/production/` directory  
**Consequences**: Clear separation, additional directory structure
