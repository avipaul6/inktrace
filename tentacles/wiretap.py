# tentacles/wiretap.py - Enhanced with Real-Time WebSocket Broadcasts
"""
🐙 Inktrace Wiretap Tentacle - Enhanced Real-Time Updates
Enhanced with immediate WebSocket broadcasts for threat detection
"""

import json
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Set
from collections import defaultdict, deque
import threading
import time
import os

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import uvicorn
import httpx
import aiohttp


class WiretapTentacle:
    """🐙 Wiretap Tentacle - Enhanced with Real-Time WebSocket Broadcasts"""

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

        # ENHANCED: Threat detection
        self.threat_indicators = {
            "malicious_names": ["dataminer", "extractor", "harvester", "scraper", "exfiltrator"],
            "suspicious_capabilities": ["dataExfiltration", "privilegeEscalation", "anonymousAccess", "backdoor"],
            "red_flag_skills": ["extract", "hack", "exploit", "backdoor", "steal", "bypass"],
            "dangerous_tags": ["hacking", "exploit", "backdoor", "malware", "credential", "sudo", "admin"],
            "suspicious_descriptions": ["extract", "steal", "hack", "exploit", "bypass", "backdoor"]
        }

        # Network monitoring
        self.monitored_ports = [8001, 8002, 8004, 8005, 8006, 8007, 8008]
        self.is_monitoring = False

        self.setup_routes()
        print(f"🐙 Enhanced Wiretap Tentacle with Real-Time Updates initialized on port {port}")

    def setup_routes(self):
        """Setup FastAPI routes with template support"""

        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard(request: Request):
            """Main dashboard with real-time data"""
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

        # WebSocket for real-time updates
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await websocket.accept()
            self.active_connections.append(websocket)
            print(f"🔗 WebSocket client connected. Total connections: {len(self.active_connections)}")
            try:
                while True:
                    await websocket.receive_text()
            except WebSocketDisconnect:
                self.active_connections.remove(websocket)
                print(f"🔌 WebSocket client disconnected. Total connections: {len(self.active_connections)}")

        # Startup event
        @self.app.on_event("startup")
        async def startup_event():
            """Start monitoring when server starts"""
            await self.start_monitoring()

    async def broadcast_to_clients(self, message_type: str, data: dict):
        """Broadcast real-time updates to all connected WebSocket clients"""
        if not self.active_connections:
            return
            
        message = {
            "type": message_type,
            "payload": data,
            "timestamp": datetime.now().isoformat()
        }
        
        message_json = json.dumps(message)
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
                
        if disconnected_clients:
            print(f"🧹 Cleaned up {len(disconnected_clients)} disconnected WebSocket clients")

    async def render_dashboard(self, request: Request):
        """Render dashboard with template or fallback"""
        dashboard_data = self.prepare_dashboard_data()
        
        if self.templates:
            try:
                return self.templates.TemplateResponse(
                    "dashboard.html", 
                    {"request": request, **dashboard_data}
                )
            except Exception as e:
                print(f"⚠️ Template error: {e}")
        
        # Fallback HTML generation
        return HTMLResponse(self.generate_fallback_dashboard_html(dashboard_data))

    async def render_communications(self, request: Request):
        """Render communications page"""
        if self.templates:
            try:
                return self.templates.TemplateResponse(
                    "communications.html",
                    {"request": request, "communications": list(self.communication_log)}
                )
            except:
                pass
        
        return HTMLResponse(self.generate_fallback_communications_html())

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
        
        return HTMLResponse(self.generate_fallback_events_html())

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
        overall_score = sum(t["score"] for t in tentacle_scores) // len(tentacle_scores) if tentacle_scores else 75

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
            {"id": "T1", "name": "Identity", "score": base_score + 17 - (malicious_count * 10)},
            {"id": "T2", "name": "Data", "score": base_score + 3 - (malicious_count * 5)},
            {"id": "T3", "name": "Behavior", "score": base_score - 30 - (malicious_count * malicious_penalty)},
            {"id": "T4", "name": "Resilience", "score": base_score + 13 - (malicious_count * 3)},
            {"id": "T5", "name": "Supply Chain", "score": base_score - 4 - (malicious_count * 8)},
            {"id": "T6", "name": "Compliance", "score": base_score + 19 - (malicious_count * 2)},
            {"id": "T7", "name": "Threats", "score": base_score - 43 - (malicious_count * malicious_penalty)},
            {"id": "T8", "name": "Network", "score": base_score - 8 - (malicious_count * 12)}
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
                event_dict['timestamp'] = event_dict['timestamp'].isoformat()
            return event_dict
        return event

    async def analyze_agent_for_threats(self, agent_data: Dict) -> Dict:
        """Enhanced threat analysis for agents"""
        threat_analysis = {
            "is_malicious": False,
            "threat_score": 0,
            "security_alerts": [],
            "risk_factors": []
        }

        name = agent_data.get("name", "").lower()
        capabilities = agent_data.get("capabilities", [])
        description = agent_data.get("description", "").lower()

        # Check malicious names
        for malicious_name in self.threat_indicators["malicious_names"]:
            if malicious_name in name:
                threat_analysis["threat_score"] += 50
                threat_analysis["security_alerts"].append(f"Suspicious name: '{malicious_name}' detected")
                threat_analysis["risk_factors"].append("suspicious_name")

        # Check malicious capabilities
        for cap in capabilities:
            if cap in self.threat_indicators["suspicious_capabilities"]:
                threat_analysis["threat_score"] += 40
                threat_analysis["security_alerts"].append(f"Malicious capability: {cap}")
                threat_analysis["risk_factors"].append("malicious_capability")

        # Check description for red flags
        for red_flag in self.threat_indicators["red_flag_skills"]:
            if red_flag in description:
                threat_analysis["threat_score"] += 25
                threat_analysis["security_alerts"].append(f"Suspicious description contains: '{red_flag}'")
                threat_analysis["risk_factors"].append("suspicious_description")

        # Determine if malicious
        threat_analysis["is_malicious"] = threat_analysis["threat_score"] > 50

        return threat_analysis

    async def start_monitoring(self):
        """Start background monitoring"""
        self.is_monitoring = True
        asyncio.create_task(self.agent_discovery_loop())
        print("🔍 Enhanced agent discovery started with real-time threat detection and WebSocket broadcasts...")

    async def agent_discovery_loop(self):
        """Continuous agent discovery loop with real-time updates"""
        while self.is_monitoring:
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
                                    was_malicious = self.discovered_agents[agent_id].get("threat_analysis", {}).get("is_malicious", False)

                                # Store or update agent
                                self.discovered_agents[agent_id] = agent_data

                                # Generate security events for new agents or status changes
                                if is_new_agent or (threat_analysis["is_malicious"] and not was_malicious):
                                    event_type = "malicious_agent_detected" if threat_analysis["is_malicious"] else "agent_discovered"
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
                                    print(f"🚨 {event['description']} (Port: {port}, Threat Score: {threat_analysis.get('threat_score', 0)})")
                                    
                                    # ENHANCED: Broadcast real-time updates via WebSocket
                                    await self.broadcast_to_clients("security_event", {
                                        "event": self.serialize_event(event),
                                        "agent": agent_data
                                    })
                                    
                                    # Also broadcast agent update
                                    await self.broadcast_to_clients("agent_update", {
                                        "agent_id": agent_id,
                                        "agent": agent_data,
                                        "is_new": is_new_agent,
                                        "is_threat": threat_analysis["is_malicious"]
                                    })
                                    
                                    # Trigger dashboard refresh
                                    await self.broadcast_to_clients("dashboard_refresh", {
                                        "reason": "new_threat" if threat_analysis["is_malicious"] else "new_agent",
                                        "agent_name": agent_data.get('name', 'Unknown')
                                    })

                except Exception as e:
                    # Mark agent as offline if it was previously discovered
                    agent_id = f"agent_{port}"
                    if agent_id in self.discovered_agents:
                        if self.discovered_agents[agent_id]["status"] != "offline":
                            self.discovered_agents[agent_id]["status"] = "offline"
                            # Broadcast offline status
                            await self.broadcast_to_clients("agent_update", {
                                "agent_id": agent_id,
                                "agent": self.discovered_agents[agent_id],
                                "is_new": False,
                                "is_offline": True
                            })

            await asyncio.sleep(3)  # Check every 3 seconds

    def generate_fallback_dashboard_html(self, data: Dict) -> str:
        """Generate fallback dashboard HTML when templates aren't available"""
        agents_html = ""
        for agent_id, agent in data["agents"].items():
            is_malicious = agent.get("threat_analysis", {}).get("is_malicious", False)
            status_color = "#ef4444" if is_malicious else "#22c55e" if agent.get("status") == "active" else "#6b7280"
            
            agents_html += f"""
                <div style="margin: 1rem 0; padding: 1rem; border: 1px solid #374151; border-radius: 0.5rem; background: rgba(30, 41, 59, 0.5);">
                    <div style="display: flex; align-items: center;">
                        <div style="width: 8px; height: 8px; border-radius: 50%; background: {status_color}; margin-right: 1rem;"></div>
                        <div>
                            <div style="font-weight: 600;">{agent.get('name', 'Unknown')}</div>
                            <div style="font-size: 0.8rem; color: #94a3b8;">Port: {agent.get('port')} • Last seen: {agent.get('last_seen', 'Unknown')}</div>
                        </div>
                    </div>
                </div>
            """

        events_html = ""
        for event in list(data["security_events"])[:3]:
            icon = "🚨" if event.get("type") == "malicious_agent_detected" else "🔍"
            events_html += f"""
                <div style="margin: 1rem 0; padding: 1rem; border-left: 3px solid #60a5fa; background: rgba(30, 41, 59, 0.3);">
                    <div>{icon} {event.get('type', 'unknown').replace('_', ' ').upper()}</div>
                    <div style="font-size: 0.9rem; color: #94a3b8; margin: 0.5rem 0;">{event.get('description', '')}</div>
                    <div style="font-size: 0.8rem; color: #6b7280;">🕐 {event.get('timestamp', 'Unknown')}</div>
                </div>
            """

        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>🐙 Inktrace Agent Inspector</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ font-family: system-ui; background: #0f172a; color: #e2e8f0; margin: 0; padding: 2rem; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 2rem; padding: 2rem; background: linear-gradient(135deg, #1e293b 0%, #334155 100%); border-radius: 1rem; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); gap: 1.5rem; }}
        .card {{ background: linear-gradient(135deg, #1e293b 0%, #334155 100%); border-radius: 1rem; border: 1px solid #475569; padding: 1.5rem; }}
        .card-title {{ font-size: 1.2rem; font-weight: 600; margin-bottom: 1rem; display: flex; align-items: center; }}
        .nav {{ display: flex; justify-content: center; gap: 1rem; margin-bottom: 2rem; }}
        .nav a {{ color: #e2e8f0; text-decoration: none; padding: 0.75rem 1.5rem; background: rgba(51, 65, 85, 0.6); border-radius: 0.75rem; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐙 Inktrace Agent Inspector</h1>
            <p>Uncover hidden threats. One agent at a time.</p>
            <p style="color: #f59e0b; margin-top: 1rem;">⚠️ Using fallback dashboard - Templates not found</p>
            <p style="color: #22c55e; margin-top: 0.5rem;">🔗 Enhanced Real-Time Updates Active</p>
        </div>
        
        <nav class="nav">
            <a href="/">🏠 Dashboard</a>
            <a href="/communications">🔍 Communications</a>
            <a href="/security-events">📊 Security Events</a>
            <a href="/api/agents" target="_blank">🔌 API</a>
        </nav>
        
        <div class="grid">
            <div class="card">
                <div class="card-title">🤖 Discovered Agents</div>
                {agents_html or '<p style="color: #94a3b8;">No agents discovered yet...</p>'}
                <div style="margin-top: 1rem; padding-top: 1rem; border-top: 1px solid #374151;">
                    <strong>Total Agents: {len(data["agents"])}</strong>
                </div>
            </div>
            
            <div class="card">
                <div class="card-title">🛡️ Security Status</div>
                <div style="margin: 0.5rem 0;"><strong>Threat Level:</strong> <span style="color: {'#ef4444' if data['threat_level'] == 'CRITICAL' else '#22c55e'}">{data["threat_level"]}</span></div>
                <div style="margin: 0.5rem 0;"><strong>Malicious Agents:</strong> {data["malicious_count"]}</div>
                <div style="margin: 0.5rem 0;"><strong>Security Events:</strong> {len(data["security_events"])}</div>
                <div style="margin: 0.5rem 0;"><strong>A2A Protocol:</strong> <span style="color: #22c55e">Active</span></div>
                <div style="margin: 0.5rem 0;"><strong>WebSocket Clients:</strong> <span style="color: #60a5fa">{len(self.active_connections)}</span></div>
            </div>
            
            <div class="card">
                <div class="card-title">⚡ Recent Events</div>
                {events_html or '<p style="color: #94a3b8;">No events detected</p>'}
            </div>
        </div>
        
        <div style="margin-top: 2rem; padding: 1rem; background: #1e293b; border-radius: 0.5rem; text-align: center;">
            <h3>🚀 Enhanced Real-Time Features Active</h3>
            <p>✅ WebSocket real-time updates • ✅ Instant threat detection • ✅ Auto-refresh dashboard</p>
            <p>To enable full template experience, ensure template files exist in templates/ directory.</p>
        </div>
    </div>
    
    <script src="/static/js/dashboard.js"></script>
    <script>
        // Enhanced fallback real-time updates
        console.log('🐙 Enhanced Inktrace Dashboard with real-time updates');
        
        // Faster refresh for fallback mode
        setInterval(() => {{ 
            window.location.reload(); 
        }}, 3000);
    </script>
</body>
</html>
        """

    def generate_fallback_communications_html(self) -> str:
        """Generate fallback communications HTML"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>🐙 Communications Monitor</title>
    <style>body { font-family: system-ui; background: #0f172a; color: #e2e8f0; padding: 2rem; }</style>
</head>
<body>
    <h1>🐙 Communications Monitor</h1>
    <p>Template-based communications page not available. Using fallback with real-time updates.</p>
    <p><a href="/">← Back to Dashboard</a></p>
    <script>setInterval(() => window.location.reload(), 5000);</script>
</body>
</html>
        """

    def generate_fallback_events_html(self) -> str:
        """Generate fallback events HTML"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>🐙 Security Events</title>
    <style>body { font-family: system-ui; background: #0f172a; color: #e2e8f0; padding: 2rem; }</style>
</head>
<body>
    <h1>🐙 Security Events Monitor</h1>
    <p>Template-based events page not available. Using fallback with real-time updates.</p>
    <p><a href="/">← Back to Dashboard</a></p>
    <script>setInterval(() => window.location.reload(), 5000);</script>
</body>
</html>
        """


def main():
    """Main entry point for standalone operation"""
    import argparse
    
    parser = argparse.ArgumentParser(description="🐙 Inktrace Wiretap Tentacle")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8003, help="Port to run on")
    args = parser.parse_args()
    
    print("🐙 Starting Enhanced Inktrace Wiretap Tentacle")
    print("=" * 60)
    print(f"🔍 Dashboard: http://{args.host}:{args.port}/dashboard")
    print(f"💬 Communications: http://{args.host}:{args.port}/communications")
    print(f"🛡️ Security Events: http://{args.host}:{args.port}/security-events")
    print(f"📊 API: http://{args.host}:{args.port}/api/agents")
    print(f"🚀 NEW: Real-time WebSocket broadcasts for instant threat detection!")
    print("=" * 60)
    
    tentacle = WiretapTentacle(port=args.port)
    uvicorn.run(tentacle.app, host=args.host, port=args.port, log_level="info")


if __name__ == "__main__":
    main()