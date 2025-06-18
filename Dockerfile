# Dockerfile - FIXED VERSION (Skip package build)
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies and UV
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Copy the entire application first
COPY . .

# Create necessary directories and files
RUN mkdir -p templates static/css static/js static/images \
    && chmod +x scripts/*.py 2>/dev/null || true \
    && touch README.md pyproject.toml

# Install dependencies directly (skip package build)
RUN uv add a2a-sdk google-cloud-bigquery google-auth uvicorn fastapi starlette jinja2 httpx aiofiles websockets pandas numpy python-dateutil cryptography pyjwt

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080
ENV GOOGLE_CLOUD_PROJECT=inktrace-463306
ENV BIGQUERY_DATASET=inktrace_policies

# Add health check endpoint script
RUN echo '#!/usr/bin/env python3\nimport requests\nimport sys\ntry:\n    r = requests.get("http://localhost:8080/dashboard", timeout=5)\n    sys.exit(0 if r.status_code == 200 else 1)\nexcept:\n    sys.exit(1)' > /app/health_check.py && chmod +x /app/health_check.py

# Expose the port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD python /app/health_check.py || exit 1

# Activate virtual environment and run (no UV needed)
CMD ["/app/.venv/bin/python", "scripts/launch.py"]