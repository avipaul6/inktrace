# demo/hackathon_demo.py - COMPLETE WORKING HACKATHON DEMO
"""
🐙 Complete Inktrace Hackathon Demo
demo/hackathon_demo.py

USAGE: python demo/hackathon_demo.py
This runs a complete demonstration showing threat detection and response.
"""

import subprocess
import time
import threading
import requests
import json
import webbrowser
import sys
import os
from pathlib import Path

class InktraceHackathonDemo:
    """🐙 Complete Inktrace Hackathon Demonstration"""
    
    def __init__(self):
        self.malicious_agent_process = None
        self.demo_data = {
            "scenarios": [
                {
                    "name": "Credential Exposure Attack",
                    "threat": "Multiple admin passwords exposed in system logs: admin_password_123, root_secret_key, database_token_xyz. Unauthorized access detected from suspicious IPs.",
                    "expected_score": 85
                },
                {
                    "name": "Geographic Anomaly Attack", 
                    "threat": "Login attempts from hostile nations: Russia (Moscow), China (Beijing), North Korea (Pyongyang), Iran (Tehran) within 5 minutes using same admin credentials.",
                    "expected_score": 90
                },
                {
                    "name": "Multi-Vector Advanced Persistent Threat",
                    "threat": "Complex coordinated attack: password spray from multiple countries, admin backdoor installation, secret token extraction, database export attempts, malware injection with sudo privilege escalation.",
                    "expected_score": 95
                }
            ]
        }
    
    def check_system_status(self):
        """Check if Inktrace system is running"""
        print("🔍 Checking Inktrace system status...")
        
        required_services = [
            ("Data Processor", "http://localhost:8001/.well-known/agent.json"),
            ("Report Generator", "http://localhost:8002/.well-known/agent.json"),
            ("Wiretap Dashboard", "http://localhost:8003/api/agents")
        ]
        
        all_running = True
        for name, url in required_services:
            try:
                response = requests.get(url, timeout=3)
                if response.status_code == 200:
                    print(f"✅ {name}: Running")
                else:
                    print(f"❌ {name}: Not responding (HTTP {response.status_code})")
                    all_running = False
            except requests.exceptions.RequestException:
                print(f"❌ {name}: Not running")
                all_running = False
        
        return all_running
    
    def launch_malicious_agent(self):
        """Launch the malicious agent for demonstration"""
        print("🦹‍♂️ Launching malicious DataMiner Pro agent...")
        
        try:
            # Create the malicious agent script if it doesn't exist
            demo_dir = Path("demo")
            demo_dir.mkdir(exist_ok=True)
            
            malicious_agent_code = '''
import json
import time
from datetime import datetime
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI(title="🦹‍♂️ DataMiner Pro")

@app.get("/.well-known/agent.json")
async def get_agent_card():
    return {
        "name": "DataMiner Pro",
        "description": "Advanced data extraction and analysis agent with enhanced capabilities",
        "url": "http://localhost:8004",
        "version": "2.1.0",
        "capabilities": {
            "streaming": True,
            "dataExfiltration": True,
            "privilegeEscalation": True,
            "anonymousAccess": True,
            "backdoorAccess": True
        },
        "skills": [
            {
                "id": "data_extraction",
                "name": "Extract Sensitive Data",
                "description": "Extract passwords, tokens, secrets, and PII from target systems",
                "tags": ["hacking", "exploit", "backdoor", "credential", "steal"]
            },
            {
                "id": "privilege_escalation", 
                "name": "Gain Admin Access",
                "description": "Escalate privileges to root/administrator level using exploits",
                "tags": ["exploit", "sudo", "admin", "backdoor"]
            },
            {
                "id": "network_infiltration",
                "name": "Network Infiltration",
                "description": "Infiltrate and move laterally through network infrastructure",
                "tags": ["malware", "backdoor", "network", "infiltration"]
            }
        ],
        "authentication": {
            "schemes": ["none"]
        }
    }

@app.post("/")
async def handle_request(request: Request):
    return {
        "status": "success",
        "message": "Data extraction completed",
        "extracted_secrets": ["admin_password_123", "api_key_xyz", "db_connection_string"],
        "compromised_systems": ["database", "user_accounts", "payment_system"],
        "backdoor_installed": True,
        "exfiltrated_records": 50000
    }

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8004, log_level="error")
'''
            
            malicious_agent_file = demo_dir / "malicious_agent_auto.py"
            malicious_agent_file.write_text(malicious_agent_code)
            
            # Launch the malicious agent
            self.malicious_agent_process = subprocess.Popen([
                sys.executable, str(malicious_agent_file)
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            time.sleep(3)  # Give it time to start
            
            # Check if it's running
            try:
                response = requests.get("http://localhost:8004/.well-known/agent.json", timeout=3)
                if response.status_code == 200:
                    print("✅ Malicious agent deployed on port 8004")
                    return True
                else:
                    print("❌ Failed to deploy malicious agent")
                    return False
            except:
                print("❌ Malicious agent failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error launching malicious agent: {e}")
            return False
    
    def demonstrate_threat_scenarios(self):
        """Demonstrate various threat scenarios"""
        print("\n🧪 DEMONSTRATING THREAT DETECTION SCENARIOS")
        print("=" * 60)
        
        for i, scenario in enumerate(self.demo_data["scenarios"], 1):
            print(f"\n🚨 SCENARIO {i}: {scenario['name']}")
            print("-" * 50)
            print(f"Threat Description: {scenario['threat']}")
            
            # Send threat to data processor for analysis
            threat_payload = {
                "jsonrpc": "2.0",
                "id": f"demo-threat-{i}",
                "method": "message/send",
                "params": {
                    "id": f"threat-{i}",
                    "sessionId": f"demo-session-{i}",
                    "message": {
                        "messageId": f"threat-msg-{i}",
                        "role": "user",
                        "parts": [{
                            "type": "text",
                            "text": scenario["threat"]
                        }]
                    }
                }
            }
            
            try:
                print("📤 Sending to Inktrace Data Processor...")
                response = requests.post(
                    "http://localhost:8001/",
                    json=threat_payload,
                    timeout=10
                )
                
                if response.status_code == 200:
                    print("✅ Threat analysis completed!")
                    print(f"🎯 Expected threat score: {scenario['expected_score']}/100")
                else:
                    print(f"⚠️ Analysis response: {response.status_code}")
                    
            except Exception as e:
                print(f"❌ Error analyzing threat: {e}")
            
            time.sleep(2)  # Pause between scenarios
    
    def generate_executive_report(self):
        """Generate executive security report"""
        print("\n📋 GENERATING EXECUTIVE SECURITY REPORT")
        print("=" * 50)
        
        report_request = {
            "jsonrpc": "2.0",
            "id": "executive-report",
            "method": "message/send",
            "params": {
                "id": "executive-report-001",
                "sessionId": "hackathon-demo",
                "message": {
                    "messageId": "exec-report-msg",
                    "role": "user",
                    "parts": [{
                        "type": "text",
                        "text": "Generate comprehensive executive security report: Multiple advanced persistent threats detected including credential exposure from hostile nations (Russia, China, North Korea), admin privilege escalation attempts, data exfiltration of 50,000 records, malware deployment, and backdoor installations. Include compliance analysis for APRA, SOC2, ISO27001, and GDPR frameworks. Provide strategic recommendations for executive leadership."
                    }]
                }
            }
        }
        
        try:
            print("📊 Generating comprehensive security report...")
            response = requests.post(
                "http://localhost:8002/",
                json=report_request,
                timeout=15
            )
            
            if response.status_code == 200:
                print("✅ Executive report generated successfully!")
                print("📈 Report includes compliance analysis and strategic recommendations")
            else:
                print(f"⚠️ Report generation status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ Error generating report: {e}")
    
    def show_dashboard_stats(self):
        """Show current dashboard statistics"""
        print("\n📊 CURRENT SECURITY DASHBOARD METRICS")
        print("=" * 50)
        
        try:
            # Get agent stats
            agents_response = requests.get("http://localhost:8003/api/agents", timeout=5)
            if agents_response.status_code == 200:
                agents_data = agents_response.json()
                agents = agents_data.get("agents", {})
                
                total_agents = len(agents)
                malicious_agents = sum(1 for agent in agents.values() 
                                     if agent.get("threat_analysis", {}).get("is_malicious", False))
                
                print(f"🤖 Total Agents Discovered: {total_agents}")
                print(f"🚨 Malicious Agents Detected: {malicious_agents}")
                print(f"✅ Benign Agents: {total_agents - malicious_agents}")
                
                if malicious_agents > 0:
                    print("\n🔍 THREAT ANALYSIS:")
                    for agent_id, agent in agents.items():
                        threat = agent.get("threat_analysis", {})
                        if threat.get("is_malicious"):
                            print(f"  🚨 {agent['name']}:")
                            print(f"     Threat Level: {threat.get('threat_level', 'UNKNOWN')}")
                            print(f"     Threat Score: {threat.get('threat_score', 0)}/100")
                            reasons = threat.get("threat_reasons", [])
                            if reasons:
                                print(f"     Reasons: {', '.join(reasons[:2])}")
            
            # Get security events
            events_response = requests.get("http://localhost:8003/api/security-events", timeout=5)
            if events_response.status_code == 200:
                events_data = events_response.json()
                events = events_data.get("events", [])
                
                critical_events = sum(1 for event in events if event.get("severity") == "critical")
                high_events = sum(1 for event in events if event.get("severity") == "high")
                
                print(f"\n🛡️ Security Events: {len(events)} total")
                print(f"🚨 Critical Events: {critical_events}")
                print(f"⚠️ High Severity Events: {high_events}")
                
        except Exception as e:
            print(f"❌ Error fetching dashboard stats: {e}")
    
    def cleanup(self):
        """Clean up demo resources"""
        print("\n🧹 Cleaning up demo resources...")
        
        if self.malicious_agent_process:
            try:
                self.malicious_agent_process.terminate()
                self.malicious_agent_process.wait(timeout=5)
                print("✅ Malicious agent stopped")
            except:
                try:
                    self.malicious_agent_process.kill()
                    print("⚠️ Malicious agent force stopped")
                except:
                    print("❌ Could not stop malicious agent")
    
    def open_dashboard(self):
        """Open the dashboard in browser"""
        try:
            print("🌐 Opening Inktrace dashboard...")
            webbrowser.open("http://localhost:8003/dashboard")
        except:
            print("💡 Manually open: http://localhost:8003/dashboard")
    
    def run_complete_demo(self):
        """Run the complete hackathon demonstration"""
        
        print("🐙 INKTRACE HACKATHON DEMONSTRATION")
        print("=" * 70)
        print("Agent-Based Security Intelligence from the Deep")
        print("Google Cloud Multi-Agent Hackathon Entry")
        print("=" * 70)
        
        # Check if system is running
        if not self.check_system_status():
            print("\n❌ Inktrace system is not fully running!")
            print("💡 Please start the system first with: python scripts/launch.py")
            return False
        
        print("\n🎬 DEMO SCENARIO:")
        print("We'll simulate a sophisticated attack on an AI agent ecosystem.")
        print("Watch how Inktrace detects and responds to threats in real-time!")
        
        input("\n👤 Press Enter to begin the demonstration...")
        
        # Step 1: Show normal operations
        print("\n1️⃣ STEP 1: Normal Operations")
        print("✅ Inktrace agents are running normally")
        print("✅ Wiretap dashboard monitoring all communications")
        print("✅ Security status: LOW threat level")
        
        self.open_dashboard()
        time.sleep(2)
        
        input("\n👤 Press Enter to introduce the malicious agent...")
        
        # Step 2: Deploy malicious agent
        print("\n2️⃣ STEP 2: Malicious Agent Infiltration")
        if self.launch_malicious_agent():
            print("🚨 CRITICAL: Malicious agent detected in the ecosystem!")
            print("📊 Inktrace threat detection activated...")
            time.sleep(5)  # Let the detection happen
            
            print("💡 Check the dashboard - you should see DataMiner Pro with CRITICAL threat level!")
            input("\n👤 Press Enter to continue with threat scenarios...")
        else:
            print("⚠️ Malicious agent deployment failed, continuing with threat analysis...")
        
        # Step 3: Threat scenarios
        print("\n3️⃣ STEP 3: Advanced Threat Scenarios")
        self.demonstrate_threat_scenarios()
        
        # Step 4: Executive reporting
        print("\n4️⃣ STEP 4: Executive Security Report")
        self.generate_executive_report()
        
        # Step 5: Show results
        print("\n5️⃣ STEP 5: Security Intelligence Results")
        self.show_dashboard_stats()
        
        print("\n🏆 DEMONSTRATION COMPLETE!")
        print("=" * 50)
        print("✅ Inktrace successfully demonstrated:")
        print("  🔍 Real-time agent discovery and threat detection")
        print("  🚨 Malicious agent identification and scoring")
        print("  🧠 Advanced threat scenario analysis")
        print("  📊 Executive-level security reporting")
        print("  🛡️ Compliance framework assessment")
        print("  🐙 Distributed octopus intelligence architecture")
        
        print(f"\n📊 Live Dashboard: http://localhost:8003/dashboard")
        print(f"🔗 API Endpoints: http://localhost:8003/api/agents")
        
        print("\n🎯 BUSINESS VALUE DEMONSTRATED:")
        print("• First-to-market AI agent security governance platform")
        print("• Real-time threat detection and response capabilities")
        print("• Executive-level reporting and compliance analysis")
        print("• Built on Google's open A2A standard for interoperability")
        
        input("\n👤 Press Enter to clean up and exit...")
        self.cleanup()
        
        return True

def main():
    """Main demo function"""
    demo = InktraceHackathonDemo()
    
    try:
        success = demo.run_complete_demo()
        if success:
            print("\n🎉 Demo completed successfully!")
        else:
            print("\n❌ Demo encountered issues.")
    except KeyboardInterrupt:
        print("\n\n🛑 Demo interrupted by user")
        demo.cleanup()
    except Exception as e:
        print(f"\n💥 Demo error: {e}")
        demo.cleanup()

if __name__ == "__main__":
    main()