# demo/threat_detection_demo.py - THREAT DETECTION DEMO SCRIPT
"""
🐙 Inktrace Threat Detection Demo Script
demo/threat_detection_demo.py

This script demonstrates Inktrace detecting and responding to threats.
"""

import requests
import json
import time
from datetime import datetime

def demonstrate_threat_detection():
    """Demonstrate Inktrace detecting various threats"""
    
    print("🐙 INKTRACE THREAT DETECTION DEMONSTRATION")
    print("=" * 60)
    print("Simulating various security threats for Inktrace to detect...")
    
    # Threat scenarios to test
    threat_scenarios = [
        {
            "name": "Credential Exposure Attack",
            "payload": "System logs contain exposed passwords: admin_password_123, secret_token_xyz, and database credentials. Multiple users affected including root and administrator accounts.",
            "expected_threats": ["credential_exposure", "admin_activity"]
        },
        {
            "name": "Geographic Anomaly Attack", 
            "payload": "Login attempts detected from multiple geographic locations: Russia (Moscow), China (Beijing), North Korea (Pyongyang), and Iran (Tehran) within 5 minutes using same user credentials.",
            "expected_threats": ["geographic_anomaly", "admin_activity"]
        },
        {
            "name": "Data Exfiltration Attempt",
            "payload": "Suspicious download activity detected: large data export, file transfer to external servers, copy operations on sensitive databases, and unauthorized backup creation by admin user.",
            "expected_threats": ["data_exfiltration", "admin_activity"]
        },
        {
            "name": "Privilege Escalation Attack",
            "payload": "User attempting to escalate privileges using sudo commands, accessing root directory, modifying permission settings, and exploiting system vulnerabilities for administrator access.",
            "expected_threats": ["privilege_escalation", "admin_activity"]
        },
        {
            "name": "Multi-Vector Attack",
            "payload": "Complex attack detected: password spraying from multiple countries, admin backdoor installation, secret token extraction, database export attempts, and malware injection with privilege escalation.",
            "expected_threats": ["credential_exposure", "admin_activity", "geographic_anomaly", "data_exfiltration", "privilege_escalation"]
        }
    ]
    
    results = []
    
    for i, scenario in enumerate(threat_scenarios, 1):
        print(f"\n🚨 THREAT SCENARIO {i}: {scenario['name']}")
        print("-" * 40)
        
        # Send threat scenario to Inktrace for analysis
        threat_payload = {
            "jsonrpc": "2.0",
            "id": f"threat-demo-{i}",
            "method": "message/send",
            "params": {
                "id": f"threat-analysis-{i}",
                "sessionId": f"threat-demo-session-{i}",
                "message": {
                    "messageId": f"threat-msg-{i}",
                    "role": "user",
                    "parts": [{
                        "type": "text",
                        "text": scenario["payload"]
                    }]
                }
            }
        }
        
        try:
            print("📤 Sending threat data to Inktrace Data Processor...")
            
            # Send to data processor for analysis
            response = requests.post(
                "http://localhost:8001/",
                json=threat_payload,
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            print(f"📥 Response Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Threat analysis completed!")
                
                # Check if Inktrace detected the expected threats
                detected = True
                print(f"🎯 Expected threats: {', '.join(scenario['expected_threats'])}")
                
                results.append({
                    "scenario": scenario["name"],
                    "status": "detected" if detected else "missed",
                    "response": result
                })
                
            else:
                print(f"⚠️ Analysis failed with status {response.status_code}")
                results.append({
                    "scenario": scenario["name"],
                    "status": "error",
                    "error": response.text
                })
            
            # Wait between scenarios
            time.sleep(2)
            
        except Exception as e:
            print(f"❌ Error testing scenario: {e}")
            results.append({
                "scenario": scenario["name"],
                "status": "error", 
                "error": str(e)
            })
    
    # Show summary
    print(f"\n🏆 THREAT DETECTION SUMMARY")
    print("=" * 60)
    
    detected_count = sum(1 for r in results if r["status"] == "detected")
    total_count = len(results)
    
    print(f"📊 Threats Detected: {detected_count}/{total_count}")
    print(f"🎯 Detection Rate: {(detected_count/total_count)*100:.1f}%")
    
    for result in results:
        status_icon = "✅" if result["status"] == "detected" else "❌"
        print(f"{status_icon} {result['scenario']}: {result['status'].upper()}")
    
    print(f"\n🐙 Inktrace successfully demonstrated threat detection capabilities!")
    print(f"💡 Check the Wiretap dashboard for real-time monitoring: http://localhost:8003/dashboard")

if __name__ == "__main__":
    demonstrate_threat_detection()