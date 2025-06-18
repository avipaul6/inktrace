#!/bin/bash
# scripts/test_docker_local.sh
# 🐙 Test Inktrace Docker Container Locally

set -e

echo "🐙 INKTRACE LOCAL DOCKER TEST"
echo "============================="

# Step 1: Build the Docker image
echo "🏗️ Building Docker image..."
docker build -t inktrace-local:latest .

# Step 2: Run the container locally
echo "🚀 Starting Inktrace container..."
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e GOOGLE_CLOUD_PROJECT=inktrace-463306 \
  -e BIGQUERY_DATASET=inktrace_policies \
  --name inktrace-test \
  --rm \
  inktrace-local:latest

echo "✅ Container running on http://localhost:8080"
echo "🎮 Dashboard: http://localhost:8080/dashboard"
echo "📊 API: http://localhost:8080/api/agents"

# To stop: docker stop inktrace-test