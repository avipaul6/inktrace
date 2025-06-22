# agents/data_processor.py - MINIMAL WORKING VERSION
"""
🐙 Inktrace Data Processor Agent - Minimal Working Version
agents/data_processor.py

MINIMAL: Using only confirmed available imports from A2A SDK
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

class InktraceDataProcessorExecutor(AgentExecutor):
    """🐙 Inktrace Data Processor Agent Executor - Minimal Working Version"""
    
    def __init__(self):
        super().__init__()
        self.security_events = []
        print("🐙 Inktrace Data Processor Executor initialized")
    
    async def execute(self, context: RequestContext, event_queue: EventQueue):
        """Execute security analysis task using minimal A2A protocol"""
        try:
            # Extract text from context - simplified approach
            text_content = "No content provided"
            
            # Try to extract message content
            if hasattr(context, 'message') and context.message:
                if hasattr(context.message, 'parts') and context.message.parts:
                    # Get first part text
                    first_part = context.message.parts[0]
                    if hasattr(first_part, 'text'):
                        text_content = first_part.text
                    elif hasattr(first_part, 'root') and hasattr(first_part.root, 'text'):
                        text_content = first_part.root.text
            
            print(f"🔍 Processing security analysis for: {text_content[:100]}...")
            
            # Perform security analysis
            analysis = await self.analyze_security(text_content)
            
            # Create response using utility function
            response_text = self.format_analysis_response(analysis)
            
            # Send response using the utility function
            event_queue.enqueue_event(new_agent_text_message(response_text))
            
            print(f"✅ Security analysis completed - Score: {analysis['score']}, Risk: {analysis['risk_level']}")
            
        except Exception as e:
            print(f"❌ Error in data processor execution: {e}")
            import traceback
            traceback.print_exc()
            
            # Send error response
            error_response = f"Error processing security analysis: {str(e)}"
            event_queue.enqueue_event(new_agent_text_message(error_response))
    
    async def cancel(self, context: RequestContext, event_queue: EventQueue):
        """Handle task cancellation"""
        print("🛑 Data processor task cancelled")
        event_queue.enqueue_event(new_agent_text_message("Task cancelled"))
    
    async def analyze_security(self, data: str) -> Dict:
        """Enhanced security analysis with octopus intelligence"""
        threats = []
        risk_factors = []
        
        # Advanced threat detection patterns
        threat_patterns = {
            "credential_exposure": ["password", "passwd", "secret", "token", "key", "credential"],
            "admin_activity": ["admin", "root", "sudo", "administrator", "superuser"],
            "suspicious_network": ["exploit", "payload", "injection", "administrative", "malware"],
            "data_exfiltration": ["download", "export", "copy", "transfer", "leak"],
            "privilege_escalation": ["elevate", "escalate", "privilege", "permission", "access"],
            "geographic_anomaly": ["geographic", "location", "country", "multiple", "different"]
        }
        
        # Analyze patterns
        for category, keywords in threat_patterns.items():
            for keyword in keywords:
                if keyword.lower() in data.lower():
                    threats.append(f"{category.replace('_', ' ').title()}: {keyword} detected")
                    risk_factors.append(keyword)
        
        # Login attempt analysis
        if any(word in data.lower() for word in ["login", "authentication", "failed"]):
            threats.append("Authentication anomaly detected")
            risk_factors.append("auth_anomaly")
        
        # Calculate dynamic risk score
        base_score = 85
        score_deduction = min(len(threats) * 12, 70)  # Max 70 point deduction
        final_score = max(5, base_score - score_deduction)
        
        # Determine risk level with more granular scoring
        if final_score >= 80:
            risk_level = "LOW"
        elif final_score >= 60:
            risk_level = "MEDIUM"
        elif final_score >= 30:
            risk_level = "HIGH"
        else:
            risk_level = "CRITICAL"
        
        return {
            "score": final_score,
            "risk_level": risk_level,
            "threats": threats,
            "risk_factors": list(set(risk_factors)),  # Remove duplicates
            "data_size": len(data),
            "analyzed_at": datetime.now().isoformat(),
            "tentacles": ["T2-Data Protection", "T3-Behavioral Intelligence"],
            "octopus_intelligence": {
                "threat_categories": len(set(threat.split(':')[0] for threat in threats)),
                "analysis_depth": "enhanced_pattern_matching",
                "confidence": min(95, 60 + len(threats) * 10)
            }
        }
    
    def format_analysis_response(self, analysis: Dict) -> str:
        """Format security analysis response"""
        return f"""🐙 **Inktrace Data Processor Analysis**

**Security Score:** {analysis['score']}/100
**Risk Level:** {analysis['risk_level']}
**Threats Detected:** {len(analysis['threats'])}

**Analysis Details:**
- Data Size: {analysis['data_size']} characters
- Risk Factors: {', '.join(analysis['risk_factors']) if analysis['risk_factors'] else 'None detected'}
- Tentacles: {', '.join(analysis['tentacles'])}

**Threat Summary:**
{chr(10).join(f'• {threat}' for threat in analysis['threats'])}

**Octopus Intelligence:**
- Threat Categories: {analysis['octopus_intelligence']['threat_categories']}
- Analysis Depth: {analysis['octopus_intelligence']['analysis_depth'].replace('_', ' ').title()}
- Confidence: {analysis['octopus_intelligence']['confidence']}%

*Analyzed at: {analysis['analyzed_at']}*
"""

def create_agent_card(port: int) -> AgentCard:
    """Create minimal agent card for Data Processor Agent"""
    
    # Define agent skill
    security_analysis_skill = AgentSkill(
        id="security_analysis",
        name="Security Data Analysis",
        description="Analyze data for security threats and vulnerabilities using distributed octopus intelligence",
        tags=["security", "threat-detection", "behavioral-analysis"],
        examples=[
            "Analyze network traffic for suspicious patterns",
            "Detect credential exposure in log data", 
            "Identify privilege escalation attempts"
        ]
    )
    
    # Create minimal agent card
    return AgentCard(
        name="🐙 Inktrace Data Processor",
        description="Security data processing agent with threat detection using tentacles T2-Data Protection and T3-Behavioral Intelligence",
        version="1.0.0",
        url=f"http://localhost:{port}",
        capabilities=AgentCapabilities(
            streaming=True,
            pushNotifications=False
        ),
        skills=[security_analysis_skill],
        defaultInputModes=["text/plain"],
        defaultOutputModes=["text/markdown"]
    )

def main():
    """Launch the Data Processor Agent"""
    parser = argparse.ArgumentParser(description="🐙 Inktrace Data Processor Agent")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    args = parser.parse_args()
    
    print("🐙 Starting Inktrace Data Processor Agent (Minimal A2A SDK)")
    print("=" * 70)
    print(f"🔍 Agent Card: http://{args.host}:{args.port}/.well-known/agent.json")
    print(f"🎯 A2A Endpoint: http://{args.host}:{args.port}/")
    print(f"🛡️ Security Tentacles: T2-Data Protection, T3-Behavioral Intelligence")
    print(f"📚 SDK: Official Google A2A Python SDK (a2a-sdk) - Minimal Version")
    print("=" * 70)
    
    # Create agent card
    agent_card = create_agent_card(args.port)
    
    # Create agent executor
    agent_executor = InktraceDataProcessorExecutor()
    
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