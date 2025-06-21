#!/bin/bash
# complete_deployment.sh
# 🐙 Complete the Inktrace VM deployment manually

set -e

PROJECT_ID="inktrace-463306"
ZONE="us-central1-a"
VM_NAME="inktrace-hackathon"

echo "🐙 COMPLETING INKTRACE DEPLOYMENT"
echo "================================="

# 1. Wait for VM to be fully ready for SSH
echo "⏳ Waiting for VM to be fully ready for SSH..."
sleep 30

# 2. Test SSH connectivity with retries
echo "🔍 Testing SSH connectivity..."
for i in {1..5}; do
    if gcloud compute ssh $VM_NAME --zone=$ZONE --command="echo 'SSH test successful'" 2>/dev/null; then
        echo "✅ SSH connection successful!"
        break
    else
        echo "   Attempt $i/5 failed, waiting 10 seconds..."
        sleep 10
    fi
done

# 3. Upload your project files
echo "📤 Uploading project files..."

# Create project archive
echo "   Creating project archive..."
tar --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='node_modules' \
    --exclude='.env' \
    -czf /tmp/inktrace-project.tar.gz .

# Upload the archive
echo "   Uploading to VM..."
gcloud compute scp /tmp/inktrace-project.tar.gz $VM_NAME:/tmp/ --zone=$ZONE

# 4. Setup and start the application
echo "🚀 Setting up and starting Inktrace..."
gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    # Extract project
    cd /opt/inktrace
    sudo tar -xzf /tmp/inktrace-project.tar.gz
    sudo chown -R \$USER:\$USER /opt/inktrace
    
    # Create templates if missing
    if [ ! -d templates ]; then
        echo '📁 Setting up templates...'
        mkdir -p templates static/css static/js
        # Create basic dashboard template
        cat > templates/dashboard.html << 'TEMPLATE_EOF'
<!DOCTYPE html>
<html>
<head>
    <title>🐙 Inktrace Dashboard</title>
    <style>
        body { font-family: sans-serif; text-align: center; padding: 20px; }
        .card { background: #f5f5f5; padding: 20px; margin: 10px; border-radius: 8px; }
    </style>
</head>
<body>
    <h1>🐙 Inktrace Security Intelligence</h1>
    <div class='card'>
        <h2>Multi-Agent System Active</h2>
        <p>Real-time security monitoring in progress...</p>
    </div>
</body>
</html>
TEMPLATE_EOF
    fi
    
    # Kill any existing processes
    pkill -f 'python.*launch' 2>/dev/null || true
    pkill -f 'python.*wiretap' 2>/dev/null || true
    
    # Start the system
    echo '🐙 Starting Inktrace multi-agent system...'
    cd /opt/inktrace
    nohup python3 scripts/launch.py > /tmp/inktrace.log 2>&1 &
    
    # Wait a bit and check status
    sleep 10
    echo '📋 System status:'
    ps aux | grep python3 | grep -v grep || echo 'No Python processes found'
    
    echo '📝 Latest log entries:'
    tail -10 /tmp/inktrace.log 2>/dev/null || echo 'No log file yet'
"

# 5. Get the public URL
echo "🌐 Getting public URL..."
EXTERNAL_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)")

# Clean up
rm -f /tmp/inktrace-project.tar.gz

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo "🌐 VM External IP: $EXTERNAL_IP"
echo ""
echo "📱 PUBLIC URLS FOR JUDGES:"
echo "   🎯 Main Dashboard: http://$EXTERNAL_IP:8003/dashboard"
echo "   🔍 Communications: http://$EXTERNAL_IP:8003/communications"
echo "   📊 Security Events: http://$EXTERNAL_IP:8003/security-events"
echo ""
echo "🔍 INDIVIDUAL AGENTS:"
echo "   📊 Data Processor: http://$EXTERNAL_IP:8001"
echo "   📈 Report Generator: http://$EXTERNAL_IP:8002" 
echo "   🛡️ Policy Agent: http://$EXTERNAL_IP:8006"
echo ""
echo "🔧 TROUBLESHOOTING:"
echo "   📋 Check logs: gcloud compute ssh $VM_NAME --zone=$ZONE --command='tail -f /tmp/inktrace.log'"
echo "   🔄 Restart: gcloud compute ssh $VM_NAME --zone=$ZONE --command='cd /opt/inktrace && pkill -f python && nohup python3 scripts/launch.py > /tmp/inktrace.log 2>&1 &'"
echo "   💻 SSH into VM: gcloud compute ssh $VM_NAME --zone=$ZONE"
echo ""
echo "🎯 GIVE JUDGES THIS URL: http://$EXTERNAL_IP:8003/dashboard"
echo "======================"

# 6. Test the deployment
echo "🧪 Testing deployment..."
sleep 5

if curl -s --connect-timeout 10 "http://$EXTERNAL_IP:8003" > /dev/null 2>&1; then
    echo "✅ Service is responding!"
else
    echo "⏳ Service may still be starting up..."
    echo "   Check logs with: gcloud compute ssh $VM_NAME --zone=$ZONE --command='tail -f /tmp/inktrace.log'"
fi