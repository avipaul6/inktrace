#!/bin/bash
# scripts/test_docker_local.sh  
# 🐙 Test Inktrace Docker Container Locally - SIMPLE VERSION

set -e

echo "🐙 INKTRACE LOCAL DOCKER TEST"
echo "============================="

# Build and run - same command for local and cloud
echo "🏗️ Building Docker image..."
docker build -t inktrace-local:latest .

echo "🚀 Starting Inktrace container..."
docker run -p 8080:8080 \
  -e PORT=8080 \
  -e GOOGLE_CLOUD_PROJECT=inktrace-463306 \
  -e BIGQUERY_DATASET=inktrace_policies \
  --name inktrace-test \
  --rm \
  inktrace-local:latest

echo "✅ Container running:"
echo "🎮 Dashboard: http://localhost:8080/dashboard"
echo "📊 API: http://localhost:8080/api/agents"

# To stop: docker stop inktrace-test