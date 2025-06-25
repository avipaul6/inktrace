#!/bin/bash
# setup_static_ip.sh - Reserve a static IP for hackathon submission
# 🔒 This ensures your IP never changes

set -e

PROJECT_ID="inktrace-463306"
ZONE="us-central1-a"
REGION="us-central1"
VM_NAME="inktrace-hackathon"
STATIC_IP_NAME="inktrace-static-ip"

echo "🔒 SETTING UP STATIC IP FOR HACKATHON"
echo "===================================="

# 1. Reserve a static external IP address
echo "📍 Reserving static IP address..."
gcloud compute addresses create $STATIC_IP_NAME \
    --project=$PROJECT_ID \
    --region=$REGION \
    --network-tier=PREMIUM

# 2. Get the reserved IP
STATIC_IP=$(gcloud compute addresses describe $STATIC_IP_NAME --region=$REGION --format="get(address)")
echo "✅ Reserved static IP: $STATIC_IP"

# 3. Stop the VM (this will release the current ephemeral IP)
echo "⏸️ Stopping VM to change IP..."
gcloud compute instances stop $VM_NAME --zone=$ZONE
echo "   Waiting for VM to stop..."
sleep 30

# 4. Assign the static IP to the VM
echo "🔗 Assigning static IP to VM..."
gcloud compute instances delete-access-config $VM_NAME \
    --zone=$ZONE \
    --access-config-name="External NAT" || echo "   No existing access config to remove"

gcloud compute instances add-access-config $VM_NAME \
    --zone=$ZONE \
    --address=$STATIC_IP \
    --access-config-name="External NAT"

# 5. Start the VM with the new static IP
echo "▶️ Starting VM with static IP..."
gcloud compute instances start $VM_NAME --zone=$ZONE

# 6. Wait for VM to be ready
echo "⏳ Waiting for VM to be ready..."
sleep 45

# 7. Verify the IP assignment
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
echo ""
echo "💰 COST: ~$1.46/month for the static IP (delete after hackathon)"
echo "🗑️ DELETE LATER: gcloud compute addresses delete $STATIC_IP_NAME --region=$REGION"
echo "=========================="

# 8. Test the system is running
echo "🧪 Testing system availability..."
sleep 10

if curl -s --connect-timeout 10 "http://$STATIC_IP:8003" > /dev/null 2>&1; then
    echo "✅ System is responding on static IP!"
    echo ""
    echo "🚀 READY FOR SUBMISSION!"
    echo "   Your URL will NEVER change: http://$STATIC_IP:8003/dashboard"
else
    echo "⏳ System may still be starting up..."
    echo "   Test manually: curl http://$STATIC_IP:8003"
    echo "   Your system should be available at: http://$STATIC_IP:8003/dashboard"
fi