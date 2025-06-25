#!/usr/bin/env python3
"""
🐙 Inktrace System Monitor and Debug Tools
Advanced debugging toolkit for diagnosing system freezes and hangs

Key Issues Identified:
1. Subprocess PIPE buffer overflow (stdout/stderr pipes filling up)
2. Blocking socket operations causing deadlocks
3. Memory leaks from unclosed file handles
4. Infinite loops in health checks
5. Resource exhaustion from spawned processes
"""

import asyncio
import psutil
import subprocess
import time
import sys
import os
import threading
import queue
import signal
import resource
import socket
import requests
from pathlib import Path
from typing import List, Dict, Optional
import json
from datetime import datetime
import logging


class InktraceSystemMonitor:
    """Real-time system monitoring with freeze detection"""
    
    def __init__(self):
        self.monitored_processes = []
        self.monitoring_active = False
        self.alerts = []
        self.start_time = time.time()
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('inktrace_monitor.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)
    
    def detect_subprocess_pipe_overflow(self, process: subprocess.Popen) -> Dict:
        """Detect if subprocess pipes are full (major cause of hangs)"""
        try:
            if not process.stdout:
                return {"status": "no_stdout", "risk": "low"}
            
            # Try to read from stdout without blocking
            try:
                # Check if there's data available
                import select
                ready, _, _ = select.select([process.stdout], [], [], 0)
                if ready:
                    data = process.stdout.read(1024)  # Read some data to prevent overflow
                    if len(data) >= 1024:
                        return {
                            "status": "pipe_overflow_detected",
                            "risk": "critical",
                            "message": "Subprocess stdout buffer is full - this WILL cause hangs",
                            "data_sample": data[:100].decode('utf-8', errors='ignore')
                        }
                return {"status": "pipe_healthy", "risk": "low"}
            except Exception as e:
                return {"status": "pipe_check_failed", "risk": "medium", "error": str(e)}
                
        except Exception as e:
            return {"status": "check_failed", "risk": "unknown", "error": str(e)}
    
    def monitor_resource_usage(self, pid: int) -> Dict:
        """Monitor CPU, memory, and file handles for a process"""
        try:
            process = psutil.Process(pid)
            
            # Get resource usage
            cpu_percent = process.cpu_percent()
            memory_info = process.memory_info()
            num_fds = process.num_fds() if hasattr(process, 'num_fds') else 0
            num_threads = process.num_threads()
            
            # Check for resource leaks
            warnings = []
            if num_fds > 100:
                warnings.append(f"High file descriptor count: {num_fds}")
            if memory_info.rss > 500 * 1024 * 1024:  # 500MB
                warnings.append(f"High memory usage: {memory_info.rss / 1024 / 1024:.1f}MB")
            if num_threads > 20:
                warnings.append(f"High thread count: {num_threads}")
            
            return {
                "pid": pid,
                "cpu_percent": cpu_percent,
                "memory_mb": memory_info.rss / 1024 / 1024,
                "file_descriptors": num_fds,
                "threads": num_threads,
                "warnings": warnings,
                "status": "warning" if warnings else "healthy"
            }
            
        except psutil.NoSuchProcess:
            return {"pid": pid, "status": "dead"}
        except Exception as e:
            return {"pid": pid, "status": "error", "error": str(e)}
    
    def detect_deadlocks(self) -> List[Dict]:
        """Detect potential deadlocks in the system"""
        deadlocks = []
        
        # Check for processes in uninterruptible sleep (D state)
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cmdline']):
            try:
                if proc.info['status'] == psutil.STATUS_DISK_SLEEP:
                    if any('inktrace' in arg.lower() for arg in proc.info['cmdline']):
                        deadlocks.append({
                            "type": "disk_sleep_deadlock",
                            "pid": proc.info['pid'],
                            "name": proc.info['name'],
                            "cmdline": ' '.join(proc.info['cmdline'][:3])
                        })
            except:
                continue
        
        # Check for zombie processes
        for proc in psutil.process_iter(['pid', 'name', 'status', 'cmdline']):
            try:
                if proc.info['status'] == psutil.STATUS_ZOMBIE:
                    if any('inktrace' in arg.lower() for arg in proc.info['cmdline']):
                        deadlocks.append({
                            "type": "zombie_process",
                            "pid": proc.info['pid'],
                            "name": proc.info['name']
                        })
            except:
                continue
        
        return deadlocks
    
    def check_port_responsiveness(self, port: int, timeout: int = 5) -> Dict:
        """Check if a port is responsive and not hanging"""
        start_time = time.time()
        
        try:
            # Socket connection test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(timeout)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            connect_time = time.time() - start_time
            
            if result == 0:
                # Port is bound, now test HTTP responsiveness
                try:
                    response = requests.get(f"http://localhost:{port}/", timeout=timeout)
                    response_time = time.time() - start_time
                    
                    return {
                        "port": port,
                        "status": "responsive",
                        "connect_time": connect_time,
                        "response_time": response_time,
                        "http_status": response.status_code,
                        "risk": "low" if response_time < 2 else "medium"
                    }
                except requests.exceptions.Timeout:
                    return {
                        "port": port,
                        "status": "hanging",
                        "connect_time": connect_time,
                        "risk": "critical",
                        "message": "Port bound but HTTP requests timeout - HANGING DETECTED"
                    }
                except Exception as e:
                    return {
                        "port": port,
                        "status": "bound_no_http",
                        "connect_time": connect_time,
                        "risk": "medium",
                        "error": str(e)
                    }
            else:
                return {
                    "port": port,
                    "status": "unbound",
                    "risk": "high",
                    "message": "Port not bound - service may have died"
                }
                
        except Exception as e:
            return {
                "port": port,
                "status": "check_failed",
                "risk": "unknown",
                "error": str(e)
            }
    
    def generate_system_report(self) -> Dict:
        """Generate comprehensive system health report"""
        report = {
            "timestamp": datetime.now().isoformat(),
            "uptime_seconds": time.time() - self.start_time,
            "system_load": os.getloadavg() if hasattr(os, 'getloadavg') else "unknown",
            "python_processes": [],
            "port_status": {},
            "deadlocks": self.detect_deadlocks(),
            "alerts": self.alerts[-10:],  # Last 10 alerts
            "recommendations": []
        }
        
        # Check all Inktrace processes
        inktrace_ports = [8001, 8002, 8003, 8006]
        for port in inktrace_ports:
            report["port_status"][port] = self.check_port_responsiveness(port)
        
        # Find Python processes related to Inktrace
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
            try:
                if proc.info['name'] in ['python', 'python3']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if any(script in cmdline for script in ['data_processor', 'report_generator', 'wiretap', 'policy_agent', 'launch']):
                        resource_info = self.monitor_resource_usage(proc.info['pid'])
                        report["python_processes"].append({
                            "pid": proc.info['pid'],
                            "cmdline": cmdline[:100],
                            "status": proc.info['status'],
                            "resources": resource_info
                        })
            except:
                continue
        
        # Generate recommendations
        if report["deadlocks"]:
            report["recommendations"].append("CRITICAL: Deadlocks detected - restart system immediately")
        
        for port_info in report["port_status"].values():
            if port_info.get("status") == "hanging":
                report["recommendations"].append(f"CRITICAL: Port {port_info['port']} is hanging - kill and restart")
        
        if len(report["python_processes"]) > 10:
            report["recommendations"].append("WARNING: Too many Python processes - potential memory leak")
        
        return report


class InktraceDebugTools:
    """Advanced debugging tools for specific Inktrace issues"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def fix_subprocess_pipes(self, script_path: str, port: int) -> subprocess.Popen:
        """Launch subprocess with proper pipe handling to prevent hangs"""
        
        # Create a proper subprocess that won't hang
        try:
            # Use DEVNULL for stdout/stderr to prevent pipe overflow
            process = subprocess.Popen([
                sys.executable, script_path,
                "--host", "0.0.0.0",
                "--port", str(port)
            ], 
            stdout=subprocess.DEVNULL,  # Prevents pipe overflow
            stderr=subprocess.DEVNULL,  # Prevents pipe overflow
            stdin=subprocess.DEVNULL,   # Prevents blocking on input
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None,  # Creates new process group
            start_new_session=True  # Prevents signal propagation issues
            )
            
            self.logger.info(f"Started {script_path} on port {port} with PID {process.pid}")
            return process
            
        except Exception as e:
            self.logger.error(f"Failed to start {script_path}: {e}")
            return None
    
    def kill_hanging_processes(self) -> List[str]:
        """Kill all hanging Inktrace processes"""
        killed = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status']):
            try:
                if proc.info['name'] in ['python', 'python3']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if any(script in cmdline for script in ['data_processor', 'report_generator', 'wiretap', 'policy_agent']):
                        # Check if process is hanging
                        if proc.info['status'] in [psutil.STATUS_DISK_SLEEP, psutil.STATUS_ZOMBIE]:
                            proc.kill()
                            killed.append(f"Killed hanging process PID {proc.info['pid']}: {cmdline[:50]}")
                        elif proc.info['status'] == psutil.STATUS_SLEEPING:
                            # Check how long it's been sleeping
                            try:
                                create_time = proc.create_time()
                                if time.time() - create_time > 300:  # 5 minutes
                                    proc.kill()
                                    killed.append(f"Killed long-sleeping process PID {proc.info['pid']}: {cmdline[:50]}")
                            except:
                                pass
            except:
                continue
        
        return killed
    
    def test_individual_services(self) -> Dict[str, Dict]:
        """Test each service individually to isolate problems"""
        services = {
            "data_processor": {"script": "agents/data_processor.py", "port": 8001},
            "report_generator": {"script": "agents/report_generator.py", "port": 8002},
            "wiretap": {"script": "tentacles/wiretap.py", "port": 8003},
            "policy_agent": {"script": "agents/policy_agent.py", "port": 8006}
        }
        
        results = {}
        
        for service_name, config in services.items():
            self.logger.info(f"Testing {service_name}...")
            
            # Test if script exists
            script_path = Path(config["script"])
            if not script_path.exists():
                results[service_name] = {
                    "status": "script_missing",
                    "error": f"Script not found: {script_path}"
                }
                continue
            
            # Try to start the service
            start_time = time.time()
            process = self.fix_subprocess_pipes(str(script_path), config["port"])
            
            if not process:
                results[service_name] = {
                    "status": "startup_failed",
                    "error": "Failed to start process"
                }
                continue
            
            # Wait for service to start
            max_wait = 30
            service_ready = False
            
            for i in range(max_wait):
                if process.poll() is not None:
                    results[service_name] = {
                        "status": "process_died",
                        "error": f"Process died after {i} seconds",
                        "return_code": process.returncode
                    }
                    break
                
                # Test port binding
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(1)
                    result = sock.connect_ex(('localhost', config["port"]))
                    sock.close()
                    
                    if result == 0:
                        service_ready = True
                        startup_time = time.time() - start_time
                        results[service_name] = {
                            "status": "success",
                            "startup_time": startup_time,
                            "pid": process.pid
                        }
                        break
                        
                except Exception as e:
                    pass
                
                time.sleep(1)
            
            if not service_ready and process.poll() is None:
                results[service_name] = {
                    "status": "startup_timeout",
                    "error": f"Service didn't bind to port after {max_wait} seconds"
                }
                process.kill()
            
            # Clean up
            if process and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        return results
    
    def create_robust_launcher(self) -> str:
        """Create a robust launcher script that won't hang"""
        
        launcher_code = '''#!/usr/bin/env python3
"""
🐙 Robust Inktrace Launcher - Anti-Hang Version
This launcher prevents the common hanging issues in the original launch.py
"""

import subprocess
import time
import sys
import os
import signal
import socket
from pathlib import Path
from typing import List, Dict
import threading
import queue


class RobustInktraceLauncher:
    """Hang-resistant launcher for Inktrace services"""
    
    def __init__(self):
        self.processes: List[subprocess.Popen] = []
        self.services = {
            "data_processor": {"script": "agents/data_processor.py", "port": 8001},
            "report_generator": {"script": "agents/report_generator.py", "port": 8002},
            "wiretap": {"script": "tentacles/wiretap.py", "port": 8003},
            "policy_agent": {"script": "agents/policy_agent.py", "port": 8006}
        }
        
        # Set up signal handlers for clean shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        print(f"\\n🛑 Received signal {signum}, shutting down...")
        self.cleanup_all()
        sys.exit(0)
    
    def start_service_robust(self, name: str, config: Dict) -> bool:
        """Start a service with anti-hang measures"""
        script_path = Path(config["script"])
        
        if not script_path.exists():
            print(f"❌ {name}: Script not found: {script_path}")
            return False
        
        print(f"🚀 Starting {name} on port {config['port']}...")
        
        try:
            # Start with proper pipe handling to prevent hangs
            process = subprocess.Popen([
                sys.executable, str(script_path),
                "--host", "0.0.0.0",
                "--port", str(config["port"])
            ],
            stdout=subprocess.DEVNULL,  # Prevents pipe overflow hangs
            stderr=subprocess.DEVNULL,  # Prevents pipe overflow hangs
            stdin=subprocess.DEVNULL,   # Prevents input blocking
            preexec_fn=os.setsid if hasattr(os, 'setsid') else None
            )
            
            self.processes.append(process)
            
            # Wait for port binding with timeout
            if self.wait_for_port(config["port"], timeout=20):
                print(f"✅ {name} started successfully (PID: {process.pid})")
                return True
            else:
                print(f"❌ {name} failed to bind to port {config['port']}")
                return False
                
        except Exception as e:
            print(f"❌ Failed to start {name}: {e}")
            return False
    
    def wait_for_port(self, port: int, timeout: int = 20) -> bool:
        """Wait for a port to become available with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex(('localhost', port))
                sock.close()
                
                if result == 0:
                    return True
                    
            except Exception:
                pass
            
            time.sleep(0.5)
        
        return False
    
    def monitor_processes(self):
        """Monitor processes and restart if they die"""
        while True:
            time.sleep(10)
            
            for i, process in enumerate(self.processes):
                if process.poll() is not None:
                    print(f"⚠️ Process {process.pid} died with code {process.returncode}")
                    # Could implement restart logic here
            
            # Check if all processes are dead
            alive_count = sum(1 for p in self.processes if p.poll() is None)
            if alive_count == 0 and self.processes:
                print("❌ All processes died!")
                break
    
    def cleanup_all(self):
        """Clean up all processes"""
        print("🧹 Cleaning up processes...")
        
        for process in self.processes:
            if process.poll() is None:
                try:
                    process.terminate()
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
        
        print("✅ Cleanup complete")
    
    def run(self):
        """Run the launcher"""
        print("🐙 ROBUST INKTRACE LAUNCHER")
        print("=" * 50)
        print("Anti-hang measures enabled:")
        print("✅ Pipe overflow prevention")
        print("✅ Timeout-based startup detection")
        print("✅ Process monitoring")
        print("✅ Graceful shutdown")
        print("=" * 50)
        
        success_count = 0
        
        # Start all services
        for name, config in self.services.items():
            if self.start_service_robust(name, config):
                success_count += 1
            time.sleep(2)  # Stagger startup
        
        print(f"\\n📊 Started {success_count}/{len(self.services)} services")
        
        if success_count == 0:
            print("❌ No services started - check logs for errors")
            return False
        
        print("\\n🎯 INKTRACE READY!")
        print("=" * 50)
        print("🌐 Wiretap Dashboard: http://localhost:8003/dashboard")
        print("🔍 Communications: http://localhost:8003/communications")
        print("📊 Agents Status: Check individual agent ports")
        print("=" * 50)
        print("\\n🔄 Monitoring processes... Press Ctrl+C to stop")
        
        # Start monitoring in background
        monitor_thread = threading.Thread(target=self.monitor_processes, daemon=True)
        monitor_thread.start()
        
        try:
            # Keep main thread alive
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\\n🛑 Shutdown requested...")
        finally:
            self.cleanup_all()
        
        return True


if __name__ == "__main__":
    launcher = RobustInktraceLauncher()
    success = launcher.run()
    sys.exit(0 if success else 1)
'''
        
        return launcher_code


def main():
    """Main diagnostic and repair function"""
    print("🐙 INKTRACE ADVANCED DEBUGGING TOOLKIT")
    print("=" * 60)
    print("Diagnosing system freezes and hangs...")
    print("=" * 60)
    
    monitor = InktraceSystemMonitor()
    debug_tools = InktraceDebugTools()
    
    # 1. Generate system report
    print("\n📊 GENERATING SYSTEM HEALTH REPORT...")
    report = monitor.generate_system_report()
    
    print(f"\\n📈 SYSTEM STATUS:")
    print(f"   Uptime: {report['uptime_seconds']:.1f} seconds")
    print(f"   Python processes: {len(report['python_processes'])}")
    print(f"   Active deadlocks: {len(report['deadlocks'])}")
    print(f"   Alerts: {len(report['alerts'])}")
    
    # 2. Check port status
    print("\\n🔌 PORT STATUS:")
    for port, status in report["port_status"].items():
        risk_emoji = {"low": "✅", "medium": "⚠️", "critical": "❌", "high": "🔥"}.get(status.get("risk"), "❓")
        print(f"   Port {port}: {risk_emoji} {status['status']}")
        if status.get("message"):
            print(f"      └─ {status['message']}")
    
    # 3. Process analysis
    print("\\n🔍 PROCESS ANALYSIS:")
    for proc in report["python_processes"]:
        status_emoji = {"healthy": "✅", "warning": "⚠️", "dead": "❌"}.get(proc["resources"].get("status"), "❓")
        print(f"   PID {proc['pid']}: {status_emoji} {proc['cmdline'][:60]}...")
        if proc["resources"].get("warnings"):
            for warning in proc["resources"]["warnings"]:
                print(f"      ⚠️ {warning}")
    
    # 4. Show recommendations
    if report["recommendations"]:
        print("\\n💡 RECOMMENDATIONS:")
        for rec in report["recommendations"]:
            print(f"   🎯 {rec}")
    
    # 5. Kill hanging processes if found
    print("\\n🧹 CLEANING UP HANGING PROCESSES...")
    killed = debug_tools.kill_hanging_processes()
    if killed:
        for msg in killed:
            print(f"   🗑️ {msg}")
    else:
        print("   ✅ No hanging processes found")
    
    # 6. Test individual services
    print("\\n🧪 TESTING INDIVIDUAL SERVICES...")
    test_results = debug_tools.test_individual_services()
    
    for service, result in test_results.items():
        status_emoji = {"success": "✅", "script_missing": "📁", "startup_failed": "❌", 
                       "process_died": "💀", "startup_timeout": "⏰"}.get(result["status"], "❓")
        print(f"   {service}: {status_emoji} {result['status']}")
        if "error" in result:
            print(f"      └─ {result['error']}")
        elif "startup_time" in result:
            print(f"      └─ Started in {result['startup_time']:.1f}s (PID {result['pid']})")
    
    # 7. Generate robust launcher
    print("\\n🛠️ GENERATING ROBUST LAUNCHER...")
    robust_launcher = debug_tools.create_robust_launcher()
    
    with open("scripts/robust_launch.py", "w") as f:
        f.write(robust_launcher)
    
    os.chmod("scripts/robust_launch.py", 0o755)
    print("   ✅ Created scripts/robust_launch.py")
    
    # 8. Save detailed report
    with open("inktrace_debug_report.json", "w") as f:
        json.dump(report, f, indent=2, default=str)
    print("   ✅ Saved detailed report to inktrace_debug_report.json")
    
    print("\\n🎯 DEBUGGING COMPLETE!")
    print("=" * 60)
    print("Next steps:")
    print("1. Use: python scripts/robust_launch.py")
    print("2. Monitor: tail -f inktrace_monitor.log")
    print("3. Review: inktrace_debug_report.json")
    print("=" * 60)


if __name__ == "__main__":
    main()