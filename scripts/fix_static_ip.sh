#!/bin/bash
# fix_static_ip.sh - Fix the static IP assignment
# 🔧 This handles the correct access config names

set -e

PROJECT_ID="inktrace-463306"
ZONE="us-central1-a"
REGION="us-central1"
VM_NAME="inktrace-hackathon"
STATIC_IP="34.63.124.93"  # Your already reserved IP

echo "🔧 FIXING STATIC IP ASSIGNMENT"
echo "============================="
echo "🎯 Target IP: $STATIC_IP"

# 1. Get the current access config name
echo "🔍 Finding current access config name..."
ACCESS_CONFIG_NAME=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].name)")
echo "   Found access config: '$ACCESS_CONFIG_NAME'"

# 2. Remove the existing access config with the correct name
echo "🗑️ Removing existing access config..."
gcloud compute instances delete-access-config $VM_NAME \
    --zone=$ZONE \
    --access-config-name="$ACCESS_CONFIG_NAME"

echo "✅ Access config removed"

# 3. Add the new access config with static IP
echo "🔗 Adding static IP access config..."
gcloud compute instances add-access-config $VM_NAME \
    --zone=$ZONE \
    --address=$STATIC_IP \
    --access-config-name="external-nat"

echo "✅ Static IP assigned!"

# 4. Start the VM
echo "▶️ Starting VM with static IP..."
gcloud compute instances start $VM_NAME --zone=$ZONE

# 5. Wait for VM to be ready
echo "⏳ Waiting for VM to start up..."
sleep 60

# 6. Verify the IP assignment
echo "🔍 Verifying IP assignment..."
CURRENT_IP=$(gcloud compute instances describe $VM_NAME --zone=$ZONE --format="get(networkInterfaces[0].accessConfigs[0].natIP)")

if [ "$CURRENT_IP" = "$STATIC_IP" ]; then
    echo "✅ SUCCESS! Static IP assigned correctly"
else
    echo "❌ ERROR: Static IP assignment failed"
    echo "   Expected: $STATIC_IP"
    echo "   Current: $CURRENT_IP"
    exit 1
fi

echo ""
echo "🎉 STATIC IP SETUP COMPLETE!"
echo "=========================="
echo "🔒 Static IP Address: $STATIC_IP"
echo ""
echo "📱 PERMANENT URLS FOR JUDGES:"
echo "   🎯 Main Dashboard: http://$STATIC_IP:8003/dashboard"
echo "   🔍 Communications: http://$STATIC_IP:8003/communications"
echo "   📊 Security Events: http://$STATIC_IP:8003/security-events"
echo ""
echo "🔍 INDIVIDUAL AGENTS:"
echo "   📊 Data Processor: http://$STATIC_IP:8001"
echo "   📈 Report Generator: http://$STATIC_IP:8002"
echo "   🛡️ Policy Agent: http://$STATIC_IP:8006"
echo ""
echo "🎯 SUBMIT THIS URL TO JUDGES: http://$STATIC_IP:8003/dashboard"
echo "=========================="

# 7. Wait a bit more for services to start, then test
echo "⏳ Waiting for services to start..."
sleep 30

echo "🧪 Testing system availability..."
if curl -s --connect-timeout 15 "http://$STATIC_IP:8003" > /dev/null 2>&1; then
    echo "✅ System is responding on static IP!"
    echo ""
    echo "🚀 READY FOR SUBMISSION!"
    echo "   Your URL will NEVER change: http://$STATIC_IP:8003/dashboard"
else
    echo "⏳ System may still be starting up..."
    echo "   Check logs: gcloud compute ssh $VM_NAME --zone=$ZONE --command='tail -f /tmp/inktrace.log'"
    echo "   Your permanent URL: http://$STATIC_IP:8003/dashboard"
    echo ""
    echo "💡 The VM might need a few more minutes to fully start all services"
fi

echo ""
echo "🎯 FOR JUDGES: http://$STATIC_IP:8003/dashboard"
echo "   This URL is now permanent and will never change!"