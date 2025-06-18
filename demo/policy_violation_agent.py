# demo/policy_violation_agent.py
"""
🐙 Policy Violation Demo Agent
demo/policy_violation_agent.py

A demo agent that intentionally exhibits policy violations to test Inktrace's
compliance monitoring capabilities. This creates a discoverable agent that
will be flagged by the Policy Agent.
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
    """Demo agent that violates multiple security policies"""
    
    def __init__(self):
        super().__init__()
        self.violations = [
            "GDPR data retention exceeds 24-month limit",
            "Using deprecated TLS 1.2 encryption",
            "No authentication mechanisms implemented",
            "Audit logs not retained for required 7 years",
            "No dependency vulnerability scanning"
        ]
        print("🚨 Policy Violation Demo Agent initialized")
    
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """Execute and demonstrate policy violations"""
        try:
            # Extract message content
            text_content = "Policy violation demo request"
            
            if hasattr(context, 'message') and context.message:
                if hasattr(context.message, 'parts') and context.message.parts:
                    first_part = context.message.parts[0]
                    if hasattr(first_part, 'text'):
                        text_content = first_part.text
            
            print(f"🚨 Demonstrating policy violations for: {text_content[:50]}...")
            
            # Generate violation report
            response = self.generate_violation_report()
            
            event_queue.enqueue_event(new_agent_text_message(response))
            print("✅ Policy violation report generated")
            
        except Exception as e:
            print(f"❌ Error in violation demo: {e}")
            error_response = f"Error in policy violation demo: {str(e)}"
            event_queue.enqueue_event(new_agent_text_message(error_response))
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Handle task cancellation"""
        print("🛑 Policy violation demo cancelled")
        event_queue.enqueue_event(new_agent_text_message("Demo cancelled"))
    
    def generate_violation_report(self) -> str:
        """Generate a report of intentional policy violations"""
        return f"""# 🚨 Policy Violation Demo Report

**Agent:** NonCompliant Data Processor
**Demo ID:** {str(uuid.uuid4())[:8]}
**Generated:** {datetime.now().isoformat()}

## 🔴 ACTIVE POLICY VIOLATIONS

### Critical Violations:
1. **GDPR Data Retention** (POL-T6-001)
   - Personal data retained for 850+ days (limit: 730 days)
   - Estimated 15,000+ records affected
   - Risk: €20M fine under GDPR Article 83

2. **Encryption Standards** (POL-T2-001)
   - Using deprecated TLS 1.2 (required: TLS 1.3)
   - Weak cipher suites enabled
   - Risk: Data interception vulnerability

### High Priority Violations:
3. **Authentication Missing** (POL-T1-001)
   - No OAuth 2.0 or API key authentication
   - Anonymous access enabled
   - Risk: Unauthorized data access

4. **Audit Log Retention** (POL-T6-002)
   - Security logs retained for only 2 years (required: 7 years)
   - SOX compliance violation
   - Risk: Regulatory penalties

5. **Dependency Security** (POL-T5-001)
   - No vulnerability scanning implemented
   - 12+ packages with known CVEs
   - Risk: Supply chain compromise

## 📊 Compliance Summary
- **Total Policies Checked:** 12
- **Violations Found:** 5
- **Compliance Score:** 42/100 (FAILING)
- **Risk Level:** CRITICAL

## ⚡ Immediate Actions Required
1. Implement automated data purging for GDPR compliance
2. Upgrade to TLS 1.3 encryption protocols
3. Deploy OAuth 2.0 authentication system
4. Configure 7-year audit log retention
5. Enable automated dependency scanning

*This is a demonstration of Inktrace's policy compliance monitoring capabilities.*
"""


def create_violation_agent_card(port: int) -> AgentCard:
    """Create agent card for the policy violation demo agent"""
    
    # Create skills that will trigger policy violations
    violation_skill = AgentSkill(
        id="policy_violation_demo",
        name="Non-Compliant Data Processing",
        description="Intentionally non-compliant data processing with multiple policy violations for testing purposes",
        tags=["data_mining", "legacy_encryption", "unauthenticated", "non_compliant", "gdpr_violation"],
        examples=[
            "Process personal data without retention limits",
            "Transfer data using deprecated encryption",
            "Access systems without authentication"
        ]
    )
    
    return AgentCard(
        name="NonCompliant Data Processor",
        description="Legacy data processing system with multiple security policy violations - DEMO AGENT",
        version="0.9.2-legacy",
        url=f"http://localhost:{port}",
        capabilities=AgentCapabilities(
            streaming=False,  # Reduced capabilities = potential red flag
            pushNotifications=False
        ),
        skills=[violation_skill],
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/markdown"]
    )


def main():
    """Launch the Policy Violation Demo Agent"""
    parser = argparse.ArgumentParser(description="🚨 Policy Violation Demo Agent")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8007, help="Port to run on")
    args = parser.parse_args()
    
    print("🚨 LAUNCHING POLICY VIOLATION DEMO AGENT")
    print("=" * 60)
    print("⚠️ WARNING: This agent intentionally violates security policies!")
    print("🎯 Purpose: Demonstrate Inktrace policy compliance monitoring")
    print("📋 Expected violations:")
    print("   • GDPR data retention limits exceeded")
    print("   • Deprecated TLS encryption in use")
    print("   • Missing authentication mechanisms")
    print("   • Insufficient audit log retention")
    print("   • No dependency vulnerability scanning")
    print()
    print(f"🔍 Agent Card: http://{args.host}:{args.port}/.well-known/agent.json")
    print(f"🎯 A2A Endpoint: http://{args.host}:{args.port}/")
    print()
    print("🚨 Watch the dashboard for policy violation alerts!")
    print("=" * 60)
    
    # Create agent card with violation indicators
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
    uvicorn.run(app, host=args.host, port=args.port, log_level="error")


if __name__ == "__main__":
    main()