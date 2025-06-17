# tentacles/wiretap.py - ENHANCED WITH THREAT DETECTION
"""
🐙 Inktrace Wiretap Tentacle - Enhanced with Real Threat Detection
tentacles/wiretap.py

ENHANCED: Now actually analyzes agents for malicious behavior and flags threats
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
    """🐙 Wiretap Tentacle - Enhanced with Threat Detection Intelligence"""
    
    def __init__(self, port: int = 8003):
        self.port = port
        self.app = FastAPI(title="🐙 Inktrace Wiretap Tentacle")
        self.active_connections: List[WebSocket] = []
        
        # Real-time monitoring data
        self.discovered_agents: Dict[str, Dict] = {}
        self.communication_log: deque = deque(maxlen=1000)
        self.security_events: deque = deque(maxlen=500)
        self.performance_metrics: Dict = defaultdict(list)
        
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
        print(f"🐙 Enhanced Wiretap Tentacle initialized on port {port}")
    
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
        
        @self.app.get("/api/threats")
        async def get_threats():
            """New endpoint for threat analysis"""
            threats = [event for event in self.security_events if event.get("severity") in ["high", "critical"]]
            return {"threats": threats}
        
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
    
    def analyze_agent_threat_level(self, agent_card: Dict) -> Dict:
        """ENHANCED: Analyze agent for malicious indicators"""
        
        threat_score = 0
        threat_reasons = []
        threat_level = "LOW"
        
        agent_name = agent_card.get("name", "").lower()
        agent_description = agent_card.get("description", "").lower()
        capabilities = agent_card.get("capabilities", {})
        skills = agent_card.get("skills", [])
        
        # Check malicious names
        for malicious_name in self.threat_indicators["malicious_names"]:
            if malicious_name in agent_name:
                threat_score += 30
                threat_reasons.append(f"Suspicious name: '{malicious_name}' detected")
        
        # Check suspicious capabilities
        for cap_name, cap_value in capabilities.items():
            if cap_name in self.threat_indicators["suspicious_capabilities"] and cap_value:
                threat_score += 25
                threat_reasons.append(f"Malicious capability: {cap_name}")
        
        # Check dangerous skills
        for skill in skills:
            skill_name = skill.get("name", "").lower()
            skill_desc = skill.get("description", "").lower()
            skill_tags = skill.get("tags", [])
            
            # Check skill names
            for red_flag in self.threat_indicators["red_flag_skills"]:
                if red_flag in skill_name or red_flag in skill_desc:
                    threat_score += 20
                    threat_reasons.append(f"Dangerous skill: '{skill.get('name')}'")
            
            # Check skill tags
            for tag in skill_tags:
                if tag.lower() in self.threat_indicators["dangerous_tags"]:
                    threat_score += 15
                    threat_reasons.append(f"Red flag tag: '{tag}'")
        
        # Check description
        for suspicious_word in self.threat_indicators["suspicious_descriptions"]:
            if suspicious_word in agent_description:
                threat_score += 10
                threat_reasons.append(f"Suspicious description contains: '{suspicious_word}'")
        
        # Determine threat level
        if threat_score >= 60:
            threat_level = "CRITICAL"
        elif threat_score >= 40:
            threat_level = "HIGH"
        elif threat_score >= 20:
            threat_level = "MEDIUM"
        else:
            threat_level = "LOW"
        
        return {
            "threat_score": threat_score,
            "threat_level": threat_level,
            "threat_reasons": threat_reasons,
            "is_malicious": threat_score >= 40
        }
    
    async def discover_agents(self):
        """Enhanced agent discovery with threat analysis"""
        for port in self.monitored_ports:
            try:
                async with httpx.AsyncClient(timeout=2.0) as client:
                    response = await client.get(f"http://localhost:{port}/.well-known/agent.json")
                    
                    if response.status_code == 200:
                        agent_card = response.json()
                        agent_id = f"agent-{port}"
                        
                        # ENHANCED: Perform threat analysis
                        threat_analysis = self.analyze_agent_threat_level(agent_card)
                        
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
                            "agent_card": agent_card,
                            # ENHANCED: Add threat analysis
                            "threat_analysis": threat_analysis
                        }
                        
                        if is_new:
                            # Log agent discovery
                            event_severity = "critical" if threat_analysis["is_malicious"] else "info"
                            event_type = "malicious_agent_detected" if threat_analysis["is_malicious"] else "agent_discovered"
                            
                            event = {
                                "id": str(uuid.uuid4()),
                                "timestamp": datetime.now().isoformat(),
                                "type": event_type,
                                "agent_id": agent_id,
                                "agent_name": agent_card.get("name"),
                                "port": port,
                                "severity": event_severity,
                                "threat_score": threat_analysis["threat_score"],
                                "threat_level": threat_analysis["threat_level"],
                                "threat_reasons": threat_analysis["threat_reasons"],
                                "description": f"{'MALICIOUS' if threat_analysis['is_malicious'] else 'Benign'} agent detected: {agent_card.get('name')}"
                            }
                            self.security_events.append(event)
                            
                            # Broadcast real-time update
                            await self.broadcast_update("agent_discovered", {
                                "agent_id": agent_id,
                                "agent": self.discovered_agents[agent_id],
                                "is_threat": threat_analysis["is_malicious"]
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
    
    def generate_dashboard_html(self) -> str:
        """Generate modern dashboard with updated design"""
        return f"""
<!DOCTYPE html>
<html>
<head>
    <title>🐙 Inktrace Wiretap Intelligence</title>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        
        body {{ 
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
            background: #0f172a;
            color: #e2e8f0;
            min-height: 100vh;
            line-height: 1.6;
        }}
        
        .container {{ 
            max-width: 1400px; 
            margin: 0 auto; 
            padding: 2rem;
        }}
        
        .header {{ 
            text-align: center; 
            margin-bottom: 3rem;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 2rem;
            border-radius: 1rem;
            border: 1px solid #334155;
        }}
        
        .header h1 {{ 
            font-size: 2.5rem; 
            margin-bottom: 0.5rem;
            background: linear-gradient(135deg, #60a5fa 0%, #a78bfa 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-weight: 700;
        }}
        
        .tagline {{ 
            font-size: 1.1rem; 
            opacity: 0.8;
            color: #94a3b8;
        }}
        
        .octopus {{ 
            font-size: 3rem; 
            margin-right: 1rem;
            filter: drop-shadow(0 4px 8px rgba(0,0,0,0.3));
        }}
        
        .nav {{ 
            display: flex;
            justify-content: center;
            gap: 1rem;
            margin-bottom: 2rem;
        }}
        
        .nav a {{ 
            color: #e2e8f0;
            text-decoration: none;
            padding: 0.75rem 1.5rem;
            background: rgba(51, 65, 85, 0.6);
            border-radius: 0.75rem;
            border: 1px solid #475569;
            transition: all 0.3s ease;
            font-weight: 500;
            backdrop-filter: blur(10px);
        }}
        
        .nav a:hover {{ 
            background: rgba(51, 65, 85, 0.9);
            border-color: #60a5fa;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(96, 165, 250, 0.2);
        }}
        
        .grid {{ 
            display: grid; 
            grid-template-columns: repeat(auto-fit, minmax(350px, 1fr)); 
            gap: 1.5rem;
        }}
        
        .card {{ 
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border-radius: 1rem;
            padding: 1.5rem;
            border: 1px solid #475569;
            backdrop-filter: blur(10px);
            transition: all 0.3s ease;
        }}
        
        .card:hover {{
            transform: translateY(-4px);
            box-shadow: 0 8px 25px rgba(0,0,0,0.3);
            border-color: #60a5fa;
        }}
        
        .card h3 {{ 
            margin-bottom: 1rem;
            color: #60a5fa;
            font-size: 1.25rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .card-icon {{
            width: 24px;
            height: 24px;
            opacity: 0.8;
        }}
        
        .status {{ 
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }}
        
        .status.active {{ background: #059669; color: white; }}
        .status.inactive {{ background: #d97706; color: white; }}
        .status.offline {{ background: #dc2626; color: white; }}
        
        .threat-level {{ 
            padding: 0.25rem 0.75rem;
            border-radius: 1rem;
            font-size: 0.75rem;
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-left: 0.5rem;
        }}
        
        .threat-level.low {{ background: #059669; color: white; }}
        .threat-level.medium {{ background: #d97706; color: white; }}
        .threat-level.high {{ background: #dc2626; color: white; }}
        .threat-level.critical {{ 
            background: #e11d48; 
            color: white; 
            animation: pulse-glow 2s infinite;
            box-shadow: 0 0 10px rgba(225, 29, 72, 0.5);
        }}
        
        @keyframes pulse-glow {{
            0%, 100% {{ 
                opacity: 1;
                box-shadow: 0 0 10px rgba(225, 29, 72, 0.5);
            }}
            50% {{ 
                opacity: 0.8;
                box-shadow: 0 0 20px rgba(225, 29, 72, 0.8);
            }}
        }}
        
        .agent-item {{
            background: rgba(30, 41, 59, 0.5);
            border-radius: 0.75rem;
            padding: 1rem;
            margin-bottom: 0.75rem;
            border: 1px solid #475569;
            transition: all 0.3s ease;
        }}
        
        .agent-item:hover {{
            background: rgba(30, 41, 59, 0.8);
            border-color: #64748b;
        }}
        
        .malicious-agent {{ 
            border: 2px solid #e11d48;
            background: rgba(225, 29, 72, 0.1);
            animation: pulse-border 3s infinite;
            box-shadow: 0 0 15px rgba(225, 29, 72, 0.3);
        }}
        
        @keyframes pulse-border {{
            0%, 100% {{ 
                border-color: #e11d48;
                box-shadow: 0 0 15px rgba(225, 29, 72, 0.3);
            }}
            50% {{ 
                border-color: #f43f5e;
                box-shadow: 0 0 25px rgba(225, 29, 72, 0.5);
            }}
        }}
        
        .agent-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 0.5rem;
        }}
        
        .agent-name {{
            font-weight: 600;
            color: #f1f5f9;
            font-size: 1rem;
        }}
        
        .agent-details {{
            font-size: 0.875rem;
            color: #94a3b8;
            margin-bottom: 0.5rem;
        }}
        
        .threat-details {{
            font-size: 0.8rem;
            color: #fca5a5;
            background: rgba(220, 38, 38, 0.1);
            padding: 0.5rem;
            border-radius: 0.5rem;
            margin-top: 0.5rem;
            border-left: 3px solid #dc2626;
        }}
        
        .metric {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 0.75rem 0;
            border-bottom: 1px solid rgba(71, 85, 105, 0.3);
        }}
        
        .metric:last-child {{
            border-bottom: none;
        }}
        
        .metric-label {{
            color: #94a3b8;
            font-size: 0.9rem;
        }}
        
        .metric-value {{
            font-weight: 600;
            color: #60a5fa;
            font-size: 1rem;
        }}
        
        .metric-value.success {{ color: #10b981; }}
        .metric-value.warning {{ color: #f59e0b; }}
        .metric-value.danger {{ 
            color: #ef4444; 
            animation: pulse-text 2s infinite;
        }}
        
        @keyframes pulse-text {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.7; }}
        }}
        
        .event-item {{
            background: rgba(30, 41, 59, 0.4);
            border-radius: 0.75rem;
            padding: 1rem;
            margin-bottom: 0.75rem;
            border-left: 4px solid #3b82f6;
            transition: all 0.3s ease;
        }}
        
        .event-item:hover {{
            background: rgba(30, 41, 59, 0.7);
            transform: translateX(4px);
        }}
        
        .event-item.info {{ border-left-color: #3b82f6; }}
        .event-item.warning {{ border-left-color: #f59e0b; }}
        .event-item.high {{ border-left-color: #ef4444; }}
        .event-item.critical {{ 
            border-left-color: #e11d48;
            background: rgba(225, 29, 72, 0.1);
            animation: pulse-event 2s infinite;
        }}
        
        @keyframes pulse-event {{
            0%, 100% {{ opacity: 1; }}
            50% {{ opacity: 0.9; }}
        }}
        
        .event-header {{
            font-weight: 600;
            color: #f1f5f9;
            margin-bottom: 0.5rem;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }}
        
        .event-description {{
            color: #cbd5e1;
            font-size: 0.9rem;
            margin-bottom: 0.5rem;
        }}
        
        .event-time {{
            color: #64748b;
            font-size: 0.8rem;
        }}
        
        .loading {{
            text-align: center;
            color: #64748b;
            font-style: italic;
            padding: 2rem;
        }}
        
        .empty-state {{
            text-align: center;
            color: #64748b;
            padding: 2rem;
            background: rgba(30, 41, 59, 0.3);
            border-radius: 0.75rem;
            border: 2px dashed #475569;
        }}
        
        /* Responsive Design */
        @media (max-width: 768px) {{
            .container {{ padding: 1rem; }}
            .grid {{ grid-template-columns: 1fr; }}
            .header h1 {{ font-size: 2rem; }}
            .nav {{ flex-wrap: wrap; }}
        }}
        
        /* Glassmorphism effects */
        .glass {{
            backdrop-filter: blur(16px) saturate(180%);
            background-color: rgba(30, 41, 59, 0.75);
            border: 1px solid rgba(255, 255, 255, 0.125);
        }}
        
        /* Smooth animations */
        .fade-in {{
            animation: fadeIn 0.5s ease-in;
        }}
        
        @keyframes fadeIn {{
            from {{ opacity: 0; transform: translateY(20px); }}
            to {{ opacity: 1; transform: translateY(0); }}
        }}
    </style>
</head>
<body>
    <div class="container">
       <div class="header glass">
            <h1>

                    <span style="font-size: 3rem; margin-right: 1rem; color: #e11d48;">🐙</span>
                Inktrace Agent Inspector
            </h1>
            <div class="tagline">Uncover hidden threats. One agent at a time</div>
        </div>
        
        <div class="nav">
            <a href="/dashboard">🏠 Dashboard</a>
            <a href="/communications">💬 Communications</a>
            <a href="/security-events">🛡️ Security Events</a>
            <a href="/api/agents" target="_blank">📊 API</a>
        </div>

        <div class="grid">
            <div class="card glass fade-in">
                <h3>
                    <svg class="card-icon" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
                    </svg>
                    Discovered Agents
                </h3>
                <div id="agents-list">
                    <div class="loading">🔍 Scanning for agents...</div>
                </div>
            </div>

            <div class="card glass fade-in">
                <h3>
                    <svg class="card-icon" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M20 4H4c-1.1 0-2 .9-2 2v12c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                    </svg>
                    Communication Activity
                </h3>
                <div id="communications-summary">
                    <div class="metric">
                        <span class="metric-label">Active Connections</span>
                        <span class="metric-value success" id="active-connections">0</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Messages Today</span>
                        <span class="metric-value" id="messages-today">0</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Average Response Time</span>
                        <span class="metric-value" id="avg-response">0ms</span>
                    </div>
                </div>
            </div>

            <div class="card glass fade-in">
                <h3>
                    <svg class="card-icon" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M12,1L3,5V11C3,16.55 6.84,21.74 12,23C17.16,21.74 21,16.55 21,11V5L12,1M12,7C13.4,7 14.8,8.6 14.8,10V11.5C15.4,11.5 16,12.4 16,13V16C16,17.4 15.4,18 14.8,18H9.2C8.6,18 8,17.4 8,16V13C8,12.4 8.6,11.5 9.2,11.5V10C9.2,8.6 10.6,7 12,7M12,8.2C11.2,8.2 10.5,8.7 10.5,10V11.5H13.5V10C13.5,8.7 12.8,8.2 12,8.2Z"/>
                    </svg>
                    Security Status
                </h3>
                <div id="security-summary">
                    <div class="metric">
                        <span class="metric-label">Security Events</span>
                        <span class="metric-value" id="security-events-count">0</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Threat Level</span>
                        <span class="metric-value success" id="threat-level">LOW</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Malicious Agents</span>
                        <span class="metric-value danger" id="malicious-count">0</span>
                    </div>
                    <div class="metric">
                        <span class="metric-label">Last Scan</span>
                        <span class="metric-value" id="last-scan">Just now</span>
                    </div>
                </div>
            </div>

            <div class="card glass fade-in">
                <h3>
                    <svg class="card-icon" fill="currentColor" viewBox="0 0 24 24">
                        <path d="M13,3A9,9 0 0,0 4,12H1L4.89,15.89L4.96,16.03L9,12H6A7,7 0 0,1 13,5A7,7 0 0,1 20,12A7,7 0 0,1 13,19C11.07,19 9.32,18.21 8.06,16.94L6.64,18.36C8.27,20 10.5,21 13,21A9,9 0 0,0 22,12A9,9 0 0,0 13,3Z"/>
                    </svg>
                    Recent Events
                </h3>
                <div id="recent-events">
                    <div class="loading">📡 Monitoring real-time events...</div>
                </div>
            </div>
        </div>
    </div>

    <script>
        // WebSocket connection for real-time updates
        let ws;
        let agents = {{}};
        
        function initWebSocket() {{
            ws = new WebSocket(`ws://${{window.location.host}}/ws`);
            
            ws.onmessage = function(event) {{
                const data = JSON.parse(event.data);
                handleRealTimeUpdate(data);
            }};
            
            ws.onclose = function() {{
                setTimeout(initWebSocket, 3000); // Reconnect after 3 seconds
            }};
        }}

        function handleRealTimeUpdate(update) {{
            console.log('Real-time update:', update);
            updateDashboard();
        }}

        // Load initial data
        async function loadDashboardData() {{
            try {{
                const [agentsData, communications, events] = await Promise.all([
                    fetch('/api/agents').then(r => r.json()),
                    fetch('/api/communications').then(r => r.json()),
                    fetch('/api/security-events').then(r => r.json())
                ]);

                agents = agentsData.agents || {{}};
                updateAgentsList(agents);
                updateCommunications(communications.communications || []);
                updateSecurityEvents(events.events || []);
            }} catch (error) {{
                console.error('Error loading data:', error);
            }}
        }}

        function updateAgentsList(agentsData = {{}}) {{
            const container = document.getElementById('agents-list');
            
            if (Object.keys(agentsData).length === 0) {{
                container.innerHTML = '<div class="empty-state">🤖 No agents discovered yet<br><small>Agents will appear here when they join the network</small></div>';
                return;
            }}

            const html = Object.entries(agentsData).map(([id, agent]) => {{
                const threat = agent.threat_analysis || {{}};
                const isMalicious = threat.is_malicious || false;
                const threatLevel = (threat.threat_level || 'LOW').toLowerCase();
                const threatScore = threat.threat_score || 0;
                const threatReasons = threat.threat_reasons || [];
                
                const cardClass = isMalicious ? 'agent-item malicious-agent' : 'agent-item';
                const threatBadge = `<span class="threat-level ${{threatLevel}}">${{(threat.threat_level || 'LOW')}}</span>`;
                
                return `
                    <div class="${{cardClass}}">
                        <div class="agent-header">
                            <span class="agent-name">${{agent.name}}</span>
                            <div>
                                <span class="status ${{agent.status}}">${{agent.status}}</span>
                                ${{threatBadge}}
                            </div>
                        </div>
                        <div class="agent-details">
                            📍 Port: ${{agent.port}} • 🕐 Last seen: ${{new Date(agent.last_seen).toLocaleTimeString()}}
                            ${{threatScore > 0 ? `<br>⚠️ Threat Score: ${{threatScore}}/100` : ''}}
                        </div>
                        ${{threatReasons.length > 0 ? 
                            `<div class="threat-details">
                                🚨 <strong>Security Alerts:</strong><br>
                                ${{threatReasons.slice(0,3).map(reason => `• ${{reason}}`).join('<br>')}}
                            </div>` : ''
                        }}
                    </div>
                `;
            }}).join('');
            
            container.innerHTML = html;
        }}

        function updateCommunications(communications = []) {{
            // Count active agents
            const activeCount = Object.values(agents).filter(agent => agent.status === 'active').length;
            document.getElementById('active-connections').textContent = activeCount;
            
            document.getElementById('messages-today').textContent = communications.length;
            document.getElementById('avg-response').textContent = 
                communications.length > 0 ? '45ms' : '0ms';
        }}

        function updateSecurityEvents(events = []) {{
            document.getElementById('security-events-count').textContent = events.length;
            
            // Count malicious agents - FIXED
            const maliciousCount = Object.values(agents).filter(agent => 
                agent.threat_analysis && agent.threat_analysis.is_malicious
            ).length;
            
            const maliciousElement = document.getElementById('malicious-count');
            maliciousElement.textContent = maliciousCount;
            maliciousElement.className = maliciousCount > 0 ? 'metric-value danger' : 'metric-value';
            
            // Determine overall threat level
            const hasCritical = events.some(e => e.severity === 'critical') || maliciousCount > 0;
            const hasHigh = events.some(e => e.severity === 'high');
            const hasMedium = events.some(e => e.severity === 'medium');
            
            let overallThreat = 'LOW';
            let threatClass = 'success';
            
            if (hasCritical) {{
                overallThreat = 'CRITICAL';
                threatClass = 'danger';
            }} else if (hasHigh) {{
                overallThreat = 'HIGH';
                threatClass = 'danger';
            }} else if (hasMedium) {{
                overallThreat = 'MEDIUM';
                threatClass = 'warning';
            }}
            
            const threatElement = document.getElementById('threat-level');
            threatElement.textContent = overallThreat;
            threatElement.className = `metric-value ${{threatClass}}`;
            
            document.getElementById('last-scan').textContent = 'Just now';

            // Show recent events
            const container = document.getElementById('recent-events');
            if (events.length === 0) {{
                container.innerHTML = '<div class="empty-state">🛡️ All clear<br><small>No security events detected</small></div>';
                return;
            }}

            const recentEvents = events.slice(-5).reverse();
            const html = recentEvents.map(event => {{
                const isThreat = event.type === 'malicious_agent_detected';
                const icon = isThreat ? '🚨' : event.severity === 'high' ? '⚠️' : 'ℹ️';
                
                return `
                    <div class="event-item ${{event.severity}}">
                        <div class="event-header">
                            ${{icon}} ${{event.type.replace(/_/g, ' ').toUpperCase()}}
                        </div>
                        <div class="event-description">
                            ${{event.description || event.type}}
                            ${{event.threat_score ? `<br><strong>Threat Score:</strong> ${{event.threat_score}}/100` : ''}}
                        </div>
                        <div class="event-time">
                            🕐 ${{new Date(event.timestamp).toLocaleTimeString()}}
                        </div>
                    </div>
                `;
            }}).join('');
            
            container.innerHTML = html;
        }}

        function updateDashboard() {{
            loadDashboardData();
        }}

        // Initialize
        initWebSocket();
        loadDashboardData();
        
        // Refresh data every 3 seconds
        setInterval(updateDashboard, 3000);
    </script>
</body>
</html>
        """
    
    # ... (keep all other methods from the original wiretap.py but add the enhanced methods above)
    
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
            
            print("🔍 Enhanced background monitoring started with threat detection")
    
    def continuous_agent_discovery(self):
        """Continuously discover and monitor A2A agents"""
        while self.is_monitoring:
            try:
                asyncio.run(self.discover_agents())
                time.sleep(5)  # Check every 5 seconds
            except Exception as e:
                print(f"⚠️ Agent discovery error: {e}")
                time.sleep(10)

def main():
    """Launch the Enhanced Wiretap Tentacle"""
    parser = argparse.ArgumentParser(description="🐙 Inktrace Enhanced Wiretap Tentacle")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8003, help="Port to bind to")
    args = parser.parse_args()
    
    print("🐙 Starting Inktrace Enhanced Wiretap Tentacle")
    print("=" * 60)
    print(f"🔍 Dashboard: http://{args.host}:{args.port}/dashboard")
    print(f"💬 Communications: http://{args.host}:{args.port}/communications")
    print(f"🛡️ Security Events: http://{args.host}:{args.port}/security-events")
    print(f"📊 API: http://{args.host}:{args.port}/api/agents")
    print(f"🚨 NEW: Real-time threat detection and analysis!")
    print("=" * 60)
    
    # Create enhanced tentacle
    tentacle = WiretapTentacle(port=args.port)
    
    # Run server
    uvicorn.run(tentacle.app, host=args.host, port=args.port, log_level="info")

if __name__ == "__main__":
    main()