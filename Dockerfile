# Use an explicit, lightweight official base image
FROM python:3.12-slim

# Set strict system environment optimization variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV HOME=/app

WORKDIR /app

# Install system utilities safely
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Generate application isolation dependencies directly inside the layer
RUN pip install --no-cache-dir --upgrade pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application layers into place
COPY data_pipeline/ ./data_pipeline/
COPY model_platform/ ./model_platform/

# Security Compliance: Create a non-root system user to drop root privileges
RUN useradd -u 8888 appuser && chown -R appuser:appuser /app
USER appuser

# Expose standard communication channel ports
EXPOSE 8000

# Execute the application server process layer safely
CMD ["uvicorn", "model_platform.app:app", "--host", "0.0.0.0", "--port", "8000"]
