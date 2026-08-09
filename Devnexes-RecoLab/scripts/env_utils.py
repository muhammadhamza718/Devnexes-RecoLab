"""Environment utility functions for deployment configuration and validation."""

import os
import logging

logger = logging.getLogger(__name__)

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

def _detect_deployment_environment() -> str:
    """Detect the current deployment environment.

    Returns:
        Environment string: "streamlit_cloud", "production", or "local"
    """
    if os.getenv("STREAMLIT_RUNTIME", "").lower() in ("true", "1", "yes"):
        return "streamlit_cloud"
    elif os.getenv("PRODUCTION", "").lower() in ("true", "1", "yes"):
        return "production"
    else:
        return "local"

def validate_environment() -> dict:
    """Validate environment variables and apply defaults for missing ones.

    Returns:
        Dictionary containing the validated environment configuration.
    """
    env_config = {}

    for key, default_val in DEFAULT_ENVIRONMENT.items():
        val = os.getenv(key)
        if val is None:
            logger.info(f"Environment variable {key} not set. Using default: {default_val}")
            env_config[key] = default_val
        else:
            env_config[key] = val

    # Validate specific types
    try:
        env_config["RECOLAB_CACHE_TTL"] = int(env_config["RECOLAB_CACHE_TTL"])
    except ValueError:
        logger.warning(f"Invalid RECOLAB_CACHE_TTL. Using default: {DEFAULT_ENVIRONMENT['RECOLAB_CACHE_TTL']}")
        env_config["RECOLAB_CACHE_TTL"] = int(DEFAULT_ENVIRONMENT["RECOLAB_CACHE_TTL"])

    try:
        env_config["RECOLAB_MAX_MEMORY"] = int(env_config["RECOLAB_MAX_MEMORY"])
    except ValueError:
        logger.warning(f"Invalid RECOLAB_MAX_MEMORY. Using default: {DEFAULT_ENVIRONMENT['RECOLAB_MAX_MEMORY']}")
        env_config["RECOLAB_MAX_MEMORY"] = int(DEFAULT_ENVIRONMENT["RECOLAB_MAX_MEMORY"])

    try:
        env_config["RECOLAB_TIMEOUT"] = int(env_config["RECOLAB_TIMEOUT"])
    except ValueError:
        logger.warning(f"Invalid RECOLAB_TIMEOUT. Using default: {DEFAULT_ENVIRONMENT['RECOLAB_TIMEOUT']}")
        env_config["RECOLAB_TIMEOUT"] = int(DEFAULT_ENVIRONMENT["RECOLAB_TIMEOUT"])

    # Convert booleans
    env_config["STREAMLIT_RUNTIME"] = str(env_config["STREAMLIT_RUNTIME"]).lower() in ("true", "1", "yes")
    env_config["PRODUCTION"] = str(env_config["PRODUCTION"]).lower() in ("true", "1", "yes")

    return env_config


def perform_health_check() -> dict:
    """Perform a system health check verifying directories, resources, and configuration.

    Returns:
        Dictionary containing health status ('healthy', 'degraded', 'unhealthy')
        and component diagnostic details.
    """
    config = validate_environment()
    data_path = config.get("RECOLAB_DATA_PATH", "data")
    model_path = config.get("RECOLAB_MODEL_PATH", "models")

    checks = {
        "data_directory": os.path.exists(data_path),
        "model_directory": os.path.exists(model_path),
        "environment": _detect_deployment_environment(),
    }

    issues = []
    if not checks["data_directory"]:
        issues.append(f"Data directory '{data_path}' not found")
    if not checks["model_directory"]:
        issues.append(f"Model directory '{model_path}' not found")

    if not issues:
        status = "healthy"
    elif len(issues) == 1:
        status = "degraded"
    else:
        status = "unhealthy"

    return {
        "status": status,
        "checks": checks,
        "issues": issues,
        "config": config,
    }

