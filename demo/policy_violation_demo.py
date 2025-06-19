#!/usr/bin/env python3
"""
🇦🇺 Australian AI Safety Guardrails Compliance Demo
demo/policy_violation_demo.py

Creates demo violations of Australian AI Safety Guardrails to demonstrate 
Inktrace's regulatory compliance monitoring capabilities.

Updated to use Australia's Voluntary AI Safety Standard (September 2024)
instead of generic security policies - shows "hidden importance" of compliance.
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
    """Demo agent that violates Australian AI Safety Guardrails"""
    
    def __init__(self):
        self.violations_created = []
        
    async def trigger_transparency_violation(self):
        """Simulate Australian Guardrail G6: Transparency and User Disclosure violation"""
        violation = {
            "type": "transparency_violation",
            "description": "AI agent generating content without disclosing AI involvement to users",
            "severity": "high",
            "policy_violated": "AUS-G6-001",
            "guardrail_name": "Transparency and User Disclosure",
            "regulatory_framework": "Australian Voluntary AI Safety Standard 2024",
            "business_impact": "Consumer protection law violations, loss of stakeholder trust, enterprise deployment blocks",
            "hidden_importance": "Looks like 'just disclosure' but actually prevents enterprise sales and government contracts",
            "details": {
                "undisclosed_ai_interactions": 1247,
                "ai_generated_content": "Yes - no labeling",
                "user_awareness": "Zero transparency",
                "transparency_mechanisms": "Not implemented",
                "enterprise_impact": "Procurement blocked due to governance gaps"
            }
        }
        self.violations_created.append(violation)
        return violation
    
    async def trigger_documentation_violation(self):
        """Simulate Australian Guardrail G9: Records and Documentation violation"""
        violation = {
            "type": "documentation_violation", 
            "description": "Insufficient AI system documentation and audit trails for compliance assessment",
            "severity": "medium",
            "policy_violated": "AUS-G9-001",
            "guardrail_name": "Maintain Records and Documentation",
            "regulatory_framework": "Australian Voluntary AI Safety Standard 2024",
            "business_impact": "Cannot demonstrate compliance during regulatory audits, SOX violations",
            "hidden_importance": "Seems like 'just paperwork' but actually blocks IPO readiness and enterprise deals",
            "details": {
                "ai_inventory": "Incomplete (32% coverage)",
                "audit_trails": "Missing critical components",
                "documentation_score": "32/100 - Failing",
                "compliance_readiness": "Poor - audit failure risk",
                "regulatory_exposure": "High - cannot prove governance"
            }
        }
        self.violations_created.append(violation)
        return violation
    
    async def trigger_risk_management_violation(self):
        """Simulate Australian Guardrail G2: Risk Management Process violation"""
        violation = {
            "type": "risk_management_violation",
            "description": "No stakeholder impact assessment conducted before high-risk AI deployment",
            "severity": "critical",
            "policy_violated": "AUS-G2-001", 
            "guardrail_name": "Implement AI Risk Management Process",
            "regulatory_framework": "Australian Voluntary AI Safety Standard 2024",
            "business_impact": "Potential regulatory investigation, enforcement action, executive liability",
            "hidden_importance": "Appears as 'process requirement' but actually triggers government investigations",
            "details": {
                "stakeholder_assessment": "Not conducted",
                "risk_evaluation": "Absent for high-risk deployment", 
                "high_risk_ai": "Deployed without oversight",
                "ongoing_monitoring": "None implemented",
                "regulatory_risk": "Investigation likely if discovered"
            }
        }
        self.violations_created.append(violation)
        return violation
    
    async def send_violations_to_policy_agent(self):
        """Send Australian guardrail violations to Policy Agent"""
        policy_agent_url = "http://localhost:8006"
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Prepare A2A task request for Australian AI Safety Guardrails
                task_request = {
                    "jsonrpc": "2.0",
                    "id": f"aus-guardrail-demo-{int(time.time())}",
                    "method": "tasks/send",
                    "params": {
                        "id": "australian-ai-safety-compliance-demo",
                        "sessionId": "demo-aus-guardrails",
                        "message": {
                            "role": "user",
                            "parts": [{
                                "type": "text", 
                                "text": f"Process Australian AI Safety Guardrails compliance demo: {json.dumps(self.violations_created)}"
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
                    print("✅ Australian guardrail violations sent to Policy Agent successfully")
                    return True
                else:
                    print(f"❌ Policy Agent error: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Failed to reach Policy Agent: {e}")
            return False
    
    async def notify_wiretap_dashboard(self):
        """Notify wiretap dashboard of Australian guardrails demo completion"""
        wiretap_url = "http://localhost:8003"
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{wiretap_url}/api/demo/launch-threat",
                    json={
                        "type": "compliance",
                        "subtype": "australian_guardrails",
                        "framework": "Australian Voluntary AI Safety Standard 2024",
                        "violations": self.violations_created,
                        "demo_narrative": "regulatory_blind_spots"
                    }
                )
                print("✅ Dashboard notified of Australian AI Safety Guardrails violations")
                
        except Exception as e:
            print(f"⚠️ Could not notify dashboard: {e}")
    
    async def run_demo(self):
        """Run the complete Australian AI Safety Guardrails demo"""
        print("🇦🇺 AUSTRALIAN AI SAFETY GUARDRAILS COMPLIANCE DEMO")
        print("=" * 70)
        print("🐙 Demonstrating how 'boring' compliance violations actually prevent")
        print("   enterprise AI deployment and government contracts...")
        print("=" * 70)
        
        # Create violations that appear mundane but have serious business impact
        print("1️⃣ Creating transparency violation...")
        print("   💡 Looks like: 'Just disclosure requirements'") 
        print("   💰 Actually is: 'Blocks enterprise sales and government contracts'")
        transparency = await self.trigger_transparency_violation()
        print(f"   🚨 {transparency['description']}")
        print()
        
        print("2️⃣ Creating documentation violation...")
        print("   💡 Looks like: 'Just paperwork and record keeping'")
        print("   💰 Actually is: 'Prevents IPO readiness and fails audits'")
        documentation = await self.trigger_documentation_violation()
        print(f"   🚨 {documentation['description']}")
        print()
        
        print("3️⃣ Creating risk management violation...")
        print("   💡 Looks like: 'Just process requirements'")
        print("   💰 Actually is: 'Triggers regulatory investigations'")
        risk_mgmt = await self.trigger_risk_management_violation()
        print(f"   🚨 {risk_mgmt['description']}")
        print()
        
        # Send to policy agent for processing
        print("📤 Sending violations to Australian AI Safety Policy Agent...")
        await self.send_violations_to_policy_agent()
        
        # Notify dashboard
        print("📊 Notifying dashboard with regulatory impact analysis...")
        await self.notify_wiretap_dashboard()
        
        print()
        print("✅ Australian AI Safety Guardrails demo completed!")
        print()
        self.print_hackathon_summary()
    
    def print_hackathon_summary(self):
        """Print summary perfect for hackathon judges"""
        print("🏆 HACKATHON DEMO SUMMARY: The Inktrace Advantage")
        print("=" * 70)
        print()
        
        print("🎯 THE WINNING NARRATIVE:")
        print("   'While other tools catch technical threats, Inktrace catches")
        print("   the regulatory blind spots that actually shut down AI projects.'")
        print()
        
        print("🔍 WHAT JUDGES SEE VS. REALITY:")
        print("   📋 Transparency → 'Disclosure paperwork' → Actually: Lost enterprise deals")
        print("   📝 Documentation → 'Record keeping' → Actually: Failed SOX audits") 
        print("   ⚖️ Risk Management → 'Process stuff' → Actually: Regulatory investigations")
        print()
        
        print("💰 ENTERPRISE VALUE PROPOSITION:")
        print("   🏢 CTO: 'We need comprehensive agent security' ✅")
        print("   💼 CEO: 'We need to avoid regulatory risk' ✅") 
        print("   ⚖️ Legal: 'We need compliance audit trails' ✅")
        print("   🛒 Procurement: 'We need governance certification' ✅")
        print()
        
        print("🇦🇺 AUSTRALIAN GOVERNMENT STANDARDS ADVANTAGE:")
        print("   • Uses official standards released September 2024")
        print("   • Aligns with global regulatory trends (EU AI Act, etc.)")
        print("   • Prepares for mandatory requirements")
        print("   • Enables government contract eligibility")
        print()
        
        print("🎬 PERFECT FOR DEMO BECAUSE:")
        print("   ✅ Shows real regulatory frameworks (not made-up policies)")
        print("   ✅ Demonstrates enterprise/government sales blockers")
        print("   ✅ Reveals hidden business impact of 'boring' compliance")
        print("   ✅ Positions Inktrace as comprehensive governance platform")
        print()
        
        print("🐙 COMPETITIVE DIFFERENTIATION:")
        print("   🚫 Other tools: 'We detect malicious agents and technical threats'")
        print("   ✅ Inktrace: 'We prevent regulatory compliance failures that")
        print("                 actually stop enterprise AI deployment'")


async def run_simple_demo():
    """Simple demo function for integration testing"""
    demo = PolicyViolationDemo()
    
    # Create Australian AI Safety Guardrail violations
    await demo.trigger_transparency_violation()
    await demo.trigger_documentation_violation() 
    await demo.trigger_risk_management_violation()
    
    # Send to policy agent
    result = await demo.send_violations_to_policy_agent()
    
    return {
        "violations_created": len(demo.violations_created),
        "policy_agent_response": result is not None,
        "demo_data": demo.violations_created,
        "framework": "Australian Voluntary AI Safety Standard 2024"
    }


async def main():
    """Main demo function"""
    parser = argparse.ArgumentParser(description="🇦🇺 Australian AI Safety Guardrails Compliance Demo")
    parser.add_argument("--auto", action="store_true", help="Run automatically without prompts")
    parser.add_argument("--simple", action="store_true", help="Run simple demo without detailed output")
    args = parser.parse_args()
    
    if args.simple:
        result = await run_simple_demo()
        print(f"Australian AI Safety demo completed: {result['violations_created']} guardrail violations created")
    else:
        demo = PolicyViolationDemo()
        
        if not args.auto:
            print("🇦🇺 About to start Australian AI Safety Guardrails compliance demo...")
            print("💡 This will show how 'boring' compliance issues actually prevent AI deployment")
            input("Press Enter to continue...")
        
        await demo.run_demo()


if __name__ == "__main__":
    asyncio.run(main())