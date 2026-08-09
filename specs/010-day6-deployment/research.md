# Day 6 Morning: Deployment Setup - Research

**Feature ID:** 010-day6-deployment  
**Date:** 2026-08-08  
**Status**: Draft

---

## Overview

This document compiles research findings on Streamlit Cloud deployment, deployment best practices, and infrastructure configuration for the Devnexes RecoLab application.

---

## Streamlit Cloud Platform Research

### Platform Overview
**What is Streamlit Cloud?**
- Streamlit's official hosting platform for Streamlit applications
- Zero-configuration deployment from Git repositories
- Built-in caching, SSL, and domain management
- Free tier available with resource limits

### Key Features
- **Git Integration**: Connect GitHub repository for automatic deployment
- **Automatic Builds**: Deploys on git push to connected branch
- **Resource Management**: Built-in memory and CPU limits
- **Caching**: @st.cache_resource decorator for model caching
- **SSL/TLS**: Automatic SSL certificates
- **Custom Domains**: Support for custom domain names
- **Monitoring**: Built-in logs and metrics
- **Collaboration**: Team collaboration features

### Pricing (as of 2026)
- **Free Tier**: 
  - Community support
  - 1GB memory limit
  - 10GB disk space
  - Standard CPU
  - Up to 3 apps
  
- **Pro Tier ($20/month)**:
  - Priority support
  - 2GB memory limit
  - 50GB disk space
  - Faster CPU
  - Unlimited apps
  - Custom domains
  - Priority builds

### Resource Limits
- **Memory**: 1GB (free), 2GB (pro)
- **Disk Space**: 10GB (free), 50GB (pro)
- **File Upload**: 200MB default
- **Request Timeout**: 300 seconds default
- **Session Duration**: Limited by inactivity timeout

---

## Deployment Configuration Research

### requirements.txt Best Practices
**Standard Dependencies**:
```txt
streamlit>=1.28.0
pandas>=2.0.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0
matplotlib>=3.7.0
seaborn>=0.12.0
```

**Best Practices**:
- Pin versions to avoid breaking changes
- Use >= for minor version compatibility
- Exclude development dependencies (pytest, mypy, ruff)
- Include only production dependencies
- Validate dependency compatibility

### .streamlit/config.toml Configuration
**Configuration Options**:
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
toolbarMode = "auto" | "viewer" | "minimal" | "server"

[logger]
level = "debug" | "info" | "warning" | "error"
```

**Best Practices**:
- Set showErrorDetails to false in production
- Configure appropriate file upload limits
- Set toolbarMode to "viewer" for production
- Set logger level to "warning" or "error" in production

### Environment Variables Strategy
**Common Patterns**:
- Use PROJECT_PREFIX for custom variables (e.g., RECOLAB_)
- Provide sensible defaults for all variables
- Document all variables in .env.example
- Never commit .env file to repository
- Use .env.example as template

**Variable Categories**:
- **Path Configuration**: MODEL_PATH, DATA_PATH
- **Logging Configuration**: LOG_LEVEL, LOG_FILE
- **Performance Configuration**: CACHE_TTL, MAX_MEMORY
- **Feature Flags**: PRODUCTION_MODE, ENHANCED_MONITORING

---

## Model Loading Research

### Streamlit Caching Strategy
**@st.cache_resource Decorator**:
- Caches expensive operations per server run
- Automatically invalidates on server restart
- Supports TTL (time-to-live) parameter
- Thread-safe by default

**Best Practices**:
```python
@st.cache_resource(ttl=3600, show_spinner=False)
def load_model(model_name: str):
    return _fit_model(model_name, train, movies)
```

**Cache Versioning**:
- Add version parameter to cache key
- Update version on model changes
- Use cache invalidation strategy

### Dual-Path Loading Strategy
**Environment Detection**:
```python
def _detect_deployment_environment() -> str:
    if os.getenv("STREAMLIT_RUNTIME"):
        return "streamlit_cloud"
    elif os.getenv("PRODUCTION"):
        return "production"
    else:
        return "local"
```

**Dual Implementation**:
```python
if _detect_deployment_environment() == "streamlit_cloud":
    @st.cache_resource
    def load_model_with_cache(name):
        return _fit_model(name, train, movies)
else:
    def load_model_direct(name):
        return _fit_model(name, train, movies)
```

### Model Artifact Management
**Bundle Strategy**:
- Pre-bundle models for faster loading
- Use persistence.py load_model_bundle() API
- Fall back to fitting if bundles not available
- Validate bundle format and version

**Optimization**:
- Compress model bundles
- Use efficient serialization (pickle)
- Validate bundle integrity
- Document bundle format

---

## Infrastructure Configuration Research

### Memory Management
**Memory Requirements**:
- **Base Application**: ~200MB
- **Data Files**: ~100MB (ml-latest-small)
- **Model Artifacts**: ~50MB per model (if bundled)
- **Runtime Memory**: ~300MB
- **Total**: ~650MB (well under 1GB limit)

**Optimization Strategies**:
- Use sparse matrices for collaborative filtering
- Lazy load data files
- Efficient model caching
- Memory profiling during development

### Timeout Configuration
**Default Timeout**: 300 seconds (5 minutes)
**Adjustment Strategy**:
- Increase for model loading: 600 seconds
- Keep default for API calls: 300 seconds
- Configure per operation type
- Document timeout settings

### Caching Strategy
**Cache Types**:
- **Model Cache**: @st.cache_resource for models
- **Data Cache**: @st.cache_data for data
- **Function Cache**: @st.cache for expensive computations

**Cache Configuration**:
```python
@st.cache_resource(ttl=3600, show_spinner=False)
def load_model(name):
    # Cache for 1 hour
    pass

@st.cache_data(ttl=300, show_spinner=False)
def compute_metrics(data):
    # Cache for 5 minutes
    pass
```

**Cache Warming**:
- Pre-load all models on deployment
- Pre-compute common metrics
- Validate cache hit rate
- Monitor cache performance

---

## Logging and Monitoring Research

### Logging Configuration
**Streamlit Cloud Logging**:
- Automatic log collection
- Accessible via Streamlit Cloud dashboard
- Structured logging support
- Log level configuration

**Logging Best Practices**:
```python
import logging

# Configure based on environment
if os.getenv("PRODUCTION"):
    logging.basicConfig(level=logging.WARNING)
else:
    logging.basicConfig(level=logging.INFO)
```

**Structured Logging**:
- Use Python logging module
- Include context in log messages
- Use appropriate log levels
- Log errors with stack traces (development only)

### Monitoring Strategy
**Built-in Monitoring**:
- Application uptime
- Resource usage (memory, CPU)
- Request metrics
- Error rate

**Custom Monitoring**:
- Model loading metrics
- API response time
- Cache hit rate
- User activity metrics

**Health Checks**:
```python
def health_check():
    return {
        "status": "healthy",
        "models_loaded": len(loaded_models),
        "data_loaded": True,
        "memory_usage": get_memory_usage(),
    }
```

---

## Error Handling Research

### Production Error Handling
**Best Practices**:
- Hide stack traces in production
- Show user-friendly error messages
- Log errors with context
- Implement graceful degradation

**Error Handler Pattern**:
```python
def production_error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if os.getenv("PRODUCTION"):
                logger.error(f"Error in {func.__name__}: {e}")
                raise UserFacingError("An error occurred. Please try again.")
            else:
                raise
    return wrapper
```

### Error Types
- **Model Loading Errors**: Fallback to fitting
- **Data Loading Errors**: Show user-friendly message
- **API Errors**: Retry with exponential backoff
- **Timeout Errors**: Increase timeout or optimize

---

## Deployment Process Research

### Staging to Production Workflow
**Staging Deployment**:
1. Deploy to staging environment
2. Run comprehensive tests
3. Validate all functionality
4. Monitor performance
5. Check error rates

**Production Deployment**:
1. Approve staging deployment
2. Deploy to production
3. Monitor initial load
4. Validate production functionality
5. Set up monitoring alerts

### Deployment Validation
**Validation Checklist**:
- [ ] Application deploys successfully
- [ ] All functionality works
- [ ] Model loading works
- [ ] Data files load
- [ ] Performance meets NFRs
- [ ] Error handling works
- [ ] Monitoring is functional

### Rollback Strategy
**Automatic Rollback**:
- Git revert to previous commit
- Streamlit Cloud auto-deploys
- Monitor rollback success

**Manual Rollback**:
- Revert configuration changes
- Restore environment variables
- Restart application

---

## Security Research

### Security Best Practices
**Secrets Management**:
- Never hardcode secrets
- Use environment variables for sensitive data
- Use .env.example for documentation
- Never commit .env file

**Input Validation**:
- Validate all user inputs
- Sanitize user data
- Implement rate limiting
- Use prepared statements for database queries

**File Access Security**:
- Use path validation (path_utils.py from Day 5)
- Validate file paths before access
- Implement file size limits
- Sanitize file names

**Error Message Security**:
- Hide stack traces in production
- Don't expose internal state
- Use generic error messages
- Log detailed errors internally

---

## Performance Optimization Research

### Load Time Optimization
**Strategies**:
- Optimize data file sizes
- Use efficient data formats
- Implement lazy loading
- Use caching strategically

**Model Loading Optimization**:
- Pre-bundle models
- Use efficient serialization
- Implement cache warming
- Parallelize model loading

### Memory Optimization
**Strategies**:
- Use sparse matrices
- Free unused objects
- Optimize data structures
- Monitor memory usage

### Response Time Optimization
**Strategies**:
- Cache expensive operations
- Optimize algorithms
- Use efficient data structures
- Implement async operations

---

## Testing Strategy Research

### Deployment Testing
**Staging Tests**:
- End-to-end functionality tests
- Performance tests
- Error scenario tests
- Model loading tests
- Data loading tests

**Production Tests**:
- Smoke tests (basic functionality)
- Health check tests
- Performance monitoring
- Error monitoring

### Continuous Integration
**CI Pipeline**:
- Run tests on every commit
- Validate deployment package
- Check performance metrics
- Validate configuration

---

## Troubleshooting Research

### Common Issues
**Deployment Failures**:
- Check requirements.txt format
- Validate Git repository connection
- Check Streamlit Cloud logs
- Verify file permissions

**Model Loading Failures**:
- Check model bundle format
- Validate model version compatibility
- Check memory limits
- Verify fallback mechanism

**Performance Issues**:
- Monitor memory usage
- Check cache hit rate
- Optimize data loading
- Profile bottlenecks

### Debugging Strategies
**Local Testing**:
- Reproduce issues locally
- Use production configuration locally
- Enable detailed logging
- Profile performance

**Production Debugging**:
- Check Streamlit Cloud logs
- Monitor metrics
- Use health checks
- Reproduce in staging

---

## Documentation Research

### Required Documentation
**Deployment Documentation**:
- Deployment guide
- Configuration guide
- Troubleshooting guide
- Environment variable reference

**User Documentation**:
- README updates
- Setup instructions
- Usage guide
- API documentation

**Technical Documentation**:
- Architecture documentation
- API reference
- Design decisions
- Code documentation

---

## References

### Streamlit Cloud Documentation
- Streamlit Cloud official documentation
- Deployment guide
- Configuration reference
- Best practices guide

### Python Deployment Best Practices
- Python packaging guide
- Virtual environment best practices
- Dependency management
- Security best practices

### Streamlit Documentation
- Streamlit API reference
- Caching documentation
- Deployment documentation
- Performance optimization guide
