# Local Development Setup Guide

This guide provides step-by-step instructions for initializing, configuring, and testing the RecoLab codebase on local development workstations (Windows, macOS, Linux).

---

## 1. Environment Requirements
- **Python**: Python 3.11, 3.12, or 3.14 (64-bit recommended)
- **Git**: 2.30+
- **Virtual Environment Tool**: Standard `venv` module or `uv` / `conda`

---

## 2. Step-by-Step Installation

### Step 1: Clone Repository
```bash
git clone https://github.com/muhammadhamza718/Devnexes-RecoLab.git
cd Devnexes-RecoLab
```

### Step 2: Create Virtual Environment
```bash
# Windows (Git Bash or PowerShell)
python -m venv venv

# Linux / macOS
python3 -m venv venv
```

### Step 3: Activate Virtual Environment
```bash
# Windows (Git Bash)
source venv/Scripts/activate

# Windows (PowerShell)
.\venv\Scripts\Activate.ps1

# Linux / macOS
source venv/bin/activate
```

### Step 4: Install Dependencies in Editable Mode
```bash
pip install --upgrade pip
pip install -e ".[dev]"
```

---

## 3. Running Quality Assurance & Tests

### Run Unit Tests
```bash
# Run all unit tests excluding UI tests
pytest tests/test_collaborative.py tests/test_content.py tests/test_hybrid.py tests/test_baseline.py tests/test_metrics.py tests/test_persistence.py tests/test_interfaces.py

# Run with test coverage output
pytest --cov=src/recolab --cov-report=term-missing
```

### Run Static Analysis & Formatting
```bash
# Code style and linting check
ruff check src/ tests/

# Type safety check
mypy src/
```

---

## 4. Environment Variables Configuration
Copy `.env.example` to `.env` (if custom paths or ports are needed):
```ini
RECOLAB_DATA_DIR=data/ml-latest-small
RECOLAB_MODELS_DIR=models
STREAMLIT_SERVER_PORT=8501
```
