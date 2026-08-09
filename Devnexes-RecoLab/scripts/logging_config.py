"""Logging configuration for Day 5 evaluation and analysis scripts.

Provides structured logging with different levels for debugging,
monitoring, and error tracking.
"""

import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logging(
    name: str = "recolab",
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None,
) -> logging.Logger:
    """Set up logging configuration for evaluation and analysis scripts.
    
    Args:
        name: Logger name.
        level: Logging level (default: INFO).
        log_file: Optional path to log file. If None, logs to console only.
        format_string: Optional custom format string.
        
    Returns:
        Configured logger instance.
    """
    if format_string is None:
        format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatter
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get an existing logger or create a new one with default configuration.
    
    Args:
        name: Logger name.
        
    Returns:
        Logger instance.
    """
    logger = logging.getLogger(name)
    if not logger.handlers:
        return setup_logging(name)
    return logger


# Pre-configured loggers for different components
def get_evaluation_logger() -> logging.Logger:
    """Get logger for evaluation scripts."""
    return get_logger("recolab.evaluation")


def get_analysis_logger() -> logging.Logger:
    """Get logger for analysis scripts."""
    return get_logger("recolab.analysis")


def get_model_logger() -> logging.Logger:
    """Get logger for model operations."""
    return get_logger("recolab.model")


# Context manager for temporary logging level changes
class LoggingContext:
    """Context manager for temporarily changing logging level."""
    
    def __init__(self, logger: logging.Logger, level: int):
        """Initialize context manager.
        
        Args:
            logger: Logger instance.
            level: Temporary logging level.
        """
        self.logger = logger
        self.level = level
        self.old_level = None
    
    def __enter__(self):
        """Enter context and set new logging level."""
        self.old_level = self.logger.level
        self.logger.setLevel(self.level)
        return self.logger
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context and restore original logging level."""
        self.logger.setLevel(self.old_level)

import functools
from typing import Callable, Any
from scripts.env_utils import _detect_deployment_environment

class UserFacingError(Exception):
    """Exception raised for errors that should be displayed to the user."""
    pass

def configure_production_logging(name: str = "recolab") -> logging.Logger:
    """Configure production logging based on the environment."""
    env = _detect_deployment_environment()
    
    if env == "production":
        level = logging.WARNING
        format_string = "%(asctime)s - %(name)s - %(levelname)s - [PRODUCTION] - %(message)s"
    elif env == "streamlit_cloud":
        level = logging.INFO
        format_string = "%(asctime)s - %(name)s - %(levelname)s - [CLOUD] - %(message)s"
    else:
        level = logging.INFO
        format_string = "%(asctime)s - %(name)s - %(levelname)s - [LOCAL] - %(message)s"
        
    return setup_logging(name=name, level=level, format_string=format_string)

def production_error_handler(
    func: Optional[Callable] = None,
    *,
    context_message: Optional[str] = None,
    user_message: str = "An error occurred. Please try again.",
) -> Callable:
    """Decorator to handle errors in production by logging them and raising user-friendly errors.

    Can be used bare (@production_error_handler) or with parameters (@production_error_handler(user_message="...")).
    """
    def decorator(fn: Callable) -> Callable:
        @functools.wraps(fn)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return fn(*args, **kwargs)
            except Exception as e:
                env = _detect_deployment_environment()
                logger = logging.getLogger("recolab.production_errors")
                err_msg = f"{context_message or 'Error in ' + fn.__name__}: {e}"
                if env in ("production", "streamlit_cloud"):
                    logger.error(err_msg, exc_info=True)
                    if isinstance(e, UserFacingError):
                        raise
                    raise UserFacingError(user_message) from e
                else:
                    logger.warning(f"Local dev exception caught in {fn.__name__}: {e}")
                    if isinstance(e, UserFacingError):
                        raise
                    raise UserFacingError(f"{user_message} (Details: {e})") from e
        return wrapper

    if func is None:
        return decorator
    return decorator(func)
