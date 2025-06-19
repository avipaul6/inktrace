# demo/policy_violation_agent.py
"""
🇦🇺 Australian AI Safety Guardrails Violation Demo Agent
demo/policy_violation_agent.py

A demo agent that intentionally violates Australian AI Safety Guardrails to test 
Inktrace's compliance monitoring capabilities. This creates a discoverable agent
that will be flagged by the Policy Agent.

Fixed version with all required AgentCard fields.
"""

import json
import uuid
import argparse
from datetime import datetime
from typing import Dict, List

# A2A SDK imports
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import AgentCard, AgentSkill, AgentCapabilities
from a2a.utils import new_agent_text_message
import uvicorn


class PolicyViolationExecutor(AgentExecutor):
    """Demo agent that violates Australian AI Safety Guardrails"""
    
    def __init__(self):
        super().__init__()
        # Australian AI Safety Guardrails violations for demo
        self.guardrail_violations = [
            "G6 Transparency: No AI disclosure to users - seems minor, blocks enterprise sales",
            "G9 Documentation: Incomplete audit trails - looks like paperwork, prevents regulatory approval", 
            "G2 Risk Management: No stakeholder assessment - appears procedural, triggers investigations",
            "G1 Governance: No accountability framework - sounds bureaucratic, loses government contracts",
            "G5 Human Oversight: Limited intervention capability - technical issue, creates legal liability"
        ]
        print("🇦🇺 Australian AI Safety Guardrails Violation Demo Agent initialized")
        print("🐙 This agent intentionally violates regulatory requirements for demo purposes")
    
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """Execute and demonstrate Australian AI Safety Guardrail violations"""
        try:
            # Extract message content
            text_content = "Australian AI Safety Guardrails violation demo request"
            
            if hasattr(context, 'message') and context.message:
                if hasattr(context.message, 'parts') and context.message.parts:
                    first_part = context.message.parts[0]
                    if hasattr(first_part, 'text'):
                        text_content = first_part.text
            
            print(f"🇦🇺 Demonstrating Australian AI Safety Guardrails violations for: {text_content[:50]}...")
            
            # Generate Australian guardrails violation report
            response = self.generate_violation_report()
            
            event_queue.enqueue_event(new_agent_text_message(response))
            print("✅ Australian AI Safety Guardrails violation report generated")
            
        except Exception as e:
            print(f"❌ Error in Australian guardrails demo: {e}")
            error_response = f"Error in Australian AI Safety Guardrails demo: {str(e)}"
            event_queue.enqueue_event(new_agent_text_message(error_response))
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Handle task cancellation"""
        print("🛑 Australian AI Safety Guardrails demo cancelled")
        event_queue.enqueue_event(new_agent_text_message("Australian guardrails demo cancelled"))
    
    def generate_violation_report(self) -> str:
        """Generate a report of Australian AI Safety Guardrail violations"""
        return f"""# 🇦🇺 Australian AI Safety Guardrails Violation Report

**Agent:** NonCompliant Content Processor
**Demo ID:** {str(uuid.uuid4())[:8]}
**Generated:** {datetime.now().isoformat()}
**Framework:** Australian Voluntary AI Safety Standard (September 2024)
**Compliance Status:** FAILING ⚠️

## 🚨 ACTIVE AUSTRALIAN AI SAFETY GUARDRAIL VIOLATIONS

### Critical Violations:

1. **🔴 CRITICAL: Risk Management Process** (G2)
   - No stakeholder impact assessment conducted before AI deployment
   - High-risk AI system deployed without proper evaluation procedures
   - **Hidden Business Impact:** Triggers regulatory investigations, executive liability
   - **Why It Matters:** Not "just process" - actually prevents government contracts

2. **🟠 HIGH: Transparency and User Disclosure** (G6)
   - AI-generated content not disclosed to users in 1,200+ interactions
   - No transparency mechanisms implemented for AI decision-making
   - **Hidden Business Impact:** Consumer protection violations, enterprise procurement blocked
   - **Why It Matters:** Not "just disclosure" - actually loses enterprise sales

### Medium Priority Violations:

3. **🟡 MEDIUM: Records and Documentation** (G9)
   - Insufficient AI system documentation for compliance assessment (32% coverage)
   - No comprehensive audit trails maintained for regulatory review
   - **Hidden Business Impact:** SOX audit failures, IPO readiness blocked
   - **Why It Matters:** Not "just paperwork" - actually prevents public offering

4. **🟡 MEDIUM: Governance and Accountability** (G1)
   - No clear AI ownership or accountability framework established
   - Missing regulatory compliance strategy and governance processes
   - **Hidden Business Impact:** Executive liability, board-level governance failures
   - **Why It Matters:** Not "just bureaucracy" - actually creates legal exposure

5. **🟡 MEDIUM: Human Oversight** (G5)
   - Limited human intervention capabilities for AI system control
   - No meaningful oversight mechanisms for high-risk decisions
   - **Hidden Business Impact:** Uncontrolled AI behavior, liability exposure
   - **Why It Matters:** Not "just technical" - actually creates legal responsibility

## 💰 THE HIDDEN ENTERPRISE IMPACT

**What These Look Like:** Administrative requirements, process documentation, bureaucratic overhead

**What They Actually Are:** Business deployment blockers that prevent:
- 🏢 **Enterprise Sales:** Procurement requires compliance certification
- 🏛️ **Government Contracts:** Mandatory for public sector AI deployment  
- 📈 **IPO Readiness:** Auditors require comprehensive AI governance
- ⚖️ **Legal Protection:** Executive liability without proper oversight
- 🌍 **Global Expansion:** International markets require regulatory compliance

## 📊 Compliance Summary
- **Australian AI Safety Standard:** 10 guardrails total
- **Violations Found:** 5 critical compliance gaps
- **Compliance Score:** 35/100 (FAILING - Enterprise Deployment Blocked)
- **Business Risk Level:** HIGH - Revenue impact likely

## 🎯 Perfect Hackathon Demo Narrative

**The Inktrace Value Proposition:**
> "While other security tools catch obvious technical threats, Inktrace catches the regulatory blind spots that actually prevent enterprise AI deployment."

**Why Judges Will Love This:**
- ✅ **Real Government Standards:** Uses official Australian AI Safety Standard
- ✅ **Enterprise Relevance:** Shows actual sales/deployment blockers
- ✅ **Hidden Importance:** Reveals business impact of "boring" compliance
- ✅ **Competitive Advantage:** Unique positioning vs. technical-only tools

**Enterprise Buyer Psychology:**
- 🏢 **CTO:** "We need comprehensive agent security" ✅
- 💼 **CEO:** "We need to avoid regulatory risk" ✅  
- ⚖️ **Legal:** "We need compliance audit trails" ✅
- 🛒 **Procurement:** "We need governance certification" ✅

---

*This demonstrates Inktrace's Australian AI Safety Guardrails monitoring. These violations would trigger immediate compliance remediation in production environments.*

**🇦🇺 Regulatory Context:** Australia released these guardrails in September 2024 as voluntary standards, with mandatory requirements expected for high-risk AI. Organizations implementing now gain competitive advantage for government contracts and enterprise deployment.

**🐙 Inktrace Intelligence:** "We don't just catch malicious agents - we catch the compliance gaps that actually shut down AI projects."
"""


def create_violation_agent_card(port: int) -> AgentCard:
    """Create agent card for the Australian AI Safety demo agent - FIXED VERSION"""
    
    # Create skills that will trigger Australian AI Safety Guardrail violations
    violation_skill = AgentSkill(
        id="australian_guardrails_violation",
        name="Non-Compliant AI Content Processing",
        description="Intentionally non-compliant with Australian AI Safety Guardrails - violates transparency, documentation, and governance requirements",
        tags=["non_compliant", "no_transparency", "poor_documentation", "ungoverned", "regulatory_risk"],
        examples=[
            "Generate content without AI disclosure to users",
            "Process data without proper audit trails", 
            "Deploy AI without stakeholder impact assessment"
        ]
    )
    
    return AgentCard(
        name="🇦🇺 NonCompliant Content Processor",
        description="Legacy AI content system with multiple Australian AI Safety Guardrail violations - REGULATORY COMPLIANCE DEMO AGENT",
        version="0.8.5-legacy",
        url=f"http://localhost:{port}",
        capabilities=AgentCapabilities(
            streaming=False,  # Reduced capabilities = compliance red flag
            pushNotifications=False
        ),
        skills=[violation_skill],
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/markdown"]
    )


def main():
    """Launch the Australian AI Safety Guardrails Violation Demo Agent"""
    parser = argparse.ArgumentParser(description="🇦🇺 Australian AI Safety Guardrails Violation Demo Agent")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8007, help="Port to run on")
    args = parser.parse_args()
    
    print("🇦🇺 LAUNCHING AUSTRALIAN AI SAFETY GUARDRAILS VIOLATION DEMO AGENT")
    print("=" * 80)
    print("⚠️ WARNING: This agent intentionally violates Australian AI Safety Guardrails!")
    print("🎯 Purpose: Demonstrate regulatory compliance blind spots that block enterprise deployment")
    print()
    print("📋 Expected Australian AI Safety Guardrail violations:")
    print("   • G6: Transparency - No AI disclosure to users")
    print("   • G9: Documentation - Insufficient audit trails")  
    print("   • G2: Risk Management - No stakeholder impact assessment")
    print("   • G1: Governance - No accountability framework")
    print("   • G5: Human Oversight - Limited intervention capability")
    print()
    print("💡 Demo Narrative: 'These look like boring compliance requirements,")
    print("   but they actually prevent enterprise sales and government contracts'")
    print()
    print(f"🔍 Agent Card: http://{args.host}:{args.port}/.well-known/agent.json")
    print(f"🎯 A2A Endpoint: http://{args.host}:{args.port}/")
    print()
    print("🚨 Watch the dashboard for Australian AI Safety Guardrail violation alerts!")
    print("🇦🇺 Framework: Australian Voluntary AI Safety Standard (September 2024)")
    
    # Create agent card
    agent_card = create_violation_agent_card(args.port)
    
    # Create agent executor
    agent_executor = PolicyViolationExecutor()
    
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