# Day 6 Morning: Deployment Setup - Data Model

**Feature ID:** 010-day6-deployment  
**Date:** 2026-08-08  
**Status:** Draft

---

## Overview

This document defines the data model for Day 6 deployment setup, including configuration files, environment variables, session state, and deployment metadata.

---

## Configuration Data Models

### .streamlit/config.toml
```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[client]
showErrorDetails = false
maxUploadSize = 200
toolbarMode = "viewer"

[logger]
level = "info"
```

### requirements.txt
```txt
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

### .env.example
```bash
# Model Configuration
RECOLAB_MODEL_PATH=models
RECOLAB_DATA_PATH=data

# Logging Configuration
RECOLAB_LOG_LEVEL=INFO
RECOLAB_CACHE_TTL=3600

# Deployment Configuration
STREAMLIT_RUNTIME=true
PRODUCTION=false

# Performance Configuration
RECOLAB_MAX_MEMORY=1024
RECOLAB_TIMEOUT=300
```

---

## Environment Variables Data Model

### Environment Variables Schema
```python
{
    "RECOLAB_MODEL_PATH": str,      # Path to model artifacts directory
    "RECOLAB_DATA_PATH": str,       # Path to data directory
    "RECOLAB_LOG_LEVEL": str,       # Logging level (DEBUG, INFO, WARNING, ERROR)
    "RECOLAB_CACHE_TTL": int,       # Cache time-to-live in seconds
    "STREAMLIT_RUNTIME": bool,      # Whether running in Streamlit Cloud
    "PRODUCTION": bool,             # Whether in production mode
    "RECOLAB_MAX_MEMORY": int,      # Maximum memory in MB
    "RECOLAB_TIMEOUT": int,         # Request timeout in seconds
}
```

### Environment Variable Defaults
```python
DEFAULT_ENVIRONMENT = {
    "RECOLAB_MODEL_PATH": "models",
    "RECOLAB_DATA_PATH": "data",
    "RECOLAB_LOG_LEVEL": "INFO",
    "RECOLAB_CACHE_TTL": "3600",
    "STREAMLIT_RUNTIME": "false",
    "PRODUCTION": "false",
    "RECOLAB_MAX_MEMORY": "1024",
    "RECOLAB_TIMEOUT": "300",
}
```

---

## Session State Data Model

### Deployment Session State Schema
```python
DEPLOYMENT_SESSION_STATE = {
    # Deployment status and information
    "deployment_status": str,      # "local" | "staging" | "production"
    "deployment_version": str,     # Deployed version identifier
    "deployment_timestamp": str,  # ISO timestamp of deployment
    
    # Health and monitoring
    "deployment_health": {
        "status": str,              # "healthy" | "unhealthy" | "degraded"
        "last_check": str,          # ISO timestamp of last health check
        "checks": {
            "model_loading": bool,
            "data_loading": bool,
            "api_response": bool,
        },
    },
    
    # Performance metrics
    "deployment_metrics": {
        "load_time_seconds": float,
        "model_load_time_seconds": float,
        "api_response_time_seconds": float,
        "memory_usage_mb": float,
        "cpu_usage_percent": float,
    },
    
    # Deployment logs
    "deployment_logs": [
        {
            "timestamp": str,
            "level": str,            # "INFO" | "WARNING" | "ERROR"
            "message": str,
            "component": str,
        }
    ],
    
    # Production mode toggles
    "production_mode": bool,       # Whether production features are enabled
    "enhanced_monitoring": bool,   # Whether enhanced monitoring is enabled
    "error_reporting": bool,       # Whether error reporting is enabled
}
```

---

## Deployment Metadata Data Model

### Deployment Metadata Schema
```python
DEPLOYMENT_METADATA = {
    "deployment_id": str,           # Unique deployment identifier
    "deployment_date": str,         # ISO timestamp of deployment
    "git_commit": str,             # Git commit SHA
    "git_branch": str,             # Git branch name
    "environment": str,             # "local" | "staging" | "production"
    "version": str,                # Application version
    "package_size_mb": float,      # Deployment package size in MB
    "model_artifacts": {
        "popularity": bool,         # Whether Popularity model bundled
        "content": bool,            # Whether Content model bundled
        "user_based_cf": bool,      # Whether User-Based CF bundled
        "item_based_cf": bool,      # Whether Item-Based CF bundled
        "hybrid": bool,             # Whether Hybrid model bundled
    },
    "data_files": {
        "ml_latest_small": bool,    # Whether MovieLens dataset included
        "split_datasets": bool,     # Whether train/test splits included
        "evaluation_results": bool, # Whether Day 5 results included
    },
    "configuration": {
        "memory_limit_mb": int,
        "timeout_seconds": int,
        "cache_ttl_seconds": int,
        "log_level": str,
    },
}
```

---

## Health Check Data Model

### Health Check Schema
```python
HEALTH_CHECK_RESULT = {
    "status": str,                  # "healthy" | "unhealthy" | "degraded"
    "timestamp": str,               # ISO timestamp of health check
    "checks": {
        "application": {
            "status": str,
            "message": str,
            "response_time_ms": float,
        },
        "models": {
            "status": str,
            "message": str,
            "models_loaded": int,
            "models_total": int,
        },
        "data": {
            "status": str,
            "message": str,
            "files_loaded": int,
            "files_total": int,
        },
        "infrastructure": {
            "status": str,
            "message": str,
            "memory_usage_mb": float,
            "memory_limit_mb": int,
        },
    },
    "overall_status": str,
    "recommendations": list,       # List of recommended actions
}
```

---

## Model Loading Data Model

### Model Loading State Schema
```python
MODEL_LOADING_STATE = {
    "model_name": str,
    "status": str,                  # "loaded" | "loading" | "failed" | "not_loaded"
    "source": str,                 # "bundle" | "fitted" | "cached"
    "load_time_seconds": float,
    "cache_hit": bool,
    "provenance": str,              # Description of where model came from
    "version": str,                # Model version if applicable
    "error": str,                  # Error message if loading failed
}
```

---

## Cache Data Model

### Cache Entry Schema
```python
CACHE_ENTRY = {
    "key": str,                    # Cache key
    "value": Any,                  # Cached value
    "timestamp": str,               # ISO timestamp of cache creation
    "ttl": int,                    # Time-to-live in seconds
    "hits": int,                   # Number of cache hits
    "size_bytes": int,             # Size in bytes
    "version": str,                # Cache version for invalidation
}
```

---

## Log Entry Data Model

### Log Entry Schema
```python
LOG_ENTRY = {
    "timestamp": str,               # ISO timestamp
    "level": str,                  # "DEBUG" | "INFO" | "WARNING" | "ERROR"
    "logger": str,                 # Logger name
    "message": str,                # Log message
    "context": dict,               # Additional context
    "component": str,              # Component that generated the log
    "user_id": str,                # User ID if applicable
    "session_id": str,             # Session ID if applicable
}
```

---

## Error Data Model

### Error Schema
```python
ERROR_INFO = {
    "error_id": str,               # Unique error identifier
    "timestamp": str,              # ISO timestamp
    "error_type": str,             # Exception type
    "error_message": str,          # Error message
    "stack_trace": str,            # Stack trace (development only)
    "user_message": str,           # User-friendly message (production)
    "component": str,             # Component where error occurred
    "severity": str,                # "low" | "medium" | "high" | "critical"
    "resolved": bool,              # Whether error was resolved
    "resolution": str,             # Resolution description
}
```

---

## Monitoring Metrics Data Model

### Performance Metrics Schema
```python
PERFORMANCE_METRICS = {
    "timestamp": str,               # ISO timestamp
    "load_time_seconds": float,
    "model_load_time_seconds": float,
    "api_response_time_seconds": float,
    "memory_usage_mb": float,
    "cpu_usage_percent": float,
    "cache_hit_rate": float,
    "error_rate": float,
    "request_count": int,
    "success_count": int,
}
```

---

## Data Validation Rules

### Configuration Validation
- **config.toml**: Must be valid TOML format
- **requirements.txt**: Must be valid pip requirements format
- **.env.example**: Must have valid variable names and defaults

### Environment Variable Validation
- **Type Validation**: Variables must match expected types
- **Range Validation**: Numeric variables must be within valid ranges
- **Existence Validation**: Required variables must be present
- **Default Validation**: Variables must have sensible defaults

### Session State Validation
- **Type Validation**: State values must match expected types
- **Namespacing Validation**: Deployment keys must use `deployment_*` prefix
- **Conflict Validation**: No conflicts with existing session state keys

### Model Loading Validation
- **Format Validation**: Model bundles must be valid format
- **Version Validation**: Model versions must be compatible
- **Size Validation**: Model files must be within size limits
- **Availability Validation**: Required models must be available

---

## Data Relationships

### Configuration → Environment
- config.toml provides default configuration
- Environment variables override config.toml values
- Environment variables take precedence

### Environment → Session State
- Environment detection influences session state initialization
- Production mode affects session state behavior
- Environment variables configure session state defaults

### Session State → Health Checks
- Session state provides current health information
- Health checks update session state
- Session state health affects monitoring

### Model Loading → Caching
- Model loading populates cache
- Cache versioning controls invalidation
- Cache hits reduce model loading time

### Error Handling → Logging
- Errors are logged with structured format
- Error severity affects log level
- Error context provides debugging information

---

## Data Storage

### File System Storage
- **Configuration Files**: Project root (.streamlit/, requirements.txt, .env.example)
- **Data Files**: data/ directory (ml-latest-small, split_datasets, evaluation)
- **Model Artifacts**: models/ directory (if pre-bundled)
- **Documentation**: docs/ directory

### In-Memory Storage
- **Session State**: Streamlit session state (per user session)
- **Cache**: Streamlit cache_resource (per server run)
- **Environment Variables**: Runtime environment (per deployment)

### External Storage
- **Streamlit Cloud Logs**: Streamlit Cloud platform logs
- **Git Repository**: Source code and configuration
- **Deployment Metadata**: Streamlit Cloud deployment records

---

## Data Migration

### Configuration Migration
- **From**: No configuration files
- **To**: .streamlit/config.toml, requirements.txt, .env.example
- **Strategy**: Create new files with sensible defaults
- **Rollback**: Delete new files, use hardcoded defaults

### Session State Migration
- **From**: No deployment state
- **To**: Deployment state with namespacing
- **Strategy**: Automatic via SessionManager.ensure_initialized()
- **Rollback**: Remove deployment state keys

### Environment Variable Migration
- **From**: No environment variables
- **To**: RECOLAB_* environment variables
- **Strategy**: Use defaults if not set
- **Rollback**: Remove environment variable references

---

## Data Retention

### Configuration Data
- **Retention**: Permanent (in repository)
- **Backup**: Git history
- **Purge**: Never

### Session State Data
- **Retention**: Per user session
- **Backup**: None (ephemeral)
- **Purge**: On session end

### Log Data
- **Retention**: 30 days (Streamlit Cloud default)
- **Backup**: Streamlit Cloud logs
- **Purge**: After 30 days

### Cache Data
- **Retention**: Per server run (TTL-based)
- **Backup**: None (rebuildable)
- **Purge**: On server restart or TTL expiration

---

## Data Security

### Sensitive Data
- **Environment Variables**: Must use .env, not commit to repository
- **API Keys**: Must use environment variables, never hardcode
- **Passwords**: Must use environment variables, never hardcode
- **User Data**: No user data persistence in this application

### Data Encryption
- **In Transit**: HTTPS (Streamlit Cloud default)
- **At Rest**: Streamlit Cloud managed encryption
- **Configuration**: No sensitive data in configuration files

### Access Control
- **Configuration**: Public (repository)
- **Environment Variables**: Application-level only
- **Session State**: Per user session (isolated)
- **Logs**: Streamlit Cloud platform (owner access only)
