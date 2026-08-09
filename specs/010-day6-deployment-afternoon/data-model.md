# Day 6 Afternoon: Production Readiness - Data Model

**Feature ID:** 010-day6-deployment-afternoon  
**Date:** 2026-08-08  
**Status**: Draft

---

## Overview

This document defines the data model for Day 6 production readiness, including error handling, loading states, empty states, user feedback, and testing data structures.

---

## Error Handling Data Model

### Error State Schema
```python
ERROR_STATE = {
    "error_id": str,               # Unique error identifier (UUID)
    "error_type": str,             # Exception type (e.g., "ValueError", "ModelLoadError")
    "error_message": str,          # Original error message
    "user_message": str,           # User-friendly error message
    "timestamp": str,              # ISO timestamp (YYYY-MM-DDTHH:MM:SSZ)
    "component": str,             # Component where error occurred
    "severity": str,                # "low" | "medium" | "high" | "critical"
    "resolved": bool,              # Whether error was resolved
    "recovery_action": str,       # Recovery action taken
    "stack_trace": str,            # Stack trace (development only)
    "context": dict,               # Additional error context
}
```

### Error Categories
```python
ERROR_CATEGORIES = {
    "model_loading": {
        "severity": "high",
        "user_message": "Failed to load model. Please try again.",
        "recovery": "Retry with fallback to fitting",
    },
    "data_loading": {
        "severity": "medium",
        "user_message": "Failed to load data. Please refresh.",
        "recovery": "Retry data loading",
    },
    "recommendation": {
        "severity": "medium",
        "user_message": "Unable to generate recommendations. Please try a different model.",
        "recovery": "Try alternative model",
    },
    "computation": {
        "severity": "low",
        "user_message": "Computation failed. Please try again.",
        "recovery": "Retry computation",
    },
}
```

---

## Loading State Data Model

### Loading State Schema
```python
LOADING_STATE = {
    "operation_id": str,           # Unique operation identifier (UUID)
    "operation_type": str,         # "model_loading" | "data_loading" | "computation"
    "status": str,                  # "loading" | "complete" | "failed" | "cancelled"
    "progress": float,              # 0.0 to 1.0 (percentage)
    "message": str,                 # Current status message
    "start_time": str,              # ISO timestamp
    "end_time": str,                # ISO timestamp (null if loading)
    "timeout": int,                 # Timeout in seconds
    "estimated_time": int,          # Estimated completion time (seconds)
    "metadata": dict,               # Operation-specific metadata
}
```

### Loading Operation Types
```python
LOADING_OPERATION_TYPES = {
    "model_loading": {
        "default_timeout": 60,
        "estimated_time": 20,
        "metadata_keys": ["model_name", "model_size"],
    },
    "data_loading": {
        "default_timeout": 30,
        "estimated_time": 10,
        "metadata_keys": ["file_name", "file_size"],
    },
    "computation": {
        "default_timeout": 120,
        "estimated_time": 30,
        "metadata_keys": ["computation_type", "input_size"],
    },
}
```

---

## Empty State Data Model

### Empty State Schema
```python
EMPTY_STATE = {
    "component": str,               # Component identifier
    "state_type": str,             # "no_data" | "no_results" | "not_found" | "error"
    "message": str,                 # User-facing message
    "actionable": bool,             # Whether suggested actions are available
    "suggested_actions": list,       # List of suggested actions
    "icon": str,                    # Visual indicator (emoji)
    "secondary_message": str,       # Additional context (optional)
    "documentation_link": str,       # Link to documentation (optional)
}
```

### Empty State Component Library
```python
EMPTY_STATE_LIBRARY = {
    "recommendations": {
        "no_user_selected": {
            "message": "No user selected",
            "actionable": True,
            "suggested_actions": ["Select a user from the dropdown"],
            "icon": "👤",
        },
        "no_model_selected": {
            "message": "No model selected",
            "actionable": True,
            "suggested_actions": ["Select a model from the dropdown"],
            "icon": "🤖",
        },
        "no_recommendations": {
            "message": "No recommendations available",
            "actionable": True,
            "suggested_actions": ["Try a different model", "Select a different user"],
            "icon": "📭",
        },
    },
    "similar_items": {
        "no_movie_selected": {
            "message": "No movie selected",
            "actionable": True,
            "suggested_actions": ["Select a movie to see similar items"],
            "icon": "🔍",
        },
        "no_similar_items": {
            "message": "No similar items found",
            "actionable": True,
            "suggested_actions": ["Try a different movie", "Rate more movies for better results"],
            "icon": "🔍",
        },
    },
    "dashboard": {
        "no_metrics": {
            "message": "No metrics available",
            "actionable": True,
            "suggested_actions": ["Run evaluation to generate metrics"],
            "icon": "📊",
        },
        "no_comparison": {
            "message": "No comparison data available",
            "actionable": True,
            "suggested_actions": ["Run model comparison to generate data"],
            "icon": "📊",
        },
    },
}
```

---

## User Feedback Data Model

### Feedback Schema
```python
USER_FEEDBACK = {
    "feedback_id": str,             # Unique feedback identifier (UUID)
    "user_id": str,                 # User ID (optional, for authenticated users)
    "timestamp": str,              # ISO timestamp
    "feedback_type": str,           # "bug" | "feature" | "improvement" | "other"
    "message": str,                 # Feedback message
    "satisfaction": int,            # 1-5 scale (1=poor, 5=excellent)
    "component": str,              # Component where feedback applies
    "resolved": bool,              # Whether feedback has been addressed
    "resolution": str,              # Resolution description (if resolved)
    "resolution_timestamp": str,    # ISO timestamp of resolution
    "metadata": dict,               # Additional feedback context
}
```

### Feedback Categories
```python
FEEDBACK_TYPES = {
    "bug": {
        "priority": "high",
        "response_time": "24 hours",
    },
    "feature": {
        "priority": "medium",
        "response_time": "7 days",
    },
    "improvement": {
        "priority": "low",
        "response_time": "14 days",
    },
    "other": {
        "priority": "low",
        "response_time": "7 days",
    },
}
```

---

## Testing Data Model

### Test Case Schema
```python
TEST_CASE = {
    "test_id": str,                 # Unique test identifier
    "test_name": str,               # Test name
    "test_type": str,               # "unit" | "integration" | "e2e" | "performance" | "security"
    "component": str,              # Component being tested
    "description": str,             # Test description
    "steps": list,                 # Test steps
    "expected_result": str,         # Expected result
    "actual_result": str,          # Actual result (after test)
    "status": str,                 # "passed" | "failed" | "skipped"
    "duration_seconds": float,      # Test duration
    "timestamp": str,              # ISO timestamp
    "error_message": str,           # Error message (if failed)
}
```

### Test Suite Schema
```python
TEST_SUITE = {
    "suite_id": str,               # Unique suite identifier
    "suite_name": str,             # Suite name
    "test_type": str,               # Type of tests in suite
    "test_cases": list,             # List of TEST_CASE objects
    "total_cases": int,             # Total number of test cases
    "passed_cases": int,            # Number of passed cases
    "failed_cases": int,            # Number of failed cases
    "skipped_cases": int,           # Number of skipped cases
    "pass_rate": float,            # Pass rate (0.0 to 1.0)
    "duration_seconds": float,      # Total suite duration
    "timestamp": str,              # ISO timestamp
}
```

---

## Performance Metrics Data Model

### Performance Metric Schema
```python
PERFORMANCE_METRIC = {
    "metric_id": str,              # Unique metric identifier
    "metric_name": str,             # Metric name
    "metric_type": str,             # "load_time" | "response_time" | "memory" | "cpu"
    "component": str,              # Component being measured
    "value": float,                # Metric value
    "unit": str,                   # Unit of measurement
    "threshold": float,            # Performance threshold
    "status": str,                 # "pass" | "fail" | "warning"
    "timestamp": str,              # ISO timestamp
    "metadata": dict,               # Additional metric context
}
```

### Performance Budgets
```python
PERFORMANCE_BUDGETS = {
    "load_time": {
        "threshold": 30.0,        # seconds
        "unit": "seconds",
        "severity": "high",
    },
    "response_time": {
        "threshold": 5.0,         # seconds
        "unit": "seconds",
        "severity": "high",
    },
    "memory_usage": {
        "threshold": 1024.0,     # MB
        "unit": "MB",
        "severity": "high",
    },
    "cpu_usage": {
        "threshold": 50.0,        # percentage
        "unit": "percent",
        "severity": "medium",
    },
}
```

---

## Security Validation Data Model

### Security Test Schema
```python
SECURITY_TEST = {
    "test_id": str,                 # Unique test identifier
    "test_name": str,               # Security test name
    "test_type": str,               # "input_validation" | "file_access" | "error_message" | "session_state" | "environment_variable"
    "component": str,              # Component being tested
    "description": str,             # Test description
    "test_procedure": str,          # Test procedure
    "expected_result": str,         # Expected result
    "actual_result": str,          # Actual result
    "status": str,                 # "passed" | "failed" | "warning"
    "vulnerability": str,          # Vulnerability type (if failed)
    "severity": str,                # "low" | "medium" | "high" | "critical"
    "timestamp": str,              # ISO timestamp
}
```

### Security Categories
```python
SECURITY_CATEGORIES = {
    "input_validation": {
        "tests": [
            "SQL injection prevention",
            "XSS prevention",
            "Command injection prevention",
            "Path traversal prevention",
        ],
        "severity": "high",
    },
    "file_access": {
        "tests": [
            "Path validation",
            "File permission checks",
            "File size limits",
        ],
        "severity": "medium",
    },
    "error_message": {
        "tests": [
            "Stack trace exposure prevention",
            "Internal state exposure prevention",
            "Sensitive data exposure prevention",
        ],
        "severity": "high",
    },
    "session_state": {
        "tests": [
            "Session isolation",
            "State manipulation prevention",
            "Data leakage prevention",
        ],
        "severity": "medium",
    },
    "environment_variable": {
        "tests": [
            "Secret exposure prevention",
            "Environment variable validation",
            "Secure default values",
        ],
        "severity": "high",
    },
}
```

---

## Data Validation Rules

### Error State Validation
- **ID Validation**: error_id must be valid UUID
- **Type Validation**: error_type must be valid exception type
- **Severity Validation**: severity must be in allowed values
- **Timestamp Validation**: timestamp must be valid ISO format
- **Message Validation**: messages must be non-empty
- **Context Validation**: context must be dict

### Loading State Validation
- **ID Validation**: operation_id must be valid UUID
- **Type Validation**: operation_type must be in allowed values
- **Status Validation**: status must be in allowed values
- **Progress Validation**: progress must be between 0.0 and 1.0
- **Timeout Validation**: timeout must be positive integer
- **Timestamp Validation**: timestamps must be valid ISO format

### Empty State Validation
- **Component Validation**: component must be in allowed values
- **Type Validation**: state_type must be in allowed values
- **Message Validation**: message must be non-empty
- **Actionable Validation**: actionable must be boolean
- **Icon Validation**: icon must be emoji or valid string

### User Feedback Validation
- **ID Validation**: feedback_id must be valid UUID
- **Type Validation**: feedback_type must be in allowed values
- **Satisfaction Validation**: satisfaction must be 1-5
- **Timestamp Validation**: timestamp must be valid ISO format
- **Message Validation**: message must be non-empty

---

## Data Relationships

### Error Handling Relationships
- **Error State → Logging**: Errors logged with context
- **Error State → User Message**: User-friendly message displayed
- **Error State → Recovery**: Recovery action executed
- **Error State → Monitoring**: Error tracked in metrics

### Loading State Relationships
- **Loading State → Progress**: Progress updates over time
- **Loading State → Timeout**: Timeout triggers cancellation
- **Loading State → Cancellation**: User can cancel operation
- **Loading State → UI**: Loading state displayed in UI

### Empty State Relationships
- **Empty State → Component**: Empty state applies to specific component
- **Empty State → UI**: Empty state displayed in UI
- **Empty State → Actions**: Suggested actions displayed
- **Empty State → Navigation**: User can navigate to suggested actions

### User Feedback Relationships
- **User Feedback → Storage**: Feedback stored (session or external)
- **User Feedback → Acknowledgment**: Acknowledgment shown to user
- **User Feedback → Analytics**: Feedback analyzed for trends
- **User Feedback → Resolution**: Feedback tracked for resolution

---

## Data Storage

### Session Storage
- **Error State**: Session state (ephemeral, per session)
- **Loading State**: Session state (ephemeral, per session)
- **User Feedback**: Session state (ephemeral) or external service (persistent)

### File System Storage
- **Empty State Library**: Code (static definitions)
- **Test Results**: tests/ directory (persistent)
- **Performance Metrics**: data/evaluation/advanced_analysis/ (persistent)

### External Storage
- **User Feedback**: Optional external service (not implemented in MVP)
- **Monitoring**: Streamlit Cloud logs (persistent)

---

## Data Migration

### Error State Migration
- **From**: No error state tracking
- **To**: Error state in session state
- **Strategy**: Automatic via SessionManager.ensure_initialized()
- **Rollback**: Remove error state keys from session state

### Loading State Migration
- **From**: No loading state tracking
- **To**: Loading state in session state
- **Strategy**: Automatic via SessionManager.ensure_initialized()
- **Rollback**: Remove loading state keys from session state

### Empty State Migration
- **From**: Inline empty state handling
- **To**: Empty state component library
- **Strategy**: Replace inline handling with component library
- **Rollback**: Revert to inline handling

### User Feedback Migration
- **From**: No user feedback
- **To**: User feedback in session state
- **Strategy**: Add new session state keys
- **Rollback**: Remove feedback keys from session state

---

## Data Retention

### Error State Data
- **Retention**: Per session (ephemeral)
- **Backup**: None (ephemeral)
- **Purge**: On session end

### Loading State Data
- **Retention**: Per session (ephemeral)
- **Backup**: None (ephemeral)
- **Purge**: On session end or completion

### Empty State Data
- **Retention**: Permanent (code-based)
- **Backup**: Git history
- **Purge**: Never

### User Feedback Data
- **Retention**: Per session (ephemeral) or external service (persistent)
- **Backup**: None (ephemeral) or external service backup
- **Purge**: On session end (ephemeral) or external service retention policy

---

## Data Security

### Sensitive Data
- **Error Messages**: No stack traces in production
- **User Feedback**: No personal data required
- **Loading State**: No sensitive data
- **Empty State**: No sensitive data

### Data Encryption
- **In Transit**: HTTPS (Streamlit Cloud default)
- **At Rest**: Streamlit Cloud managed encryption
- **Configuration**: No sensitive data in configuration

### Access Control
- **Error State**: Per user session (isolated)
- **Loading State**: Per user session (isolated)
- **Empty State**: No access control (public code)
- **User Feedback**: Per user session (isolated)
