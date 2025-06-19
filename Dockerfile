# Dockerfile - CLOUD RUN READY VERSION
FROM --platform=linux/amd64 python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copy dependency files first for better Docker layer caching
COPY requirements.txt pyproject.toml ./

# Create README.md if it doesn't exist (required by some packages)
RUN touch README.md

# Install Python dependencies directly with pip (more reliable than UV in containers)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy the entire application
COPY . .

# Ensure template directories and files are properly copied
# (The COPY . . should have included them, but let's be explicit)
COPY templates/ ./templates/
COPY static/ ./static/

# Set permissions for scripts
RUN find scripts/ -name "*.py" -exec chmod +x {} \; 2>/dev/null || true

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080
ENV GOOGLE_CLOUD_PROJECT=inktrace-463306
ENV BIGQUERY_DATASET=inktrace_policies

# Cloud Run health check script (updated for port 8080)
RUN echo '#!/usr/bin/env python3\nimport requests\nimport sys\ntry:\n    r = requests.get("http://localhost:8080/dashboard", timeout=5)\n    sys.exit(0 if r.status_code == 200 else 1)\nexcept:\n    sys.exit(1)' > /app/health_check.py && chmod +x /app/health_check.py

# Expose the port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python /app/health_check.py || exit 1

# For Cloud Run, we run the complete system using your existing launch script
# This starts all agents (Data Processor, Report Generator, Policy Agent) + Wiretap Tentacle
# But we'll modify the wiretap to run on port 8080 via environment variable
# In Dockerfile, change the CMD to:
CMD ["python", "scripts/launch.py"]