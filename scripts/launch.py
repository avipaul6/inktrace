#!/usr/bin/env python3
"""
🐙 Inktrace Development Launcher - FIXED STARTUP DETECTION
scripts/launch.py

Launch the complete Inktrace distributed intelligence system with better startup detection.
 Proper port binding detection and startup sequencing
"""

import subprocess
import time
import sys
import os
import requests
import json
import argparse
import signal
from pathlib import Path
from typing import List, Dict
import socket


class InktraceLauncher:
    """🐙 Inktrace System Launcher - Fixed Startup Detection"""

    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.project_root = Path(__file__).parent.parent
        self.agents_dir = self.project_root / "agents"
        self.tentacles_dir = self.project_root / "tentacles"

        # Ensure template directories exist
        self.ensure_template_structure()

        # Enhanced agent configuration with Policy Agent
        self.agents = {
            "data_processor": {
                "script": "data_processor.py",
                "port": 8001,
                "name": "🐙 Data Processor Agent",
                "tentacles": ["T2-Data Protection", "T3-Behavioral Intelligence"]
            },
            "report_generator": {
                "script": "report_generator.py",
                "port": 8002,
                "name": "🐙 Report Generator Agent",
                "tentacles": ["T1-Identity & Access", "T6-Compliance & Governance"]
            },
            "policy_agent": {
                "script": "policy_agent.py",
                "port": 8006,
                "name": "🐙 Policy Agent",
                "tentacles": ["T6-Compliance & Governance"],
                "description": "BigQuery-driven policy compliance checker"
            }
        }

        # Tentacle configuration
        self.tentacles = {
            "wiretap": {
                "script": "wiretap.py",
                "port": int(os.environ.get('PORT', 8003)),  # Use PORT env var, default 8003
                "name": "🐙 Wiretap Tentacle",
                "function": "Real-time A2A Communications Monitor with Enhanced Dashboard"
            }
        }

    def ensure_template_structure(self):
        """Ensure template and static directories exist"""
        required_dirs = [
            self.project_root / "templates",
            self.project_root / "static" / "css",
            self.project_root / "static" / "js",
            self.project_root / "static" / "images"
        ]
        
        for dir_path in required_dirs:
            dir_path.mkdir(parents=True, exist_ok=True)

    def check_port_available(self, port: int) -> bool:
        """Check if a port is available (not bound)"""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                return result != 0  # 0 means connection successful (port is bound)
        except:
            return True

    def wait_for_port_binding(self, port: int, timeout: int = 30) -> bool:
        """Wait for a port to be bound (service to start)"""
        print(f"   ⏳ Waiting for port {port} to bind...")
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', port))
                    if result == 0:  # Connection successful
                        print(f"   ✅ Port {port} is now bound")
                        return True
            except:
                pass
            time.sleep(1)
        
        print(f"   ❌ Port {port} failed to bind within {timeout}s")
        return False

    def check_agent_ready(self, port: int) -> bool:
        """Check if agent is ready by testing A2A endpoint"""
        try:
            response = requests.get(f"http://localhost:{port}/.well-known/agent.json", timeout=5)
            return response.status_code == 200
        except:
            return False

    def launch_agent(self, agent_id: str, config: Dict) -> bool:
        """Launch a single agent with improved startup detection"""
        script_path = self.agents_dir / config["script"]
        
        print(f"🚀 Starting {config['name']} on port {config['port']}...")
        print(f"   Tentacles: {', '.join(config['tentacles'])}")
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return False

        # Check if port is already in use
        if not self.check_port_available(config["port"]):
            print(f"⚠️ Port {config['port']} already in use")
            return False

        try:
            # Launch the agent
            process = subprocess.Popen([
                sys.executable, str(script_path),
                "--host", "0.0.0.0",
                "--port", str(config["port"])
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
            
            self.processes.append(process)
            
            # Wait for port binding first
            if not self.wait_for_port_binding(config["port"], timeout=20):
                print(f"❌ {config['name']} failed to bind to port")
                return False
            
            # Give it a moment to fully initialize
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is not None:
                print(f"❌ {config['name']} process died")
                # Print any error output
                if process.stdout:
                    output = process.stdout.read()
                    print(f"   Output: {output[:200]}...")
                return False
            
            print(f"✅ {config['name']} started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {config['name']}: {e}")
            return False

    def launch_tentacle(self, tentacle_id: str, config: Dict) -> bool:
        """Launch a single tentacle with improved startup detection"""
        script_path = self.tentacles_dir / config["script"]
        
        print(f"🚀 Starting {config['name']} on port {config['port']}...")
        print(f"   Function: {config['function']}")
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return False

        # Check if port is already in use
        if not self.check_port_available(config["port"]):
            print(f"⚠️ Port {config['port']} already in use")
            return False

        try:
            # Launch the tentacle
            process = subprocess.Popen([
                sys.executable, str(script_path),
                "--host", "0.0.0.0", 
                "--port", str(config["port"])
            ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, text=True)
            
            self.processes.append(process)
            
            # Wait for port binding
            if not self.wait_for_port_binding(config["port"], timeout=20):
                print(f"❌ {config['name']} failed to bind to port")
                return False
            
            # Give it a moment to fully initialize
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is not None:
                print(f"❌ {config['name']} process died")
                # Print any error output
                if process.stdout:
                    output = process.stdout.read()
                    print(f"   Output: {output[:200]}...")
                return False
            
            print(f"✅ {config['name']} started successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to start {config['name']}: {e}")
            return False

    def wait_for_readiness(self) -> int:
        """Wait for all services to be ready and return count"""
        print("\n⏳ Waiting for all services to be ready...")
        ready_count = 0
        
        # Check agents
        for agent_id, config in self.agents.items():
            max_attempts = 10
            for attempt in range(max_attempts):
                if self.check_agent_ready(config["port"]):
                    print(f"✅ {config['name']} is ready")
                    ready_count += 1
                    break
                elif attempt < max_attempts - 1:
                    print(f"⏳ {config['name']} not ready yet... (attempt {attempt + 1}/{max_attempts})")
                    time.sleep(2)
                else:
                    print(f"❌ {config['name']} failed to become ready")
        
        # Check tentacles (simpler check for tentacles)
        for tentacle_id, config in self.tentacles.items():
            try:
                response = requests.get(f"http://localhost:{config['port']}/dashboard", timeout=5)
                if response.status_code == 200:
                    print(f"✅ {config['name']} is ready")
                    ready_count += 1
                else:
                    print(f"❌ {config['name']} not responding properly")
            except:
                print(f"❌ {config['name']} not ready")
        
        return ready_count

    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}")
            self.shutdown_all_processes()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)

    def display_system_info(self, ready_count: int):
        """Display system information and access URLs"""
        total_services = len(self.agents) + len(self.tentacles)
        
        print("\n🐙 INKTRACE SYSTEM STATUS")
        print("=" * 70)
        print(f"Services Ready: {ready_count}/{total_services}")
        print(f"Project: inktrace-463306")
        print(f"Environment: Development")
        print("=" * 70)
        
        print("\n🌟 PRIMARY INTERFACES:")
        print(f"🎮 Enhanced Dashboard: http://localhost:8003/dashboard")
        print(f"💬 Communications: http://localhost:8003/communications")
        print(f"🛡️ Security Events: http://localhost:8003/security-events")
        print(f"📊 API Endpoints: http://localhost:8003/api/")
        
        print("\n🤖 AGENT ENDPOINTS:")
        for agent_id, config in self.agents.items():
            print(f"📡 {config['name']}: http://localhost:{config['port']}")
        
        print("\n🐙 8-TENTACLE SECURITY MATRIX:")
        print("T1: Identity & Access Management (Report Generator)")
        print("T2: Data Protection (Data Processor)")  
        print("T3: Behavioral Intelligence (Data Processor)")
        print("T4: Operational Resilience (Wiretap)")
        print("T5: Supply Chain Security (Future)")
        print("T6: Compliance & Governance (Policy Agent) ⭐ NEW!")
        print("T7: Advanced Threats (Wiretap)")
        print("T8: Network Security (Future)")
        
        print("\n🚀 DEMO SCENARIOS:")
        print("1. Visit dashboard and click 'Launch Malicious Agent Demo'")
        print("2. Test Policy Agent: curl -X POST http://localhost:8006/")
        print("3. Check BigQuery Console: https://console.cloud.google.com/bigquery")
        print("4. View real-time threat detection in action")

    def shutdown_all_processes(self):
        """Shutdown all processes gracefully"""
        print("\n🛑 Shutting down all Inktrace services...")
        
        for process in self.processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()
        
        print("✅ All services stopped")

    def run(self):
        """Run the complete Inktrace system with improved startup detection"""
        print("🐙 INKTRACE DISTRIBUTED INTELLIGENCE LAUNCHER")
        print("=" * 70)
        print("Agent-Based Security Intelligence from the Deep")
        print("Enhanced with Policy Agent (T6 Compliance & Governance)")
        print("=" * 70)

        # Set up signal handlers
        self.setup_signal_handlers()

        # Launch all agents
        print("\n🤖 LAUNCHING AGENTS...")
        agent_success_count = 0
        
        for agent_id, config in self.agents.items():
            if self.launch_agent(agent_id, config):
                agent_success_count += 1
            time.sleep(3)  # Stagger startup to avoid conflicts

        # Launch all tentacles
        print("\n🐙 LAUNCHING TENTACLES...")
        tentacle_success_count = 0
        
        for tentacle_id, config in self.tentacles.items():
            if self.launch_tentacle(tentacle_id, config):
                tentacle_success_count += 1
            time.sleep(3)

        total_success = agent_success_count + tentacle_success_count
        total_services = len(self.agents) + len(self.tentacles)

        print(f"\n✅ Started {total_success}/{total_services} services")

        if total_success == 0:
            print("❌ No services started successfully!")
            return False

        # Wait for readiness
        ready_count = self.wait_for_readiness()
        
        # Display system info
        self.display_system_info(ready_count)

        # Keep running until interrupted
        try:
            print("\n🔄 System running... Press Ctrl+C to stop")
            while True:
                time.sleep(10)
                # Check if any process died
                alive_count = sum(1 for p in self.processes if p.poll() is None)
                if alive_count < len(self.processes):
                    print(f"⚠️ Some processes died ({alive_count}/{len(self.processes)} alive)")
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
        finally:
            self.shutdown_all_processes()

        return True


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="🐙 Inktrace Distributed Intelligence Launcher")
    parser.add_argument("--quick", action="store_true", help="Quick launch without demos")
    args = parser.parse_args()
    
    launcher = InktraceLauncher()
    success = launcher.run()
    
    if not success:
        print("❌ Launch failed!")
        sys.exit(1)
    
    print("✅ Launch completed successfully!")


if __name__ == "__main__":
    main()