#!/bin/bash
# scripts/deploy_startup_probe_only.sh
# 🚀 CLEAN Deploy with ONLY Startup + Liveness Probes

set -e

PROJECT_ID="inktrace-463306"
REGION="us-central1"
SERVICE_NAME="inktrace-agents"
IMAGE_NAME="us-central1-docker.pkg.dev/${PROJECT_ID}/inktrace-agents/inktrace-multiagent"

echo "🚀 CLEAN DEPLOY - STARTUP PROBE ONLY"
echo "===================================="

# Build and push
gcloud auth configure-docker us-central1-docker.pkg.dev --quiet
docker build -t ${IMAGE_NAME}:latest .
docker push ${IMAGE_NAME}:latest

# Clean YAML - NO READINESS PROBE
cat > /tmp/clean-service.yaml << 'EOF'
apiVersion: serving.knative.dev/v1
kind: Service
metadata:
  name: inktrace-agents
  annotations:
    run.googleapis.com/execution-environment: gen2
    run.googleapis.com/cpu-boost: "true"
spec:
  template:
    metadata:
      annotations:
        run.googleapis.com/memory: "4Gi"
        run.googleapis.com/cpu: "4"
        run.googleapis.com/timeout: "1200s"
        autoscaling.knative.dev/minScale: "3"
        autoscaling.knative.dev/maxScale: "8"
        run.googleapis.com/cpu-throttling: "false"
    spec:
      timeoutSeconds: 1200
      containerConcurrency: 25
      containers:
        - name: inktrace-multiagent
          image: us-central1-docker.pkg.dev/inktrace-463306/inktrace-agents/inktrace-multiagent:latest
          ports:
            - name: http1
              containerPort: 8080
          env:
            - name: GOOGLE_CLOUD_PROJECT
              value: "inktrace-463306"
            - name: BIGQUERY_DATASET
              value: "inktrace_policies"
          resources:
            limits:
              memory: "4Gi"
              cpu: "4"
          startupProbe:
            httpGet:
              path: /healthz
              port: 8080
            initialDelaySeconds: 30
            periodSeconds: 10
            timeoutSeconds: 5
            failureThreshold: 30
            successThreshold: 1
          livenessProbe:
            httpGet:
              path: /healthz
              port: 8080
            periodSeconds: 60
            timeoutSeconds: 10
            failureThreshold: 3
EOF

echo "🔍 Checking generated YAML..."
grep -n "readinessProbe" /tmp/clean-service.yaml || echo "✅ No readiness probe found"

echo "🚀 Deploying clean configuration..."
gcloud run services replace /tmp/clean-service.yaml --region=${REGION}

echo "🔐 Setting public access..."
gcloud run services add-iam-policy-binding ${SERVICE_NAME} \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region=${REGION}

SERVICE_URL=$(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')

echo ""
echo "✅ CLEAN DEPLOYMENT COMPLETE!"
echo "============================="
echo "🌟 Dashboard: ${SERVICE_URL}/dashboard"
echo "🔍 Health: ${SERVICE_URL}/healthz"
echo ""
echo "🚀 STARTUP PROBE: 5 minutes for multi-agent startup"
echo "❤️ LIVENESS PROBE: Ongoing health monitoring"
echo "🚫 NO READINESS PROBE: Skipped completely"

rm -f /tmp/clean-service.yaml