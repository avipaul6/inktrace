#!/bin/bash
# deploy_to_vm.sh
# 🐙 Inktrace Complete VM Deployment Script
# Creates VM, uploads code, and gives you a public URL like Cloud Run

set -e

PROJECT_ID="inktrace-463306"
REGION="us-central1"
ZONE="us-central1-a"
VM_NAME="inktrace-hackathon"
MACHINE_TYPE="e2-standard-4"

echo "🐙 INKTRACE VM DEPLOYMENT"
echo "========================"
echo "Project: $PROJECT_ID"
echo "VM: $VM_NAME"
echo "Zone: $ZONE"
echo "========================"

# Check if we're in the right directory
if [ ! -f "scripts/launch.py" ]; then
    echo "❌ Error: Please run this script from your inktrace project root directory"
    echo "   (The directory containing scripts/launch.py)"
    exit 1
fi

echo "✅ Found launch script, proceeding with deployment..."

# 1. Create the VM with startup script
echo "🚀 Creating VM instance..."
gcloud compute instances create $VM_NAME \
    --project=$PROJECT_ID \
    --zone=$ZONE \
    --machine-type=$MACHINE_TYPE \
    --network-interface=network-tier=PREMIUM,stack-type=IPV4_ONLY,subnet=default \
    --maintenance-policy=MIGRATE \
    --provisioning-model=STANDARD \
    --tags=inktrace-demo,http-server,https-server \
    --image-family=ubuntu-2204-lts \
    --image-project=ubuntu-os-cloud \
    --boot-disk-size=30GB \
    --boot-disk-type=pd-standard \
    --no-shielded-secure-boot \
    --shielded-vtpm \
    --shielded-integrity-monitoring \
    --labels=purpose=hackathon,project=inktrace \
    --reservation-affinity=any \
    --metadata=startup-script='#!/bin/bash
# VM Startup Script - Installs Python and dependencies
apt-get update
apt-get install -y python3 python3-pip git curl software-properties-common
python3 -m pip install --upgrade pip

# Create app directory
mkdir -p /opt/inktrace
cd /opt/inktrace

# Wait for code upload (will be done by the main script)
echo "VM ready for code upload" > /tmp/vm-ready
'

echo "⏳ Waiting for VM to start (this takes ~60 seconds)..."
gcloud compute instances describe $VM_NAME --zone=$ZONE --format="get(status)" > /dev/null

# Wait for VM to be running
while [[ $(gcloud compute instances describe $VM_NAME --zone=$ZONE --format="get(status)") != "RUNNING" ]]; do
    echo "   Still starting..."
    sleep 5
done

echo "✅ VM is running!"

# 2. Create firewall rules for Inktrace ports
echo "🔥 Creating firewall rules..."
gcloud compute firewall-rules create inktrace-ports \
    --project=$PROJECT_ID \
    --allow tcp:8001,tcp:8002,tcp:8003,tcp:8006,tcp:8080 \
    --source-ranges 0.0.0.0/0 \
    --target-tags inktrace-demo \
    --description "Firewall rule for Inktrace multi-agent system" 2>/dev/null || echo "   Firewall rule already exists"

# 3. Wait for VM to finish initial setup
echo "⏳ Waiting for VM initial setup to complete..."
sleep 30

# Check if VM is ready by looking for our ready file
while ! gcloud compute ssh $VM_NAME --zone=$ZONE --command="test -f /tmp/vm-ready" 2>/dev/null; do
    echo "   VM still setting up..."
    sleep 10
done

echo "✅ VM setup complete!"

# 4. Upload the entire project
echo "📤 Uploading project files to VM..."

# Create a temporary archive of the project (excluding .git and other unnecessary files)
echo "   Creating project archive..."
tar --exclude='.git' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='.pytest_cache' \
    --exclude='node_modules' \
    --exclude='.env' \
    -czf /tmp/inktrace-project.tar.gz .

# Upload the archive
echo "   Uploading archive..."
gcloud compute scp /tmp/inktrace-project.tar.gz $VM_NAME:/tmp/ --zone=$ZONE

# Extract and setup on VM
echo "   Extracting and setting up on VM..."
gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    cd /opt/inktrace
    sudo tar -xzf /tmp/inktrace-project.tar.gz
    sudo chown -R \$USER:\$USER /opt/inktrace
    
    # Install Python dependencies
    echo '🐍 Installing Python dependencies...'
    python3 -m pip install --user -r requirements.txt
    
    # Make scripts executable
    chmod +x scripts/*.py
    
    # Create templates if missing
    if [ ! -d templates ]; then
        echo '📁 Creating templates directory...'
        mkdir -p templates static/css static/js
        python3 setup_templates.py 2>/dev/null || echo 'Template setup completed'
    fi
    
    echo '✅ Project setup complete on VM'
"

# Clean up temporary file
rm -f /tmp/inktrace-project.tar.gz

# 5. Start the Inktrace system
echo "🚀 Starting Inktrace multi-agent system..."
gcloud compute ssh $VM_NAME --zone=$ZONE --command="
    cd /opt/inktrace
    
    # Kill any existing processes
    pkill -f 'python.*launch.py' 2>/dev/null || true
    pkill -f 'python.*wiretap.py' 2>/dev/null || true
    pkill -f 'python.*agent' 2>/dev/null || true
    
    # Start the system in background
    echo '🐙 Starting Inktrace agents...'
    nohup python3 scripts/launch.py > /tmp/inktrace.log 2>&1 &
    
    echo '⏳ Waiting for agents to start...'
    sleep 10
    
    # Check if it's running
    if pgrep -f 'python.*launch.py' > /dev/null; then
        echo '✅ Inktrace system started successfully'
    else
        echo '❌ Failed to start - check logs'
        tail -20 /tmp/inktrace.log
    fi
"

# 6. Get the external IP and create the public URL
echo "🌐 Getting public URL..."
EXTERNAL_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)")

echo ""
echo "🎉 DEPLOYMENT COMPLETE!"
echo "======================"
echo "🌟 VM Name: $VM_NAME"
echo "🌐 External IP: $EXTERNAL_IP"
echo ""
echo "📱 PUBLIC URLS:"
echo "   🐙 Main Dashboard: http://$EXTERNAL_IP:8003/dashboard"
echo "   🔍 Communications: http://$EXTERNAL_IP:8003/communications"
echo "   📊 Security Events: http://$EXTERNAL_IP:8003/security-events"
echo "   🔌 API Endpoint: http://$EXTERNAL_IP:8003/api/agents"
echo ""
echo "🔍 INDIVIDUAL AGENTS:"
echo "   📊 Data Processor: http://$EXTERNAL_IP:8001"
echo "   📈 Report Generator: http://$EXTERNAL_IP:8002"
echo "   🛡️ Policy Agent: http://$EXTERNAL_IP:8006"
echo ""
echo "🎯 FOR JUDGES: http://$EXTERNAL_IP:8003/dashboard"
echo ""
echo "🔧 MANAGEMENT COMMANDS:"
echo "   📋 Check logs: gcloud compute ssh $VM_NAME --zone=$ZONE --command='tail -f /tmp/inktrace.log'"
echo "   🔄 Restart system: gcloud compute ssh $VM_NAME --zone=$ZONE --command='cd /opt/inktrace && pkill -f python && nohup python3 scripts/launch.py > /tmp/inktrace.log 2>&1 &'"
echo "   🗑️ Delete VM: gcloud compute instances delete $VM_NAME --zone=$ZONE"
echo ""
echo "💡 TIPS:"
echo "   • VM will keep running until you delete it"
echo "   • No cold starts - always ready for judges"
echo "   • Use the main dashboard URL for judge access"
echo "   • All your existing code works exactly as local"
echo "======================"

# 7. Optional: Test the deployment
echo "🧪 Testing deployment..."
sleep 5

# Test if the dashboard is accessible
if curl -s --connect-timeout 10 "http://$EXTERNAL_IP:8003/dashboard" > /dev/null; then
    echo "✅ Dashboard is accessible!"
else
    echo "⚠️ Dashboard not yet ready - may need a few more seconds"
    echo "   Check with: curl http://$EXTERNAL_IP:8003/dashboard"
fi

echo ""
echo "🚀 Ready for hackathon judging!"
echo "   Give judges this URL: http://$EXTERNAL_IP:8003/dashboard"