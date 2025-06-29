#!/usr/bin/env python3
"""
🐙 Quick Inktrace Diagnostic - Run This First
scripts/quick_diagnose.py

Quickly identify why your Inktrace system is hanging/freezing
"""

import subprocess
import time
import os
import sys
import socket
import psutil
import signal
from pathlib import Path


def check_hanging_processes():
    """Find processes that might be causing hangs"""
    print("🔍 Checking for hanging processes...")
    
    hanging_processes = []
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'create_time']):
        try:
            # Look for Python processes related to Inktrace
            if proc.info['name'] in ['python', 'python3']:
                cmdline = ' '.join(proc.info['cmdline'])
                if any(script in cmdline for script in ['data_processor', 'report_generator', 'wiretap', 'policy_agent', 'launch']):
                    
                    # Check if process is in problematic state
                    status = proc.info['status']
                    age = time.time() - proc.info['create_time']
                    
                    problem = None
                    if status == psutil.STATUS_DISK_SLEEP:
                        problem = "DISK_SLEEP (deadlocked waiting for I/O)"
                    elif status == psutil.STATUS_ZOMBIE:
                        problem = "ZOMBIE (process died but not cleaned up)"
                    elif age > 300 and status == psutil.STATUS_SLEEPING:
                        problem = f"LONG_SLEEP (sleeping for {age/60:.1f} minutes)"
                    
                    if problem:
                        hanging_processes.append({
                            "pid": proc.info['pid'],
                            "problem": problem,
                            "cmdline": cmdline[:80],
                            "age_minutes": age / 60
                        })
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if hanging_processes:
        print("❌ HANGING PROCESSES DETECTED:")
        for proc in hanging_processes:
            print(f"   PID {proc['pid']}: {proc['problem']}")
            print(f"      Command: {proc['cmdline']}")
            print(f"      Age: {proc['age_minutes']:.1f} minutes")
        return hanging_processes
    else:
        print("✅ No hanging processes detected")
        return []


def check_pipe_overflow():
    """Check if subprocess pipes are causing hangs"""
    print("\\n🔍 Checking for subprocess pipe overflow...")
    
    # Look at the current launch.py to see how it handles subprocess pipes
    launch_script = Path("scripts/launch.py")
    if not launch_script.exists():
        print("❌ launch.py not found")
        return False
    
    with open(launch_script, 'r') as f:
        content = f.read()
    
    # Check for problematic subprocess patterns
    pipe_issues = []
    
    if "stdout=subprocess.PIPE" in content:
        pipe_issues.append("❌ CRITICAL: Using subprocess.PIPE for stdout - THIS CAUSES HANGS!")
    
    if "stderr=subprocess.PIPE" in content:
        pipe_issues.append("❌ CRITICAL: Using subprocess.PIPE for stderr - THIS CAUSES HANGS!")
    
    if "stdout=subprocess.STDOUT" in content:
        pipe_issues.append("⚠️ WARNING: Redirecting stdout to stderr - can cause pipe overflow")
    
    if ".communicate()" not in content and "subprocess.PIPE" in content:
        pipe_issues.append("❌ CRITICAL: Using PIPE without .communicate() - GUARANTEED HANG!")
    
    if pipe_issues:
        print("❌ PIPE OVERFLOW ISSUES DETECTED:")
        for issue in pipe_issues:
            print(f"   {issue}")
        print("\\n   💡 SOLUTION: Use subprocess.DEVNULL instead of subprocess.PIPE")
        return True
    else:
        print("✅ No obvious pipe overflow issues")
        return False


def check_port_conflicts():
    """Check for port conflicts that could cause hangs"""
    print("\\n🔍 Checking for port conflicts...")
    
    inktrace_ports = [8001, 8002, 8003, 8006]
    conflicts = []
    
    for port in inktrace_ports:
        try:
            # Try to bind to the port
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sock.settimeout(2)
            
            try:
                sock.bind(('localhost', port))
                sock.close()
                print(f"   Port {port}: ✅ Available")
            except OSError as e:
                conflicts.append(f"Port {port}: ❌ In use - {e}")
                sock.close()
                
        except Exception as e:
            conflicts.append(f"Port {port}: ❓ Error checking - {e}")
    
    if conflicts:
        print("❌ PORT CONFLICTS DETECTED:")
        for conflict in conflicts:
            print(f"   {conflict}")
        return True
    else:
        print("✅ No port conflicts")
        return False


def check_resource_limits():
    """Check system resource limits that could cause hangs"""
    print("\\n🔍 Checking system resource limits...")
    
    issues = []
    
    try:
        # Check file descriptor limit
        import resource
        soft_limit, hard_limit = resource.getrlimit(resource.RLIMIT_NOFILE)
        if soft_limit < 1024:
            issues.append(f"❌ Low file descriptor limit: {soft_limit} (should be >= 1024)")
        else:
            print(f"   File descriptors: ✅ {soft_limit}/{hard_limit}")
        
        # Check memory usage
        memory = psutil.virtual_memory()
        if memory.percent > 90:
            issues.append(f"❌ High memory usage: {memory.percent}% (may cause swapping/hangs)")
        else:
            print(f"   Memory usage: ✅ {memory.percent}%")
        
        # Check load average
        if hasattr(os, 'getloadavg'):
            load = os.getloadavg()[0]
            cpu_count = os.cpu_count()
            if load > cpu_count * 2:
                issues.append(f"❌ High system load: {load:.2f} (CPU count: {cpu_count})")
            else:
                print(f"   System load: ✅ {load:.2f}")
        
    except Exception as e:
        issues.append(f"❓ Error checking resources: {e}")
    
    if issues:
        print("❌ RESOURCE ISSUES DETECTED:")
        for issue in issues:
            print(f"   {issue}")
        return True
    else:
        print("✅ Resource limits OK")
        return False


def test_minimal_service():
    """Test if we can start a minimal service without hanging"""
    print("\\n🧪 Testing minimal service startup...")
    
    # Create a minimal test service
    test_script = '''#!/usr/bin/env python3
import time
import sys
import signal
from http.server import HTTPServer, BaseHTTPRequestHandler

class TestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()
        self.wfile.write(b'Test service OK')
    
    def log_message(self, format, *args):
        pass  # Suppress logging

def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)

if __name__ == "__main__":
    try:
        server = HTTPServer(('localhost', 9999), TestHandler)
        print("Test service ready")
        server.serve_forever()
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
'''
    
    # Write test script
    test_file = Path("test_service.py")
    test_file.write_text(test_script)
    
    try:
        # Start test service with proper subprocess handling
        print("   Starting test service...")
        process = subprocess.Popen([
            sys.executable, str(test_file)
        ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # Wait for startup
        time.sleep(3)
        
        # Test if it responds
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex(('localhost', 9999))
            sock.close()
            
            if result == 0:
                print("   ✅ Test service started successfully")
                success = True
            else:
                print("   ❌ Test service failed to bind")
                success = False
        except Exception as e:
            print(f"   ❌ Test service connection failed: {e}")
            success = False
        
        # Cleanup
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        
        test_file.unlink()  # Remove test file
        
        return success
        
    except Exception as e:
        print(f"   ❌ Test service startup failed: {e}")
        if test_file.exists():
            test_file.unlink()
        return False


def kill_all_inktrace_processes():
    """Kill all Inktrace processes to start fresh"""
    print("\\n🧹 Killing all Inktrace processes...")
    
    killed_count = 0
    
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            if proc.info['name'] in ['python', 'python3']:
                cmdline = ' '.join(proc.info['cmdline'])
                if any(script in cmdline for script in ['data_processor', 'report_generator', 'wiretap', 'policy_agent', 'launch']):
                    print(f"   Killing PID {proc.info['pid']}: {cmdline[:60]}...")
                    proc.kill()
                    killed_count += 1
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    
    if killed_count > 0:
        print(f"   ✅ Killed {killed_count} processes")
        time.sleep(2)  # Wait for cleanup
    else:
        print("   ✅ No Inktrace processes running")
    
    return killed_count


def create_fixed_launcher():
    """Create a fixed launcher that won't hang"""
    print("\\n🛠️ Creating fixed launcher...")
    
    fixed_launcher = '''#!/usr/bin/env python3
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
        print("\\n🛑 Shutting down...")
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
        
        print(f"\\n📊 Started {success_count}/{len(self.services)} services")
        
        if success_count == 0:
            print("❌ No services started")
            return False
        
        print("\\n🎯 INKTRACE READY!")
        print("=" * 50)
        print("🌐 Wiretap Dashboard: http://localhost:8003/dashboard")
        print("🔍 Communications: http://localhost:8003/communications")
        print("=" * 50)
        print("\\n🔄 Running... Press Ctrl+C to stop")
        
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
'''
    
    # Write the fixed launcher
    fixed_file = Path("scripts/launch_fixed.py")
    fixed_file.write_text(fixed_launcher)
    os.chmod(fixed_file, 0o755)
    
    print(f"   ✅ Created {fixed_file}")
    return str(fixed_file)


def main():
    """Main diagnostic function"""
    print("🐙 INKTRACE QUICK DIAGNOSTIC")
    print("=" * 60)
    print("Identifying why your system is hanging/freezing...")
    print("=" * 60)
    
    issues_found = []
    
    # 1. Check for hanging processes
    hanging_procs = check_hanging_processes()
    if hanging_procs:
        issues_found.append("hanging_processes")
    
    # 2. Check pipe overflow issues
    if check_pipe_overflow():
        issues_found.append("pipe_overflow")
    
    # 3. Check port conflicts
    if check_port_conflicts():
        issues_found.append("port_conflicts")
    
    # 4. Check resource limits
    if check_resource_limits():
        issues_found.append("resource_limits")
    
    # 5. Test minimal service
    if not test_minimal_service():
        issues_found.append("subprocess_issues")
    
    print("\\n" + "=" * 60)
    print("🎯 DIAGNOSTIC RESULTS")
    print("=" * 60)
    
    if not issues_found:
        print("✅ No obvious issues detected!")
        print("\\nYour system should work. Try running:")
        print("   python scripts/launch.py")
    else:
        print("❌ ISSUES DETECTED:")
        for issue in issues_found:
            print(f"   🔸 {issue}")
        
        print("\\n💡 RECOMMENDED ACTIONS:")
        
        if "hanging_processes" in issues_found:
            print("   1. Kill hanging processes:")
            kill_count = kill_all_inktrace_processes()
        
        if "pipe_overflow" in issues_found:
            print("   2. Use the fixed launcher (creating now...):")
            fixed_launcher = create_fixed_launcher()
            print(f"      python {fixed_launcher}")
        
        if "port_conflicts" in issues_found:
            print("   3. Check what's using your ports:")
            print("      lsof -i :8001 :8002 :8003 :8006")
        
        if "resource_limits" in issues_found:
            print("   4. Free up system resources or restart your machine")
        
        if "subprocess_issues" in issues_found:
            print("   5. Check your Python environment - may need to reinstall dependencies")
    
    print("\\n" + "=" * 60)
    print("🚀 NEXT STEPS:")
    print("1. Run this diagnostic again after fixes")
    print("2. Use: python scripts/launch_fixed.py (if created)")
    print("3. Monitor: ps aux | grep python")
    print("=" * 60)


if __name__ == "__main__":
    main()