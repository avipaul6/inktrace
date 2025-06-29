#!/usr/bin/env python3
"""
🐙 FIXED Inktrace Launcher - No More Hangs!
This version fixes the subprocess pipe overflow issue
"""

import subprocess
import time
import sys
import os
import signal
import socket
from pathlib import Path


class FixedInktraceLauncher:
    def __init__(self):
        self.processes = []
        
        # Services configuration
        self.services = {
            "data_processor": {"script": "agents/data_processor.py", "port": 8001},
            "report_generator": {"script": "agents/report_generator.py", "port": 8002},
            "wiretap": {"script": "tentacles/wiretap.py", "port": 8003},
            "policy_agent": {"script": "agents/policy_agent.py", "port": 8006}
        }
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self.cleanup_and_exit)
        signal.signal(signal.SIGTERM, self.cleanup_and_exit)
    
    def cleanup_and_exit(self, signum=None, frame=None):
        """Clean shutdown"""
        print("\n🛑 Shutting down...")
        for process in self.processes:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        sys.exit(0)
    
    def wait_for_port(self, port, timeout=20):
        """Wait for port to become available"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                if result == 0:
                    return True
            except:
                pass
            time.sleep(0.5)
        return False
    
    def start_service(self, name, config):
        """Start a service with fixed subprocess handling"""
        script_path = Path(config["script"])
        
        if not script_path.exists():
            print(f"❌ {name}: Script not found: {script_path}")
            return False
        
        print(f"🚀 Starting {name} on port {config['port']}...")
        
        try:
            # FIXED: Use DEVNULL instead of PIPE to prevent hangs
            process = subprocess.Popen([
                sys.executable, str(script_path),
                "--host", "0.0.0.0",
                "--port", str(config["port"])
            ],
            stdout=subprocess.DEVNULL,  # ✅ No more pipe overflow!
            stderr=subprocess.DEVNULL,  # ✅ No more pipe overflow!
            stdin=subprocess.DEVNULL    # ✅ No input blocking!
            )
            
            self.processes.append(process)
            
            # Wait for port binding
            if self.wait_for_port(config["port"]):
                print(f"✅ {name} started successfully (PID: {process.pid})")
                return True
            else:
                print(f"❌ {name} failed to bind to port")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return False
    
    def run(self):
        """Run the launcher"""
        print("🐙 FIXED INKTRACE LAUNCHER")
        print("=" * 50)
        print("✅ Pipe overflow prevention enabled")
        print("✅ Proper subprocess handling")
        print("✅ Clean shutdown support")
        print("=" * 50)
        
        success_count = 0
        
        # Start all services
        for name, config in self.services.items():
            if self.start_service(name, config):
                success_count += 1
            time.sleep(2)  # Stagger startup
        
        print(f"\n📊 Started {success_count}/{len(self.services)} services")
        
        if success_count == 0:
            print("❌ No services started")
            return False
        
        print("\n🎯 INKTRACE READY!")
        print("=" * 50)
        print("🌐 Wiretap Dashboard: http://localhost:8003/dashboard")
        print("🔍 Communications: http://localhost:8003/communications")
        print("=" * 50)
        print("\n🔄 Running... Press Ctrl+C to stop")
        
        try:
            # Monitor processes
            while True:
                time.sleep(10)
                alive_count = sum(1 for p in self.processes if p.poll() is None)
                if alive_count < len(self.processes):
                    print(f"⚠️ Some processes died ({alive_count}/{len(self.processes)} alive)")
        except KeyboardInterrupt:
            pass
        finally:
            self.cleanup_and_exit()
        
        return True


if __name__ == "__main__":
    launcher = FixedInktraceLauncher()
    launcher.run()
