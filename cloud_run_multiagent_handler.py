# cloud_run_multiagent_handler.py
# 🐙 Inktrace Cloud Run Multi-Agent Handler
# Preserves your distributed architecture while being Cloud Run compatible

import os
import asyncio
import subprocess
import time
import signal
import sys
from pathlib import Path
from typing import Dict, List
import requests
import socket
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse, RedirectResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import httpx

app = FastAPI(
    title="🐙 Inktrace Multi-Agent Security Platform",
    description="Agent-Based Security Intelligence from the Deep - Multi-Agent Orchestrator",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class InktraceOrchestrator:
    """Orchestrates multiple agents while exposing single Cloud Run service"""
    
    def __init__(self):
        self.agents_config = {
            "data_processor": {"port": 8001, "script": "agents/data_processor.py"},
            "report_generator": {"port": 8002, "script": "agents/report_generator.py"},
            "wiretap": {"port": 8003, "script": "tentacles/wiretap.py"},
            "policy_agent": {"port": 8006, "script": "agents/policy_agent.py"}
        }
        self.processes: List[subprocess.Popen] = []
        self.startup_complete = False
        self.health_status = "starting"
        
    async def start_agents(self):
        """Start all agents in background"""
        print("🐙 Starting Inktrace multi-agent system...")
        
        for agent_id, config in self.agents_config.items():
            await self.start_single_agent(agent_id, config)
            await asyncio.sleep(2)  # Stagger startup
        
        # Wait for all agents to be ready
        await self.wait_for_all_agents()
        self.startup_complete = True
        self.health_status = "healthy"
        print("✅ All Inktrace agents are ready!")
    
    async def start_single_agent(self, agent_id: str, config: Dict):
        """Start a single agent"""
        script_path = Path(config["script"])
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return
        
        try:
            print(f"🚀 Starting {agent_id} on port {config['port']}...")
            process = subprocess.Popen([
                sys.executable, str(script_path),
                "--host", "0.0.0.0",
                "--port", str(config["port"])
            ], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            
            self.processes.append(process)
            print(f"✅ {agent_id} process started (PID: {process.pid})")
            
        except Exception as e:
            print(f"❌ Failed to start {agent_id}: {e}")
    
    async def wait_for_all_agents(self, timeout=60):
        """Wait for all agents to become responsive"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            ready_count = 0
            
            for agent_id, config in self.agents_config.items():
                if await self.check_agent_health(config["port"]):
                    ready_count += 1
            
            if ready_count == len(self.agents_config):
                return True
            
            await asyncio.sleep(2)
        
        print(f"⚠️ Only {ready_count}/{len(self.agents_config)} agents ready after {timeout}s")
        return False
    
    async def check_agent_health(self, port: int) -> bool:
        """Check if an agent is responsive with better logging"""
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"http://localhost:{port}/.well-known/agent.json")
                success = response.status_code == 200
                print(f"🔍 Health check port {port}: {'✅' if success else '❌'} (HTTP {response.status_code})")
                return success
        except Exception as e:
            print(f"🔍 Health check port {port}: ❌ Exception: {e}")
            return False
    
    def cleanup_processes(self):
        """Cleanup all agent processes"""
        print("🧹 Cleaning up agent processes...")
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except:
                try:
                    process.kill()
                except:
                    pass

# Global orchestrator instance
orchestrator = InktraceOrchestrator()

@app.on_event("startup")
async def startup_event():
    """Start all agents on app startup"""
    # Start agents in background task to not block startup
    asyncio.create_task(orchestrator.start_agents())

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    orchestrator.cleanup_processes()

@app.get("/", response_class=RedirectResponse)
async def root():
    """Redirect to dashboard"""
    return RedirectResponse(url="/dashboard")

@app.get("/health")
async def health_check():
    """Cloud Run health check"""
    if not orchestrator.startup_complete:
        return JSONResponse(
            status_code=503,
            content={
                "status": "starting", 
                "message": "Agents still starting up",
                "agents_ready": sum(1 for _, config in orchestrator.agents_config.items() 
                                   if await orchestrator.check_agent_health(config["port"]))
            }
        )
    
    return {
        "status": "healthy",
        "service": "inktrace-multi-agent",
        "agents": len(orchestrator.agents_config),
        "all_ready": orchestrator.startup_complete
    }

@app.get("/dashboard")
async def dashboard():
    """Proxy to Wiretap dashboard with detailed debugging"""
    if not orchestrator.startup_complete:
        return HTMLResponse("""
        <!DOCTYPE html>
        <html>
        <head>
            <title>🐙 Inktrace - Starting Up</title>
            <style>
                body { font-family: sans-serif; text-align: center; padding: 50px; 
                       background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; }
                .spinner { border: 4px solid #f3f3f3; border-top: 4px solid #3498db; 
                          border-radius: 50%; width: 50px; height: 50px; 
                          animation: spin 2s linear infinite; margin: 20px auto; }
                @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            </style>
        </head>
        <body>
            <h1>🐙 Inktrace</h1>
            <div class="spinner"></div>
            <h2>Starting Multi-Agent System...</h2>
            <p>Please wait while all security tentacles come online</p>
            <script>setTimeout(() => window.location.reload(), 5000);</script>
        </body>
        </html>
        """)
    
    # Detailed debugging of wiretap connection
    print("🔍 Dashboard request - checking wiretap connection...")
    
    # Test different wiretap endpoints to see what works
    wiretap_tests = [
        ("/.well-known/agent.json", "Agent discovery"),
        ("/dashboard", "Dashboard page"),
        ("/api/agents", "API endpoint"),
        ("/", "Root page")
    ]
    
    working_endpoint = None
    for endpoint, description in wiretap_tests:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                test_url = f"http://localhost:8003{endpoint}"
                print(f"🧪 Testing wiretap {description}: {test_url}")
                response = await client.get(test_url)
                print(f"   Response: HTTP {response.status_code}")
                
                if response.status_code == 200:
                    working_endpoint = endpoint
                    print(f"   ✅ {description} works!")
                    if endpoint == "/dashboard":
                        # Dashboard works, return it
                        return HTMLResponse(response.text)
                    break
                else:
                    print(f"   ❌ {description} failed with HTTP {response.status_code}")
        except Exception as e:
            print(f"   ❌ {description} exception: {e}")
    
    # If we get here, dashboard didn't work but maybe something else did
    if working_endpoint:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Try to get the working endpoint content
                response = await client.get(f"http://localhost:8003{working_endpoint}")
                if working_endpoint == "/.well-known/agent.json":
                    agent_data = response.json()
                    return HTMLResponse(f"""
                    <!DOCTYPE html>
                    <html>
                    <head><title>🐙 Inktrace Debug</title></head>
                    <body style="font-family: sans-serif; padding: 20px; background: #1e293b; color: white;">
                        <h1>🐙 Inktrace Wiretap Debug</h1>
                        <h2>✅ Wiretap is responding!</h2>
                        <p><strong>Agent Name:</strong> {agent_data.get('name', 'Unknown')}</p>
                        <p><strong>Working Endpoint:</strong> {working_endpoint}</p>
                        <p><strong>Issue:</strong> Dashboard endpoint not responding properly</p>
                        
                        <h3>🔧 Troubleshooting:</h3>
                        <p>1. Wiretap service is running (agent discovery works)</p>
                        <p>2. Dashboard endpoint might have template issues</p>
                        <p>3. Try: <a href="/agent/wiretap/dashboard" style="color: #4ade80;">/agent/wiretap/dashboard</a></p>
                        
                        <button onclick="window.location.reload()" style="background: #4ade80; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer;">Retry Dashboard</button>
                    </body>
                    </html>
                    """)
        except Exception as e:
            print(f"❌ Error getting working endpoint content: {e}")
    
    # Complete failure - show detailed error
    return HTMLResponse(f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>🐙 Inktrace Dashboard Debug</title>
        <style>
            body {{ font-family: sans-serif; padding: 20px; background: #1e293b; color: white; }}
            .error {{ background: rgba(239, 68, 68, 0.2); padding: 15px; border-radius: 8px; margin: 10px 0; }}
            .debug {{ background: rgba(59, 130, 246, 0.2); padding: 15px; border-radius: 8px; margin: 10px 0; }}
        </style>
    </head>
    <body>
        <h1>🐙 Inktrace Dashboard Debug</h1>
        
        <div class="error">
            <h3>❌ Wiretap Dashboard Connection Failed</h3>
            <p>The orchestrator cannot connect to the wiretap dashboard service.</p>
        </div>
        
        <div class="debug">
            <h3>🔍 Debug Information</h3>
            <p><strong>Expected URL:</strong> http://localhost:8003/dashboard</p>
            <p><strong>All tests failed</strong> - wiretap service might not be responding</p>
            <p><strong>Startup complete:</strong> {orchestrator.startup_complete}</p>
        </div>
        
        <h3>🧪 Alternative Access:</h3>
        <p><a href="/agent/wiretap/dashboard" style="color: #4ade80;">Try direct proxy: /agent/wiretap/dashboard</a></p>
        <p><a href="/api/agents" style="color: #4ade80;">Check agent status: /api/agents</a></p>
        <p><a href="/health" style="color: #4ade80;">Check system health: /health</a></p>
        
        <button onclick="window.location.reload()" style="background: #4ade80; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px 5px;">Retry Connection</button>
        <button onclick="window.location.href='/agent/wiretap/dashboard'" style="background: #f59e0b; color: white; border: none; padding: 10px 20px; border-radius: 5px; cursor: pointer; margin: 10px 5px;">Try Direct Proxy</button>
    </body>
    </html>
    """)

@app.get("/api/agents")
async def list_agents():
    """List all agents with their status"""
    agents_status = {}
    
    for agent_id, config in orchestrator.agents_config.items():
        is_healthy = await orchestrator.check_agent_health(config["port"])
        agents_status[agent_id] = {
            "port": config["port"],
            "status": "active" if is_healthy else "down",
            "url": f"http://localhost:{config['port']}"
        }
    
    return {
        "agents": agents_status,
        "total": len(orchestrator.agents_config),
        "active": sum(1 for agent in agents_status.values() if agent["status"] == "active")
    }

@app.get("/.well-known/agent.json")
async def agent_discovery():
    """Main agent discovery - represents the orchestrator"""
    return {
        "name": "🐙 Inktrace Multi-Agent Security Platform",
        "description": "Agent-Based Security Intelligence from the Deep - Orchestrator Service",
        "version": "1.0.0",
        "url": f"https://{os.getenv('HOSTNAME', 'localhost')}",
        "capabilities": {"streaming": True, "pushNotifications": False},
        "skills": [
            {
                "id": "multi_agent_orchestration",
                "name": "Multi-Agent Security Orchestration",
                "description": "Coordinates multiple specialized security agents using A2A protocol"
            }
        ],
        "managed_agents": list(orchestrator.agents_config.keys()),
        "tentacles": {
            "T1": "Identity & Access Management",
            "T2": "Data Protection", 
            "T3": "Behavioral Intelligence",
            "T4": "Operational Resilience",
            "T6": "Compliance & Governance",
            "T7": "Advanced Threats"
        }
    }

# Proxy endpoints for each agent
@app.api_route("/agent/{agent_id:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy_to_agent(agent_id: str, request: Request):
    """Proxy requests to specific agents"""
    if agent_id not in orchestrator.agents_config:
        return JSONResponse(status_code=404, content={"error": f"Agent {agent_id} not found"})
    
    config = orchestrator.agents_config[agent_id]
    target_url = f"http://localhost:{config['port']}"
    
    # Get request details
    method = request.method
    path = str(request.url.path).replace(f"/agent/{agent_id}", "")
    if not path:
        path = "/"
    
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            # Forward the request
            if method == "GET":
                response = await client.get(f"{target_url}{path}")
            elif method == "POST":
                body = await request.body()
                response = await client.post(f"{target_url}{path}", content=body)
            else:
                return JSONResponse(status_code=405, content={"error": "Method not allowed"})
            
            return JSONResponse(
                content=response.json() if response.headers.get("content-type", "").startswith("application/json") else {"data": response.text},
                status_code=response.status_code
            )
    except Exception as e:
        return JSONResponse(status_code=503, content={"error": f"Agent {agent_id} unavailable: {str(e)}"})

# Direct proxy endpoints for specific agent functions
@app.post("/policy-check")
async def policy_check():
    """Proxy to policy agent"""
    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("http://localhost:8006/", 
                                       json={"method": "policy_check", "params": {}})
            return response.json()
    except Exception as e:
        return JSONResponse(status_code=503, content={"error": f"Policy agent unavailable: {str(e)}"})

@app.get("/communications")
async def communications():
    """Proxy to wiretap communications"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:8003/communications")
            return HTMLResponse(response.text)
    except Exception as e:
        return HTMLResponse(f"<h1>Communications unavailable: {e}</h1>")

@app.get("/security-events")
async def security_events():
    """Proxy to wiretap security events"""
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get("http://localhost:8003/security-events")
            return HTMLResponse(response.text)
    except Exception as e:
        return HTMLResponse(f"<h1>Security events unavailable: {e}</h1>")

# Demo functionality proxy
@app.post("/api/demo/launch-threat")
async def launch_threat_demo(request: Request):
    """Proxy demo controls to wiretap"""
    try:
        data = await request.json()
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post("http://localhost:8003/api/demo/launch-threat", json=data)
            return response.json()
    except Exception as e:
        return JSONResponse(status_code=503, content={"error": f"Demo unavailable: {str(e)}"})

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    print(f"🐙 Starting Inktrace Multi-Agent Orchestrator on port {port}")
    print("=" * 70)
    print("✅ Preserves your distributed agent architecture")
    print("✅ Proxies to your existing Wiretap dashboard")
    print("✅ Maintains A2A inter-agent communication")
    print("✅ Compatible with Cloud Run requirements")
    print("=" * 70)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(signum, frame):
        print(f"\n🛑 Received signal {signum}")
        orchestrator.cleanup_processes()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    uvicorn.run(app, host="0.0.0.0", port=port)