#!/bin/bash
# scripts/deploy_to_cloud_run.sh
# 🐙 Inktrace Cloud Run Deployment Script

set -e

# Configuration
PROJECT_ID="inktrace-463306"
REGION="us-central1"
SERVICE_NAME="inktrace-agents"
IMAGE_NAME="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "🐙 INKTRACE CLOUD RUN DEPLOYMENT"
echo "=================================="
echo "Project: ${PROJECT_ID}"
echo "Region: ${REGION}"
echo "Service: ${SERVICE_NAME}"
echo "Image: ${IMAGE_NAME}"
echo "=================================="

# Step 1: Authenticate with Google Cloud
echo "🔐 Authenticating with Google Cloud..."
gcloud auth application-default login --quiet || echo "⚠️ Already authenticated"

# Step 2: Set the project
echo "📋 Setting project to ${PROJECT_ID}..."
gcloud config set project ${PROJECT_ID}

# Step 3: Enable required APIs
echo "🔧 Enabling required Google Cloud APIs..."
gcloud services enable cloudbuild.googleapis.com --quiet
gcloud services enable run.googleapis.com --quiet
gcloud services enable bigquery.googleapis.com --quiet
gcloud services enable containerregistry.googleapis.com --quiet

# Step 4: Build the Docker image
echo "🏗️ Building Docker image..."
docker build -t ${IMAGE_NAME}:latest .

# Step 5: Push the image to Google Container Registry
echo "📤 Pushing image to Container Registry..."
docker push ${IMAGE_NAME}:latest

# Step 6: Deploy to Cloud Run
echo "🚀 Deploying to Cloud Run..."
gcloud run deploy ${SERVICE_NAME} \
  --image ${IMAGE_NAME}:latest \
  --platform managed \
  --region ${REGION} \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600 \
  --port 8080 \
  --set-env-vars="GOOGLE_CLOUD_PROJECT=${PROJECT_ID}" \
  --set-env-vars="BIGQUERY_DATASET=inktrace_policies" \
  --min-instances 1 \
  --max-instances 10 \
  --concurrency 100

# Step 7: Get the service URL
echo "🔗 Getting service URL..."
SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')

echo ""
echo "✅ DEPLOYMENT SUCCESSFUL!"
echo "========================="
echo "🌟 Inktrace Dashboard: ${SERVICE_URL}/dashboard"
echo "📊 API Endpoints: ${SERVICE_URL}/api/"
echo "🔍 Agent Discovery: ${SERVICE_URL}/.well-known/agent.json"
echo "📋 Policy Agent: ${SERVICE_URL}/policy-check"
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Set up BigQuery: python scripts/setup_bigquery.py"
echo "2. Test the dashboard: open ${SERVICE_URL}/dashboard"
echo "3. Run policy check: curl ${SERVICE_URL}/policy-check"
echo "4. View logs: gcloud run logs tail ${SERVICE_NAME} --region=${REGION}"
echo ""
echo "📚 DOCUMENTATION:"
echo "- Cloud Run Console: https://console.cloud.google.com/run"
echo "- BigQuery Console: https://console.cloud.google.com/bigquery"
echo "- Logs: https://console.cloud.google.com/logs"
echo ""