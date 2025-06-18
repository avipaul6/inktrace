#!/usr/bin/env python3
"""
🐙 Policy Violation Demo Agent
demo/policy_violation_demo.py

Creates a demo agent that intentionally violates multiple security policies
to demonstrate Inktrace's policy enforcement capabilities.
"""

import asyncio
import httpx
import json
import time
import uuid
import argparse
from datetime import datetime
from typing import Dict, List

class PolicyViolationDemo:
    """Demo agent that violates security policies"""
    
    def __init__(self):
        self.violations_created = []
        
    async def trigger_gdpr_violation(self):
        """Simulate GDPR data retention violation"""
        violation = {
            "type": "gdpr_violation",
            "description": "Personal data retained beyond 24-month GDPR limit",
            "severity": "critical",
            "policy_violated": "POL-T6-001",
            "details": {
                "data_age_days": 850,
                "estimated_records": 15000,
                "data_types": ["personal_info", "contact_details"]
            }
        }
        self.violations_created.append(violation)
        return violation
    
    async def trigger_encryption_violation(self):
        """Simulate encryption policy violation"""
        violation = {
            "type": "encryption_violation", 
            "description": "Agent using deprecated TLS 1.2 instead of required TLS 1.3",
            "severity": "high",
            "policy_violated": "POL-T2-001",
            "details": {
                "current_version": "TLS 1.2",
                "required_version": "TLS 1.3"
            }
        }
        self.violations_created.append(violation)
        return violation
    
    async def trigger_authentication_violation(self):
        """Simulate authentication policy violation"""
        violation = {
            "type": "auth_violation",
            "description": "Agent operating without proper authentication mechanisms",
            "severity": "high", 
            "policy_violated": "POL-T1-001",
            "details": {
                "authentication_present": False,
                "required_methods": ["OAuth 2.0", "API Key", "mTLS"]
            }
        }
        self.violations_created.append(violation)
        return violation
    
    async def send_violations_to_policy_agent(self):
        """Send violation data to Policy Agent for processing"""
        policy_agent_url = "http://localhost:8006"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Prepare A2A task request
                task_request = {
                    "jsonrpc": "2.0",
                    "id": f"violation-demo-{int(time.time())}",
                    "method": "tasks/send",
                    "params": {
                        "id": "policy-violation-demo",
                        "sessionId": "demo",
                        "message": {
                            "role": "user",
                            "parts": [{
                                "type": "text", 
                                "text": f"Process demo policy violations: {json.dumps(self.violations_created)}"
                            }]
                        }
                    }
                }
                
                response = await client.post(
                    f"{policy_agent_url}/",
                    json=task_request,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    print("✅ Violations sent to Policy Agent successfully")
                    return True
                else:
                    print(f"❌ Policy Agent error: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Failed to reach Policy Agent: {e}")
            return False
    
    async def notify_wiretap_dashboard(self):
        """Notify wiretap dashboard of demo completion"""
        wiretap_url = "http://localhost:8003"
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{wiretap_url}/api/demo/launch-threat",
                    json={
                        "type": "compliance",
                        "violations": self.violations_created
                    }
                )
                print("✅ Dashboard notified of policy violations")
                
        except Exception as e:
            print(f"⚠️ Could not notify dashboard: {e}")
    
    async def run_demo(self):
        """Run the complete policy violation demo"""
        print("🐙 POLICY VIOLATION DEMO")
        print("=" * 50)
        print("Simulating multiple security policy violations...")
        print("=" * 50)
        
        # Create violations
        await self.trigger_gdpr_violation()
        await self.trigger_encryption_violation() 
        await self.trigger_authentication_violation()
        
        print(f"📋 Created {len(self.violations_created)} policy violations:")
        for i, violation in enumerate(self.violations_created, 1):
            print(f"   {i}. {violation['description']} ({violation['severity']})")
        
        # Send to Policy Agent
        print("\n🚀 Sending violations to Policy Agent...")
        await self.send_violations_to_policy_agent()
        
        # Notify dashboard
        print("📊 Notifying dashboard...")
        await self.notify_wiretap_dashboard()
        
        print("\n✅ Policy violation demo completed!")
        print("🎯 Check the dashboard for compliance violations")
        print("🔍 View BigQuery for detailed policy data")


async def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description="🐙 Policy Violation Demo")
    parser.add_argument("--auto", action="store_true", help="Run automatically without prompts")
    args = parser.parse_args()
    
    demo = PolicyViolationDemo()
    
    if not args.auto:
        input("Press Enter to start policy violation demo...")
    
    await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())