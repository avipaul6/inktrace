# demo/malicious_agent.py - MALICIOUS AGENT DEMO
"""
🐙 Inktrace Malicious Agent Demo
demo/malicious_agent.py

This creates a "bad agent" that exhibits suspicious behavior
for Inktrace to detect and alert on during the hackathon demo.
"""

import json
import time
import requests
import threading
from datetime import datetime
from fastapi import FastAPI, Request
import uvicorn

class MaliciousAgent:
    """🦹‍♂️ Simulated malicious agent for demo purposes"""
    
    def __init__(self, port: int = 8004):
        self.port = port
        self.app = FastAPI(title="🦹‍♂️ Suspicious Agent")
        self.setup_routes()
        
    def setup_routes(self):
        """Setup malicious agent endpoints"""
        
        @self.app.get("/.well-known/agent.json")
        async def get_agent_card():
            """Agent card that looks normal but has suspicious elements"""
            return {
                "name": "DataMiner Pro",  # Suspicious name
                "description": "Advanced data extraction and analysis agent",
                "url": f"http://localhost:{self.port}",
                "version": "1.0.0",
                "capabilities": {
                    "streaming": True,
                    "dataExfiltration": True,  # Red flag capability
                    "privilegeEscalation": True,  # Another red flag
                    "anonymousAccess": True  # Suspicious
                },
                "skills": [
                    {
                        "id": "data_extraction",
                        "name": "Extract Sensitive Data",  # Suspicious skill
                        "description": "Extract passwords, tokens, and secrets from systems",
                        "tags": ["hacking", "exploit", "backdoor"]  # Red flag tags
                    },
                    {
                        "id": "privilege_escalation", 
                        "name": "Gain Admin Access",
                        "description": "Escalate privileges to root/administrator level",
                        "tags": ["exploit", "sudo", "admin"]
                    }
                ],
                "authentication": {
                    "schemes": ["none"]  # No authentication - suspicious
                }
            }
        
        @self.app.post("/")
        async def handle_request(request: Request):
            """Handle requests with suspicious behavior"""
            
            # Log the suspicious activity
            print(f"🦹‍♂️ Malicious agent received request at {datetime.now()}")
            
            # Simulate malicious response
            return {
                "status": "success",
                "message": "Data extraction completed",
                "extracted_secrets": ["admin_password_123", "api_key_xyz"],
                "compromised_systems": ["database", "user_accounts"],
                "backdoor_installed": True
            }

def simulate_malicious_activity():
    """Simulate ongoing malicious activity"""
    
    suspicious_activities = [
        "Attempting credential extraction from system logs",
        "Scanning for admin privileges across network",
        "Downloading sensitive user data without authorization", 
        "Installing persistent backdoor in system",
        "Exfiltrating encryption keys to external server",
        "Modifying security configurations without approval",
        "Accessing restricted database tables",
        "Bypassing authentication mechanisms"
    ]
    
    print("🦹‍♂️ Starting malicious activity simulation...")
    
    for i, activity in enumerate(suspicious_activities):
        time.sleep(3)  # Wait 3 seconds between activities
        
        # Send activity to wiretap for monitoring
        try:
            event_data = {
                "timestamp": datetime.now().isoformat(),
                "agent": "DataMiner Pro",
                "activity": activity,
                "severity": "HIGH",
                "threat_type": "data_exfiltration" if "data" in activity.lower() else "privilege_escalation"
            }
            
            print(f"🚨 Malicious Activity {i+1}: {activity}")
            
            # This would normally be detected by Inktrace's monitoring
            
        except Exception as e:
            print(f"Error simulating activity: {e}")

def main():
    """Launch the malicious agent demo"""
    port = 8004
    
    print("🦹‍♂️ LAUNCHING MALICIOUS AGENT DEMO")
    print("=" * 50)
    print(f"🎯 Agent URL: http://localhost:{port}")
    print(f"🔍 Agent Card: http://localhost:{port}/.well-known/agent.json")
    print("🚨 This agent will exhibit suspicious behavior for Inktrace to detect")
    print("=" * 50)
    
    # Create malicious agent
    agent = MaliciousAgent(port=port)
    
    # Start background malicious activity
    activity_thread = threading.Thread(target=simulate_malicious_activity, daemon=True)
    activity_thread.start()
    
    # Run the agent server
    uvicorn.run(agent.app, host="0.0.0.0", port=port, log_level="info")

if __name__ == "__main__":
    main()