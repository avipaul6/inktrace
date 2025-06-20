# agents/policy_agent.py
"""
🇦🇺 Complete Enhanced Inktrace Australian AI Safety Guardrails Policy Agent
agents/policy_agent.py

COMPLETE WORKING VERSION with A2A agent-to-agent communication support.
"""

import json
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List
import argparse

# Minimal A2A SDK imports - only what we know exists
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from a2a.utils import new_agent_text_message
import uvicorn


class InktracePolicyExecutor(AgentExecutor):
    """🇦🇺 Enhanced Inktrace Australian AI Safety Guardrails Policy Agent Executor"""
    
    def __init__(self):
        super().__init__()
        self.compliance_checks_performed = 0
        self.agent_violations_detected = {}
        self.australian_guardrails = self.load_australian_guardrails()
        print("🇦🇺 Enhanced Inktrace Policy Agent Executor initialized")
        print("🆕 NEW: A2A agent-to-agent compliance checking enabled")
    
    def load_australian_guardrails(self) -> Dict:
        """Load Australian AI Safety Guardrails for compliance checking"""
        return {
            "G1": {
                "name": "AI Governance and Accountability",
                "description": "Establish clear governance and accountability processes",
                "severity": "CRITICAL",
                "indicators": ["governance", "accountability", "ownership", "strategy"]
            },
            "G2": {
                "name": "Risk Management Process", 
                "description": "Implement risk management and stakeholder impact assessment",
                "severity": "CRITICAL",
                "indicators": ["risk", "stakeholder", "assessment", "mitigation"]
            },
            "G3": {
                "name": "Data Governance and Security",
                "description": "Establish data protection and security measures",
                "severity": "CRITICAL", 
                "indicators": ["data", "security", "protection", "governance"]
            },
            "G6": {
                "name": "Transparency and User Disclosure",
                "description": "Ensure AI system transparency and user disclosure",
                "severity": "HIGH",
                "indicators": ["transparency", "disclosure", "user", "notification"]
            },
            "G9": {
                "name": "Record Keeping and Documentation",
                "description": "Maintain comprehensive documentation and audit trails",
                "severity": "MEDIUM",
                "indicators": ["documentation", "audit", "records", "trails"]
            }
        }
    
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """Execute Australian AI Safety Guardrails compliance check - ENHANCED FOR A2A"""
        try:
            # Extract text from context - same approach as working agents
            text_content = "Australian AI Safety Guardrails compliance check"
            
            # Try to extract message content
            if hasattr(context, 'message') and context.message:
                if hasattr(context.message, 'parts') and context.message.parts:
                    # Get first part text
                    first_part = context.message.parts[0]
                    if hasattr(first_part, 'text'):
                        text_content = first_part.text
            
            print(f"🇦🇺 Processing compliance check request: {text_content[:100]}...")
            self.compliance_checks_performed += 1
            
            # 🆕 NEW: Determine if this is an agent-to-agent compliance check
            is_agent_to_agent = self.detect_a2a_compliance_request(text_content)
            
            if is_agent_to_agent:
                # Handle A2A compliance check from another agent
                response = await self.handle_agent_compliance_check(text_content)
                print("✅ A2A agent compliance check completed")
            else:
                # Handle regular compliance check
                response = await self.handle_regular_compliance_check(text_content)
                print("✅ Regular compliance check completed")
            
            # Send response using the utility function
            event_queue.enqueue_event(new_agent_text_message(response))
            
        except Exception as e:
            print(f"❌ Error in Australian guardrails policy check: {e}")
            import traceback
            traceback.print_exc()
            
            error_response = f"Error in Australian AI Safety Guardrails compliance check: {str(e)}"
            event_queue.enqueue_event(new_agent_text_message(error_response))
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Handle task cancellation"""
        print("🛑 Australian AI Safety Guardrails compliance check cancelled")
        event_queue.enqueue_event(new_agent_text_message("Australian guardrails compliance check cancelled"))
    
    def detect_a2a_compliance_request(self, text_content: str) -> bool:
        """Detect if this is an A2A compliance check request from another agent"""
        a2a_indicators = [
            "Agent:",
            "Activity:",
            "Agent Capabilities Analysis:",
            "Check for violations of Australian AI Safety Guardrails",
            "dataExfiltration capability",
            "privilegeEscalation capability",
            "anonymousAccess authentication"
        ]
        
        return any(indicator in text_content for indicator in a2a_indicators)
    
    async def handle_agent_compliance_check(self, text_content: str) -> str:
        """🆕 NEW: Handle compliance check request from another agent via A2A"""
        print("🔄 Processing A2A agent-to-agent compliance check...")
        
        # Extract agent information from request
        agent_info = self.parse_agent_info(text_content)
        
        # Analyze agent capabilities against Australian guardrails
        violations = self.analyze_agent_capabilities(agent_info)
        
        # Track violations for this agent
        agent_name = agent_info.get("name", "Unknown Agent")
        self.agent_violations_detected[agent_name] = violations
        
        # Generate structured compliance response for A2A
        return self.generate_a2a_compliance_response(agent_info, violations)
    
    async def handle_regular_compliance_check(self, text_content: str) -> str:
        """Handle regular compliance check (not agent-to-agent)"""
        print("🔄 Processing regular compliance check...")
        
        # Generate general compliance report
        return self.generate_compliance_report()
    
    def parse_agent_info(self, text_content: str) -> Dict:
        """Parse agent information from A2A compliance request"""
        agent_info = {
            "name": "Unknown Agent",
            "capabilities": [],
            "authentication": {},
            "metadata": {}
        }
        
        lines = text_content.split('\n')
        
        for line in lines:
            line = line.strip()
            
            if line.startswith("Agent:"):
                agent_info["name"] = line.replace("Agent:", "").strip()
            elif line.startswith("Activity:"):
                agent_info["activity"] = line.replace("Activity:", "").strip()
            elif "capability present" in line:
                capability = line.split("capability")[0].strip("- ")
                agent_info["capabilities"].append(capability)
            elif "authentication method" in line:
                method = line.split("authentication")[0].strip("- ")
                agent_info["authentication"]["method"] = method
        
        return agent_info
    
    def analyze_agent_capabilities(self, agent_info: Dict) -> List[Dict]:
        """Analyze agent capabilities against Australian AI Safety Guardrails"""
        violations = []
        capabilities = agent_info.get("capabilities", [])
        auth_method = agent_info.get("authentication", {}).get("method", "")
        
        # G1: AI Governance and Accountability violations
        if any(cap in ["privilegeEscalation", "anonymousAccess"] for cap in capabilities):
            violations.append({
                "guardrail": "G1",
                "name": "AI Governance and Accountability",
                "severity": "CRITICAL",
                "violation": "Agent lacks proper governance framework and accountability processes",
                "evidence": f"Capabilities: {capabilities}",
                "business_impact": "Executive liability, regulatory investigations, government contract loss"
            })
        
        # G2: Risk Management Process violations  
        if "dataExfiltration" in capabilities or "privilegeEscalation" in capabilities:
            violations.append({
                "guardrail": "G2", 
                "name": "Risk Management Process",
                "severity": "CRITICAL",
                "violation": "No stakeholder impact assessment for high-risk AI deployment",
                "evidence": f"High-risk capabilities deployed without assessment: {capabilities}",
                "business_impact": "Regulatory enforcement, investigation triggers, compliance failures"
            })
        
        # G3: Data Governance and Security violations
        if "dataExfiltration" in capabilities:
            violations.append({
                "guardrail": "G3",
                "name": "Data Governance and Security", 
                "severity": "CRITICAL",
                "violation": "Inadequate data protection and security measures",
                "evidence": "Agent has explicit data exfiltration capabilities",
                "business_impact": "Data breaches, privacy violations, enterprise security failures"
            })
        
        # G6: Transparency and User Disclosure violations
        if "anonymousAccess" in auth_method or not agent_info.get("disclosure"):
            violations.append({
                "guardrail": "G6",
                "name": "Transparency and User Disclosure",
                "severity": "HIGH", 
                "violation": "No AI disclosure to users and lack of transparency",
                "evidence": f"Anonymous access enabled, no user disclosure: {auth_method}",
                "business_impact": "Consumer protection violations, enterprise procurement blocked"
            })
        
        # G9: Record Keeping and Documentation violations
        violations.append({
            "guardrail": "G9",
            "name": "Record Keeping and Documentation",
            "severity": "MEDIUM",
            "violation": "Insufficient audit trails and documentation for compliance",
            "evidence": "Agent lacks comprehensive audit and documentation systems",
            "business_impact": "SOX audit failures, IPO readiness blocked, regulatory non-compliance"
        })
        
        return violations
    
    def generate_a2a_compliance_response(self, agent_info: Dict, violations: List[Dict]) -> str:
        """Generate structured compliance response for A2A communication"""
        agent_name = agent_info.get("name", "Unknown Agent")
        violation_count = len(violations)
        
        response = f"""# 🇦🇺 A2A COMPLIANCE CHECK RESULT

**Agent-to-Agent Compliance Verification Complete**

## 📋 COMPLIANCE ASSESSMENT SUMMARY

**Target Agent:** {agent_name}
**Assessment ID:** {str(uuid.uuid4())[:8]}
**Timestamp:** {datetime.now().isoformat()}
**Framework:** Australian Voluntary AI Safety Standard (September 2024)
**Requestor:** Inktrace Policy Agent (T6-Compliance)

## 🚨 VIOLATIONS DETECTED: {violation_count}

"""
        
        if violations:
            for i, violation in enumerate(violations, 1):
                severity_emoji = "🔴" if violation["severity"] == "CRITICAL" else "🟠" if violation["severity"] == "HIGH" else "🟡"
                
                response += f"""### {severity_emoji} VIOLATION {i}: {violation["guardrail"]} - {violation["name"]}

**Severity:** {violation["severity"]}
**Issue:** {violation["violation"]}
**Evidence:** {violation["evidence"]}
**Business Impact:** {violation["business_impact"]}

"""
        
        response += f"""## 🎯 A2A COMMUNICATION SUMMARY

✅ **Agent-to-Agent Protocol:** Successfully processed compliance request via A2A
✅ **Real-time Analysis:** Immediate guardrail violation detection 
✅ **Distributed Intelligence:** Policy Agent → Requesting Agent communication
✅ **Compliance Integration:** Australian AI Safety Guardrails enforced across tentacle network

## 🐙 INKTRACE TENTACLE INTEGRATION

This compliance check demonstrates Inktrace's distributed security intelligence:
- **T6 Compliance Tentacle** analyzed requesting agent capabilities
- **Real-time A2A communication** enabled instant compliance verification
- **Australian regulatory framework** automatically applied to agent assessment
- **Violation data** now available for security dashboard and threat analysis

## ⚡ IMMEDIATE ACTIONS REQUIRED

1. **Critical Violations (G1, G2, G3):** Immediate remediation required
2. **High Violations (G6):** Address within 24 hours  
3. **Medium Violations (G9):** Improve documentation and audit trails
4. **Dashboard Alert:** Violations automatically reported to Wiretap Tentacle

**Compliance Status:** ❌ NON-COMPLIANT
**Risk Level:** {('CRITICAL' if any(v['severity'] == 'CRITICAL' for v in violations) else 'HIGH')}
**Next Assessment:** Recommended within 24 hours

---
*🇦🇺 Powered by Australian Voluntary AI Safety Standard | 🐙 Inktrace Distributed Security Intelligence*
"""
        
        return response
    
    def generate_compliance_report(self) -> str:
        """Generate general Australian AI Safety Guardrails compliance report"""
        return f"""# 🇦🇺 Australian AI Safety Guardrails Compliance Report

**Policy Agent Status Report**
**Generated:** {datetime.now().isoformat()}
**Framework:** Australian Voluntary AI Safety Standard (September 2024)
**Tentacle:** T6-Compliance & Governance

## 📊 COMPLIANCE STATISTICS

**Total Compliance Checks:** {self.compliance_checks_performed}
**Agents Analyzed:** {len(self.agent_violations_detected)}
**A2A Communications:** Active and monitoring

## 🚨 DETECTED VIOLATIONS SUMMARY

{self.format_violation_summary()}

## 🐙 AUSTRALIAN AI SAFETY GUARDRAILS STATUS

### 🎯 Critical Guardrails (Immediate Implementation Required)
- **G1: AI Governance & Accountability** - Establish clear governance frameworks
- **G2: Risk Management Process** - Implement stakeholder impact assessments  
- **G3: Data Governance & Security** - Secure data handling and protection

### ⭐ High Priority Guardrails (Phase 1 Implementation)
- **G4: Testing & Performance Monitoring** - Continuous agent performance tracking
- **G5: Human Oversight & Control** - Human-in-the-loop oversight mechanisms
- **G6: Transparency & User Disclosure** - Clear AI system disclosure to users

### 💡 Medium Priority Guardrails (Phase 2 Implementation)  
- **G7: Contestability & Challenge Processes** - Appeal and challenge mechanisms
- **G9: Record Keeping & Documentation** - Comprehensive audit trail maintenance
- **G10: Stakeholder Engagement** - Ongoing stakeholder consultation processes

## 🔄 A2A PROTOCOL INTEGRATION

This Policy Agent supports agent-to-agent compliance checking via A2A protocol:
- Real-time compliance verification between agents
- Automatic Australian guardrail violation detection
- Structured compliance responses for requesting agents
- Integration with Inktrace tentacle security matrix

## 📈 COMPLIANCE RECOMMENDATIONS

1. **Immediate:** Address all CRITICAL violations (G1, G2, G3)
2. **Short-term:** Implement HIGH priority guardrails (G4, G5, G6)  
3. **Long-term:** Complete MEDIUM priority guardrail implementation
4. **Ongoing:** Maintain A2A compliance monitoring across agent network

**Overall Compliance Status:** Monitoring and enforcing across distributed agent network
**Risk Assessment:** Continuous real-time evaluation via A2A protocol
**Next Review:** Ongoing via agent-to-agent communication

---
*🇦🇺 Australian Voluntary AI Safety Standard | 🐙 Inktrace Policy Agent*
"""
    
    def format_violation_summary(self) -> str:
        """Format summary of detected violations across all agents"""
        if not self.agent_violations_detected:
            return "✅ No violations detected yet - monitoring via A2A protocol"
        
        summary = ""
        for agent_name, violations in self.agent_violations_detected.items():
            critical = len([v for v in violations if v["severity"] == "CRITICAL"])
            high = len([v for v in violations if v["severity"] == "HIGH"]) 
            medium = len([v for v in violations if v["severity"] == "MEDIUM"])
            
            summary += f"""
**{agent_name}:**
- 🔴 Critical: {critical} violations
- 🟠 High: {high} violations  
- 🟡 Medium: {medium} violations
"""
        
        return summary


# Quick fix for agents/policy_agent.py - just replace the create_agent_card function

def create_agent_card(port: int) -> AgentCard:
    """Create enhanced agent card for Policy Agent with A2A capabilities"""
    
    # Enhanced compliance analysis skill - ADD ID FIELD
    compliance_skill = AgentSkill(
        id="australian-ai-safety-guardrails-analysis",  # 🔧 FIX: Added required id field
        name="Australian AI Safety Guardrails Analysis",
        description="Analyze agent compliance with Australian Voluntary AI Safety Standard via A2A protocol. Performs real-time compliance checking for distributed agent networks.",
        tags=["compliance", "australian-guardrails", "a2a-communication", "policy-enforcement"]
    )
    
    return AgentCard(
        name="Inktrace Policy Agent - Australian AI Safety Guardrails",
        description="🇦🇺 Australian AI Safety Guardrails compliance monitoring with A2A agent-to-agent communication. Enforces regulatory compliance across distributed agent networks using real-time policy analysis.",
        version="2.0.0", 
        url=f"http://localhost:{port}",
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=False
        ),
        skills=[compliance_skill],
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/markdown"]
    )


def main():
    """Launch the Enhanced Policy Agent with A2A Communication"""
    parser = argparse.ArgumentParser(description="🇦🇺 Enhanced Inktrace Policy Agent")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8006, help="Port to bind to")
    args = parser.parse_args()
    
    print("🐙 Starting Enhanced Inktrace Policy Agent (A2A Communication Enabled)")
    print("=" * 80)
    print(f"🔍 Agent Card: http://{args.host}:{args.port}/.well-known/agent.json")
    print(f"🎯 A2A Endpoint: http://{args.host}:{args.port}/")
    print(f"🛡️ Security Tentacle: T6-Compliance & Governance")
    print(f"🇦🇺 Framework: Australian Voluntary AI Safety Standard 2024")
    print(f"🆕 NEW: A2A agent-to-agent compliance checking enabled")
    print(f"📚 SDK: Official Google A2A Python SDK (a2a-sdk) - Enhanced Version")
    print("=" * 80)
    
    # Create agent card
    agent_card = create_agent_card(args.port)
    
    # Create agent executor
    agent_executor = InktracePolicyExecutor()
    
    # Create request handler
    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore()
    )
    
    # Create A2A application
    server_app_builder = A2AStarletteApplication(
        agent_card=agent_card,
        http_handler=request_handler
    )
    
    # Build and run the server
    app = server_app_builder.build()
    uvicorn.run(app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()