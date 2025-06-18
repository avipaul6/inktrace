# Dockerfile
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies and UV
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && pip install uv

# Copy UV project files for better caching
COPY pyproject.toml uv.lock* ./

# Install dependencies with UV
RUN uv sync --frozen

# Copy the entire application
COPY . .

# Create necessary directories
RUN mkdir -p templates static/css static/js static/images

# Set environment variables
ENV PYTHONPATH=/app
ENV PORT=8080
ENV GOOGLE_CLOUD_PROJECT=inktrace-463306

# Expose the port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Use the existing launch script (modified for Cloud Run environment)
CMD ["uv", "run", "python", "scripts/launch.py"]