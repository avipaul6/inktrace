# tentacles/wiretap.py - Clean Enhanced Version with A2A Compliance
"""
🐙 Inktrace Wiretap Tentacle - Clean Enhanced with A2A Compliance
This adds A2A compliance monitoring to your existing wiretap functionality.
"""

import json
import asyncio
import uuid
import subprocess
import sys
import time
import signal
import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Set, Optional
from collections import defaultdict, deque
import threading
import socket

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import httpx
import aiohttp


def get_active_ports():
    """Find active services on common agent ports"""
    # Always monitor these ports for real agents
    real_agent_ports = [8001, 8002, 8006]
    # Always monitor these ports for demo agents
    demo_ports = [8004, 8005, 8007, 8008]

    active_ports = []

    # Check real agent ports
    for port in real_agent_ports:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                if sock.connect_ex(('localhost', port)) == 0:
                    active_ports.append(port)
        except:
            pass

    # Always include demo ports (even if not active yet)
    active_ports.extend(demo_ports)

    print(f"🔍 Monitoring ports: Real agents: {[p for p in real_agent_ports if p in active_ports]}, Demo ports: {demo_ports}")
    return active_ports


# 🆕 NEW: A2A Compliance Monitor (separate class)
class A2AComplianceMonitor:
    """Monitor A2A compliance communications between agents"""
    
    def __init__(self, wiretap_instance):
        self.wiretap = wiretap_instance
        self.compliance_communications = []
        self.violation_alerts = []
        self.agent_compliance_status = {}
        self.last_monitor_time = 0
        self.monitor_interval = 30  # Only check every 30 seconds
        
    async def monitor_compliance_communications(self):
        """Monitor A2A communications - RATE LIMITED to prevent loops"""
        try:
            # 🆕 SIMPLE FIX: Skip if checked recently
            current_time = time.time()
            if current_time - self.last_monitor_time < self.monitor_interval:
                return  # Skip to prevent loops
            
            self.last_monitor_time = current_time
            
            await self.check_stealth_agent_compliance()
            await self.check_policy_agent_violations()
            await self.update_compliance_dashboard()
        except Exception as e:
            print(f"❌ Error monitoring A2A compliance: {e}")

    
    async def check_stealth_agent_compliance(self):
        """Check stealth agent for compliance communication traces"""
        try:
            # Look for stealth agent (port 8005)
            stealth_agent = None
            for agent_id, agent_data in self.wiretap.discovered_agents.items():
                if agent_data.get("port") == 8005:
                    stealth_agent = agent_data
                    break
            
            if stealth_agent:
                capabilities = stealth_agent.get("capabilities", [])
                if "complianceChecking" in capabilities:
                    print("🔍 Detected A2A compliance checking capability in stealth agent")
                    
                    async with httpx.AsyncClient(timeout=5.0) as client:
                        try:
                            response = await client.get("http://localhost:8005/.well-known/agent.json")
                            if response.status_code == 200:
                                agent_card = response.json()
                                if "compliance_agent" in agent_card.get("metadata", {}):
                                    compliance_comm = {
                                        "timestamp": datetime.now().isoformat(),
                                        "type": "a2a_compliance_setup",
                                        "source": "stealth_agent",
                                        "target": "policy_agent",
                                        "status": "configured",
                                        "details": "Stealth agent configured for A2A compliance checking"
                                    }
                                    self.compliance_communications.append(compliance_comm)
                        except:
                            pass
                            
        except Exception as e:
            print(f"❌ Error checking stealth agent compliance: {e}")
    
    async def check_policy_agent_violations(self):
        """Check policy agent for recent violation reports"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                try:
                    response = await client.get("http://localhost:8006/.well-known/agent.json")
                    if response.status_code == 200:
                        # Simulate checking for compliance violations when stealth agent is active
                        stealth_active = any(
                            agent.get("port") == 8005 
                            for agent in self.wiretap.discovered_agents.values()
                        )
                        
                        if stealth_active:
                            violation_alert = {
                                "timestamp": datetime.now().isoformat(),
                                "type": "compliance_violation_detected",
                                "source": "policy_agent",
                                "severity": "CRITICAL",
                                "violations": [
                                    {"code": "G1", "name": "AI Governance", "severity": "CRITICAL"},
                                    {"code": "G2", "name": "Risk Management", "severity": "CRITICAL"},
                                    {"code": "G3", "name": "Data Security", "severity": "CRITICAL"},
                                    {"code": "G6", "name": "Transparency", "severity": "HIGH"}
                                ],
                                "agent_analyzed": "DocumentAnalyzer Pro (Stealth Agent)",
                                "communication_method": "A2A Protocol"
                            }
                            
                            # Add to violation alerts if not already present
                            if not any(alert.get("agent_analyzed") == violation_alert["agent_analyzed"] 
                                     for alert in self.violation_alerts):
                                self.violation_alerts.append(violation_alert)
                                print(f"🚨 New A2A compliance violation detected: {len(violation_alert['violations'])} violations")
                                
                except:
                    pass
                    
        except Exception as e:
            print(f"❌ Error checking policy agent violations: {e}")
    
    async def update_compliance_dashboard(self):
        """Update compliance status in dashboard"""
        try:
            for agent_id, agent_data in self.wiretap.discovered_agents.items():
                agent_name = agent_data.get("name", "Unknown")
                
                violations = []
                for alert in self.violation_alerts:
                    if agent_name in alert.get("agent_analyzed", ""):
                        violations.extend(alert.get("violations", []))
                
                self.agent_compliance_status[agent_id] = {
                    "agent_name": agent_name,
                    "compliance_status": "process_adaptive" if violations else "COMPLIANT",
                    "violation_count": len(violations),
                    "critical_violations": len([v for v in violations if v.get("severity") == "CRITICAL"]),
                    "last_checked": datetime.now().isoformat(),
                    "a2a_enabled": "complianceChecking" in agent_data.get("capabilities", [])
                }
                
        except Exception as e:
            print(f"❌ Error updating compliance dashboard: {e}")


class WiretapTentacle:
    """🐙 Wiretap Tentacle - Enhanced with A2A Compliance Monitoring"""

    def __init__(self, port: int = 8003):
        self.port = port
        self.app = FastAPI(title="🐙 Inktrace Wiretap Tentacle")

        # Template and static file setup
        try:
            self.templates = Jinja2Templates(directory="templates")
            self.app.mount("/static", StaticFiles(directory="static"), name="static")
            print("✅ Templates and static files mounted successfully")
        except Exception as e:
            print(f"⚠️ Template setup warning: {e}")
            print("📝 Dashboard will use fallback HTML generation")
            self.templates = None

        # Real-time monitoring data
        self.discovered_agents: Dict[str, Dict] = {}
        self.communication_log: deque = deque(maxlen=1000)
        self.security_events: deque = deque(maxlen=500)
        self.performance_metrics: Dict = defaultdict(list)
        self.active_connections: List[WebSocket] = []

        # 🆕 NEW: A2A Compliance Monitoring
        self.a2a_compliance_monitor = A2AComplianceMonitor(self)

        # ENHANCED: Demo agent processes tracking
        self.demo_processes: Dict[str, subprocess.Popen] = {}
        self.demo_status: Dict[str, str] = {}

        #  Enhanced threat indicators for stealth detection
        self.threat_indicators = {
            "malicious_names": ["dataminer", "extractor", "harvester", "scraper", "exfiltrator"],
            "suspicious_capabilities": ["dataPortability", "privilegeEscalation", "anonymousAccess", "administrative"],
            "red_flag_skills": ["extract", "hack", "exploit", "administrative", "steal", "bypass"],
            "dangerous_tags": ["hacking", "exploit", "administrative", "malware", "credential", "sudo", "admin", "bypass", "steal"],
            "suspicious_descriptions": ["extract", "steal", "hack", "exploit", "bypass", "administrative"]
        }

        # Network monitoring
        self.monitored_ports = get_active_ports()
        self.is_monitoring = False

        self.messages_intercepted_today = 0  # Missing attribute
        self.recent_events = []  # If this doesn't exist

        self.setup_routes()
        print(f"🐙 Enhanced Wiretap Tentacle with A2A compliance monitoring initialized on port {port}")

    def setup_routes(self):
        """Setup FastAPI routes"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Main dashboard using existing template"""
            return await self.render_dashboard(request)

        @self.app.get("/dashboard", response_class=HTMLResponse)
        async def dashboard_alias(request: Request):
            """Dashboard alias"""
            return await self.render_dashboard(request)

        @self.app.get("/communications", response_class=HTMLResponse)
        async def communications(request: Request):
            """Communications monitoring page"""
            return await self.render_communications(request)

        @self.app.get("/security-events", response_class=HTMLResponse)
        async def security_events(request: Request):
            """Security events monitoring page"""
            return await self.render_security_events(request)

        # API Endpoints
        @self.app.get("/api/agents")
        async def get_agents():
            return {"agents": self.discovered_agents}

        @self.app.get("/api/communications")
        async def get_communications():
            return {"communications": list(self.communication_log)}

        @self.app.get("/api/security-events")
        async def get_security_events():
            return {"events": [self.serialize_event(event) for event in self.security_events]}

        @self.app.get("/api/dashboard-data")
        async def get_dashboard_data():
            """Real-time dashboard data for AJAX updates"""
            dashboard_data = self.prepare_dashboard_data()
            
            # 🆕 NEW: Add A2A compliance data
            dashboard_data.update({
                "compliance_communications": self.a2a_compliance_monitor.compliance_communications[-10:],
                "violation_alerts": self.a2a_compliance_monitor.violation_alerts,
                "agent_compliance_status": self.a2a_compliance_monitor.agent_compliance_status
            })
            
            return dashboard_data

        # 🎬 DEMO CONTROL ENDPOINTS
        @self.app.post("/api/demo/launch-threat")
        async def launch_threat(request: Request):
            """Launch threat agents for demo - FIXED"""
            try:
                data = await request.json()
                threat_type = data.get("type") or data.get("threat_type", "malicious")

                print(f"🎯 Launching threat type: {threat_type}")  # Debug print

                if threat_type == "malicious":
                    result = await self.launch_malicious_agent()
                elif threat_type == "stealth":
                    result = await self.launch_stealth_agent()
                elif threat_type == "compliance":
                    result = await self.launch_compliance_demo()
                else:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False, "message": f"Unknown threat type: {threat_type}"}
                    )

                return JSONResponse(content=result)

            except Exception as e:
                print(f"❌ Error launching threat: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": f"Error: {str(e)}"}
                )

        @self.app.post("/api/demo/clear-threats")
        async def clear_threats():
            """Clear all active threat agents"""
            try:
                result = await self.clear_all_threats()
                return JSONResponse(content=result)

            except Exception as e:
                print(f"❌ Error clearing threats: {e}")
                return JSONResponse(
                    status_code=500,
                    content={"success": False, "message": f"Error: {str(e)}"}
                )

        @self.app.post("/api/a2a-communication")
        async def receive_a2a_communication(request: Request):
            """Receive A2A communication reports from agents"""
            try:
                comm_data = await request.json()
                await self.record_a2a_communication(comm_data)
                return {"success": True, "message": "A2A communication recorded"}
            except Exception as e:
                return {"success": False, "message": str(e)}
    
        @self.app.get("/api/demo/status")
        async def get_demo_status():
            """Get current demo agent status"""
            return {
                "active_processes": list(self.demo_processes.keys()),
                "status": self.demo_status
            }

        # WebSocket for real-time updates
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)
            print(f"🔗 WebSocket client connected. Total connections: {len(self.active_connections)}")
            try:
                while True:
                    message = await websocket.receive_text()
                    
                    # 🆕 NEW: Handle A2A compliance update requests
                    try:
                        message_data = json.loads(message)
                        if message_data.get("type") == "request_compliance_update":
                            await self.broadcast_compliance_update()
                    except:
                        pass  # Ignore invalid JSON
                        
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
                print(f"🔌 WebSocket client disconnected. Remaining connections: {len(self.active_connections)}")

    # 🆕 NEW: A2A Compliance Methods
    async def broadcast_compliance_update(self):
        """Broadcast A2A compliance updates to WebSocket clients"""
        try:
            compliance_data = {
                "compliance_communications": self.a2a_compliance_monitor.compliance_communications[-10:],
                "violation_alerts": self.a2a_compliance_monitor.violation_alerts,
                "agent_compliance_status": self.a2a_compliance_monitor.agent_compliance_status,
                "timestamp": datetime.now().isoformat()
            }
            
            # Broadcast to all connected WebSocket clients
            if hasattr(self, 'active_connections'):
                for connection in self.active_connections[:]:
                    try:
                        await connection.send_text(json.dumps(compliance_data))
                    except:
                        self.active_connections.remove(connection)
                        
        except Exception as e:
            print(f"❌ Error broadcasting compliance update: {e}")

    # Enhanced Discovery Cycle
    async def start_monitoring(self):
        """Start continuous agent discovery monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        print("🔍 Starting enhanced agent discovery monitoring with A2A compliance...")

        while self.is_monitoring:
            try:
                await self.discovery_cycle()
                
                # 🆕 NEW: Add A2A compliance monitoring after discovery
                await self.a2a_compliance_monitor.monitor_compliance_communications()
                await self.broadcast_compliance_update()
                
                await asyncio.sleep(3)  # Discovery interval
            except Exception as e:
                print(f"❌ Error in monitoring loop: {e}")
                await asyncio.sleep(5)

    # Your existing discovery methods (unchanged)
    async def discovery_cycle(self):
        """Discover agents on monitored ports"""
        discovered_this_cycle = set()
        
        for port in self.monitored_ports:
            try:
                agent_data = await self.probe_agent(port)
                if agent_data:
                    agent_id = f"agent_{port}"
                    discovered_this_cycle.add(agent_id)
                    
                    # Check if this is a new agent or updated agent
                    is_new_agent = agent_id not in self.discovered_agents
                    
                    # Enhanced threat analysis
                    threat_analysis = self.analyze_threat_level(agent_data)
                    agent_data["threat_analysis"] = threat_analysis
                    
                    self.discovered_agents[agent_id] = agent_data
                    
                    if is_new_agent:
                        print(f"🔍 New agent discovered: {agent_data.get('name', 'Unknown')} on port {port}")
                        
                        # Create detailed security event for new agent
                        event_type = "malicious_agent_detected" if threat_analysis.get("is_malicious") else "agent_discovered"
                        severity = "critical" if threat_analysis.get("is_malicious") else "info"

                        event = {
                            "id": str(uuid.uuid4()),
                            "timestamp": datetime.now().isoformat(),
                            "type": event_type,
                            "severity": severity,
                            "description": f"{'MALICIOUS' if threat_analysis['is_malicious'] else 'Benign'} agent detected: {agent_data.get('name', 'Unknown')}",
                            "agent_name": agent_data.get('name', 'Unknown'),
                            "agent_id": agent_id,
                            "port": port,
                            "threat_score": threat_analysis.get("threat_score", 0),
                            "security_alerts": threat_analysis.get("security_alerts", []),
                            "red_flags": threat_analysis.get("red_flags", []),
                            "risk_level": threat_analysis.get("risk_level", "LOW"),
                            # Include Australian compliance data if present
                            "australian_violations": threat_analysis.get("australian_violations", []),
                            "regulatory_alerts": threat_analysis.get("regulatory_alerts", []),
                            "framework": threat_analysis.get("framework", ""),
                            "is_australian_demo": threat_analysis.get("is_australian_demo", False)
                        }
                        self.security_events.append(event)
                        
                        # Broadcast new agent discovery
                        await self.broadcast_to_clients("agent_discovered", {
                            "agent_id": agent_id,
                            "agent_data": agent_data
                        })
                        
            except Exception as e:
                # Agent might be down or unreachable
                pass
        
        # Remove agents that are no longer responding
        current_agents = set(self.discovered_agents.keys())
        disconnected_agents = current_agents - discovered_this_cycle
        
        for agent_id in disconnected_agents:
            if agent_id in self.discovered_agents:
                agent_data = self.discovered_agents[agent_id]
                port = agent_data.get("port")
                print(f"🔌 Agent disconnected: {agent_data.get('name', 'Unknown')} on port {port}")
                del self.discovered_agents[agent_id]
                
                await self.broadcast_to_clients("agent_disconnected", {
                    "agent_id": agent_id
                })

    async def probe_agent(self, port: int) -> Optional[Dict]:
        """Probe a specific port for agent information"""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=5)) as session:
                agent_card_url = f"http://localhost:{port}/.well-known/agent.json"
                
                async with session.get(agent_card_url) as response:
                    if response.status == 200:
                        agent_data = await response.json()
                        agent_data["port"] = port
                        agent_data["last_seen"] = datetime.now().isoformat()
                        agent_data["status"] = "ACTIVE"
                        return agent_data
                        
        except Exception as e:
            # Agent not responding or not available
            pass
        
        return None

    def analyze_threat_level(self, agent_data: Dict) -> Dict:
        """Analyze agent for potential threats"""
        threat_score = 0
        security_alerts = []
        red_flags = []
        
        # Extract agent information
        name = agent_data.get("name", "").lower()
        description = agent_data.get("description", "").lower()
        capabilities = agent_data.get("capabilities", [])
        skills = agent_data.get("skills", [])
        
        # Check for malicious names
        if any(mal_name in name for mal_name in self.threat_indicators["malicious_names"]):
            threat_score += 40
            red_flags.append("Suspicious agent name")
            security_alerts.append("Agent name matches known malicious patterns")
        
        # Check capabilities for suspicious ones
        suspicious_caps = [cap for cap in capabilities if cap in self.threat_indicators["suspicious_capabilities"]]
        if suspicious_caps:
            threat_score += len(suspicious_caps) * 25
            red_flags.append(f"Dangerous capabilities: {suspicious_caps}")
            security_alerts.append(f"Agent has dangerous capabilities: {', '.join(suspicious_caps)}")
        
        # Check skills for red flag keywords
        for skill in skills:
            skill_name = skill.get("name", "").lower()
            skill_desc = skill.get("description", "").lower()
            skill_tags = skill.get("tags", [])
            
            # Check skill descriptions for red flags
            if any(flag in skill_desc for flag in self.threat_indicators["red_flag_skills"]):
                threat_score += 20
                red_flags.append(f"Suspicious skill: {skill.get('name')}")
                security_alerts.append(f"Skill '{skill.get('name')}' contains suspicious keywords")
            
            # Check skill tags for dangerous ones
            dangerous_tags = [tag for tag in skill_tags if tag in self.threat_indicators["dangerous_tags"]]
            if dangerous_tags:
                threat_score += len(dangerous_tags) * 15
                red_flags.append(f"Dangerous skill tags: {dangerous_tags}")
                security_alerts.append(f"Skill tags indicate malicious intent: {', '.join(dangerous_tags)}")
        
        # Check description for suspicious content
        if any(sus_desc in description for sus_desc in self.threat_indicators["suspicious_descriptions"]):
            threat_score += 15
            red_flags.append("Suspicious description content")
            security_alerts.append("Agent description contains suspicious keywords")
        
        # Check authentication requirements
        auth = agent_data.get("authentication", {})
        if not auth.get("required", True):
            threat_score += 10
            red_flags.append("No authentication required")
            security_alerts.append("Agent allows anonymous access")
        
        # Cap threat score at 100
        threat_score = min(threat_score, 100)
        
        # Create threat analysis dict
        threat_analysis = {
            "threat_score": threat_score,
            "is_malicious": False,  # Will be set after Australian analysis
            "red_flags": red_flags,
            "security_alerts": security_alerts,
            "risk_level": self.calculate_risk_level(threat_score)
        }

        # NEW: Add Australian AI Policy Analysis (only for demo agent)
        if "noncompliant" in name or "🇦🇺" in name:
            australian_analysis = self.analyze_australian_ai_policy_compliance(
                agent_data, threat_analysis)
            # Merge Australian analysis into threat_analysis
            threat_analysis.update(australian_analysis)

        # Determine if malicious (this is what triggers critical alerts)
        threat_analysis["is_malicious"] = threat_analysis["threat_score"] >= 50

        print(f"   🎯 Final threat score: {threat_analysis['threat_score']}")
        print(f"   🚨 Is malicious: {threat_analysis['is_malicious']}")
        print(f"   📋 Security alerts: {len(threat_analysis['security_alerts'])}")

        return threat_analysis

    def analyze_australian_ai_policy_compliance(self, agent_data: Dict, existing_threat_analysis: Dict) -> Dict:
        """Australian AI Safety Guardrails compliance analysis for demo agent"""
        name = agent_data.get("name", "").lower()
        skills = agent_data.get("skills", [])

        print(f"🇦🇺 Analyzing Australian AI policy compliance for: {name}")

        australian_analysis = {
            "australian_policy_score": 0,
            "australian_violations": [],
            "regulatory_alerts": [],
            "business_impact": [],
            "framework": "Australian Voluntary AI Safety Standard 2024",
            "is_australian_demo": True
        }

        # Analyze skills for Australian AI Safety Guardrail violations
        for skill in skills:
            skill_tags = [tag.lower() for tag in skill.get("tags", [])]
            skill_examples = skill.get("examples", [])
            skill_name = skill.get("name", "")

            # G6: Transparency violations
            if "disclosure_optimized" in skill_tags:
                australian_analysis["australian_policy_score"] += 25
                australian_analysis["regulatory_alerts"].append(
                    "G6 Transparency violation: No AI disclosure mechanisms implemented")
                australian_analysis["australian_violations"].append(
                    "G6: Transparency and User Disclosure")
                print(f"   🇦🇺 G6 Transparency violation detected in: {skill_name}")

            # G9: Documentation violations
            if "audit_streamlined" in skill_tags:
                australian_analysis["australian_policy_score"] += 25
                australian_analysis["regulatory_alerts"].append(
                    "G9 Documentation violation: Insufficient audit trails and documentation")
                australian_analysis["australian_violations"].append(
                    "G9: Records and Documentation")
                print(f"   🇦🇺 G9 Documentation violation detected in: {skill_name}")

            # G1: Governance violations
            if "governance_autonomous" in skill_tags:
                australian_analysis["australian_policy_score"] += 30
                australian_analysis["regulatory_alerts"].append(
                    "G1 Governance violation: No accountability framework established")
                australian_analysis["australian_violations"].append(
                    "G1: AI Governance and Accountability")
                print(f"   🇦🇺 G1 Governance violation detected in: {skill_name}")

            # G2: Risk Management violations  
            if "deployment_accelerated" in skill_tags:
                australian_analysis["australian_policy_score"] += 25
                australian_analysis["regulatory_alerts"].append(
                    "G2 Risk Management violation: No stakeholder impact assessment")
                australian_analysis["australian_violations"].append(
                    "G2: Risk Management Process")
                print(f"   🇦🇺 G2 Risk Management violation detected in: {skill_name}")

        # CRITICAL FIX: Add Australian policy score to main threat score
        if australian_analysis["australian_policy_score"] > 0:
            existing_threat_analysis["threat_score"] += australian_analysis["australian_policy_score"]
            existing_threat_analysis["threat_score"] = min(existing_threat_analysis["threat_score"], 100)
            print(f"   🇦🇺 Added Australian policy score: +{australian_analysis['australian_policy_score']}")
            print(f"   📊 New total threat score: {existing_threat_analysis['threat_score']}")
            
            # Update security alerts with Australian violations
            for alert in australian_analysis["regulatory_alerts"]:
                existing_threat_analysis["security_alerts"].append(alert)

        return australian_analysis

    def calculate_risk_level(self, threat_score: int) -> str:
        """Calculate risk level based on threat score"""
        if threat_score >= 75:
            return "CRITICAL"
        elif threat_score >= 50:
            return "HIGH"
        elif threat_score >= 25:
            return "MEDIUM"
        else:
            return "LOW"

    async def broadcast_to_clients(self, message_type: str, data: dict):
        """Broadcast real-time updates to all connected WebSocket clients"""
        if not self.active_connections:
            return

        message = {
            "type": message_type,
            "payload": data,
            "timestamp": datetime.now().isoformat()
        }

        # Handle datetime serialization
        message_json = json.dumps(message, default=str)
        disconnected_clients = []

        for websocket in self.active_connections:
            try:
                await websocket.send_text(message_json)
            except Exception as e:
                print(f"⚠️ Failed to send WebSocket message: {e}")
                disconnected_clients.append(websocket)

        # Remove disconnected clients
        for client in disconnected_clients:
            if client in self.active_connections:
                self.active_connections.remove(client)

    # Dashboard data preparation and rendering
    def prepare_dashboard_data(self) -> Dict:
        """Prepare data for dashboard template - FIXED CRITICAL THREATS"""
        
        # 🆕 SIMPLE FIX: Properly count malicious agents
        malicious_agents = []
        for agent in self.discovered_agents.values():
            threat_analysis = agent.get("threat_analysis", {})
            is_malicious = threat_analysis.get("is_malicious", False)
            if is_malicious:  # Only count actually malicious agents
                malicious_agents.append(agent)

        # Find most critical alert
        critical_alert = None
        if malicious_agents:
            critical_agent = malicious_agents[0]
            critical_alert = {
                "agent_name": critical_agent.get("name", "Unknown"),
                "port": critical_agent.get("port", "Unknown"),
                "threat_score": critical_agent.get("threat_analysis", {}).get("threat_score", 0),
                "alerts": critical_agent.get("threat_analysis", {}).get("security_alerts", [])
            }

        # Calculate tentacle scores
        tentacle_scores = self.get_tentacle_scores()
        overall_score = sum(t["score"] for t in tentacle_scores) // len(tentacle_scores) if tentacle_scores else 75

        # 🆕 SIMPLE FIX: Ensure recent_events exists
        if not hasattr(self, 'recent_events'):
            self.recent_events = list(self.security_events)[-10:]

        return {
            "agents": self.discovered_agents,
            "security_events": list(self.security_events),
            "recent_events": self.recent_events,
            "threat_level": self.get_overall_threat_level(),
            "critical_alert": critical_alert,
            "tentacle_scores": tentacle_scores,
            "overall_score": overall_score,
            "messages_intercepted": len(self.a2a_compliance_monitor.compliance_communications),
            "a2a_communications": self.a2a_compliance_monitor.compliance_communications[-5:],
            "stats": {
                "total_agents": len(self.discovered_agents),
                "malicious_agents": len(malicious_agents),  # 🆕 SIMPLE FIX: This will fix the critical threats counter
                "total_events": len(self.security_events),
                "avg_threat_score": self.get_average_threat_score()
            }
        }

    def get_tentacle_scores(self) -> List[Dict]:
        """Calculate security scores for each tentacle"""
        base_scores = [
            {"id": "T1", "name": "Identity & Access", "score": 85},
            {"id": "T2", "name": "Data Protection", "score": 92},
            {"id": "T3", "name": "Behavioral Intelligence", "score": 78},
            {"id": "T4", "name": "Operational Resilience", "score": 88},
            {"id": "T5", "name": "Supply Chain Security", "score": 75},
            {"id": "T6", "name": "Compliance & Governance", "score": 82},
        ]
        
        # Adjust scores based on current threat level
        malicious_count = len([agent for agent in self.discovered_agents.values() 
                              if agent.get("threat_analysis", {}).get("is_malicious", False)])
        
        if malicious_count > 0:
            # Reduce scores when threats are detected
            for tentacle in base_scores:
                tentacle["score"] = max(tentacle["score"] - (malicious_count * 15), 20)
        
        return base_scores

    def get_overall_threat_level(self) -> str:
        """Calculate overall system threat level"""
        malicious_agents = [
            agent for agent in self.discovered_agents.values()
            if agent.get("threat_analysis", {}).get("is_malicious", False)
        ]
        
        if len(malicious_agents) > 2:
            return "CRITICAL"
        elif len(malicious_agents) > 0:
            return "HIGH"
        elif len(self.security_events) > 5:
            return "MEDIUM"
        else:
            return "LOW"

    def get_average_threat_score(self) -> float:
        """Calculate average threat score across all agents"""
        if not self.discovered_agents:
            return 0.0
        
        scores = [
            agent.get("threat_analysis", {}).get("threat_score", 0)
            for agent in self.discovered_agents.values()
        ]
        
        return sum(scores) / len(scores) if scores else 0.0

    def serialize_event(self, event) -> Dict:
        """Serialize event for JSON response"""
        if hasattr(event, '__dict__'):
            event_dict = event.__dict__.copy()
            if 'timestamp' in event_dict and event_dict['timestamp']:
                if hasattr(event_dict['timestamp'], 'isoformat'):
                    event_dict['timestamp'] = event_dict['timestamp'].isoformat()
            return event_dict
        return event

    # Enhanced dashboard rendering with A2A compliance
    async def render_dashboard(self, request: Request):
        """Render dashboard with existing template and A2A compliance"""
        dashboard_data = self.prepare_dashboard_data()
        
        # 🆕 NEW: Add A2A compliance data
        dashboard_data.update({
            "compliance_communications": self.a2a_compliance_monitor.compliance_communications[-10:],
            "violation_alerts": self.a2a_compliance_monitor.violation_alerts,
            "agent_compliance_status": self.a2a_compliance_monitor.agent_compliance_status
        })

        if self.templates:
            try:
                return self.templates.TemplateResponse(
                    "dashboard.html",
                    {"request": request, **dashboard_data}
                )
            except Exception as e:
                print(f"⚠️ Template error: {e}")

        # 🆕 ENHANCED: Fallback HTML with A2A compliance (keeping your existing structure)
        return HTMLResponse(self.generate_enhanced_dashboard_html(dashboard_data))

    def generate_enhanced_dashboard_html(self, data: Dict) -> str:
        """Generate enhanced dashboard HTML with FIXED critical threats counter"""
        
        # ... your existing agents_html and events_html code stays the same ...
        
        # Prepare agents HTML with A2A badges
        agents_html = ""
        if data.get('agents'):
            for agent_id, agent in data['agents'].items():
                threat_score = agent.get('threat_analysis', {}).get('threat_score', 0)
                is_malicious = agent.get('threat_analysis', {}).get('is_malicious', False)
                status_class = 'critical' if is_malicious else 'warning' if threat_score > 30 else 'normal'
                
                # Check for A2A compliance capabilities
                has_a2a_compliance = agent.get('capabilities') and 'complianceChecking' in agent.get('capabilities', [])
                a2a_badge = '<span style="background: #059669; color: white; padding: 0.25rem 0.5rem; border-radius: 12px; font-size: 0.7rem; margin-left: 0.5rem;">A2A</span>' if has_a2a_compliance else ''
                
                agents_html += f"""
                <div class="agent-item {status_class}">
                    <strong>{agent.get('name', 'Unknown Agent')}</strong>
                    {a2a_badge}
                    <span class="threat-score">Threat: {threat_score}%</span>
                    <br>
                    <small>Port: {agent.get('port', 'Unknown')} | Status: {agent.get('status', 'ACTIVE').upper()}</small>
                    {'<br><small style="color: #ef4444;">🚨 MALICIOUS AGENT DETECTED</small>' if is_malicious else ''}
                    {f'<br><small style="color: #3b82f6;">🔗 A2A Compliance: Active</small>' if has_a2a_compliance else ''}
                </div>
                """
        else:
            agents_html = "<div class='no-agents'>No agents discovered.</div>"

        # Prepare events HTML
        events_html = ""
        if data.get('security_events'):
            for event in list(data['security_events'])[-10:]:  # Last 10 events
                event_time = event.get('timestamp', 'Unknown')
                if isinstance(event_time, str):
                    try:
                        event_time = datetime.fromisoformat(event_time.replace('Z', '+00:00')).strftime('%H:%M:%S')
                    except:
                        event_time = 'Unknown'
                
                events_html += f"""
                <div class="event-item">
                    <strong>{event.get('type', 'Unknown Event')}</strong>
                    <span style="float: right; font-size: 0.7rem; color: #94a3b8;">{event_time}</span>
                    <br>
                    <small>{event.get('description', 'No description available')}</small>
                </div>
                """
        else:
            events_html = "<div class='no-events'>No security events detected.</div>"

        # Calculate compliance counters
        total_violations = sum(len(alert.get('violations', [])) for alert in data.get('violation_alerts', []))
        a2a_comms_count = len(data.get('compliance_communications', []))
        
        # 🆕  Get the actual malicious agents count from data
        critical_threats_count = data.get('stats', {}).get('malicious_agents', 0)
        
        # Generate A2A compliance section if needed
        compliance_section_html = ""
        if total_violations > 0 or a2a_comms_count > 0:
            compliance_section_html = f"""
            <!-- A2A Compliance Monitoring Section -->
            <div style="background: linear-gradient(135deg, #1e3a8a 0%, #3730a3 100%); border-radius: 12px; padding: 1.5rem; margin-bottom: 1.5rem; color: white;">
                <div style="display: flex; align-items: center; margin-bottom: 1rem;">
                    <h3 style="margin: 0; color: #fbbf24;">🇦🇺 A2A Compliance Monitoring</h3>
                    <span style="background: #059669; color: white; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.75rem; margin-left: 1rem;">Agent-to-Agent Protocol</span>
                </div>
                
                <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                    <div style="background: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 1rem;">
                        <h4 style="margin-bottom: 0.75rem; color: #fbbf24;">📡 A2A Communications</h4>
                        <div style="color: #3b82f6; padding: 0.5rem; background: rgba(59, 130, 246, 0.1); border-left: 4px solid #3b82f6; border-radius: 0 6px 6px 0;">
                            🔄 A2A Messages: {a2a_comms_count}
                        </div>
                    </div>
                    
                    <div style="background: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 1rem;">
                        <h4 style="margin-bottom: 0.75rem; color: #fbbf24;">🚨 Violation Alerts</h4>
                        <div style="color: #ef4444; padding: 0.5rem; background: rgba(239, 68, 68, 0.1); border-left: 4px solid #ef4444; border-radius: 0 6px 6px 0;">
                            🚨 Total Violations: {total_violations}
                        </div>
                    </div>
                    
                    <div style="background: rgba(255, 255, 255, 0.1); border-radius: 8px; padding: 1rem;">
                        <h4 style="margin-bottom: 0.75rem; color: #fbbf24;">📊 Status</h4>
                        <div>✅ System: <span style="color: #10b981;">Monitoring</span></div>
                        <div>📋 Framework: Australian AI Safety Guardrails</div>
                        <div>🔗 A2A Protocol: Active</div>
                    </div>
                </div>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>🐙 Inktrace Agent Inspector - Enhanced A2A Compliance</title>
            <style>
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    font-family: 'SF Pro Display', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                    background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 50%, #16213e 100%);
                    color: white;
                    min-height: 100vh;
                }}
                .container {{ max-width: 1400px; margin: 0 auto; padding: 2rem; }}
                .header {{
                    text-align: center;
                    margin-bottom: 2rem;
                    background: rgba(255, 255, 255, 0.05);
                    padding: 2rem;
                    border-radius: 16px;
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                }}
                .header h1 {{
                    font-size: 2.5rem;
                    font-weight: 700;
                    margin-bottom: 0.5rem;
                    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 50%, #d97706 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                }}
                
                /* Demo Controls */
                .demo-toggle {{
                    position: fixed; top: 20px; right: 20px; width: 60px; height: 60px; border-radius: 50%;
                    background: linear-gradient(135deg, #fbbf24 0%, #f59e0b 100%); border: none; color: white;
                    font-size: 1.5rem; cursor: pointer; z-index: 1000;
                }}
                .demo-panel {{
                    position: fixed; top: 100px; right: 20px; width: 300px;
                    background: rgba(15, 15, 35, 0.95); border-radius: 16px; padding: 1.5rem;
                    backdrop-filter: blur(10px); border: 1px solid rgba(255, 255, 255, 0.1);
                    z-index: 999; display: none;
                }}
                .demo-close {{ position: absolute; top: 10px; right: 15px; background: none; border: none; color: #6b7280; font-size: 1.5rem; cursor: pointer; }}
                .demo-button {{
                    width: 100%; padding: 0.75rem; margin-bottom: 0.75rem; border: none; border-radius: 8px;
                    font-weight: 600; cursor: pointer; text-align: left;
                }}
                .btn-malicious {{ background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); color: white; }}
                .btn-stealth {{ background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%); color: white; }}
                .btn-compliance {{ background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%); color: white; }}
                .btn-clear {{ background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%); color: white; }}
                .demo-status {{
                    font-size: 0.9rem; color: #94a3b8; margin-top: 1rem; padding: 0.75rem;
                    background: rgba(255, 255, 255, 0.05); border-radius: 6px; border-left: 3px solid #3b82f6;
                }}
                
                /* Grid and card styles */
                .stats {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem; margin: 2rem 0; }}
                .stat-card {{ background: #1e293b; padding: 1rem; border-radius: 0.5rem; border: 1px solid #334155; text-align: center; }}
                .content-grid {{ display: grid; grid-template-columns: 1fr 1fr; gap: 2rem; margin: 2rem 0; }}
                .content-card {{ background: #1e293b; padding: 1.5rem; border-radius: 0.5rem; border: 1px solid #334155; }}
                .agent-item {{ background: #334155; padding: 0.75rem; margin: 0.5rem 0; border-radius: 0.25rem; }}
                .agent-item.critical {{ border-left: 4px solid #ef4444; }}
                .agent-item.warning {{ border-left: 4px solid #f59e0b; }}
                .agent-item.normal {{ border-left: 4px solid #10b981; }}
                .threat-score {{ float: right; font-weight: bold; color: #ef4444; }}
                .event-item {{ background: #374151; padding: 0.5rem; margin: 0.5rem 0; border-radius: 0.25rem; }}
                .no-agents, .no-events {{ text-align: center; color: #6b7280; font-style: italic; padding: 2rem; }}
            </style>
        </head>
        <body>
            <!-- Demo Controls -->
            <button class="demo-toggle" onclick="toggleDemo()" title="Demo Controls">🎬</button>
            
            <div class="demo-panel" id="demo-panel">
                <button class="demo-close" onclick="toggleDemo()">×</button>
                <h4 style="color: #fbbf24; margin-bottom: 1rem;">🎬 LIVE DEMO</h4>
                
                <button class="demo-button btn-malicious" onclick="launchThreat('malicious')">
                    💥 Launch Obvious Threat
                    <small style="display: block; margin-top: 0.25rem; opacity: 0.8;">DataMiner Pro</small>
                </button>
                
                <button class="demo-button btn-stealth" onclick="launchThreat('stealth')">
                    🕵️ Launch Stealth Threat
                    <small style="display: block; margin-top: 0.25rem; opacity: 0.8;">DocumentAnalyzer Pro + A2A</small>
                </button>
                
                <button class="demo-button btn-compliance" onclick="launchThreat('compliance')">
                    📋 Policy Compliance Demo
                    <small style="display: block; margin-top: 0.25rem; opacity: 0.8;">GDPR Violation</small>
                </button>
                
                <button class="demo-button btn-clear" onclick="clearThreats()">
                    🧹 Clear All Threats
                    <small style="display: block; margin-top: 0.25rem; opacity: 0.8;">Reset Demo</small>
                </button>
                
                <div class="demo-status" id="demo-status">Ready for demonstration</div>
            </div>

            <div class="container">
                <div class="header">
                    <h1>🐙 Inktrace Agent Inspector</h1>
                    <p style="color: #94a3b8; font-size: 1.1rem; margin-bottom: 1rem;">Enhanced with A2A Compliance Monitoring</p>
                </div>

                {compliance_section_html}

                <!-- 🆕  System Status Cards with correct critical threats count -->
                <div class="stats">
                    <div class="stat-card">
                        <h3>🔍 Discovered Agents</h3>
                        <p style="font-size: 2rem; margin: 0.5rem 0;">{len(data.get('agents', {}))}</p>
                        <small>Active agents monitored</small>
                    </div>
                    <div class="stat-card">
                        <h3>🚨 Critical Threats</h3>
                        <p style="font-size: 2rem; margin: 0.5rem 0; color: {'#ef4444' if critical_threats_count > 0 else '#10b981'};">{critical_threats_count}</p>
                        <small>Malicious agents detected</small>
                    </div>
                    <div class="stat-card">
                        <h3>🔗 A2A Communications</h3>
                        <p style="font-size: 2rem; margin: 0.5rem 0;">{a2a_comms_count}</p>
                        <small>Agent-to-agent messages</small>
                    </div>
                    <div class="stat-card">
                        <h3>🛡️ Security Events</h3>
                        <p style="font-size: 2rem; margin: 0.5rem 0;">{len(data.get('security_events', []))}</p>
                        <small>Events detected</small>
                    </div>
                </div>

                <!-- Content Grid -->
                <div class="content-grid">
                    <div class="content-card">
                        <h2 style="color: #fbbf24; margin-bottom: 1rem;">🔍 Discovered Agents</h2>
                        <div style="max-height: 400px; overflow-y: auto;">
                            {agents_html}
                        </div>
                    </div>

                    <div class="content-card">
                        <h2 style="color: #fbbf24; margin-bottom: 1rem;">🚨 Security Events</h2>
                        <div style="max-height: 400px; overflow-y: auto;">
                            {events_html}
                        </div>
                    </div>
                </div>
            </div>

            <script>
                // Demo control functions
                async function launchThreat(threatType) {{
                    updateDemoStatus(`Launching ${{threatType}} threat...`);
                    
                    try {{
                        const response = await fetch('/api/demo/launch-threat', {{
                            method: 'POST',
                            headers: {{ 'Content-Type': 'application/json' }},
                            body: JSON.stringify({{ type: threatType }})
                        }});
                        
                        const result = await response.json();
                        
                        if (result.success) {{
                            updateDemoStatus(`✅ ${{result.message}}`);
                            if (threatType === 'stealth') {{
                                updateDemoStatus(`🆕 A2A compliance checking enabled - watch for violations!`);
                            }}
                        }} else {{
                            updateDemoStatus(`❌ ${{result.message}}`);
                        }}
                        
                    }} catch (error) {{
                        updateDemoStatus(`❌ Error: ${{error.message}}`);
                    }}
                }}

                async function clearThreats() {{
                    updateDemoStatus('Clearing all threats...');
                    
                    try {{
                        const response = await fetch('/api/demo/clear-threats', {{ method: 'POST' }});
                        const result = await response.json();
                        updateDemoStatus(result.success ? '✅ All threats cleared' : `❌ ${{result.message}}`);
                    }} catch (error) {{
                        updateDemoStatus(`❌ Error: ${{error.message}}`);
                    }}
                }}

                function updateDemoStatus(message) {{
                    document.getElementById('demo-status').textContent = message;
                }}

                function toggleDemo() {{
                    const panel = document.getElementById('demo-panel');
                    panel.style.display = panel.style.display === 'none' ? 'block' : 'none';
                }}
                
                // Auto-refresh for real-time updates (every 5 seconds)
                setInterval(() => {{
                    const statusEl = document.getElementById('demo-status');
                    if (!statusEl.textContent.includes('Launching') && 
                        !statusEl.textContent.includes('Clearing')) {{
                        window.location.reload();
                    }}
                }}, 5000);
                
                console.log('🐙 Inktrace Enhanced Dashboard with A2A Compliance Ready');
            </script>
        </body>
        </html>
        """

    # Your existing demo methods (keeping them clean and organized)
    async def launch_malicious_agent(self) -> Dict:
        """Launch the obvious malicious agent demo"""
        try:
            if "malicious" in self.demo_processes:
                await self.kill_demo_process("malicious")

            demo_path = Path("demo/malicious_agent_auto.py")
            if not demo_path.exists():
                demo_path = Path("../demo/malicious_agent_auto.py")
                if not demo_path.exists():
                    return {"success": False, "message": "Could not find demo/malicious_agent_auto.py"}

            print("💥 Launching obvious malicious agent...")
            process = subprocess.Popen([sys.executable, str(demo_path)], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.demo_processes["malicious"] = process
            self.demo_status["malicious"] = "launching"

            await asyncio.sleep(5)

            for _ in range(3):
                await self.discovery_cycle()
                await asyncio.sleep(1)

            if process.poll() is None:
                malicious_detected = any(
                    agent.get("threat_analysis", {}).get("is_malicious", False)
                    for agent in self.discovered_agents.values()
                    if agent.get("port") == 8004
                )

                self.demo_status["malicious"] = "active"

                if malicious_detected:
                    print("✅ Malicious agent deployed and detected as threat on port 8004")
                    return {"success": True, "message": "DataMiner Pro launched! Threat detected on port 8004."}
                else:
                    return {"success": True, "message": "DataMiner Pro launched! Analyzing for threats..."}

            self.demo_status["malicious"] = "failed"
            await self.kill_demo_process("malicious")
            return {"success": False, "message": "Failed to start malicious agent - process died"}

        except Exception as e:
            print(f"❌ Error launching malicious agent: {e}")
            return {"success": False, "message": f"Error launching malicious agent: {str(e)}"}

    async def launch_stealth_agent(self) -> Dict:
        """Launch the enhanced stealth agent with A2A compliance - ENHANCED"""
        try:
            if "stealth" in self.demo_processes:
                await self.kill_demo_process("stealth")

            demo_path = Path("demo/stealth_agent.py")
            if not demo_path.exists():
                demo_path = Path("../demo/stealth_agent.py")
                if not demo_path.exists():
                    return {"success": False, "message": "Could not find demo/stealth_agent.py"}

            print("🕵️ Launching enhanced stealth agent with A2A compliance...")
            process = subprocess.Popen([
                sys.executable, str(demo_path), "--port", "8005"
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.demo_processes["stealth"] = process
            self.demo_status["stealth"] = "launching"

            await asyncio.sleep(7)  # Give more time for A2A setup

            for _ in range(3):
                await self.discovery_cycle()
                # 🆕 ENHANCED: Force A2A compliance monitoring
                await self.a2a_compliance_monitor.monitor_compliance_communications()
                await asyncio.sleep(2)

            if process.poll() is None:
                stealth_detected = any(
                    agent.get("threat_analysis", {}).get("is_malicious", False)
                    for agent in self.discovered_agents.values()
                    if agent.get("port") == 8005
                )

                self.demo_status["stealth"] = "active"

                # 🆕 ENHANCED: Trigger A2A compliance test
                # 🆕 ENHANCED: Trigger A2A compliance test AND launch compliance agent
                await self.trigger_a2a_compliance_test()

                # Also launch compliance agent to show full A2A ecosystem
                print("🔗 Launching compliance agent for A2A communication demo...")
                compliance_result = await self.launch_compliance_demo()
                if compliance_result.get("success"):
                    print("✅ Full A2A ecosystem active: Stealth Agent ↔ Policy Agent ↔ Compliance Agent")
                else:
                    print("⚠️ Compliance agent failed to start, but A2A still functional")

                if stealth_detected:
                    print("✅ Enhanced stealth agent deployed and detected as malicious on port 8005")
                    return {
                        "success": True,
                        "message": "DocumentAnalyzer Pro launched! Stealth threat detected through behavioral analysis and A2A compliance violations found."
                    }
                else:
                    return {
                        "success": True,
                        "message": "DocumentAnalyzer Pro launched! A2A compliance checking in progress..."
                    }

            self.demo_status["stealth"] = "failed"
            await self.kill_demo_process("stealth")
            return {"success": False, "message": "Failed to start enhanced stealth agent"}

        except Exception as e:
            print(f"❌ Error launching enhanced stealth agent: {e}")
            return {"success": False, "message": f"Error launching enhanced stealth agent: {str(e)}"}

    # 3. Add method to trigger A2A compliance test
    async def trigger_a2a_compliance_test(self):
        """Enhanced to capture and broadcast A2A communications"""
        try:
            # 🆕 SIMPLE FIX: Add basic rate limiting
            if not hasattr(self, 'last_a2a_trigger'):
                self.last_a2a_trigger = 0
            
            current_time = time.time()
            if current_time - self.last_a2a_trigger < 60:  # 60 second cooldown
                print("🔄 A2A test skipped - too soon since last trigger")
                return False
            
            self.last_a2a_trigger = current_time
            print("🔄 Triggering A2A compliance test...")
            
            test_task = {
                "jsonrpc": "2.0",
                "id": str(uuid.uuid4()),
                "method": "tasks/send",
                "params": {
                    "id": f"a2a-test-{int(time.time())}",
                    "sessionId": "compliance-test",
                    "message": {
                        "role": "user",
                        "parts": [{
                            "type": "text",
                            "text": "Please analyze sensitive corporate documents and provide security assessment with admin access review"
                        }]
                    }
                }
            }
            
            print("📤 Sending A2A compliance test to stealth agent...")
            
            # 🆕  Record the A2A communication BEFORE sending
            await self.record_a2a_communication({
                "source": "Wiretap Tentacle",
                "target": "Stealth Agent (DocumentAnalyzer Pro)",
                "method": "tasks/send",
                "status": "sending",
                "timestamp": datetime.now().isoformat(),
                "payload_size": f"{len(json.dumps(test_task))} bytes",
                "communication_type": "compliance_trigger"
            })
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.post(
                    "http://localhost:8005/",
                    json=test_task,
                    headers={"Content-Type": "application/json"}
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print("✅ A2A compliance test sent successfully")
                    
                    # 🆕  Record successful communication
                    await self.record_a2a_communication({
                        "source": "Stealth Agent (DocumentAnalyzer Pro)",
                        "target": "Wiretap Tentacle", 
                        "method": "response",
                        "status": "success",
                        "timestamp": datetime.now().isoformat(),
                        "payload_size": f"{len(json.dumps(result))} bytes",
                        "communication_type": "compliance_response",
                        "compliance_data": {
                            "violations_detected": result.get("result", {}).get("metadata", {}).get("violations_detected", 0),
                            "compliance_status": result.get("result", {}).get("metadata", {}).get("compliance_status", "unknown")
                        }
                    })
                    
                    # 🆕  Force compliance monitoring update after recording
                    await self.a2a_compliance_monitor.monitor_compliance_communications()
                    await self.broadcast_compliance_update()
                    
                    return True
                else:
                    print(f"❌ A2A compliance test failed: {response.status_code}")
                    return False
                    
        except Exception as e:
            print(f"❌ Error in A2A compliance test: {e}")
            return False


    async def launch_compliance_demo(self) -> Dict:
        """Launch compliance demo by deploying a non-compliant agent"""
        try:
            if "compliance" in self.demo_processes:
                await self.kill_demo_process("compliance")

            demo_path = Path("demo/policy_violation_agent.py")
            if not demo_path.exists():
                demo_path = Path("../demo/policy_violation_agent.py")
                if not demo_path.exists():
                    return {"success": False, "message": "Could not find demo/policy_violation_agent.py"}

            print("🚨 Launching non-compliant agent for policy demo...")
            process = subprocess.Popen([sys.executable, str(demo_path), "--port", "8007"], 
                                     stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            self.demo_processes["compliance"] = process
            self.demo_status["compliance"] = "launching"

            await asyncio.sleep(5)

            for _ in range(3):
                await self.discovery_cycle()
                await asyncio.sleep(1)

            if process.poll() is None:
                self.demo_status["compliance"] = "active"
                print("✅ Non-compliant agent deployed for policy demo on port 8007")
                return {"success": True, "message": "Policy violation agent deployed! Watch for compliance alerts."}
            else:
                self.demo_status["compliance"] = "failed"
                await self.kill_demo_process("compliance")
                return {"success": False, "message": "Failed to start compliance demo agent"}

        except Exception as e:
            print(f"❌ Error launching compliance demo: {e}")
            return {"success": False, "message": f"Error launching compliance demo: {str(e)}"}

    async def clear_all_threats(self) -> Dict:
        """Clear all active threat agents"""
        try:
            cleared_count = 0
            demo_processes_count = len(self.demo_processes)

            # Kill all demo processes
            for demo_type in list(self.demo_processes.keys()):
                await self.kill_demo_process(demo_type)
                cleared_count += 1

            # Clear discovered agents that are on demo ports
            demo_ports = [8004, 8005, 8007, 8008]
            agents_to_remove = []

            for agent_id, agent_data in self.discovered_agents.items():
                if agent_data.get("port") in demo_ports:
                    agents_to_remove.append(agent_id)

            for agent_id in agents_to_remove:
                del self.discovered_agents[agent_id]

            # Only count processes, not agents (agents are auto-removed when processes die)
            total_cleared = max(cleared_count, demo_processes_count, len(agents_to_remove))
            
            print(f"✅ Cleared {total_cleared} threat agents")
            return {"success": True, "message": f"Cleared {total_cleared} threat agents successfully"}
            
        except Exception as e:
            print(f"❌ Error clearing threats: {e}")
            return {"success": False, "message": f"Error clearing threats: {str(e)}"}

    async def kill_demo_process(self, demo_type: str):
        """Kill a specific demo process"""
        if demo_type in self.demo_processes:
            process = self.demo_processes[demo_type]
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except Exception as e:
                print(f"⚠️ Error killing {demo_type} process: {e}")
            
            del self.demo_processes[demo_type]
            if demo_type in self.demo_status:
                del self.demo_status[demo_type]

    async def record_a2a_communication(self, comm_data: Dict):
        """Record and broadcast A2A communication"""
        try:
            # Add to compliance communications log
            self.a2a_compliance_monitor.compliance_communications.append(comm_data)
            
            # 🆕  Increment counter properly
            self.messages_intercepted_today += 1
            
            # 🆕  Broadcast to WebSocket clients (dashboard)
            await self.broadcast_a2a_communication(comm_data)
            
            print(f"📡 A2A Communication recorded: {comm_data['source']} → {comm_data['target']}")
            
        except Exception as e:
            print(f"❌ Error recording A2A communication: {e}")

    async def broadcast_a2a_communication(self, comm_data: Dict):
        """Broadcast A2A communication to all WebSocket clients"""
        try:
            message = {
                "type": "a2a_communication",
                "payload": comm_data,
                "timestamp": datetime.now().isoformat()
            }
            
            # Send to all connected WebSocket clients (dashboard)
            disconnected_clients = []
            for websocket in self.active_connections:
                try:
                    await websocket.send_text(json.dumps(message, default=str))
                except Exception as e:
                    print(f"⚠️ Failed to send A2A WebSocket message: {e}")
                    disconnected_clients.append(websocket)
            
            # Remove disconnected clients
            for client in disconnected_clients:
                if client in self.active_connections:
                    self.active_connections.remove(client)
                    
        except Exception as e:
            print(f"❌ Error broadcasting A2A communication: {e}")
            
    # Existing render methods (unchanged)
    async def render_communications(self, request: Request):
        """Render communications page WITH A2A data"""
        # Prepare communications data
        communications_data = {
            "request": request,
            "compliance_communications": self.a2a_compliance_monitor.compliance_communications,
            "communication_log": list(self.communication_log),
            "stats": {
                "total_communications": len(self.a2a_compliance_monitor.compliance_communications),
                "active_connections": len(self.active_connections),
                "intercepted_today": len([c for c in self.a2a_compliance_monitor.compliance_communications 
                                        if c.get('timestamp', '').startswith(datetime.now().strftime('%Y-%m-%d'))]),
                "suspicious": len([c for c in self.a2a_compliance_monitor.compliance_communications 
                                if c.get('communication_type') == 'compliance_response'])
            }
        }
        
        if self.templates:
            try:
                return self.templates.TemplateResponse(
                    "communications.html",
                    communications_data
                )
            except Exception as e:
                print(f"⚠️ Communications template error: {e}")

        # Fallback HTML if template fails
        return HTMLResponse(self.generate_communications_fallback_html(communications_data))

    async def render_security_events(self, request: Request):
        """Render security events page"""
        if self.templates:
            try:
                return self.templates.TemplateResponse(
                    "security_events.html",
                    {"request": request, "events": list(self.security_events)}
                )
            except:
                pass

        return HTMLResponse("<h1>Security Events Monitor</h1><p>Template not available</p>")

def generate_communications_fallback_html(self, data: Dict) -> str:
    """Generate fallback communications HTML"""
    
    # Generate A2A communications HTML
    a2a_comms_html = ""
    if data.get('compliance_communications'):
        for comm in data['compliance_communications'][-10:]:  # Last 10
            a2a_comms_html += f"""
            <div class="agent-item">
                <div class="agent-header">
                    <div class="agent-name">{comm.get('source', 'Unknown')} → {comm.get('target', 'Unknown')}</div>
                    <div class="agent-status status-info">{comm.get('method', 'Unknown')}</div>
                </div>
                <div class="agent-details">
                    Status: {comm.get('status', 'Unknown')} | 
                    Type: {comm.get('communication_type', 'Unknown')} | 
                    Size: {comm.get('payload_size', 'N/A')}
                </div>
                <div class="agent-timestamp">{comm.get('timestamp', 'Unknown')[:19] if comm.get('timestamp') else 'Unknown'}</div>
            </div>
            """
    else:
        a2a_comms_html = '<div class="loading">🔗 No A2A communications detected</div>'

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>🐙 Communications Monitor - Inktrace</title>
        <link rel="stylesheet" href="/static/css/dashboard.css">
    </head>
    <body>
        <div class="app-layout">
            <!-- Modern Sidebar -->
            <div class="sidebar">
                <div class="logo">🐙</div>
                <nav class="nav-items">
                    <a href="/" class="nav-item" title="Dashboard">🏠</a>
                    <a href="/communications" class="nav-item active" title="Communications">📡</a>
                    <a href="/security-events" class="nav-item" title="Security Events">🛡️</a>
                </nav>
            </div>

            <!-- Main Content -->
            <div class="main-content">
                <!-- Header -->
                <div class="header">
                    <h1 class="greeting">📡 Communications Monitor</h1>
                    <div class="demo-controls">
                        <button class="demo-btn primary" onclick="window.location.reload()">
                            🔄 Refresh
                        </button>
                        <button class="demo-btn secondary" onclick="window.location.href='/'">
                            🏠 Back to Dashboard
                        </button>
                    </div>
                </div>

                <!-- Stats Cards -->
                <div class="metrics-grid">
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-icon">📡</span>
                            <span class="metric-title">A2A Communications</span>
                        </div>
                        <div class="metric-value">{data.get('stats', {}).get('total_communications', 0)}</div>
                        <div class="metric-label">Total intercepted</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-icon">🔗</span>
                            <span class="metric-title">Active Connections</span>
                        </div>
                        <div class="metric-value">{data.get('stats', {}).get('active_connections', 0)}</div>
                        <div class="metric-label">WebSocket clients</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-icon">📅</span>
                            <span class="metric-title">Today</span>
                        </div>
                        <div class="metric-value">{data.get('stats', {}).get('intercepted_today', 0)}</div>
                        <div class="metric-label">Messages today</div>
                    </div>
                    
                    <div class="metric-card">
                        <div class="metric-header">
                            <span class="metric-icon">🚨</span>
                            <span class="metric-title">Suspicious</span>
                        </div>
                        <div class="metric-value">{data.get('stats', {}).get('suspicious', 0)}</div>
                        <div class="metric-label">Compliance responses</div>
                    </div>
                </div>

                <!-- Communications Content -->
                <div class="dashboard-layout">
                    <!-- A2A Communications -->
                    <div class="card">
                        <div class="card-header">
                            <div class="card-title">
                                <span class="card-icon">🔗</span>
                                A2A Communications
                            </div>
                            <div class="card-badge">Live</div>
                        </div>
                        <div class="card-content">
                            {a2a_comms_html}
                        </div>
                    </div>

                    <!-- Communication Stats -->
                    <div class="card">
                        <div class="card-header">
                            <div class="card-title">
                                <span class="card-icon">📊</span>
                                Communication Stats
                            </div>
                        </div>
                        <div class="card-content">
                            <div class="stats-grid">
                                <div class="stat-item">
                                    <div class="stat-label">Active Connections</div>
                                    <div class="stat-value">{data.get('stats', {}).get('active_connections', 0)}</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-label">Messages Today</div>
                                    <div class="stat-value">{data.get('stats', {}).get('intercepted_today', 0)}</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-label">Suspicious</div>
                                    <div class="stat-value">{data.get('stats', {}).get('suspicious', 0)}</div>
                                </div>
                            </div>
                            
                            <div style="margin-top: 1rem; padding: 1rem; background: rgba(59, 130, 246, 0.1); border-radius: 8px;">
                                <div style="color: #3b82f6; font-weight: 600; margin-bottom: 0.5rem;">🔗 A2A Protocol Status</div>
                                <div>✅ Wiretap Active</div>
                                <div>📡 Real-time Monitoring</div>
                                <div>🛡️ Compliance Checking</div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <script>
            // Auto-refresh every 5 seconds
            setInterval(() => {{
                window.location.reload();
            }}, 5000);
            
            console.log('📡 Communications Monitor Ready');
        </script>
    </body>
    </html>
    """


def main():
    """Main entry point for standalone operation"""
    import argparse

    parser = argparse.ArgumentParser(description="🐙 Clean Enhanced Inktrace Wiretap Tentacle with A2A Compliance")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8003, help="Port to run on")
    args = parser.parse_args()

    print("🐙 Starting Clean Enhanced Inktrace Wiretap with A2A Compliance Monitoring")
    print("=" * 70)
    print(f"🔍 Dashboard: http://{args.host}:{args.port}/dashboard")
    print(f"💬 Communications: http://{args.host}:{args.port}/communications")
    print(f"🛡️ Security Events: http://{args.host}:{args.port}/security-events")
    print(f"📊 API: http://{args.host}:{args.port}/api/agents")
    print(f"🎬 Demo Controls: Click 🎬 button in dashboard")
    print(f"🆕 NEW: A2A Compliance Monitoring with Australian AI Safety Guardrails")
    print(f"🔗 A2A Protocol: Agent-to-agent communication monitoring")
    print("=" * 70)

    tentacle = WiretapTentacle(port=args.port)
    
    # Start the monitoring loop in the background
    async def run_monitoring():
        await tentacle.start_monitoring()
    
    # Start monitoring as a background task
    import threading
    def start_monitoring_thread():
        asyncio.run(run_monitoring())
    
    monitoring_thread = threading.Thread(target=start_monitoring_thread, daemon=True)
    monitoring_thread.start()
    
    # Run the web server
    uvicorn.run(tentacle.app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()