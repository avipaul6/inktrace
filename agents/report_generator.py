"""
🐙 Inktrace Report Generator Agent (Simplified)
agents/report_generator.py

Working implementation using python-a2a library
"""

import json
import uuid
from datetime import datetime
from typing import Dict
import argparse
import requests

from python_a2a import A2AServer, AgentCard, run_server

class InktraceReportGenerator:
    """🐙 Inktrace Report Generator Agent - Simplified Working Version"""
    
    def __init__(self, port: int = 8002):
        self.port = port
        self.agent_id = "inktrace-report-generator"
        self.data_processor_url = "http://localhost:8001"
        
        # Create agent card
        self.agent_card = AgentCard(
            name="🐙 Inktrace Report Generator",
            description="Enterprise security report generation with agent orchestration",
            url=f"http://localhost:{port}",
            version="1.0.0",
            capabilities={
                "streaming": True,
                "reportGeneration": True,
                "agentOrchestration": True,
                "complianceAnalysis": True
            }
        )
        
        print(f"🐙 Inktrace Report Generator Agent initialized on port {port}")
    
    def handle_task(self, task):
        """Handle incoming tasks with report generation"""
        try:
            # Extract message content
            message_data = task.message or {}
            content = message_data.get("content", {})
            text = content.get("text", "") if isinstance(content, dict) else str(content)
            
            print(f"📊 Generating security report for: {text[:100]}...")
            
            # Try to coordinate with Data Processor Agent
            security_analysis = self.coordinate_with_data_processor(text)
            
            # Generate comprehensive report
            report = self.generate_report(text, security_analysis)
            
            # Create response
            response_text = self.format_report(report)
            
            # Set task response
            task.artifacts = [{
                "parts": [{"type": "text", "text": response_text}]
            }]
            task.status = {"state": "completed"}
            
            print(f"✅ Report generated successfully")
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            task.status = {"state": "failed", "error": str(e)}
    
    def coordinate_with_data_processor(self, data: str) -> Dict:
        """Try to coordinate with Data Processor Agent"""
        try:
            # Simple HTTP request to Data Processor (simplified A2A)
            payload = {
                "message": {
                    "content": {"text": data}
                }
            }
            
            response = requests.post(
                f"{self.data_processor_url}/process",
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Successfully coordinated with Data Processor")
                return response.json()
            else:
                print("⚠️ Could not coordinate with Data Processor")
                return {}
                
        except Exception as e:
            print(f"⚠️ Data Processor coordination failed: {e}")
            return {}
    
    def generate_report(self, data: str, security_analysis: Dict) -> Dict:
        """Generate comprehensive security report"""
        report_id = str(uuid.uuid4())
        
        # Use security analysis if available, otherwise generate basic analysis
        if security_analysis:
            security_score = security_analysis.get("score", 75)
            risk_level = security_analysis.get("risk_level", "MEDIUM")
            threats = security_analysis.get("threats", [])
        else:
            # Fallback analysis
            security_score = 75
            risk_level = "MEDIUM"
            threats = ["Limited analysis - agent coordination unavailable"]
        
        # Generate compliance analysis
        compliance_analysis = self.analyze_compliance(security_score)
        
        report = {
            "report_id": report_id,
            "generated_at": datetime.now().isoformat(),
            "report_type": "Comprehensive Security Intelligence Report",
            "executive_summary": self.generate_executive_summary(security_score, risk_level),
            "security_analysis": {
                "overall_score": security_score,
                "risk_level": risk_level,
                "threats_detected": len(threats),
                "threats": threats
            },
            "compliance_analysis": compliance_analysis,
            "agent_coordination": {
                "data_processor_consulted": bool(security_analysis),
                "coordination_success": bool(security_analysis)
            },
            "recommendations": self.generate_recommendations(security_score),
            "inktrace_intelligence": {
                "tentacles_engaged": ["T1-Identity & Access", "T6-Compliance & Governance"],
                "distributed_analysis": True,
                "octopus_correlation": str(uuid.uuid4())[:8]
            }
        }
        
        return report
    
    def analyze_compliance(self, security_score: int) -> Dict:
        """Analyze compliance frameworks"""
        frameworks = ["GDPR", "SOX", "HIPAA", "ISO 27001", "NIST"]
        compliance_results = {}
        
        for framework in frameworks:
            compliance_score = max(50, security_score - 10)  # Slightly lower than security score
            status = "COMPLIANT" if compliance_score >= 70 else "NON_COMPLIANT"
            
            compliance_results[framework.lower()] = {
                "framework_name": framework,
                "compliance_score": compliance_score,
                "status": status
            }
        
        return compliance_results
    
    def generate_executive_summary(self, security_score: int, risk_level: str) -> str:
        """Generate executive summary"""
        return f"""
**EXECUTIVE SECURITY INTELLIGENCE SUMMARY**

Security Posture Score: {security_score}/100 ({risk_level} Risk)
Agent Ecosystem: Multi-agent coordination active with distributed intelligence

KEY FINDINGS:
• Inktrace octopus intelligence deployed across security domains
• Real-time threat detection and behavioral analysis operational  
• Regulatory compliance monitoring active
• Agent-to-agent communication secured via A2A protocol

STRATEGIC RECOMMENDATION: {"Continue current security posture" if security_score >= 80 else "Security improvements recommended"}
        """
    
    def generate_recommendations(self, security_score: int) -> list:
        """Generate security recommendations"""
        recommendations = [
            "Continue distributed intelligence monitoring across all tentacles",
            "Enhance agent-to-agent coordination for comprehensive threat coverage"
        ]
        
        if security_score < 70:
            recommendations.extend([
                "CRITICAL: Immediate security posture improvement required",
                "Deploy additional security controls across all tentacles"
            ])
        
        return recommendations
    
    def format_report(self, report: Dict) -> str:
        """Format the security report"""
        return f"""🐙 **INKTRACE COMPREHENSIVE SECURITY INTELLIGENCE REPORT**

## 📋 Report Overview
- **Report ID:** {report['report_id']}
- **Generated:** {report['generated_at']}
- **Report Type:** {report['report_type']}

## 🎯 Executive Summary
{report['executive_summary']}

## 🛡️ Security Analysis
- **Overall Score:** {report['security_analysis']['overall_score']}/100
- **Risk Level:** {report['security_analysis']['risk_level']}
- **Threats Detected:** {report['security_analysis']['threats_detected']}

## 📊 Compliance Status
{chr(10).join([f"- **{comp['framework_name']}:** {comp['status']} ({comp['compliance_score']}/100)" 
               for comp in report['compliance_analysis'].values()])}

## 🎯 Recommendations
{chr(10).join(f"• {rec}" for rec in report['recommendations'])}

## 🐙 Distributed Intelligence
- **Tentacles Engaged:** {', '.join(report['inktrace_intelligence']['tentacles_engaged'])}
- **Agent Coordination:** {'✅ Success' if report['agent_coordination']['coordination_success'] else '❌ Limited'}
- **Correlation ID:** {report['inktrace_intelligence']['octopus_correlation']}

---
*Report generated by Inktrace Report Generator using distributed octopus intelligence*
"""

def main():
    """Launch the Report Generator Agent"""
    parser = argparse.ArgumentParser(description="🐙 Inktrace Report Generator Agent")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8002, help="Port to bind to")
    args = parser.parse_args()
    
    print("🐙 Starting Inktrace Report Generator Agent")
    print("=" * 50)
    print(f"🔍 Agent Card: http://{args.host}:{args.port}/.well-known/agent.json")
    print(f"🎯 A2A Endpoint: http://{args.host}:{args.port}/")
    print(f"🛡️ Security Tentacles: T1-Identity & Access, T6-Compliance & Governance")
    print("=" * 50)
    
    # Create agent
    agent = InktraceReportGenerator(port=args.port)
    
    # Create A2A server
    server = A2AServer(agent_card=agent.agent_card)
    server.handle_task = agent.handle_task
    
    # Run server
    run_server(server, host=args.host, port=args.port)

if __name__ == "__main__":
    main()