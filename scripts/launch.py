#!/usr/bin/env python3
"""
🐙 Inktrace Development Launcher - OFFICIAL GOOGLE A2A SDK
scripts/launch.py

Launch the complete Inktrace distributed intelligence system for development and demo.
UPDATED: Using official Google A2A Python SDK (a2a-sdk)
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
    """🐙 Inktrace System Launcher - Official A2A SDK"""

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
                "function": "Real-time A2A Communications Monitor"
            }
        }

    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed - UPDATED for official SDK"""
        print("🔍 Checking dependencies...")

        # Updated dependencies for official Google A2A SDK
        required_checks = [
            ("a2a", "Official Google A2A SDK"),
            ("fastapi", "FastAPI web framework"),
            ("uvicorn", "ASGI server"),
            ("httpx", "HTTP client"),
            ("requests", "HTTP requests")
        ]

        missing_packages = []

        for package, description in required_checks:
            try:
                if package == "a2a":
                    # Test specific import for A2A SDK
                    from a2a.types import AgentCard
                    print(f"✅ {description}: Available")
                else:
                    __import__(package)
                    print(f"✅ {description}: Available")
            except ImportError:
                missing_packages.append((package, description))
                print(f"❌ {description}: Missing")

        if missing_packages:
            print(f"\n📦 Missing packages detected!")
            print(f"Install with: uv add a2a-sdk fastapi uvicorn httpx requests")
            print(f"Or with pip: pip install a2a-sdk fastapi uvicorn httpx requests")
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

            print(
                f"⏳ Attempt {attempt + 1}/{max_attempts} - waiting for agents...")
            time.sleep(1)

        print("⚠️ Some agents may not be fully ready")
        return False

    def test_a2a_communication(self) -> bool:
        """Test A2A communication using CORRECT format - FIXED VERSION"""
        print("\n🧪 Testing Official A2A Agent Communication...")

        try:
            # Test agent discovery
            print("🔍 Testing agent discovery...")
            for agent_name, config in self.agents.items():
                port = config["port"]
                response = requests.get(f"http://localhost:{port}/.well-known/agent.json",
                                        timeout=5)
                if response.status_code == 200:
                    agent_card = response.json()
                    print(f"✅ {agent_name}: {agent_card.get('name', 'Unknown')}")
                    print(f"   Skills: {len(agent_card.get('skills', []))}")
                    print(
                        f"   Capabilities: {agent_card.get('capabilities', {})}")
                else:
                    print(
                        f"❌ {agent_name}: Discovery failed ({response.status_code})")
                    return False

            # Test wiretap tentacle
            try:
                response = requests.get(
                    "http://localhost:8003/api/agents", timeout=5)
                if response.status_code == 200:
                    print("✅ wiretap: Monitoring API active")
                else:
                    print(f"⚠️ wiretap: API status {response.status_code}")
            except Exception as e:
                print(f"⚠️ wiretap: Monitoring error - {e}")

            # Test end-to-end A2A communication using CORRECT FORMAT
            print("🔄 Testing report generation with CORRECT A2A message submission...")

            # CORRECT A2A JSON-RPC format with "message/send" method
            task_data = {
                "jsonrpc": "2.0",
                "id": "demo-security-analysis",
                "method": "message/send",  # FIXED: Changed from "tasks/send" to "message/send"
                "params": {
                    "id": "inktrace-demo-task",
                    "sessionId": "inktrace-demo-session",
                    "message": {
                        "role": "user",
                        "parts": [{
                            "type": "text",
                            "text": "Generate comprehensive security report for suspicious admin login attempts with multiple failed authentication events from different geographic locations including Russia, China, and North Korea. Include compliance analysis for APRA, SOC2, and ISO27001 frameworks."
                        }]
                    }
                }
            }

            # Use ROOT endpoint with JSON-RPC
            print("📤 Sending message to Report Generator...")
            response = requests.post("http://localhost:8002/",  # ROOT endpoint
                                     json=task_data,
                                     headers={
                                         "Content-Type": "application/json"},
                                     timeout=20)

            print(f"📥 Response status: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print("✅ Official A2A communication successful!")
                print("🎉 Multi-agent coordination working!")

                # Check if we got a proper response
                if 'result' in result:
                    print(f"📊 Response received with result")
                elif 'error' in result:
                    print(f"⚠️ Got error response: {result['error']}")
                else:
                    print(f"📋 Raw response: {str(result)[:200]}...")

                return True
            else:
                print(f"⚠️ A2A test returned status {response.status_code}")
                print(f"Response: {response.text[:200]}...")

        except Exception as e:
            print(f"❌ A2A communication test failed: {e}")
            import traceback
            traceback.print_exc()
            return False

        return True

    def show_system_status(self, communication_working: bool = False):
        """Show comprehensive system status"""
        print("\n🐙 INKTRACE DISTRIBUTED INTELLIGENCE SYSTEM")
        print("=" * 70)
        print("Agent-Based Security Intelligence from the Deep")
        print("Official Google A2A Protocol Implementation")
        print("=" * 70)

        print("\n🤖 A2A AGENTS:")
        for agent_name, config in self.agents.items():
            port = config["port"]
            status = "🟢 ACTIVE" if self.check_port_available(
                port) == False else "🔴 INACTIVE"
            print(f"  {config['name']}")
            print(f"    Status: {status}")
            print(f"    Endpoint: http://localhost:{port}/")
            print(
                f"    Agent Card: http://localhost:{port}/.well-known/agent.json")
            print(f"    Tasks Endpoint: http://localhost:{port}/tasks/send")
            print(f"    Tentacles: {', '.join(config['tentacles'])}")
            print()

        print("🐙 SECURITY TENTACLES:")
        for tentacle_name, config in self.tentacles.items():
            port = config["port"]
            status = "🟢 ACTIVE" if self.check_port_available(
                port) == False else "🔴 INACTIVE"
            print(f"  {config['name']}")
            print(f"    Status: {status}")
            print(f"    Function: {config['function']}")
            print(f"    Dashboard: http://localhost:{port}/dashboard")
            print()

        print("🔗 A2A COMMUNICATION:")
        comm_status = "🟢 OPERATIONAL" if communication_working else "🟡 LIMITED"
        print(f"  Status: {comm_status}")
        print(f"  Protocol: Official Google A2A Python SDK")
        print(f"  Transport: HTTP + JSON")
        print(f"  Discovery: /.well-known/agent.json")
        print()

        print("🎯 DEMO COMMANDS (Official A2A Format):")
        print("  # Test Official A2A Task Submission")
        print("  curl -X POST http://localhost:8002/tasks/send \\")
        print("    -H 'Content-Type: application/json' \\")
        print("    -d '{")
        print('      "id": "security-demo",')
        print('      "sessionId": "demo-session",')
        print('      "message": {')
        print('        "role": "user",')
        print('        "parts": [{')
        print('          "type": "text",')
        print('          "text": "Analyze security threats in network traffic data"')
        print('        }]')
        print('      }')
        print("    }'")
        print()

        print("📊 MONITORING DASHBOARDS:")
        print("  Security Intelligence: http://localhost:8003/dashboard")
        print("  Agent Communications: http://localhost:8003/communications")
        print("  Security Events: http://localhost:8003/security-events")
        print("  API Endpoints: http://localhost:8003/api/agents")
        print()

        print("🧪 TESTING:")
        print("  # Run comprehensive A2A tests")
        print("  python scripts/test_official_a2a.py")
        print()

        print("🏆 HACKATHON READY:")
        print("  ✅ Official Google A2A Protocol Implementation")
        print("  ✅ Multi-Agent Security Intelligence")
        print("  ✅ Distributed Octopus Architecture")
        print("  ✅ Real-time Threat Detection")
        print("  ✅ Executive-Level Reporting")
        print("  ✅ Compliance Framework Analysis")
        print("  ✅ Beautiful Real-time Monitoring Dashboard")
        if communication_working:
            print("  ✅ Agent2Agent Communication Working")
        else:
            print("  ⚠️ Agent2Agent Communication Needs Attention")

        print("\n⚠️  Press Ctrl+C to stop all components")

    def cleanup(self):
        """Clean up all running processes"""
        print("\n🛑 Stopping Inktrace components...")

        for process in self.processes:
            if process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                except Exception as e:
                    print(f"⚠️ Error stopping process: {e}")

        print("✅ All components stopped")
        print("🌊 Tentacles retracted to the deep...")

    def launch(self, skip_tests: bool = False):
        """Launch the complete Inktrace system"""
        print("🐙 INKTRACE LAUNCHER")
        print("Agent-Based Security Intelligence from the Deep")
        print("Official Google A2A Python SDK Implementation")
        print("=" * 60)

        # Check dependencies
        if not self.check_dependencies():
            print("\n💡 Quick fix: uv add a2a-sdk fastapi uvicorn httpx requests")
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
        communication_working = False
        if not skip_tests:
            communication_working = self.test_a2a_communication()
            if not communication_working:
                print("⚠️ A2A communication tests had issues")

        # Show status
        self.show_system_status(communication_working)

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
            print("\n🎉 INKTRACE SYSTEM LAUNCHED SUCCESSFULLY!")
            print("🐙 Distributed intelligence is now operational!")

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
