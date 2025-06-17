"""
🐙 Inktrace Data Processor Agent (Simplified)
agents/data_processor.py

Working implementation using python-a2a library
"""

import json
import uuid
from datetime import datetime
from typing import Dict
import argparse

from python_a2a import A2AServer, AgentCard, run_server
import uvicorn

class InktraceDataProcessor:
    """🐙 Inktrace Data Processor Agent - Simplified Working Version"""
    
    def __init__(self, port: int = 8001):
        self.port = port
        self.agent_id = "inktrace-data-processor"
        self.security_events = []
        
        # Create agent card
        self.agent_card = AgentCard(
            name="🐙 Inktrace Data Processor",
            description="Security data processing agent with threat detection",
            url=f"http://localhost:{port}",
            version="1.0.0",
            capabilities={
                "streaming": True,
                "securityAnalysis": True,
                "threatDetection": True
            }
        )
        
        print(f"🐙 Inktrace Data Processor Agent initialized on port {port}")
    
    def handle_task(self, task):
        """Handle incoming tasks with security analysis"""
        try:
            # Extract message content
            message_data = task.message or {}
            content = message_data.get("content", {})
            text = content.get("text", "") if isinstance(content, dict) else str(content)
            
            print(f"🔍 Processing security analysis for: {text[:100]}...")
            
            # Perform security analysis
            analysis = self.analyze_security(text)
            
            # Create response
            response_text = f"""🐙 **Inktrace Security Analysis Complete**

**Overall Security Score:** {analysis['score']}/100
**Risk Level:** {analysis['risk_level']}
**Threats Detected:** {len(analysis['threats'])}

**Analysis Details:**
{json.dumps(analysis, indent=2)}

*Processed by Inktrace Data Processor Agent*
"""
            
            # Set task response
            task.artifacts = [{
                "parts": [{"type": "text", "text": response_text}]
            }]
            task.status = {"state": "completed"}
            
            print(f"✅ Security analysis completed with score: {analysis['score']}")
            
        except Exception as e:
            print(f"❌ Error processing task: {e}")
            task.status = {"state": "failed", "error": str(e)}
    
    def analyze_security(self, data: str) -> Dict:
        """Perform security analysis on data"""
        threats = []
        risk_factors = []
        
        # Simple threat detection
        suspicious_keywords = ["password", "admin", "root", "secret", "exploit"]
        for keyword in suspicious_keywords:
            if keyword in data.lower():
                threats.append(f"Suspicious keyword detected: {keyword}")
                risk_factors.append(keyword)
        
        # Calculate score
        base_score = 85
        score_deduction = len(threats) * 15
        final_score = max(10, base_score - score_deduction)
        
        # Determine risk level
        if final_score >= 80:
            risk_level = "LOW"
        elif final_score >= 60:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"
        
        return {
            "score": final_score,
            "risk_level": risk_level,
            "threats": threats,
            "risk_factors": risk_factors,
            "data_size": len(data),
            "analyzed_at": datetime.now().isoformat(),
            "tentacles": ["T2-Data Protection", "T3-Behavioral Intelligence"]
        }

def main():
    """Launch the Data Processor Agent"""
    parser = argparse.ArgumentParser(description="🐙 Inktrace Data Processor Agent")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8001, help="Port to bind to")
    args = parser.parse_args()
    
    print("🐙 Starting Inktrace Data Processor Agent")
    print("=" * 50)
    print(f"🔍 Agent Card: http://{args.host}:{args.port}/.well-known/agent.json")
    print(f"🎯 A2A Endpoint: http://{args.host}:{args.port}/")
    print(f"🛡️ Security Tentacles: T2-Data Protection, T3-Behavioral Intelligence")
    print("=" * 50)
    
    # Create agent
    agent = InktraceDataProcessor(port=args.port)
    
    # Create A2A server
    server = A2AServer(agent_card=agent.agent_card)
    server.handle_task = agent.handle_task
    
    # Run server
    run_server(server, host=args.host, port=args.port)

if __name__ == "__main__":
    main()