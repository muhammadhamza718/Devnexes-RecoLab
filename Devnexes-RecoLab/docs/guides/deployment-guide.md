# Deployment & Production Operations Guide

This guide covers building, containerizing, deploying, and operating the RecoLab recommendation engine and Streamlit web interface in production or staging environments.

---

## 1. Streamlit Web Dashboard Deployment

### Local Process Serving
```bash
# Activate virtual environment
source venv/Scripts/activate

# Launch Streamlit app
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```
Access the application at `http://localhost:8501`.

---

## 2. Docker Containerization

### Dockerfile Specification
RecoLab includes a production-optimized `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY pyproject.toml .
RUN pip install --no-cache-dir .

# Copy application source code
COPY . .

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build & Run Container
```bash
# Build image
docker build -t recolab-hybrid:v1.0 .

# Run container in background
docker run -d \
  --name recolab-service \
  -p 8501:8501 \
  --restart unless-stopped \
  recolab-hybrid:v1.0
```

---

## 3. Health Checks & Monitoring
- **Endpoint**: `http://<host>:8501/_stcore/health`
- **Expected Status**: `200 OK`
- **Memory Consumption**: Expected ~150 MB (including Streamlit UI state and cached models).
