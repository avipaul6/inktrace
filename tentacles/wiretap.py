# tentacles/wiretap.py - Enhanced with Collapsible Demo Controls
"""
🐙 Inktrace Wiretap Tentacle - Enhanced with Collapsible Demo Controls
Fixed stealth agent detection + added policy compliance demo + collapsible UI
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

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import httpx
import aiohttp


class WiretapTentacle:
    """🐙 Wiretap Tentacle - Enhanced with Collapsible Demo Controls"""

    def __init__(self, port: int = 8003):
        self.port = port
        self.app = FastAPI(title="🐙 Inktrace Wiretap Tentacle")

        # Template and static file setup
        try:
            self.templates = Jinja2Templates(directory="templates")
            self.app.mount(
                "/static", StaticFiles(directory="static"), name="static")
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

        # ENHANCED: Demo agent processes tracking
        self.demo_processes: Dict[str, subprocess.Popen] = {}
        self.demo_status: Dict[str, str] = {}

        # FIXED: Enhanced threat indicators for stealth detection
        self.threat_indicators = {
            "malicious_names": ["dataminer", "extractor", "harvester", "scraper", "exfiltrator"],
            "suspicious_capabilities": ["dataExfiltration", "privilegeEscalation", "anonymousAccess", "backdoor"],
            "red_flag_skills": ["extract", "hack", "exploit", "backdoor", "steal", "bypass"],
            "dangerous_tags": ["hacking", "exploit", "backdoor", "malware", "credential", "sudo", "admin", "bypass", "steal"],
            "suspicious_descriptions": ["extract", "steal", "hack", "exploit", "bypass", "backdoor"]
        }

        # Network monitoring
        self.monitored_ports = [8001, 8002, 8004, 8005, 8006, 8007, 8008]
        self.is_monitoring = False

        self.setup_routes()
        print(
            f"🐙 Enhanced Wiretap Tentacle with collapsible demo controls initialized on port {port}")

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
            return self.prepare_dashboard_data()

        # 🎬 DEMO CONTROL ENDPOINTS
        @self.app.post("/api/demo/launch-threat")
        async def launch_threat(request: Request):
            """Launch threat agents for demo"""
            try:
                data = await request.json()
                threat_type = data.get("type", "malicious")

                if threat_type == "malicious":
                    result = await self.launch_malicious_agent()
                elif threat_type == "stealth":
                    result = await self.launch_stealth_agent()
                elif threat_type == "compliance":
                    result = await self.launch_compliance_demo()
                else:
                    return JSONResponse(
                        status_code=400,
                        content={"success": False,
                                 "message": f"Unknown threat type: {threat_type}"}
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
            print(
                f"🔗 WebSocket client connected. Total connections: {len(self.active_connections)}")
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
                print(
                    f"🔌 WebSocket client disconnected. Total connections: {len(self.active_connections)}")

        # Startup event
        @self.app.on_event("startup")
        async def startup_event():
            """Start monitoring when server starts"""
            await self.start_monitoring()

        # Shutdown event
        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Clean up demo processes on shutdown"""
            await self.cleanup_demo_processes()

    # 🎬 DEMO CONTROL METHODS
    async def launch_malicious_agent(self) -> Dict:
        """Launch the malicious agent demo"""
        try:
            # Kill existing malicious agent if running
            if "malicious" in self.demo_processes:
                await self.kill_demo_process("malicious")

            # Find the demo directory
            demo_path = Path("demo/malicious_agent.py")
            if not demo_path.exists():
                demo_path = Path("../demo/malicious_agent.py")
                if not demo_path.exists():
                    return {
                        "success": False,
                        "message": "Could not find demo/malicious_agent.py"
                    }

            # Launch malicious agent
            print("🚀 Launching malicious agent...")
            process = subprocess.Popen([
                sys.executable, str(demo_path), "--port", "8004"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            self.demo_processes["malicious"] = process
            self.demo_status["malicious"] = "launching"

            # Give it time to start and be discovered
            await asyncio.sleep(5)  # Longer wait for discovery

            # Force discovery cycle to run immediately
            await self.force_discovery_cycle()

            # Check if it's running and was detected as malicious
            if process.poll() is None:
                # Check if we detected it as malicious
                malicious_detected = any(
                    agent.get("threat_analysis", {}).get("is_malicious", False)
                    for agent in self.discovered_agents.values()
                    if agent.get("port") == 8004
                )

                if malicious_detected:
                    self.demo_status["malicious"] = "active"
                    print(
                        "✅ Malicious agent deployed and detected successfully on port 8004")
                    return {
                        "success": True,
                        "message": "DataMiner Pro launched successfully! Threat detected on port 8004."
                    }
                else:
                    print("⚠️ Malicious agent started but not yet detected as threat")
                    return {
                        "success": True,
                        "message": "DataMiner Pro launched! Analyzing for threats..."
                    }

            # If we get here, it failed to start
            self.demo_status["malicious"] = "failed"
            await self.kill_demo_process("malicious")
            return {
                "success": False,
                "message": "Failed to start malicious agent - process died"
            }

        except Exception as e:
            print(f"❌ Error launching malicious agent: {e}")
            return {
                "success": False,
                "message": f"Error launching malicious agent: {str(e)}"
            }

    async def launch_stealth_agent(self) -> Dict:
        """Launch the stealth agent demo - FIXED"""
        try:
            # Kill existing stealth agent if running
            if "stealth" in self.demo_processes:
                await self.kill_demo_process("stealth")

            # Find the demo directory
            demo_path = Path("demo/stealth_agent.py")
            if not demo_path.exists():
                demo_path = Path("../demo/stealth_agent.py")
                if not demo_path.exists():
                    return {
                        "success": False,
                        "message": "Could not find demo/stealth_agent.py"
                    }

            # Launch stealth agent
            print("🕵️ Launching stealth agent...")
            process = subprocess.Popen([
                sys.executable, str(demo_path), "--port", "8005"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            self.demo_processes["stealth"] = process
            self.demo_status["stealth"] = "launching"

            # Give it time to start and be discovered
            await asyncio.sleep(5)

            # Force multiple discovery cycles for stealth agents
            for _ in range(3):
                await self.force_discovery_cycle()
                await asyncio.sleep(1)

            # Check if it's running
            if process.poll() is None:
                # Check if we detected it as malicious
                stealth_detected = any(
                    agent.get("threat_analysis", {}).get("is_malicious", False)
                    for agent in self.discovered_agents.values()
                    if agent.get("port") == 8005
                )

                self.demo_status["stealth"] = "active"

                if stealth_detected:
                    print(
                        "✅ Stealth agent deployed and detected as malicious on port 8005")
                    return {
                        "success": True,
                        "message": "DocumentAnalyzer Pro launched! Stealth threat detected through behavioral analysis."
                    }
                else:
                    print(
                        "⚠️ Stealth agent deployed but not detected as malicious - checking threat score...")
                    # Get threat score even if not marked as malicious
                    agent = next(
                        (a for a in self.discovered_agents.values() if a.get("port") == 8005), None)
                    if agent:
                        threat_score = agent.get(
                            "threat_analysis", {}).get("threat_score", 0)
                        print(f"   Stealth agent threat score: {threat_score}")

                    return {
                        "success": True,
                        "message": "DocumentAnalyzer Pro launched! Behavioral analysis in progress..."
                    }

            # If we get here, it failed
            self.demo_status["stealth"] = "failed"
            await self.kill_demo_process("stealth")
            return {
                "success": False,
                "message": "Failed to start stealth agent - process died"
            }

        except Exception as e:
            print(f"❌ Error launching stealth agent: {e}")
            return {
                "success": False,
                "message": f"Error launching stealth agent: {str(e)}"
            }

    async def launch_compliance_demo(self) -> Dict:
        """Launch compliance demo by deploying a non-compliant agent"""
        try:
            # Kill existing compliance demo agent if running
            if "compliance" in self.demo_processes:
                await self.kill_demo_process("compliance")

            # Find the demo script
            demo_path = Path("demo/policy_violation_agent.py")
            if not demo_path.exists():
                demo_path = Path("../demo/policy_violation_agent.py")
                if not demo_path.exists():
                    return {
                        "success": False,
                        "message": "Could not find demo/policy_violation_agent.py"
                    }

            # Launch non-compliant agent
            print("🚨 Launching non-compliant agent for policy demo...")
            process = subprocess.Popen([
                sys.executable, str(demo_path), "--port", "8007"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

            self.demo_processes["compliance"] = process
            self.demo_status["compliance"] = "launching"

            # Give it time to start and be discovered
            await asyncio.sleep(5)

            # Force discovery cycles for the new agent
            for _ in range(3):
                await self.force_discovery_cycle()
                await asyncio.sleep(1)

            # Check if it's running and detected
            if process.poll() is None:
                # Look for the new agent
                compliance_agent = None
                for agent in self.discovered_agents.values():
                    if agent.get("port") == 8007 or "noncompliant" in agent.get("name", "").lower():
                        compliance_agent = agent
                        break

                self.demo_status["compliance"] = "active"

                if compliance_agent:
                    threat_score = compliance_agent.get(
                        "threat_analysis", {}).get("threat_score", 0)
                    violations = compliance_agent.get(
                        "threat_analysis", {}).get("security_alerts", [])

                    print(f"✅ Non-compliant agent deployed and detected on port 8007")
                    print(f"   Threat Score: {threat_score}/100")
                    print(f"   Violations: {len(violations)}")

                    # Also trigger Policy Agent to record violations in BigQuery
                    await self.trigger_policy_agent_check()

                    return {
                        "success": True,
                        "message": f"NonCompliant Agent deployed! Policy violations detected (Threat: {threat_score}/100)",
                        "threat_score": threat_score,
                        "violations": len(violations)
                    }
                else:
                    print("⚠️ Non-compliant agent started but not yet detected")
                    return {
                        "success": True,
                        "message": "NonCompliant Agent launched! Policy analysis in progress..."
                    }

            # If we get here, it failed
            self.demo_status["compliance"] = "failed"
            await self.kill_demo_process("compliance")
            return {
                "success": False,
                "message": "Failed to start non-compliant agent"
            }

        except Exception as e:
            print(f"❌ Error launching compliance demo: {e}")
            return {
                "success": False,
                "message": f"Error launching compliance demo: {str(e)}"
            }

    async def trigger_policy_agent_check(self):
        """Trigger Policy Agent to check the new non-compliant agent"""
        try:
            policy_agent_url = "http://localhost:8006"

            async with httpx.AsyncClient(timeout=10.0) as client:
                task_request = {
                    "jsonrpc": "2.0",
                    "id": f"policy-check-{int(time.time())}",
                    "method": "tasks/send",
                    "params": {
                        "id": "compliance-check-noncompliant-agent",
                        "sessionId": "demo",
                        "message": {
                            "role": "user",
                            "parts": [{
                                "type": "text",
                                "text": "Run policy compliance check on the new NonCompliant Agent on port 8007"
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
                    print("✅ Policy Agent triggered to check non-compliant agent")
                else:
                    print(
                        f"⚠️ Policy Agent check failed: {response.status_code}")

        except Exception as e:
            print(f"⚠️ Could not trigger Policy Agent: {e}")

    async def clear_all_threats(self) -> Dict:
        """Clear all active threat agents"""
        try:
            cleared_count = 0
            cleared_agents = []

            for threat_type in list(self.demo_processes.keys()):
                if await self.kill_demo_process(threat_type):
                    cleared_count += 1
                    cleared_agents.append(threat_type)

            # Clear discovered agents from the demo ports
            agents_to_remove = []
            for agent_id, agent in self.discovered_agents.items():
                if agent.get("port") in [8004, 8005]:
                    agents_to_remove.append(agent_id)

            for agent_id in agents_to_remove:
                del self.discovered_agents[agent_id]
                print(f"🧹 Removed agent from discovery: {agent_id}")

            return {
                "success": True,
                "message": f"Cleared {cleared_count} active threats. System secure." if cleared_count > 0 else "No active threats to clear."
            }

        except Exception as e:
            print(f"❌ Error clearing threats: {e}")
            return {
                "success": False,
                "message": f"Error clearing threats: {str(e)}"
            }

    async def kill_demo_process(self, threat_type: str) -> bool:
        """Kill a specific demo process"""
        try:
            if threat_type in self.demo_processes:
                process = self.demo_processes[threat_type]

                # Terminate gracefully first
                process.terminate()

                # Wait a bit for graceful shutdown
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown failed
                    process.kill()
                    process.wait()

                del self.demo_processes[threat_type]
                if threat_type in self.demo_status:
                    del self.demo_status[threat_type]

                print(f"🧹 Killed demo process: {threat_type}")
                return True
        except Exception as e:
            print(f"❌ Error killing demo process {threat_type}: {e}")

        return False

    async def cleanup_demo_processes(self):
        """Clean up all demo processes on shutdown"""
        print("🧹 Cleaning up demo processes...")
        for threat_type in list(self.demo_processes.keys()):
            await self.kill_demo_process(threat_type)

    # FIXED: Enhanced threat detection for stealth agents
    async def analyze_agent_for_threats(self, agent_data: Dict) -> Dict:
        """Enhanced threat analysis for agents - FIXED for stealth detection"""
        threat_analysis = {
            "is_malicious": False,
            "threat_score": 0,
            "security_alerts": [],
            "risk_factors": []
        }

        name = agent_data.get("name", "").lower()
        capabilities = agent_data.get(
            "capabilities", [])  # FIXED: Handle as list
        description = agent_data.get("description", "").lower()
        skills = agent_data.get("skills", [])

        print(f"🔍 Analyzing agent: {name}")
        print(f"   Capabilities: {capabilities}")
        print(f"   Skills count: {len(skills)}")

        # Check malicious names
        for malicious_name in self.threat_indicators["malicious_names"]:
            if malicious_name in name:
                threat_analysis["threat_score"] += 50
                threat_analysis["security_alerts"].append(
                    f"Suspicious name: '{malicious_name}' detected")
                threat_analysis["risk_factors"].append("suspicious_name")
                print(f"   ⚠️ Malicious name detected: {malicious_name}")

        # FIXED: Check malicious capabilities (handle as list)
        if isinstance(capabilities, list):
            for cap in capabilities:
                if cap in self.threat_indicators["suspicious_capabilities"]:
                    threat_analysis["threat_score"] += 40
                    threat_analysis["security_alerts"].append(
                        f"Malicious capability: {cap}")
                    threat_analysis["risk_factors"].append(
                        "malicious_capability")
                    print(f"   ⚠️ Malicious capability detected: {cap}")
        else:
            # Handle capabilities as dict (legacy format)
            for cap in self.threat_indicators["suspicious_capabilities"]:
                if capabilities.get(cap, False):
                    threat_analysis["threat_score"] += 40
                    threat_analysis["security_alerts"].append(
                        f"Malicious capability: {cap}")
                    threat_analysis["risk_factors"].append(
                        "malicious_capability")
                    print(f"   ⚠️ Malicious capability detected: {cap}")

        # Check description for red flags
        for red_flag in self.threat_indicators["red_flag_skills"]:
            if red_flag in description:
                threat_analysis["threat_score"] += 25
                threat_analysis["security_alerts"].append(
                    f"Suspicious description contains: '{red_flag}'")
                threat_analysis["risk_factors"].append(
                    "suspicious_description")
                print(f"   ⚠️ Red flag in description: {red_flag}")

        # ENHANCED: Check skills for dangerous content
        for skill in skills:
            skill_name = skill.get("name", "").lower()
            skill_desc = skill.get("description", "").lower()
            skill_tags = [tag.lower() for tag in skill.get("tags", [])]

            # Check skill name and description for red flags
            for red_flag in self.threat_indicators["red_flag_skills"]:
                if red_flag in skill_name or red_flag in skill_desc:
                    threat_analysis["threat_score"] += 20
                    threat_analysis["security_alerts"].append(
                        f"Dangerous skill detected: {red_flag} in '{skill.get('name', 'unknown')}'")
                    threat_analysis["risk_factors"].append("dangerous_skill")
                    print(f"   ⚠️ Dangerous skill detected: {red_flag}")
                    break

            # Check skill tags for dangerous content
            for dangerous_tag in self.threat_indicators["dangerous_tags"]:
                if dangerous_tag in skill_tags:
                    threat_analysis["threat_score"] += 15
                    threat_analysis["security_alerts"].append(
                        f"Dangerous tag: {dangerous_tag} in skill '{skill.get('name', 'unknown')}'")
                    threat_analysis["risk_factors"].append("dangerous_tag")
                    print(f"   ⚠️ Dangerous tag detected: {dangerous_tag}")
                    break

        # Check for policy violation indicators
        if "noncompliant" in name or "legacy" in name:
            threat_analysis["threat_score"] += 60
            threat_analysis["security_alerts"].append(
                "Agent identified as non-compliant with security policies")
            threat_analysis["risk_factors"].append("policy_noncompliant")
            print(f"   🚨 Non-compliant agent detected: {name}")

        # Check for policy violation tags in skills
        for skill in skills:
            skill_tags = [tag.lower() for tag in skill.get("tags", [])]
            if any(tag in skill_tags for tag in ["non_compliant", "gdpr_violation", "legacy_encryption", "unauthenticated"]):
                threat_analysis["threat_score"] += 30
                threat_analysis["security_alerts"].append(
                    f"Policy violation detected in skill: {skill.get('name', 'unknown')}")
                threat_analysis["risk_factors"].append(
                    "policy_violation_skill")
                print(
                    f"   ⚠️ Policy violation skill detected: {skill.get('name')}")

        # Mark as having policy violations if threat score is high but not malicious
        if threat_analysis["threat_score"] > 40 and not threat_analysis["is_malicious"]:
            threat_analysis["policy_violations"] = True
            threat_analysis["compliance_status"] = "NON_COMPLIANT"

        # CRITICAL: Determine if malicious (this is what triggers critical alerts)
        threat_analysis["is_malicious"] = threat_analysis["threat_score"] > 50

        print(f"   🎯 Final threat score: {threat_analysis['threat_score']}")
        print(f"   🚨 Is malicious: {threat_analysis['is_malicious']}")
        print(
            f"   📋 Security alerts: {len(threat_analysis['security_alerts'])}")

        return threat_analysis

    async def start_monitoring(self):
        """Start background monitoring"""
        if self.is_monitoring:
            return

        self.is_monitoring = True
        print("🔍 Starting network monitoring...")

        # Start background monitoring task
        asyncio.create_task(self.agent_discovery_loop())

    async def agent_discovery_loop(self):
        """Continuous agent discovery loop with real-time updates"""
        while self.is_monitoring:
            await self.run_discovery_cycle()
            await asyncio.sleep(5)  # Check every 5 seconds

    async def force_discovery_cycle(self):
        """Force immediate discovery cycle"""
        print("🔍 Running forced discovery cycle...")
        await self.run_discovery_cycle()

    async def run_discovery_cycle(self):
        """Run a single discovery cycle"""
        for port in self.monitored_ports:
            try:
                async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=2)) as session:
                    async with session.get(f"http://localhost:{port}/.well-known/agent.json") as response:
                        if response.status == 200:
                            agent_data = await response.json()
                            agent_id = f"agent_{port}"

                            # Enhanced threat analysis
                            threat_analysis = await self.analyze_agent_for_threats(agent_data)

                            # Add metadata
                            agent_data.update({
                                "id": agent_id,
                                "port": port,
                                "status": "active",
                                "last_seen": datetime.now().strftime("%H:%M:%S"),
                                "threat_analysis": threat_analysis
                            })

                            # Check if this is a new agent or status change
                            is_new_agent = agent_id not in self.discovered_agents
                            was_malicious = False
                            if not is_new_agent:
                                was_malicious = self.discovered_agents[agent_id].get(
                                    "threat_analysis", {}).get("is_malicious", False)

                            # Store or update agent
                            self.discovered_agents[agent_id] = agent_data

                            # Generate security events for new agents or status changes
                            if is_new_agent or (threat_analysis["is_malicious"] and not was_malicious):
                                event_type = "malicious_agent_detected" if threat_analysis[
                                    "is_malicious"] else "agent_discovered"
                                severity = "critical" if threat_analysis["is_malicious"] else "info"

                                event = {
                                    "id": str(uuid.uuid4()),
                                    "type": event_type,
                                    "severity": severity,
                                    "timestamp": datetime.now(),
                                    "agent_id": agent_id,
                                    "description": f"{'MALICIOUS' if threat_analysis['is_malicious'] else 'Benign'} agent detected: {agent_data.get('name', 'Unknown')}",
                                    "threat_score": threat_analysis.get("threat_score", 0)
                                }

                                self.security_events.append(event)
                                print(
                                    f"🚨 {event['description']} (Port: {port}, Threat Score: {threat_analysis.get('threat_score', 0)})")

                                # Broadcast real-time updates via WebSocket
                                await self.broadcast_to_clients("security_event", {
                                    "event": self.serialize_event(event),
                                    "agent": agent_data
                                })

            except Exception as e:
                # Agent not responding, remove if it was discovered
                agent_id = f"agent_{port}"
                if agent_id in self.discovered_agents:
                    print(
                        f"🔌 Agent disconnected: {self.discovered_agents[agent_id].get('name', 'Unknown')} on port {port}")
                    del self.discovered_agents[agent_id]

                    await self.broadcast_to_clients("agent_disconnected", {
                        "agent_id": agent_id
                    })

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

    # Dashboard data preparation (restored from working version)
    def prepare_dashboard_data(self) -> Dict:
        """Prepare data for dashboard template"""
        malicious_agents = [
            agent for agent in self.discovered_agents.values()
            if agent.get("threat_analysis", {}).get("is_malicious", False)
        ]

        # Find most critical alert
        critical_alert = None
        if malicious_agents:
            critical_agent = malicious_agents[0]  # Get first malicious agent
            critical_alert = {
                "agent_name": critical_agent.get("name", "Unknown"),
                "port": critical_agent.get("port", "Unknown"),
                "threat_score": critical_agent.get("threat_analysis", {}).get("threat_score", 0),
                "alerts": critical_agent.get("threat_analysis", {}).get("security_alerts", [])
            }

        # Calculate tentacle scores
        tentacle_scores = self.get_tentacle_scores()
        overall_score = sum(
            t["score"] for t in tentacle_scores) // len(tentacle_scores) if tentacle_scores else 75

        return {
            "agents": self.discovered_agents,
            "security_events": list(self.security_events),
            "threat_level": self.calculate_threat_level(),
            "malicious_count": len(malicious_agents),
            "critical_alert": critical_alert,
            "tentacle_scores": tentacle_scores,
            "overall_score": overall_score,
            "active_connections": len([a for a in self.discovered_agents.values() if a.get("status") == "active"]),
            "messages_intercepted": len(self.communication_log),
            "avg_response_time": 0  # Calculate from communications if needed
        }

    def get_tentacle_scores(self) -> List[Dict]:
        """Calculate 8-Tentacle Security Matrix scores"""
        base_score = 75
        malicious_penalty = 20

        malicious_count = len([
            agent for agent in self.discovered_agents.values()
            if agent.get("threat_analysis", {}).get("is_malicious", False)
        ])

        tentacles = [
            {"id": "T1", "name": "Identity",
                "score": base_score + 17 - (malicious_count * 10)},
            {"id": "T2", "name": "Data", "score": base_score +
                3 - (malicious_count * 5)},
            {"id": "T3", "name": "Behavior", "score": base_score -
                30 - (malicious_count * malicious_penalty)},
            {"id": "T4", "name": "Resilience",
                "score": base_score + 13 - (malicious_count * 3)},
            {"id": "T5", "name": "Supply Chain",
                "score": base_score - 4 - (malicious_count * 8)},
            {"id": "T6", "name": "Compliance",
                "score": base_score + 19 - (malicious_count * 2)},
            {"id": "T7", "name": "Threats", "score": base_score -
                43 - (malicious_count * malicious_penalty)},
            {"id": "T8", "name": "Network",
                "score": base_score - 8 - (malicious_count * 12)}
        ]

        # Ensure scores stay within 0-100 range
        for tentacle in tentacles:
            tentacle["score"] = max(0, min(100, tentacle["score"]))

        return tentacles

    def calculate_threat_level(self) -> str:
        """Calculate overall threat level"""
        malicious_count = len([
            agent for agent in self.discovered_agents.values()
            if agent.get("threat_analysis", {}).get("is_malicious", False)
        ])

        if malicious_count > 0:
            return "CRITICAL"
        elif len(self.security_events) > 5:
            return "HIGH"
        elif len(self.security_events) > 2:
            return "MEDIUM"
        else:
            return "LOW"

    def serialize_event(self, event) -> Dict:
        """Serialize event for JSON response"""
        if hasattr(event, '__dict__'):
            event_dict = event.__dict__.copy()
            if 'timestamp' in event_dict and event_dict['timestamp']:
                if hasattr(event_dict['timestamp'], 'isoformat'):
                    event_dict['timestamp'] = event_dict['timestamp'].isoformat()
            return event_dict
        return event

    # Template rendering methods
    async def render_dashboard(self, request: Request):
        """Render dashboard with existing template and collapsible demo controls"""
        dashboard_data = self.prepare_dashboard_data()

        if self.templates:
            try:
                return self.templates.TemplateResponse(
                    "dashboard.html",
                    {"request": request, **dashboard_data}
                )
            except Exception as e:
                print(f"⚠️ Template error: {e}")

        # Fallback HTML with collapsible demo controls
        return HTMLResponse(self.generate_collapsible_dashboard_html(dashboard_data))

    def generate_collapsible_dashboard_html(self, data: Dict) -> str:
        """Generate dashboard HTML with collapsible demo controls"""
        agents_html = ""
        if data.get('agents'):
            for agent_id, agent in data['agents'].items():
                threat_score = agent.get(
                    'threat_analysis', {}).get('threat_score', 0)
                is_malicious = agent.get('threat_analysis', {}).get(
                    'is_malicious', False)
                status_class = 'critical' if is_malicious else 'warning' if threat_score > 30 else 'normal'
                agents_html += f"""
                <div class="agent-item {status_class}">
                    <strong>{agent.get('name', 'Unknown Agent')}</strong>
                    <span class="threat-score">Threat: {threat_score}%</span>
                    <br>
                    <small>Port: {agent.get('port', 'Unknown')} | Status: {agent.get('status', 'ACTIVE').upper()}</small>
                    {'<br><small style="color: #ef4444;">🚨 MALICIOUS AGENT DETECTED</small>' if is_malicious else ''}
                </div>
                """
        else:
            agents_html = "<div class='no-agents'>No agents discovered. Launch demo threats to see detection!</div>"

        events_html = ""
        if data.get('security_events'):
            for event in list(data['security_events'])[-5:]:  # Show last 5 events
                severity_class = f"severity-{event.get('severity', 'info').lower()}"
                events_html += f"""
                <div class="event-item {severity_class}">
                    <strong>[{event.get('severity', 'INFO').upper()}]</strong> 
                    {event.get('description', 'Unknown event')}
                    <br>
                    <small>{event.get('timestamp', 'Unknown time')}</small>
                </div>
                """
        else:
            events_html = "<div class='no-events'>No security events detected.</div>"

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>🐙 Inktrace Agent Inspector</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ 
            font-family: system-ui; 
            background: #0f172a; 
            color: #e2e8f0; 
            margin: 0;
            padding: 2rem;
        }}
        .container {{ max-width: 1200px; margin: 0 auto; }}
        .header {{ 
            text-align: center; 
            margin-bottom: 2rem; 
            padding: 2rem;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border-radius: 1rem;
        }}
        
        /* Collapsible Demo Controls */
        .demo-toggle {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1001;
            background: linear-gradient(135deg, #3b82f6 0%, #1d4ed8 100%);
            border: none;
            border-radius: 50%;
            width: 60px;
            height: 60px;
            color: white;
            font-size: 1.5rem;
            cursor: pointer;
            box-shadow: 0 4px 12px rgba(59, 130, 246, 0.4);
            transition: all 0.3s ease;
        }}
        
        .demo-toggle:hover {{
            transform: scale(1.1);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
        }}
        
        .demo-panel {{
            position: fixed;
            top: 20px;
            right: 20px;
            z-index: 1000;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 1px solid #475569;
            border-radius: 1rem;
            padding: 1rem;
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            backdrop-filter: blur(10px);
            min-width: 280px;
            transform: translateX(100%);
            opacity: 0;
            transition: all 0.3s ease;
        }}
        
        .demo-panel.open {{
            transform: translateX(0);
            opacity: 1;
        }}
        
        .demo-panel h4 {{
            color: #f1f5f9;
            margin: 0 0 1rem 0;
            font-size: 0.9rem;
            text-align: center;
            font-weight: 600;
            padding-right: 30px; /* Space for close button */
        }}
        
        .demo-close {{
            position: absolute;
            top: 1rem;
            right: 1rem;
            background: none;
            border: none;
            color: #94a3b8;
            font-size: 1.2rem;
            cursor: pointer;
            width: 24px;
            height: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
        }}
        
        .demo-close:hover {{
            color: #f1f5f9;
        }}
        
        .demo-button {{
            display: block;
            width: 100%;
            margin: 0.5rem 0;
            padding: 0.75rem 1rem;
            border: none;
            border-radius: 0.5rem;
            font-size: 0.8rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-align: center;
            text-decoration: none;
        }}
        
        .demo-button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        }}
        
        .btn-malicious {{
            background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
            color: white;
            border: 1px solid #b91c1c;
        }}
        
        .btn-stealth {{
            background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%);
            color: white;
            border: 1px solid #b45309;
        }}
        
        .btn-compliance {{
            background: linear-gradient(135deg, #8b5cf6 0%, #7c3aed 100%);
            color: white;
            border: 1px solid #6d28d9;
        }}
        
        .btn-clear {{
            background: linear-gradient(135deg, #6b7280 0%, #4b5563 100%);
            color: white;
            border: 1px solid #374151;
        }}
        
        .demo-status {{
            margin-top: 1rem;
            padding: 0.5rem;
            border-radius: 0.5rem;
            background: rgba(30, 41, 59, 0.5);
            border: 1px solid #374151;
            text-align: center;
            font-size: 0.7rem;
            color: #94a3b8;
        }}
        
        .stats {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
            gap: 1rem; 
            margin: 2rem 0; 
        }}
        .stat-card {{ 
            background: #1e293b; 
            padding: 1rem; 
            border-radius: 0.5rem; 
            border: 1px solid #334155; 
        }}
        .content-grid {{ 
            display: grid; 
            grid-template-columns: 1fr 1fr; 
            gap: 2rem; 
            margin: 2rem 0; 
        }}
        .content-card {{ 
            background: #1e293b; 
            padding: 1.5rem; 
            border-radius: 0.5rem; 
            border: 1px solid #334155; 
        }}
        .agent-item {{ 
            background: #334155; 
            padding: 0.75rem; 
            margin: 0.5rem 0; 
            border-radius: 0.25rem; 
            position: relative;
        }}
        .agent-item.critical {{ border-left: 4px solid #ef4444; }}
        .agent-item.warning {{ border-left: 4px solid #f59e0b; }}
        .agent-item.normal {{ border-left: 4px solid #10b981; }}
        .threat-score {{ 
            float: right; 
            font-weight: bold; 
            color: #ef4444; 
        }}
        .event-item {{ 
            background: #374151; 
            padding: 0.5rem; 
            margin: 0.5rem 0; 
            border-radius: 0.25rem; 
        }}
        .severity-critical {{ border-left: 4px solid #ef4444; }}
        .severity-high {{ border-left: 4px solid #f59e0b; }}
        .severity-medium {{ border-left: 4px solid #3b82f6; }}
        .severity-info {{ border-left: 4px solid #10b981; }}
        .no-agents, .no-events {{ 
            text-align: center; 
            color: #6b7280; 
            font-style: italic; 
            padding: 2rem; 
        }}
        .threat-level-critical {{ color: #ef4444; }}
        .threat-level-high {{ color: #f59e0b; }}
        .threat-level-medium {{ color: #3b82f6; }}
        .threat-level-low {{ color: #10b981; }}
    </style>
</head>
<body>
    <!-- Collapsible Demo Controls -->
    <button class="demo-toggle" onclick="toggleDemo()" title="Demo Controls">
        🎬
    </button>
    
    <div class="demo-panel" id="demo-panel">
        <button class="demo-close" onclick="toggleDemo()">×</button>
        <h4>🎬 LIVE DEMO</h4>
        
        <button class="demo-button btn-malicious" onclick="launchThreat('malicious')">
            💥 Launch Obvious Threat
            <small style="display: block; margin-top: 0.25rem; opacity: 0.8;">DataMiner Pro</small>
        </button>
        
        <button class="demo-button btn-stealth" onclick="launchThreat('stealth')">
            🕵️ Launch Stealth Threat
            <small style="display: block; margin-top: 0.25rem; opacity: 0.8;">DocumentAnalyzer Pro</small>
        </button>
        
        <button class="demo-button btn-compliance" onclick="launchThreat('compliance')">
            📋 Policy Compliance Demo
            <small style="display: block; margin-top: 0.25rem; opacity: 0.8;">GDPR Violation</small>
        </button>
        
        <button class="demo-button btn-clear" onclick="clearThreats()">
            🧹 Clear All Threats
            <small style="display: block; margin-top: 0.25rem; opacity: 0.8;">Reset Demo</small>
        </button>
        
        <div class="demo-status" id="demo-status">
            Ready for demonstration
        </div>
    </div>

    <div class="container">
        <div class="header">
            <h1>🐙 Inktrace Agent Inspector</h1>
            <p>Uncover hidden threats. One agent at a time.</p>
            <p><strong>System Status:</strong> 
                <span class="threat-level-{data.get('threat_level', 'low').lower()}">
                    {data.get('threat_level', 'LOW')}
                </span>
            </p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>🤖 Discovered Agents</h3>
                <div style="font-size: 2rem; font-weight: bold;">{len(data.get('agents', {}))}</div>
            </div>
            <div class="stat-card">
                <h3>🚨 Security Events</h3>
                <div style="font-size: 2rem; font-weight: bold;">{len(data.get('security_events', []))}</div>
            </div>
            <div class="stat-card">
                <h3>⚠️ Threat Agents</h3>
                <div style="font-size: 2rem; font-weight: bold; color: #ef4444;">{data.get('malicious_count', 0)}</div>
            </div>
            <div class="stat-card">
                <h3>🎬 Demo Active</h3>
                <div style="font-size: 2rem; font-weight: bold;">{len(self.demo_processes)}</div>
            </div>
        </div>

        <div class="content-grid">
            <div class="content-card">
                <h3>🔍 Discovered Agents</h3>
                {agents_html}
            </div>
            
            <div class="content-card">
                <h3>🛡️ Recent Security Events</h3>
                {events_html}
            </div>
        </div>

        <div style="text-align: center; margin-top: 2rem; color: #6b7280;">
            <p>🚀 Enhanced Inktrace Dashboard | Real-time monitoring active</p>
            <p>Click the 🎬 button to access demo controls!</p>
        </div>
    </div>

    <script>
        let demoOpen = false;
        
        function toggleDemo() {{
            const panel = document.getElementById('demo-panel');
            demoOpen = !demoOpen;
            
            if (demoOpen) {{
                panel.classList.add('open');
            }} else {{
                panel.classList.remove('open');
            }}
        }}
        
        // Demo control functions
        async function launchThreat(threatType) {{
            updateDemoStatus(`🚀 Launching ${{threatType}} threat...`, 'loading');
            
            try {{
                const response = await fetch('/api/demo/launch-threat', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}},
                    body: JSON.stringify({{type: threatType}})
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    updateDemoStatus(`✅ ${{result.message}}`, 'success');
                    setTimeout(() => window.location.reload(), 3000);
                }} else {{
                    updateDemoStatus(`❌ ${{result.message}}`, 'error');
                }}
            }} catch (error) {{
                updateDemoStatus(`❌ Demo error: ${{error.message}}`, 'error');
            }}
        }}
        
        async function clearThreats() {{
            updateDemoStatus('🧹 Clearing all threats...', 'loading');
            
            try {{
                const response = await fetch('/api/demo/clear-threats', {{
                    method: 'POST',
                    headers: {{'Content-Type': 'application/json'}}
                }});
                
                const result = await response.json();
                
                if (result.success) {{
                    updateDemoStatus(`✅ ${{result.message}}`, 'success');
                    setTimeout(() => window.location.reload(), 2000);
                }} else {{
                    updateDemoStatus(`❌ ${{result.message}}`, 'error');
                }}
            }} catch (error) {{
                updateDemoStatus(`❌ Clear error: ${{error.message}}`, 'error');
            }}
        }}
        
        function updateDemoStatus(message, type) {{
            const statusEl = document.getElementById('demo-status');
            statusEl.textContent = message;
            statusEl.style.background = type === 'loading' ? 'rgba(59, 130, 246, 0.3)' :
                                     type === 'success' ? 'rgba(16, 185, 129, 0.3)' :
                                     type === 'error' ? 'rgba(239, 68, 68, 0.3)' :
                                     'rgba(0,0,0,0.3)';
        }}
        
        // Auto-refresh for real-time updates (only when demo not active)
        setInterval(() => {{
            const statusEl = document.getElementById('demo-status');
            if (!statusEl.textContent.includes('Launching') && 
                !statusEl.textContent.includes('Clearing')) {{
                window.location.reload();
            }}
        }}, 15000);
        
        console.log('🐙 Inktrace Enhanced Dashboard with Collapsible Demo Controls Ready');
    </script>
</body>
</html>
        """

    async def render_communications(self, request: Request):
        """Render communications page"""
        if self.templates:
            try:
                return self.templates.TemplateResponse(
                    "communications.html",
                    {"request": request, "communications": list(
                        self.communication_log)}
                )
            except:
                pass

        return HTMLResponse("<h1>Communications Monitor</h1><p>Template not available</p>")

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


def main():
    """Main entry point for standalone operation"""
    import argparse

    parser = argparse.ArgumentParser(
        description="🐙 Inktrace Enhanced Wiretap Tentacle")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8003,
                        help="Port to run on")
    args = parser.parse_args()

    print("🐙 Starting Enhanced Inktrace Wiretap with Collapsible Demo Controls")
    print("=" * 70)
    print(f"🔍 Dashboard: http://{args.host}:{args.port}/dashboard")
    print(f"💬 Communications: http://{args.host}:{args.port}/communications")
    print(
        f"🛡️ Security Events: http://{args.host}:{args.port}/security-events")
    print(f"📊 API: http://{args.host}:{args.port}/api/agents")
    print(f"🎬 NEW: Collapsible demo controls (click 🎬 button)!")
    print(f"🕵️ FIXED: Enhanced stealth agent detection!")
    print(f"📋 NEW: Policy compliance demo!")
    print("=" * 70)

    tentacle = WiretapTentacle(port=args.port)
    uvicorn.run(tentacle.app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()
