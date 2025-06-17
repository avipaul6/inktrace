#!/usr/bin/env python3
"""
🐙 Inktrace Development Launcher
scripts/launch.py

Launch the complete Inktrace distributed intelligence system for development and demo.
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
    """🐙 Inktrace System Launcher"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.project_root = Path(__file__).parent.parent
        self.agents_dir = self.project_root / "agents"
        self.tentacles_dir = self.project_root / "tentacles"
        
        # Agent configuration
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
            }
        }
        
        # Tentacle configuration
        self.tentacles = {
            "wiretap": {
                "script": "wiretap.py",
                "port": 8003,
                "name": "🐙 Wiretap Tentacle",
                "function": "Communications Monitor"
            }
        }
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")
        
        required_packages = ["python_a2a", "fastapi", "uvicorn", "aiohttp", "requests"]
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package.replace("-", "_"))
            except ImportError:
                missing_packages.append(package)
        
        if missing_packages:
            print(f"❌ Missing packages: {', '.join(missing_packages)}")
            print("📦 Install with: uv add python-a2a fastapi uvicorn aiohttp requests")
            return False
        
        print("✅ All dependencies satisfied")
        return True
    
    def check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('localhost', port))
            return result != 0
    
    def start_component(self, component_type: str, component_name: str, config: Dict) -> bool:
        """Start an agent or tentacle component"""
        port = config["port"]
        script_name = config["script"]
        display_name = config["name"]
        
        # Check port availability
        if not self.check_port_available(port):
            print(f"❌ Port {port} is already in use for {display_name}")
            return False
        
        # Determine script path
        if component_type == "agent":
            script_path = self.agents_dir / script_name
        else:
            script_path = self.tentacles_dir / script_name
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return False
        
        print(f"🚀 Starting {display_name} on port {port}...")
        
        try:
            # Start the process
            process = subprocess.Popen([
                sys.executable, str(script_path),
                "--host", "0.0.0.0",
                "--port", str(port)
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            # Give it time to start
            time.sleep(3)
            
            # Check if it's still running
            if process.poll() is None:
                self.processes.append(process)
                print(f"✅ {display_name} started successfully")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ Failed to start {display_name}")
                print(f"STDOUT: {stdout.decode()[:300]}")
                print(f"STDERR: {stderr.decode()[:300]}")
                return False
                
        except Exception as e:
            print(f"❌ Error starting {display_name}: {e}")
            return False
    
    def wait_for_agents_ready(self) -> bool:
        """Wait for all agents to be ready"""
        print("⏳ Waiting for agents to be ready...")
        
        max_attempts = 30
        for attempt in range(max_attempts):
            all_ready = True
            
            for agent_name, config in self.agents.items():
                port = config["port"]
                try:
                    response = requests.get(f"http://localhost:{port}/.well-known/agent.json", 
                                          timeout=2)
                    if response.status_code != 200:
                        all_ready = False
                        break
                except:
                    all_ready = False
                    break
            
            if all_ready:
                print("✅ All agents are ready!")
                return True
            
            time.sleep(1)
        
        print("⚠️ Some agents may not be fully ready")
        return False
    
    def test_a2a_communication(self) -> bool:
        """Test A2A communication between agents"""
        print("\n🧪 Testing A2A Agent Communication...")
        
        try:
            # Test agent discovery
            for agent_name, config in self.agents.items():
                port = config["port"]
                response = requests.get(f"http://localhost:{port}/.well-known/agent.json", 
                                      timeout=5)
                if response.status_code == 200:
                    agent_card = response.json()
                    print(f"✅ {agent_name}: {agent_card.get('name', 'Unknown')}")
                else:
                    print(f"❌ {agent_name}: Discovery failed")
                    return False
            
            # Test end-to-end A2A communication
            print("🔄 Testing report generation with agent coordination...")
            
            task_data = {
                "jsonrpc": "2.0",
                "id": "test-coordination",
                "method": "tasks/send",
                "params": {
                    "id": "demo-security-analysis",
                    "sessionId": "inktrace-demo",
                    "message": {
                        "role": "user",
                        "parts": [{
                            "type": "text",
                            "text": "Generate comprehensive security report for suspicious admin login attempts with multiple failed authentication events from different geographic locations"
                        }]
                    }
                }
            }
            
            response = requests.post("http://localhost:8002/",
                                   json=task_data,
                                   headers={"Content-Type": "application/json"},
                                   timeout=15)
            
            if response.status_code == 200:
                print("✅ A2A communication successful!")
                print("🎉 Multi-agent coordination working!")
                return True
            else:
                print(f"⚠️ A2A test returned status {response.status_code}")
                
        except Exception as e:
            print(f"❌ A2A communication test failed: {e}")
            return False
        
        return True
    
    def show_system_status(self):
        """Show comprehensive system status"""
        print("\n🐙 INKTRACE DISTRIBUTED INTELLIGENCE SYSTEM")
        print("=" * 60)
        print("Agent-Based Security Intelligence from the Deep")
        print("=" * 60)
        
        print("\n🤖 A2A AGENTS:")
        for agent_name, config in self.agents.items():
            port = config["port"]
            status = "🟢 ACTIVE" if self.check_port_available(port) == False else "🔴 INACTIVE"
            print(f"  {config['name']}")
            print(f"    Status: {status}")
            print(f"    Endpoint: http://localhost:{port}/")
            print(f"    Agent Card: http://localhost:{port}/.well-known/agent.json")
            print(f"    Tentacles: {', '.join(config['tentacles'])}")
            print()
        
        print("🐙 SECURITY TENTACLES:")
        for tentacle_name, config in self.tentacles.items():
            port = config["port"]
            status = "🟢 ACTIVE" if self.check_port_available(port) == False else "🔴 INACTIVE"
            print(f"  {config['name']}")
            print(f"    Status: {status}")
            print(f"    Function: {config['function']}")
            print(f"    Dashboard: http://localhost:{port}/dashboard")
            print()
        
        print("🎯 DEMO COMMANDS:")
        print("  # Test A2A Communication")
        print("  curl -X POST http://localhost:8002/ \\")
        print("    -H 'Content-Type: application/json' \\")
        print("    -d '{")
        print('      "jsonrpc": "2.0",')
        print('      "id": "security-demo",')
        print('      "method": "tasks/send",')
        print('      "params": {')
        print('        "id": "threat-analysis",')
        print('        "sessionId": "demo",')
        print('        "message": {')
        print('          "role": "user",')
        print('          "parts": [{')
        print('            "type": "text",')
        print('            "text": "Analyze security threats in network traffic data"')
        print('          }]')
        print('        }')
        print('      }')
        print("    }'")
        print()
        
        print("📊 MONITORING DASHBOARDS:")
        print("  Security Intelligence: http://localhost:8003/dashboard")
        print("  Agent Communications: http://localhost:8003/communications")
        print("  Security Events: http://localhost:8003/security-events")
        print()
        
        print("🏆 HACKATHON READY:")
        print("  ✅ Google A2A Protocol Implementation")
        print("  ✅ Multi-Agent Security Intelligence")
        print("  ✅ Distributed Octopus Architecture")
        print("  ✅ Real-time Threat Detection")
        print("  ✅ Executive-Level Reporting")
        print("  ✅ Compliance Framework Analysis")
        
        print("\n⚠️  Press Ctrl+C to stop all components")
    
    def cleanup(self):
        """Clean up all running processes"""
        print("\n🛑 Stopping Inktrace components...")
        
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("✅ All components stopped")
        print("🌊 Tentacles retracted to the deep...")
    
    def launch(self, skip_tests: bool = False):
        """Launch the complete Inktrace system"""
        print("🐙 INKTRACE LAUNCHER")
        print("Agent-Based Security Intelligence from the Deep")
        print("=" * 50)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Start agents
        print("\n🤖 Starting A2A Agents...")
        agents_started = 0
        for agent_name, config in self.agents.items():
            if self.start_component("agent", agent_name, config):
                agents_started += 1
        
        # Start tentacles  
        print("\n🐙 Deploying Security Tentacles...")
        tentacles_started = 0
        for tentacle_name, config in self.tentacles.items():
            if self.start_component("tentacle", tentacle_name, config):
                tentacles_started += 1
        
        if agents_started == 0:
            print("❌ No agents started successfully")
            return False
        
        # Wait for system to be ready
        if not self.wait_for_agents_ready():
            print("⚠️ System may not be fully operational")
        
        # Test communication
        if not skip_tests:
            if not self.test_a2a_communication():
                print("⚠️ A2A communication tests had issues")
        
        # Show status
        self.show_system_status()
        
        return True

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print("\n🛑 Received interrupt signal...")
    sys.exit(0)

def main():
    """Main launcher entry point"""
    parser = argparse.ArgumentParser(description="🐙 Inktrace System Launcher")
    parser.add_argument("--skip-tests", action="store_true", 
                       help="Skip A2A communication tests")
    parser.add_argument("--agents-only", action="store_true",
                       help="Start only agents, skip tentacles")
    args = parser.parse_args()
    
    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)
    
    launcher = InktraceLauncher()
    
    # Remove tentacles if agents-only mode
    if args.agents_only:
        launcher.tentacles = {}
    
    try:
        if launcher.launch(skip_tests=args.skip_tests):
            # Keep running until interrupted
            while True:
                time.sleep(1)
        else:
            print("❌ Failed to launch Inktrace system")
            sys.exit(1)
    except KeyboardInterrupt:
        pass
    finally:
        launcher.cleanup()

if __name__ == "__main__":
    main()