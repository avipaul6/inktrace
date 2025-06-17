#!/usr/bin/env python3
"""
🐙 Inktrace Development Launcher - Template-Based Version
scripts/launch.py

Launch the complete Inktrace distributed intelligence system for development and demo.
UPDATED: Works with template-based wiretap tentacle
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
    """🐙 Inktrace System Launcher - Template-Based"""

    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.project_root = Path(__file__).parent.parent
        self.agents_dir = self.project_root / "agents"
        self.tentacles_dir = self.project_root / "tentacles"

        # Ensure template directories exist
        self.ensure_template_structure()

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
                "function": "Real-time A2A Communications Monitor with Template Dashboard"
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
            
        # Check for critical template files
        critical_files = [
            self.project_root / "templates" / "dashboard.html",
            self.project_root / "static" / "css" / "dashboard.css",
            self.project_root / "static" / "js" / "dashboard.js"
        ]
        
        missing_files = [f for f in critical_files if not f.exists()]
        if missing_files:
            print("⚠️ Missing template files:")
            for f in missing_files:
                print(f"   - {f}")
            print("📝 Please ensure all template files are created as per the implementation guide.")

    def check_dependencies(self) -> bool:
        """Check if required dependencies are installed"""
        print("🔍 Checking dependencies...")

        required_checks = [
            ("fastapi", "FastAPI web framework"),
            ("uvicorn", "ASGI server"),
            ("httpx", "HTTP client"),
            ("requests", "HTTP requests"),
            ("jinja2", "Jinja2 templating engine"),  # Added for templates
            ("aiohttp", "Async HTTP client")
        ]

        missing_packages = []

        for package, description in required_checks:
            try:
                __import__(package)
                print(f"✅ {description}: Available")
            except ImportError:
                missing_packages.append((package, description))
                print(f"❌ {description}: Missing")

        if missing_packages:
            print(f"\n📦 Missing packages detected!")
            print("Run: uv pip install fastapi uvicorn httpx requests jinja2 aiohttp")
            return False

        return True

    def start_component(self, component_type: str, name: str, config: Dict) -> bool:
        """Start an individual component (agent or tentacle)"""
        script_path = (self.agents_dir if component_type == "agent" else self.tentacles_dir) / config["script"]
        
        if not script_path.exists():
            print(f"❌ {config['name']}: Script not found at {script_path}")
            return False

        try:
            print(f"🚀 Starting {config['name']} on port {config['port']}...")
            
            # Use python -m to ensure proper module loading
            if component_type == "agent":
                cmd = [sys.executable, "-m", f"agents.{config['script'][:-3]}", "--port", str(config['port'])]
            else:
                cmd = [sys.executable, "-m", f"tentacles.{config['script'][:-3]}", "--port", str(config['port'])]
            
            process = subprocess.Popen(
                cmd,
                cwd=self.project_root,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            self.processes.append(process)
            
            # Wait a moment and check if process started successfully
            time.sleep(1)
            if process.poll() is None:
                print(f"✅ {config['name']}: Started successfully")
                return True
            else:
                stdout, stderr = process.communicate()
                print(f"❌ {config['name']}: Failed to start")
                if stderr:
                    print(f"   Error: {stderr}")
                return False
                
        except Exception as e:
            print(f"❌ {config['name']}: Failed to start - {e}")
            return False

    def wait_for_agents_ready(self, timeout: int = 30) -> bool:
        """Wait for agents to be ready for A2A communication"""
        print("⏳ Waiting for agents to be ready...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            ready_count = 0
            
            for agent_name, config in self.agents.items():
                try:
                    response = requests.get(
                        f"http://localhost:{config['port']}/.well-known/agent.json",
                        timeout=2
                    )
                    if response.status_code == 200:
                        ready_count += 1
                except:
                    pass
            
            if ready_count == len(self.agents):
                print(f"✅ All {ready_count} agents are ready!")
                return True
            
            print(f"⏳ {ready_count}/{len(self.agents)} agents ready, waiting...")
            time.sleep(2)
        
        print(f"⚠️ Timeout: Only {ready_count}/{len(self.agents)} agents ready")
        return False

    def test_a2a_communication(self) -> bool:
        """Test A2A communication between agents"""
        print("🧪 Testing A2A communication...")
        
        try:
            # Test simple communication between agents
            response = requests.post(
                "http://localhost:8002/",
                json={
                    "jsonrpc": "2.0",
                    "id": "test-communication",
                    "method": "tasks/send",
                    "params": {
                        "id": "test-001",
                        "sessionId": "launch-test",
                        "message": {
                            "role": "user",
                            "parts": [{
                                "type": "text",
                                "text": "Generate a test security report for launch verification"
                            }]
                        }
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                print("✅ A2A communication test successful")
                return True
            else:
                print(f"⚠️ A2A communication test failed: HTTP {response.status_code}")
                return False
                
        except Exception as e:
            print(f"⚠️ A2A communication test failed: {e}")
            return False

    def check_dashboard_ready(self, timeout: int = 15) -> bool:
        """Check if the dashboard is ready"""
        print("🌐 Checking dashboard availability...")
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                response = requests.get("http://localhost:8003/dashboard", timeout=3)
                if response.status_code == 200:
                    print("✅ Dashboard is ready!")
                    return True
            except:
                pass
            
            print("⏳ Waiting for dashboard...")
            time.sleep(2)
        
        print("⚠️ Dashboard not responding")
        return False

    def show_system_status(self, communication_working: bool = False):
        """Display system status and access information"""
        print("\n" + "="*70)
        print("🐙 INKTRACE SECURITY INTELLIGENCE SYSTEM")
        print("="*70)
        
        print("\n📊 SYSTEM COMPONENTS:")
        for agent_name, config in self.agents.items():
            print(f"  🤖 {config['name']}: http://localhost:{config['port']}")
        
        for tentacle_name, config in self.tentacles.items():
            print(f"  🐙 {config['name']}: http://localhost:{config['port']}")
        
        print("\n🌐 DASHBOARD ACCESS:")
        print(f"  📊 Main Dashboard: http://localhost:8003/dashboard")
        print(f"  🔍 Communications: http://localhost:8003/communications")
        print(f"  🛡️ Security Events: http://localhost:8003/security-events")
        print(f"  🔌 API Endpoint: http://localhost:8003/api/agents")
        
        print("\n🧪 DEMO SCENARIOS:")
        print("  # Start malicious agent for demo")
        print("  python demo/malicious_agent_auto.py --port 8004")
        print("\n  # Test A2A communication")
        print("  python scripts/test_a2a.py")
        
        print("\n📈 STATUS INDICATORS:")
        print(f"  {'✅' if communication_working else '⚠️'} A2A Communication")
        print(f"  {'✅' if len(self.processes) > 0 else '❌'} System Components")
        print(f"  🐙 Template-Based Dashboard")
        
        print("\n🎯 HACKATHON FEATURES:")
        print("  • Real-time agent discovery & threat detection")
        print("  • 8-Tentacle security matrix visualization")
        print("  • Professional template-based dashboard")
        print("  • WebSocket real-time updates")
        print("  • Critical alert system for malicious agents")
        
        print("\n💡 Press Ctrl+C to stop all components")
        print("="*70)

    def cleanup(self):
        """Clean up all processes"""
        print("\n🛑 Stopping all Inktrace components...")
        
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        print("✅ All components stopped")

    def launch(self, skip_tests: bool = False) -> bool:
        """Launch the complete Inktrace system"""
        print("🐙 LAUNCHING INKTRACE SECURITY INTELLIGENCE SYSTEM")
        print("=" * 60)
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Start agents
        print("\n🤖 Deploying Security Agents...")
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

        if tentacles_started == 0:
            print("❌ No tentacles started successfully")
            return False

        # Wait for system to be ready
        if not self.wait_for_agents_ready():
            print("⚠️ System may not be fully operational")

        # Check dashboard
        if not self.check_dashboard_ready():
            print("⚠️ Dashboard may not be ready")

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
    parser.add_argument("--dashboard-only", action="store_true",
                        help="Start only the dashboard tentacle")
    args = parser.parse_args()

    # Set up signal handler
    signal.signal(signal.SIGINT, signal_handler)

    launcher = InktraceLauncher()

    # Modify configuration based on arguments
    if args.agents_only:
        launcher.tentacles = {}
    elif args.dashboard_only:
        launcher.agents = {}

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