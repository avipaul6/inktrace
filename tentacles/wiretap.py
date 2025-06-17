# tentacles/wiretap.py - WIRETAP TENTACLE
"""
🐙 Inktrace Wiretap Tentacle - Real-time A2A Communication Monitoring
tentacles/wiretap.py

This is the critical monitoring tentacle that provides real-time visibility
into all Agent2Agent communications across the ecosystem.
"""

import json
import asyncio
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Set
from collections import defaultdict, deque
import argparse
import threading
import time

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request, Response
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import httpx
import aiohttp

class WiretapTentacle:
    """🐙 Wiretap Tentacle - The All-Seeing Eye of Agent Communications"""
    
    def __init__(self, port: int = 8003):
        self.port = port
        self.app = FastAPI(title="🐙 Inktrace Wiretap Tentacle")
        self.active_connections: List[WebSocket] = []
        
        # Real-time monitoring data
        self.discovered_agents: Dict[str, Dict] = {}
        self.communication_log: deque = deque(maxlen=1000)  # Last 1000 communications
        self.security_events: deque = deque(maxlen=500)    # Last 500 security events
        self.performance_metrics: Dict = defaultdict(list)
        
        # Network monitoring
        self.monitored_ports = [8001, 8002, 8004, 8005, 8006, 8007, 8008]
        self.is_monitoring = False
        
        self.setup_routes()
        print(f"🐙 Wiretap Tentacle initialized on port {port}")
    
    def setup_routes(self):
        """Setup FastAPI routes for dashboard and monitoring"""
        
        @self.app.get("/", response_class=HTMLResponse)
        async def dashboard():
            return self.generate_dashboard_html()
        
        @self.app.get("/dashboard", response_class=HTMLResponse)
        async def dashboard_alias():
            return self.generate_dashboard_html()
        
        @self.app.get("/api/agents")
        async def get_agents():
            return {"agents": self.discovered_agents}
        
        @self.app.get("/api/communications")
        async def get_communications():
            return {"communications": list(self.communication_log)}
        
        @self.app.get("/api/security-events")
        async def get_security_events():
            return {"events": list(self.security_events)}
        
        @self.app.get("/api/metrics")
        async def get_metrics():
            return {"metrics": dict(self.performance_metrics)}
        
        @self.app.websocket("/ws")
        async def websocket_endpoint(websocket: WebSocket):
            await self.connect_websocket(websocket)
        
        @self.app.get("/communications", response_class=HTMLResponse)
        async def communications_view():
            return self.generate_communications_html()
        
        @self.app.get("/security-events", response_class=HTMLResponse)
        async def security_events_view():
            return self.generate_security_events_html()
        
        @self.app.on_event("startup")
        async def start_monitoring():
            """Start background monitoring when server starts"""
            self.start_background_monitoring()
    
    async def connect_websocket(self, websocket: WebSocket):
        """Handle WebSocket connections for real-time updates"""
        await websocket.accept()
        self.active_connections.append(websocket)
        try:
            while True:
                await websocket.receive_text()  # Keep connection alive
        except WebSocketDisconnect:
            self.active_connections.remove(websocket)
    
    async def broadcast_update(self, event_type: str, data: Dict):
        """Broadcast real-time updates to connected clients"""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        disconnected = []
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                disconnected.append(connection)
        
        # Remove disconnected connections
        for conn in disconnected:
            if conn in self.active_connections:
                self.active_connections.remove(conn)
    
    def start_background_monitoring(self):
        """Start background monitoring threads"""
        if not self.is_monitoring:
            self.is_monitoring = True
            
            # Start agent discovery
            discovery_thread = threading.Thread(target=self.continuous_agent_discovery, daemon=True)
            discovery_thread.start()
            
            # Start communication monitoring
            monitor_thread = threading.Thread(target=self.monitor_communications, daemon=True)
            monitor_thread.start()
            
            print("🔍 Background monitoring started")
    
    def continuous_agent_discovery(self):
        """Continuously discover and monitor A2A agents"""
        while self.is_monitoring:
            try:
                asyncio.run(self.discover_agents())
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"⚠️ Agent discovery error: {e}")
                time.sleep(10)
    
    async def discover_agents(self):
        """Discover A2A agents across monitored ports"""
        for port in self.monitored_ports:
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get(f"http://localhost:{port}/.well-known/agent.json")
                    
                    if response.status_code == 200:
                        agent_card = response.json()
                        agent_id = f"agent-{port}"
                        
                        # Check if this is a new agent or status change
                        is_new = agent_id not in self.discovered_agents
                        
                        self.discovered_agents[agent_id] = {
                            "port": port,
                            "name": agent_card.get("name", f"Agent-{port}"),
                            "description": agent_card.get("description", ""),
                            "capabilities": agent_card.get("capabilities", {}),
                            "url": agent_card.get("url", f"http://localhost:{port}"),
                            "last_seen": datetime.now().isoformat(),
                            "status": "active",
                            "agent_card": agent_card
                        }
                        
                        if is_new:
                            # Log agent discovery
                            event = {
                                "id": str(uuid.uuid4()),
                                "timestamp": datetime.now().isoformat(),
                                "type": "agent_discovered",
                                "agent_id": agent_id,
                                "agent_name": agent_card.get("name"),
                                "port": port,
                                "severity": "info"
                            }
                            self.security_events.append(event)
                            
                            # Broadcast real-time update
                            await self.broadcast_update("agent_discovered", {
                                "agent_id": agent_id,
                                "agent": self.discovered_agents[agent_id]
                            })
                    
                    else:
                        # Agent not responding, mark as inactive
                        agent_id = f"agent-{port}"
                        if agent_id in self.discovered_agents:
                            self.discovered_agents[agent_id]["status"] = "inactive"
                            self.discovered_agents[agent_id]["last_seen"] = datetime.now().isoformat()
                            
            except Exception as e:
                # Port not accessible, agent likely offline
                agent_id = f"agent-{port}"
                if agent_id in self.discovered_agents:
                    self.discovered_agents[agent_id]["status"] = "offline"
    
    def monitor_communications(self):
        """Monitor A2A communications (simplified implementation)"""
        while self.is_monitoring:
            try:
                # Simulate communication monitoring
                # In a real implementation, this would intercept HTTP traffic
                self.simulate_communication_monitoring()
                time.sleep(3)
            except Exception as e:
                print(f"⚠️ Communication monitoring error: {e}")
                time.sleep(5)
    
    def simulate_communication_monitoring(self):
        """Simulate communication monitoring for demo purposes"""
        # This would be replaced with actual network monitoring
        
        # Check for recent activity by attempting to trigger communications
        active_agents = [agent for agent in self.discovered_agents.values() 
                        if agent["status"] == "active"]
        
        if len(active_agents) >= 2:
            # Simulate inter-agent communication detection
            comm_event = {
                "id": str(uuid.uuid4()),
                "timestamp": datetime.now().isoformat(),
                "type": "a2a_communication",
                "source_agent": active_agents[0]["name"],
                "target_agent": active_agents[1]["name"] if len(active_agents) > 1 else "Unknown",
                "method": "tasks/send",
                "status": "completed",
                "response_time_ms": 45,
                "data_size": 1234
            }
            
            self.communication_log.append(comm_event)
            
            # Check for security events
            if "admin" in comm_event.get("payload", "").lower():
                security_event = {
                    "id": str(uuid.uuid4()),
                    "timestamp": datetime.now().isoformat(),
                    "type": "suspicious_communication",
                    "description": "Admin-related communication detected",
                    "severity": "medium",
                    "source": comm_event["source_agent"],
                    "target": comm_event["target_agent"]
                }
                self.security_events.append(security_event)
    
    def generate_dashboard_html(self) -> str:
        """Generate the main monitoring dashboard"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>🐙 Inktrace Wiretap Dashboard</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body {{ 
            font-family: 'Segoe UI', Arial, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            color: white;
            min-height: 100vh;
        }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 30px; }}
        .header h1 {{ font-size: 2.5em; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.3); }}
        .tagline {{ font-size: 1.2em; opacity: 0.9; margin-top: 10px; }}
        .grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(400px, 1fr)); gap: 20px; }}
        .card {{ 
            background: rgba(255,255,255,0.1); 
            backdrop-filter: blur(10px);
            border-radius: 15px; 
            padding: 20px; 
            border: 1px solid rgba(255,255,255,0.2);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        .card h3 {{ margin-top: 0; color: #4fc3f7; }}
        .status {{ padding: 4px 12px; border-radius: 20px; font-size: 0.9em; font-weight: bold; }}
        .status.active {{ background: #4caf50; color: white; }}
        .status.inactive {{ background: #ff9800; color: white; }}
        .status.offline {{ background: #f44336; color: white; }}
        .metric {{ display: flex; justify-content: space-between; margin: 10px 0; }}
        .metric-value {{ font-weight: bold; color: #81c784; }}
        .event {{ 
            background: rgba(255,255,255,0.05); 
            padding: 10px; 
            margin: 5px 0; 
            border-radius: 8px; 
            border-left: 4px solid #2196f3;
        }}
        .event.warning {{ border-left-color: #ff9800; }}
        .event.error {{ border-left-color: #f44336; }}
        .nav {{ margin-bottom: 20px; text-align: center; }}
        .nav a {{ 
            color: white; 
            text-decoration: none; 
            margin: 0 15px; 
            padding: 10px 20px; 
            background: rgba(255,255,255,0.1); 
            border-radius: 25px; 
            transition: all 0.3s;
        }}
        .nav a:hover {{ background: rgba(255,255,255,0.2); }}
        .realtime {{ animation: pulse 2s infinite; }}
        @keyframes pulse {{ 0%, 100% {{ opacity: 1; }} 50% {{ opacity: 0.7; }} }}
        .octopus {{ font-size: 2em; margin-right: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1><span class="octopus">🐙</span>Inktrace Wiretap Intelligence</h1>
            <div class="tagline">Real-time Agent2Agent Communication Monitoring</div>
        </div>
        
        <div class="nav">
            <a href="/dashboard">🏠 Dashboard</a>
            <a href="/communications">💬 Communications</a>
            <a href="/security-events">🛡️ Security Events</a>
            <a href="/api/agents" target="_blank">📊 API</a>
        </div>

        <div class="grid">
            <div class="card">
                <h3>🤖 Discovered Agents</h3>
                <div id="agents-list">
                    <div class="realtime">Loading agent discovery...</div>
                </div>
            </div>

            <div class="card">
                <h3>📡 Communication Activity</h3>
                <div id="communications-summary">
                    <div class="metric">
                        <span>Active Connections:</span>
                        <span class="metric-value" id="active-connections">0</span>
                    </div>
                    <div class="metric">
                        <span>Messages Today:</span>
                        <span class="metric-value" id="messages-today">0</span>
                    </div>
                    <div class="metric">
                        <span>Average Response Time:</span>
                        <span class="metric-value" id="avg-response">0ms</span>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>🛡️ Security Status</h3>
                <div id="security-summary">
                    <div class="metric">
                        <span>Security Events:</span>
                        <span class="metric-value" id="security-events-count">0</span>
                    </div>
                    <div class="metric">
                        <span>Threat Level:</span>
                        <span class="metric-value" id="threat-level">LOW</span>
                    </div>
                    <div class="metric">
                        <span>Last Scan:</span>
                        <span class="metric-value" id="last-scan">Just now</span>
                    </div>
                </div>
            </div>

            <div class="card">
                <h3>📊 Recent Events</h3>
                <div id="recent-events">
                    <div class="realtime">Monitoring real-time events...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // WebSocket connection for real-time updates
        const ws = new WebSocket(`ws://${{window.location.host}}/ws`);
        
        ws.onmessage = function(event) {{
            const data = JSON.parse(event.data);
            handleRealTimeUpdate(data);
        }};

        function handleRealTimeUpdate(update) {{
            console.log('Real-time update:', update);
            if (update.type === 'agent_discovered') {{
                updateAgentsList();
            }}
            updateDashboard();
        }}

        // Load initial data
        async function loadDashboardData() {{
            try {{
                const [agents, communications, events] = await Promise.all([
                    fetch('/api/agents').then(r => r.json()),
                    fetch('/api/communications').then(r => r.json()),
                    fetch('/api/security-events').then(r => r.json())
                ]);

                updateAgentsList(agents.agents);
                updateCommunications(communications.communications);
                updateSecurityEvents(events.events);
            }} catch (error) {{
                console.error('Error loading data:', error);
            }}
        }}

        function updateAgentsList(agents = {{}}) {{
            const container = document.getElementById('agents-list');
            if (Object.keys(agents).length === 0) {{
                container.innerHTML = '<div class="realtime">No agents discovered yet...</div>';
                return;
            }}

            const html = Object.entries(agents).map(([id, agent]) => `
                <div class="event">
                    <strong>${{agent.name}}</strong>
                    <span class="status ${{agent.status}}">${{agent.status.toUpperCase()}}</span>
                    <div style="font-size: 0.9em; opacity: 0.8; margin-top: 5px;">
                        Port: ${{agent.port}} | Last seen: ${{new Date(agent.last_seen).toLocaleTimeString()}}
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = html;
        }}

        function updateCommunications(communications = []) {{
            document.getElementById('active-connections').textContent = 
                Object.keys(agents || {{}}).filter(id => agents[id].status === 'active').length;
            document.getElementById('messages-today').textContent = communications.length;
            document.getElementById('avg-response').textContent = 
                communications.length > 0 ? '45ms' : '0ms';
        }}

        function updateSecurityEvents(events = []) {{
            document.getElementById('security-events-count').textContent = events.length;
            document.getElementById('threat-level').textContent = 
                events.some(e => e.severity === 'high') ? 'HIGH' : 
                events.some(e => e.severity === 'medium') ? 'MEDIUM' : 'LOW';
            document.getElementById('last-scan').textContent = 'Just now';

            // Show recent events
            const container = document.getElementById('recent-events');
            if (events.length === 0) {{
                container.innerHTML = '<div class="realtime">No security events detected</div>';
                return;
            }}

            const recentEvents = events.slice(-5).reverse();
            const html = recentEvents.map(event => `
                <div class="event ${{event.severity}}">
                    <strong>${{event.type.replace('_', ' ').toUpperCase()}}</strong>
                    <div style="font-size: 0.9em; margin-top: 5px;">
                        ${{event.description || event.type}}
                    </div>
                    <div style="font-size: 0.8em; opacity: 0.7;">
                        ${{new Date(event.timestamp).toLocaleTimeString()}}
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = html;
        }}

        function updateDashboard() {{
            loadDashboardData();
        }}

        // Load data on page load
        loadDashboardData();
        
        // Refresh data every 5 seconds
        setInterval(updateDashboard, 5000);
    </script>
</body>
</html>
        """
    
    def generate_communications_html(self) -> str:
        """Generate communications monitoring page"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>🐙 Agent Communications Monitor</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: white; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .back-link { color: #4fc3f7; text-decoration: none; margin-bottom: 20px; display: inline-block; }
        .communication { 
            background: rgba(255,255,255,0.1); 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 8px; 
            border-left: 4px solid #2196f3;
        }
        .comm-header { display: flex; justify-content: space-between; align-items: center; }
        .comm-details { margin-top: 10px; font-size: 0.9em; opacity: 0.8; }
        .status-success { border-left-color: #4caf50; }
        .status-error { border-left-color: #f44336; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/dashboard" class="back-link">← Back to Dashboard</a>
        <div class="header">
            <h1>🐙 Agent2Agent Communications</h1>
            <p>Real-time monitoring of inter-agent messages</p>
        </div>
        
        <div id="communications-list">
            <div style="text-align: center; padding: 40px;">
                Loading communications data...
            </div>
        </div>
    </div>

    <script>
        async function loadCommunications() {
            try {
                const response = await fetch('/api/communications');
                const data = await response.json();
                displayCommunications(data.communications);
            } catch (error) {
                console.error('Error loading communications:', error);
            }
        }

        function displayCommunications(communications) {
            const container = document.getElementById('communications-list');
            
            if (communications.length === 0) {
                container.innerHTML = '<div style="text-align: center; padding: 40px;">No communications detected yet</div>';
                return;
            }

            const html = communications.reverse().map(comm => `
                <div class="communication status-${comm.status}">
                    <div class="comm-header">
                        <strong>${comm.source_agent} → ${comm.target_agent}</strong>
                        <span>${new Date(comm.timestamp).toLocaleString()}</span>
                    </div>
                    <div class="comm-details">
                        Method: ${comm.method} | Status: ${comm.status} | 
                        Response Time: ${comm.response_time_ms}ms | 
                        Data Size: ${comm.data_size} bytes
                    </div>
                </div>
            `).join('');
            
            container.innerHTML = html;
        }

        loadCommunications();
        setInterval(loadCommunications, 3000);
    </script>
</body>
</html>
        """
    
    def generate_security_events_html(self) -> str:
        """Generate security events monitoring page"""
        return """
<!DOCTYPE html>
<html>
<head>
    <title>🐙 Security Events Monitor</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 0; padding: 20px; background: #1a1a2e; color: white; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { text-align: center; margin-bottom: 30px; }
        .back-link { color: #4fc3f7; text-decoration: none; margin-bottom: 20px; display: inline-block; }
        .event { 
            background: rgba(255,255,255,0.1); 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 8px; 
        }
        .event.info { border-left: 4px solid #2196f3; }
        .event.warning { border-left: 4px solid #ff9800; }
        .event.error { border-left: 4px solid #f44336; }
        .event.high { border-left: 4px solid #e91e63; }
        .event-header { display: flex; justify-content: space-between; align-items: center; }
        .severity { padding: 4px 8px; border-radius: 4px; font-size: 0.8em; font-weight: bold; }
        .severity.info { background: #2196f3; }
        .severity.medium { background: #ff9800; }
        .severity.high { background: #f44336; }
    </style>
</head>
<body>
    <div class="container">
        <a href="/dashboard" class="back-link">← Back to Dashboard</a>
        <div class="header">
            <h1>🛡️ Security Events Monitor</h1>
            <p>Real-time security event detection and analysis</p>
        </div>
        
        <div id="events-list">
            <div style="text-align: center; padding: 40px;">
                Loading security events...
            </div>
        </div>
    </div>

    <script>
        async function loadSecurityEvents() {
            try {
                const response = await fetch('/api/security-events');
                const data = await response.json();
                displayEvents(data.events);
            } catch (error) {
                console.error('Error loading events:', error);
            }
        }

        function displayEvents(events) {
            const container = document.getElementById('events-list');
            
            if (events.length === 0) {
                container.innerHTML = '<div style="text-align: center; padding: 40px;">No security events detected</div>';
                return;
            }

            const html = events.reverse().map(event => `
                <div class="event ${event.severity}">
                    <div class="event-header">
                        <strong>${event.type.replace('_', ' ').toUpperCase()}</strong>
                        <div>
                            <span class="severity ${event.severity}">${event.severity.toUpperCase()}</span>
                            <span style="margin-left: 10px;">${new Date(event.timestamp).toLocaleString()}</span>
                        </div>
                    </div>
                    <div style="margin-top: 10px;">
                        ${event.description || event.type}
                    </div>
                    ${event.source ? `<div style="margin-top: 5px; font-size: 0.9em; opacity: 0.7;">
                        Source: ${event.source} → ${event.target || 'Unknown'}
                    </div>` : ''}
                </div>
            `).join('');
            
            container.innerHTML = html;
        }

        loadSecurityEvents();
        setInterval(loadSecurityEvents, 3000);
    </script>
</body>
</html>
        """

def main():
    """Launch the Wiretap Tentacle"""
    parser = argparse.ArgumentParser(description="🐙 Inktrace Wiretap Tentacle")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8003, help="Port to bind to")
    args = parser.parse_args()
    
    print("🐙 Starting Inktrace Wiretap Tentacle")
    print("=" * 50)
    print(f"🔍 Dashboard: http://{args.host}:{args.port}/dashboard")
    print(f"💬 Communications: http://{args.host}:{args.port}/communications")
    print(f"🛡️ Security Events: http://{args.host}:{args.port}/security-events")
    print(f"📊 API: http://{args.host}:{args.port}/api/agents")
    print("=" * 50)
    
    # Create tentacle
    tentacle = WiretapTentacle(port=args.port)
    
    # Run server
    uvicorn.run(tentacle.app, host=args.host, port=args.port, log_level="info")

if __name__ == "__main__":
    main()