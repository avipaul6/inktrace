# scripts/launch.py - UPDATED WITH POLICY AGENT
#!/usr/bin/env python3
"""
🐙 Inktrace Development Launcher - Enhanced with Policy Agent
scripts/launch.py

Launch the complete Inktrace distributed intelligence system with all 3 agents + wiretap.
UPDATED: Now includes the Policy Agent (T6 Compliance & Governance)
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


class InktraceLauncher:
    """🐙 Inktrace System Launcher - Enhanced with Policy Agent"""

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
                "port": 8003,
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

    def setup_signal_handlers(self):
        """Set up signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            print(f"\n🛑 Received signal {signum}, shutting down Inktrace...")
            self.shutdown_all_processes()
            sys.exit(0)

        signal.signal(signal.SIGTERM, signal_handler)
        signal.signal(signal.SIGINT, signal_handler)

    def launch_agent(self, agent_id: str, config: dict) -> bool:
        """Launch a single agent"""
        script_path = self.agents_dir / config["script"]
        
        if not script_path.exists():
            print(f"❌ Agent script not found: {script_path}")
            return False
        
        print(f"🚀 Starting {config['name']} on port {config['port']}...")
        print(f"   Tentacles: {', '.join(config['tentacles'])}")
        if 'description' in config:
            print(f"   {config['description']}")
        
        try:
            cmd = [
                sys.executable, str(script_path),
                "--host", "0.0.0.0",
                "--port", str(config['port'])
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=self.project_root
            )
            
            self.processes.append(process)
            
            # Give it a moment to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ {config['name']} started successfully")
                return True
            else:
                print(f"❌ {config['name']} failed to start")
                stdout, _ = process.communicate()
                if stdout:
                    print(f"   Output: {stdout[-200:]}")  # Last 200 chars
                return False
                
        except Exception as e:
            print(f"❌ Error starting {config['name']}: {e}")
            return False

    def launch_tentacle(self, tentacle_id: str, config: dict) -> bool:
        """Launch a single tentacle"""
        script_path = self.tentacles_dir / config["script"]
        
        if not script_path.exists():
            print(f"❌ Tentacle script not found: {script_path}")
            return False
        
        print(f"🚀 Starting {config['name']} on port {config['port']}...")
        print(f"   Function: {config['function']}")
        
        try:
            cmd = [
                sys.executable, str(script_path),
                "--host", "0.0.0.0",
                "--port", str(config['port'])
            ]
            
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                universal_newlines=True,
                cwd=self.project_root
            )
            
            self.processes.append(process)
            
            # Give it a moment to start
            time.sleep(3)
            
            # Check if process is still running
            if process.poll() is None:
                print(f"✅ {config['name']} started successfully")
                return True
            else:
                print(f"❌ {config['name']} failed to start")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {config['name']}: {e}")
            return False

    def wait_for_services(self):
        """Wait for all services to be ready"""
        print("\n⏳ Waiting for all services to be ready...")
        
        all_services = {**self.agents, **self.tentacles}
        ready_services = 0
        
        for service_id, config in all_services.items():
            max_retries = 15
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    url = f"http://localhost:{config['port']}/.well-known/agent.json"
                    response = requests.get(url, timeout=3)
                    
                    if response.status_code == 200:
                        print(f"✅ {config['name']} is ready")
                        ready_services += 1
                        break
                        
                except:
                    pass
                
                retry_count += 1
                time.sleep(2)
                
                if retry_count >= max_retries:
                    print(f"⚠️ {config['name']} may not be ready (timeout)")
        
        return ready_services

    def test_policy_agent(self):
        """Test the policy agent with a sample request"""
        print("\n🧪 Testing Policy Agent...")
        
        try:
            # Test the policy agent endpoint
            response = requests.post(
                "http://localhost:8006/",
                json={
                    "jsonrpc": "2.0",
                    "id": "policy-test",
                    "method": "tasks/send",
                    "params": {
                        "id": "compliance-check-001",
                        "sessionId": "test",
                        "message": {
                            "role": "user",
                            "parts": [{
                                "type": "text",
                                "text": "Run comprehensive policy compliance check"
                            }]
                        }
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ Policy Agent test successful")
                return True
            else:
                print(f"⚠️ Policy Agent test returned HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"❌ Policy Agent test failed: {e}")
            return False

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
        
        print("\n📋 POLICY AGENT FEATURES:")
        print("🗄️ BigQuery Policy Store: inktrace_policies.security_policies")
        print("📊 Violations Tracking: inktrace_policies.policy_violations")
        print("🔧 Config-Driven Rules: Dynamic policy management")
        print("⚡ Real-time Compliance: Instant violation detection")
        
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
        """Run the complete Inktrace system"""
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
            time.sleep(2)  # Stagger startup

        # Launch all tentacles
        print("\n🐙 LAUNCHING TENTACLES...")
        tentacle_success_count = 0
        
        for tentacle_id, config in self.tentacles.items():
            if self.launch_tentacle(tentacle_id, config):
                tentacle_success_count += 1
            time.sleep(2)

        total_success = agent_success_count + tentacle_success_count
        total_services = len(self.agents) + len(self.tentacles)

        if total_success == 0:
            print("❌ No services started successfully!")
            return False

        print(f"\n✅ Started {total_success}/{total_services} services")
        
        # Wait for services to be ready
        ready_count = self.wait_for_services()
        
        # Test the new policy agent
        self.test_policy_agent()
        
        # Display system information
        self.display_system_info(ready_count)
        
        print("\n💡 TIP: Use Ctrl+C to stop all services")
        
        # Keep main process alive and monitor
        try:
            while True:
                time.sleep(60)
                # Could add health checks here
        except KeyboardInterrupt:
            print("\n🛑 Shutdown requested...")
            self.shutdown_all_processes()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(description="🐙 Inktrace System Launcher")
    parser.add_argument("--setup-bigquery", action="store_true", 
                       help="Set up BigQuery before launching")
    args = parser.parse_args()
    
    if args.setup_bigquery:
        print("🗄️ Setting up BigQuery first...")
        try:
            subprocess.run([sys.executable, "scripts/setup_bigquery.py"], 
                         cwd=Path(__file__).parent.parent, check=True)
            print("✅ BigQuery setup complete")
        except subprocess.CalledProcessError:
            print("❌ BigQuery setup failed, continuing anyway...")
        print()
    
    launcher = InktraceLauncher()
    launcher.run()


if __name__ == "__main__":
    main()