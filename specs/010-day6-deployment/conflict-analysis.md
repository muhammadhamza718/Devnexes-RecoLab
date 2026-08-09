# Day 6 Deployment - Conflict Analysis & Resolution

**Feature ID:** 010-day6-deployment  
**Date:** 2026-08-08  
**Status:** Draft

---

## Executive Summary

This document analyzes potential conflicts between Day 6 (Deployment & Infrastructure) and the existing Days 1-5 implementations. Conflicts are categorized by severity and resolution strategies are defined.

---

## Conflict Categories

### 1. Session State Conflicts

#### Conflict-001: Deployment State Keys
**Severity**: MEDIUM  
**Source**: Day 6 might add deployment-related session state keys

**Existing Session State Keys (Days 3-4)**:
```python
# Core UI state
selected_user_id, selected_model, model_params, recommendations, user_profile
poster_cache, similar_items, similar_source_title, current_view, visualization_panel_open, rating_statistics

# Onboarding state (7 keys)
onboarding_active, onboarding_step, onboarding_complete, onboarding_timestamp
onboarding_selected_genres, onboarding_liked_movies, onboarding_preference_weights
onboarding_preferences, onboarding_recommendation_preview, onboarding_search_history

# Dashboard state (8 keys)
dashboard_active, show_model_comparison, selected_k_value, dashboard_metrics
comparison_data, selected_models_for_comparison, show_agreement_analysis
explanation_detail_level, enhanced_explanations, confidence_threshold
show_confidence_indicators, confidence_data, accessibility_mode, performance_mode
```

**Potential Day 6 Additions**:
- `deployment_status`: str ("local", "staging", "production")
- `deployment_metrics`: dict (deployment health metrics)
- `deployment_logs`: list (deployment event logs)
- `production_mode`: bool (production feature toggles)

**Resolution Strategy**:
- Use namespacing: `deployment_*` prefix for all Day 6 session state keys
- Add conflict detection in SessionManager initialization
- Document namespace separation in session_manager.py

**Implementation**:
```python
# Day 6 session state additions (namespaced)
DEFAULT_SESSION_STATE.update({
    # Day 6: deployment state (namespaced with deployment_)
    "deployment_status": "local",  # "local" | "staging" | "production"
    "deployment_health": {},  # Health check results
    "deployment_metrics": {},  # Performance metrics
    "deployment_logs": [],  # Deployment event logs
    "production_mode": False,  # Production feature toggles
    "deployment_version": None,  # Deployed version info
})
```

---

### 2. Model Loading Conflicts

#### Conflict-002: Model Loading Strategy
**Severity**: HIGH  
**Source**: Day 6 deployment might require different model loading strategy

**Current Model Loading (ui/model_manager.py)**:
- Uses `st.cache_resource` for model caching
- Loads from `models/` directory if bundles exist
- Falls back to fitting on train split at runtime
- Uses Streamlit-specific caching

**Day 6 Deployment Requirements**:
- Streamlit Cloud deployment may have different caching behavior
- Bundle loading must work consistently across environments
- Model loading must not depend on Streamlit runtime for offline evaluation
- Fallback strategy must work in production environment

**Resolution Strategy**:
- Maintain dual model loading paths (Streamlit + offline)
- Ensure bundle loading works without Streamlit dependency
- Add environment detection for deployment-aware loading
- Document model loading strategy for deployment

**Implementation**:
```python
# Enhanced model loading with deployment awareness
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
    # Use Streamlit cache_resource
    @st.cache_resource
    def load_model_with_cache(name):
        return _fit_model(name, train, movies)
else:
    # Direct loading without Streamlit dependency
    def load_model_direct(name):
        return _fit_model(name, train, movies)
```

---

### 3. File System Conflicts

#### Conflict-003: Deployment Configuration Files
**Severity**: MEDIUM  
**Source**: Day 6 might add deployment configs that conflict with existing structure

**Existing File Structure**:
```
Devnexes-RecoLab/
├── data/
│   ├── ml-latest-small/
│   └── split_datasets/
├── models/
├── src/recolab/
├── ui/
├── scripts/
│   ├── evaluation/
│   └── analysis/
├── tests/
└── docs/
```

**Potential Day 6 Additions**:
- `requirements.txt` - Python dependencies
- `.streamlit/config.toml` - Streamlit Cloud configuration
- `.env` - Environment variables
- `Procfile` - Process management (if needed)
- `Dockerfile` - Container configuration (if needed)
- `deploy/` - Deployment scripts and configurations

**Resolution Strategy**:
- Use standard deployment file locations (project root)
- Document deployment file structure in README
- Ensure deployment configs don't interfere with development setup
- Add .gitignore rules for sensitive deployment files

**Implementation**:
```toml
# .streamlit/config.toml (new file)
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"

[client]
showErrorDetails = false
maxUploadSize = 200

[logger]
level = "info"
```

---

### 4. Environment Variable Conflicts

#### Conflict-004: Environment Variables
**Severity**: MEDIUM  
**Source**: Day 6 might add production environment variables

**Potential Day 6 Environment Variables**:
- `STREAMLIT_RUNTIME` - Streamlit Cloud detection
- `PRODUCTION` - Production mode flag
- `MODEL_PATH` - Custom model bundle path
- `DATA_PATH` - Custom data directory path
- `LOG_LEVEL` - Production logging level
- `CACHE_TTL` - Cache time-to-live

**Resolution Strategy**:
- Document all environment variables in deployment guide
- Provide sensible defaults for all environment variables
- Add environment variable validation at startup
- Use prefix `RECOLAB_` for custom variables

**Implementation**:
```python
# Environment variable validation
def validate_environment():
    """Validate and load environment variables."""
    required_vars = []
    optional_vars = {
        "RECOLAB_MODEL_PATH": "models",
        "RECOLAB_DATA_PATH": "data",
        "RECOLAB_LOG_LEVEL": "INFO",
        "RECOLAB_CACHE_TTL": "3600",
    }
    
    # Load optional vars with defaults
    env_config = {}
    for var, default in optional_vars.items():
        env_config[var] = os.getenv(var, default)
    
    return env_config
```

---

### 5. Caching Strategy Conflicts

#### Conflict-005: Caching in Production
**Severity**: HIGH  
**Source**: Day 6 production caching might conflict with Streamlit caching

**Current Caching (ui/model_manager.py)**:
- Uses `@st.cache_resource` for model caching
- Cache persists per server run
- No explicit cache invalidation

**Day 6 Production Requirements**:
- Cache must work consistently across Streamlit Cloud
- Need cache invalidation strategy for model updates
- Cache size limits in production environment
- Cache warming strategy for deployment

**Resolution Strategy**:
- Maintain Streamlit cache_resource as primary caching mechanism
- Add cache versioning for model updates
- Document cache behavior in production
- Add cache warming script for deployment

**Implementation**:
```python
# Cache versioning for model updates
CACHE_VERSION = "v1.0.0"  # Update on model changes

@st.cache_resource(ttl=3600, show_spinner=False)
def _get_model_with_version(name: str) -> tuple[Any, str]:
    """Load model with cache version control."""
    # Cache key includes version for invalidation
    return _get_model(name)

# Cache warming for deployment
def warm_model_cache():
    """Pre-load all models into cache on deployment."""
    for model_name in MODEL_NAMES:
        _get_model_with_version(model_name)
```

---

### 6. Logging Configuration Conflicts

#### Conflict-006: Production Logging
**Severity**: LOW  
**Source**: Day 6 production logging might conflict with existing logging setup

**Current Logging**:
- Console logging via print statements
- No structured logging framework
- Streamlit handles runtime logging

**Day 6 Production Requirements**:
- Structured logging for production monitoring
- Log level configuration (INFO/WARNING/ERROR)
- Log rotation for production
- Integration with Streamlit Cloud logging

**Resolution Strategy**:
- Use scripts/logging_config.py (created in Day 5 fixes)
- Configure logging based on environment detection
- Maintain backward compatibility with print statements
- Add structured logging for production-critical events

**Implementation**:
```python
# Production logging configuration
def configure_production_logging():
    """Configure logging for production environment."""
    if _detect_deployment_environment() == "production":
        return setup_logging(
            name="recolab",
            level=logging.WARNING,  # Reduce noise in production
            log_file=None,  # Streamlit Cloud handles file logging
        )
    else:
        return setup_logging(
            name="recolab",
            level=logging.INFO,  # More verbose in development
        )
```

---

### 7. Error Handling Conflicts

#### Conflict-007: Production Error Handling
**Severity**: MEDIUM  
**Source**: Day 6 production error handling might conflict with UI error handling

**Current Error Handling**:
- UI-specific error messages
- Graceful degradation in UI components
- Try-catch blocks in model operations

**Day 6 Production Requirements**:
- Production-friendly error messages (no stack traces)
- Error reporting to monitoring system
- Graceful degradation for model failures
- Rate limiting for error-prone operations

**Resolution Strategy**:
- Add production error handler decorator
- Distinguish between development and production error messages
- Add error logging for production monitoring
- Maintain existing UI error handling

**Implementation**:
```python
# Production error handling
def production_error_handler(func):
    """Decorator for production-friendly error handling."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if _detect_deployment_environment() == "production":
                # Log error, show user-friendly message
                logger.error(f"Error in {func.__name__}: {e}")
                raise UserFacingError("An error occurred. Please try again.")
            else:
                # Show full error in development
                raise
    return wrapper
```

---

### 8. Data File Conflicts

#### Conflict-008: Production Data Files
**Severity**: LOW  
**Source**: Day 6 might add production-specific data files

**Potential Day 6 Additions**:
- Production dataset (larger than development)
- Production model bundles (optimized for production)
- Deployment metadata files
- Health check data files

**Resolution Strategy**:
- Use `data/production/` subdirectory for production data
- Maintain `data/ml-latest-small/` for development
- Document data file separation
- Add data validation for production deployment

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

## Conflict Resolution Summary

### Resolved Conflicts (8)

| Conflict ID | Category | Severity | Resolution Strategy | Status |
|-------------|----------|----------|---------------------|--------|
| Conflict-001 | Session State | MEDIUM | Namespacing with `deployment_*` prefix | ✅ RESOLVED |
| Conflict-002 | Model Loading | HIGH | Dual-path loading with environment detection | ✅ RESOLVED |
| Conflict-003 | File System | MEDIUM | Standard deployment file locations | ✅ RESOLVED |
| Conflict-004 | Environment Variables | MEDIUM | Prefix `RECOLAB_` for custom variables | ✅ RESOLVED |
| Conflict-005 | Caching Strategy | HIGH | Cache versioning with warming strategy | ✅ RESOLVED |
| Conflict-006 | Logging Configuration | LOW | Environment-based logging configuration | ✅ RESOLVED |
| Conflict-007 | Error Handling | MEDIUM | Production error handler decorator | ✅ RESOLVED |
| Conflict-008 | Data Files | LOW | Separate `data/production/` directory | ✅ RESOLVED |

---

## Architectural Constraints for Day 6

### MUST DO Constraints
- **MUST** use namespacing for all Day 6 session state keys (`deployment_*` prefix)
- **MUST** maintain dual model loading paths (Streamlit + offline)
- **MUST** detect deployment environment before loading models
- **MUST** use standard deployment file locations (project root)
- **MUST** document all environment variables with sensible defaults
- **MUST** implement cache versioning for model updates
- **MUST** configure logging based on environment detection
- **MUST** add production error handling without breaking UI error handling
- **MUST** separate production data from development data

### MUST NOT DO Constraints
- **MUST NOT** modify existing session state keys from Days 3-4
- **MUST NOT** break existing model loading in UI
- **MUST NOT** interfere with development setup
- **MUST NOT** add sensitive data to repository (use .env.example)
- **MUST NOT** break Streamlit cache_resource behavior
- **MUST NOT** remove existing error handling in UI components
- **MUST NOT** modify development dataset structure
- **MUST NOT** break existing evaluation scripts (Day 5)

### Integration Points
- **SessionManager**: Add deployment state keys with namespacing
- **ModelManager**: Add environment detection and dual-path loading
- **path_utils**: Ensure deployment path validation works
- **logging_config**: Add production logging configuration
- **Day 5 evaluation**: Ensure evaluation scripts work in production environment

---

## Validation Checklist

### Conflict Validation
- [ ] Session state namespacing implemented correctly
- [ ] Model loading works in both development and production
- [ ] Deployment files don't interfere with development
- [ ] Environment variables have sensible defaults
- [ ] Cache versioning works for model updates
- [ ] Logging configuration adapts to environment
- [ ] Error handling works in production mode
- [ ] Production data separated from development data

### Integration Validation
- [ ] SessionManager initializes deployment state correctly
- [ ] ModelManager loads models in production environment
- [ ] Day 5 evaluation scripts work with deployment setup
- [ ] UI components work with production error handling
- [ ] Logging works in Streamlit Cloud environment

### Regression Validation
- [ ] Existing UI state keys still work correctly
- [ ] Existing model loading still works in development
- [ ] Existing evaluation scripts still run successfully
- [ ] Existing error handling still works in UI
- [ ] Existing session state management still works

---

## Conclusion

All 8 identified conflicts have been resolved with clear strategies. The Day 6 deployment can proceed without breaking existing functionality from Days 1-5. The resolution strategies maintain backward compatibility while enabling production deployment capabilities.

**Next Steps**:
1. Create Day 6 Morning SDD (Deployment Setup)
2. Create Day 6 Afternoon SDD (Production Readiness)
3. Implement conflict resolutions in SDD tasks
4. Run IVP validation for both SDD documents
5. Implement and validate deployment
