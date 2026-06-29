# Secure Local AI Platform & Data Pipeline

A production-grade, containerized local inference serving layer and data ingestion pipeline engineered for secure financial compliance processing. This platform implements strict runtime data validation, automated PII masking, local Small Language Model (SLM) optimization configurations, and full CI/CD test automation.

## System Architecture

* **Ingestion & Validation Layer (`data_pipeline/`):** Enforces data contracts using `Pydantic v2.13.4` , masks sensitive financial accounts dynamically before persistence, and batch-inserts records into an indexed SQLite database layer.
* **Model Platform Layer (`model_platform/`):** Handles runtime hardware acceleration detection (CPU/CUDA/MPS) and quantization mapping configurations. Exposes inference execution and system health endpoints via an asynchronous FastAPI application.
* **Automation & DevOps Layer:** Enforces zero-trust isolation boundaries inside a multi-stage Dockerfile running under a non-root system user, integrated into an automated GitHub Actions testing and compilation workflow.

---

## Prerequisites

Ensure your host machine has the following foundational dependencies installed:
* **Python 3.12+**
* **Docker / Podman**
* **Git**

---

## Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/grunundweiss/secure-ai-platform.git](https://github.com/grunundweiss/secure-ai-platform.git)
   cd secure-ai-platform

2. **Establish Isolated Virtual Environment:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install Package Dependencies:**
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

 ---

## Running the Platform

### 1. Execute Data Pipeline Ingestion
To run a local integration check of the validation engine, schema structures, and data masking pipeline:
```bash
python data_pipeline/ingest.py
```

### 2. Launch the Local AI API Server
To initiate the asynchronous HTTP API server locally using Uvicorn:
```bash
python model_platform/app.py
```
The server will bind to `http://127.0.0.1:8000`. You can inspect the interactive OpenAPI/Swagger documentation at `http://127.0.0.1:8000/docs`.

### 3. Verify System Health Endpoint
Open a separate terminal window and ping the platform's SRE health probe:
```bash
curl [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
```

---

## Verification & Testing

The repository maintains an automated unit and integration test suite using an isolated, temporary database lifecycle layout to guarantee code integrity.

To execute the test validation matrix locally, ensure your virtual environment is active and run:
```bash
pytest -v
```

---

## Containerization & Deployment

To verify the secure multi-stage container build and execute the application within an isolated infrastructure boundary:

1. **Build the Secure Docker Image:**
   ```bash
   docker build -t secure-ai-platform:latest .
   ```

2. **Run the Containerized Platform Instance:**
   ```bash
   docker run -p 8000:8000 secure-ai-platform:latest
   ```
