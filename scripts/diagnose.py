#!/usr/bin/env python3
"""
🐙 Inktrace Diagnostic Script
scripts/diagnose.py

Quick diagnostic tool to check Inktrace system health and identify issues.
"""

import requests
import socket
import subprocess
import sys
from pathlib import Path
import json


class InktraceDiagnostic:
    """🐙 Inktrace System Diagnostic Tool"""

    def __init__(self):
        self.services = {
            "Data Processor": {"port": 8001, "endpoint": "/.well-known/agent.json"},
            "Report Generator": {"port": 8002, "endpoint": "/.well-known/agent.json"},
            "Wiretap Tentacle": {"port": 8003, "endpoint": "/dashboard"},
            "Policy Agent": {"port": 8006, "endpoint": "/.well-known/agent.json"}
        }

    def check_port_status(self, port: int) -> str:
        """Check if a port is bound and responsive"""
        try:
            # Check if port is bound
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                result = sock.connect_ex(('localhost', port))
                if result == 0:
                    return "BOUND"
                else:
                    return "UNBOUND"
        except Exception as e:
            return f"ERROR: {str(e)}"

    def check_http_response(self, port: int, endpoint: str) -> dict:
        """Check HTTP response from a service"""
        try:
            url = f"http://localhost:{port}{endpoint}"
            response = requests.get(url, timeout=5)
            return {
                "status_code": response.status_code,
                "response_time": response.elapsed.total_seconds(),
                "content_length": len(response.content),
                "success": response.status_code == 200
            }
        except requests.exceptions.ConnectionError:
            return {"error": "Connection refused"}
        except requests.exceptions.Timeout:
            return {"error": "Timeout"}
        except Exception as e:
            return {"error": str(e)}

    def check_processes(self) -> dict:
        """Check for running Inktrace processes"""
        try:
            # Use ps to find python processes
            result = subprocess.run([
                "ps", "aux"
            ], capture_output=True, text=True)
            
            lines = result.stdout.split('\n')
            inktrace_processes = []
            
            for line in lines:
                if 'python' in line and any(script in line for script in [
                    'data_processor.py', 'report_generator.py', 
                    'wiretap.py', 'policy_agent.py', 'launch.py'
                ]):
                    inktrace_processes.append(line.strip())
            
            return {"processes": inktrace_processes, "count": len(inktrace_processes)}
        except Exception as e:
            return {"error": str(e)}

    def check_dependencies(self) -> dict:
        """Check if required dependencies are installed"""
        dependencies = ['a2a', 'fastapi', 'uvicorn', 'httpx', 'requests']
        results = {}
        
        for dep in dependencies:
            try:
                __import__(dep)
                results[dep] = "✅ INSTALLED"
            except ImportError:
                results[dep] = "❌ MISSING"
        
        return results

    def check_file_structure(self) -> dict:
        """Check if required files exist"""
        required_files = {
            "agents/data_processor.py": Path("agents/data_processor.py"),
            "agents/report_generator.py": Path("agents/report_generator.py"),
            "agents/policy_agent.py": Path("agents/policy_agent.py"),
            "tentacles/wiretap.py": Path("tentacles/wiretap.py"),
            "scripts/launch.py": Path("scripts/launch.py"),
            "templates/": Path("templates"),
            "static/": Path("static")
        }
        
        results = {}
        for name, path in required_files.items():
            results[name] = "✅ EXISTS" if path.exists() else "❌ MISSING"
        
        return results

    def check_wiretap_dependencies(self) -> dict:
        """Check wiretap-specific dependencies and template files"""
        wiretap_deps = {
            "jinja2": "Template engine",
            "aiohttp": "Async HTTP client", 
            "websockets": "WebSocket support"
        }
        
        results = {}
        for dep, description in wiretap_deps.items():
            try:
                __import__(dep)
                results[dep] = f"✅ INSTALLED ({description})"
            except ImportError:
                results[dep] = f"❌ MISSING ({description})"
        
        return results

    def check_template_files(self) -> dict:
        """Check specific template files that wiretap needs"""
        template_files = {
            "templates/dashboard.html": Path("templates/dashboard.html"),
            "static/css/dashboard.css": Path("static/css/dashboard.css"),
            "static/js/dashboard.js": Path("static/js/dashboard.js"),
            "demo/": Path("demo")
        }
        
        results = {}
        for name, path in template_files.items():
            if path.exists():
                if path.is_file():
                    size = path.stat().st_size
                    results[name] = f"✅ EXISTS ({size} bytes)"
                else:
                    results[name] = "✅ EXISTS (directory)"
            else:
                results[name] = "❌ MISSING"
        
        return results

    def test_wiretap_startup(self) -> dict:
        """Test wiretap tentacle startup manually"""
        print("🧪 TESTING WIRETAP STARTUP...")
        
        try:
            # Try to import wiretap tentacle
            sys.path.insert(0, str(Path.cwd()))
            
            # Test the import
            try:
                from tentacles.wiretap import WiretapTentacle
                print("   ✅ Wiretap module imports successfully")
                
                # Try to create instance
                try:
                    tentacle = WiretapTentacle(port=8003)
                    print("   ✅ WiretapTentacle instance created successfully")
                    
                    # Check if FastAPI app was created
                    if hasattr(tentacle, 'app'):
                        print("   ✅ FastAPI app created successfully")
                        return {"status": "✅ SUCCESS", "details": "Wiretap can be instantiated"}
                    else:
                        return {"status": "❌ FAILED", "details": "FastAPI app not created"}
                        
                except Exception as e:
                    print(f"   ❌ Error creating WiretapTentacle: {e}")
                    return {"status": "❌ FAILED", "details": f"Instantiation error: {str(e)}"}
                    
            except Exception as e:
                print(f"   ❌ Error importing wiretap: {e}")
                return {"status": "❌ FAILED", "details": f"Import error: {str(e)}"}
                
        except Exception as e:
            return {"status": "❌ FAILED", "details": f"General error: {str(e)}"}

    def test_manual_wiretap_start(self) -> dict:
        """Try to start wiretap manually and capture output"""
        print("🚀 ATTEMPTING MANUAL WIRETAP START...")
        
        try:
            import subprocess
            import time
            
            # Try to start wiretap in a subprocess
            process = subprocess.Popen([
                sys.executable, "tentacles/wiretap.py", 
                "--host", "0.0.0.0", "--port", "8003"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait a bit for startup
            time.sleep(3)
            
            if process.poll() is None:
                # Process is still running
                process.terminate()
                process.wait()
                return {"status": "✅ SUCCESS", "details": "Wiretap started successfully (killed after test)"}
            else:
                # Process died
                stdout, stderr = process.communicate()
                return {
                    "status": "❌ FAILED", 
                    "details": f"Process died immediately",
                    "stdout": stdout[-500:] if stdout else "No stdout",
                    "stderr": stderr[-500:] if stderr else "No stderr"
                }
                
        except Exception as e:
            return {"status": "❌ FAILED", "details": f"Manual start error: {str(e)}"}

    def check_launch_script_behavior(self) -> dict:
        """Check what the launch script is doing with wiretap"""
        print("📋 ANALYZING LAUNCH SCRIPT BEHAVIOR...")
        
        try:
            # Read the launch script to see how it starts wiretap
            launch_script = Path("scripts/launch.py")
            if not launch_script.exists():
                return {"status": "❌ FAILED", "details": "Launch script not found"}
            
            with open(launch_script, 'r') as f:
                content = f.read()
            
            # Look for wiretap-related code
            wiretap_lines = []
            for i, line in enumerate(content.split('\n'), 1):
                if 'wiretap' in line.lower():
                    wiretap_lines.append(f"Line {i}: {line.strip()}")
            
            if wiretap_lines:
                return {
                    "status": "✅ FOUND", 
                    "details": f"Found {len(wiretap_lines)} wiretap references",
                    "lines": wiretap_lines[:10]  # First 10 lines
                }
            else:
                return {"status": "⚠️ WARNING", "details": "No wiretap references found in launch script"}
                
        except Exception as e:
            return {"status": "❌ FAILED", "details": f"Error reading launch script: {str(e)}"}

    def test_wiretap_with_launcher(self) -> dict:
        """Test if launcher can start wiretap"""
        print("🎯 TESTING WIRETAP VIA LAUNCHER...")
        
        try:
            import subprocess
            import time
            
            # Try to run the launcher and see what happens
            process = subprocess.Popen([
                sys.executable, "scripts/launch.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Wait longer for the full launch process
            time.sleep(8)
            
            # Check if wiretap port becomes bound
            wiretap_bound = self.check_port_status(8003) == "BOUND"
            
            # Kill the process
            process.terminate()
            stdout, stderr = process.communicate(timeout=5)
            
            return {
                "status": "✅ SUCCESS" if wiretap_bound else "❌ FAILED",
                "details": f"Wiretap port bound: {wiretap_bound}",
                "launcher_stdout": stdout[-1000:] if stdout else "No stdout",
                "launcher_stderr": stderr[-1000:] if stderr else "No stderr"
            }
            
        except Exception as e:
            return {"status": "❌ FAILED", "details": f"Launcher test error: {str(e)}"}

    def check_current_processes(self) -> dict:
        """Check what processes are currently running (Docker-friendly)"""
        try:
            # Use a Docker-friendly approach to check processes
            import os
            import glob
            
            # Check /proc for python processes
            python_procs = []
            try:
                for pid_dir in glob.glob('/proc/[0-9]*'):
                    try:
                        pid = os.path.basename(pid_dir)
                        cmdline_path = f"{pid_dir}/cmdline"
                        if os.path.exists(cmdline_path):
                            with open(cmdline_path, 'rb') as f:
                                cmdline = f.read().decode('utf-8', errors='ignore')
                                if 'python' in cmdline and any(script in cmdline for script in [
                                    'data_processor', 'report_generator', 'wiretap', 'policy_agent', 'launch'
                                ]):
                                    python_procs.append(f"PID {pid}: {cmdline.replace(chr(0), ' ')}")
                    except:
                        continue
            except:
                pass
            
            return {"processes": python_procs, "count": len(python_procs)}
            
        except Exception as e:
            return {"error": f"Process check failed: {str(e)}"}

    def diagnose_port_binding_issue(self) -> dict:
        """Diagnose why wiretap port isn't binding"""
        print("🔍 DIAGNOSING PORT BINDING ISSUE...")
        
        issues = []
        
        # Check if any process is holding port 8003
        try:
            import socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                sock.bind(('0.0.0.0', 8003))
                sock.close()
                issues.append("✅ Port 8003 is available for binding")
            except OSError as e:
                issues.append(f"❌ Port 8003 binding failed: {e}")
        except Exception as e:
            issues.append(f"❌ Socket test failed: {e}")
        
        # Check if wiretap process starts but dies quickly
        try:
            import subprocess
            import time
            
            process = subprocess.Popen([
                sys.executable, "tentacles/wiretap.py", 
                "--host", "0.0.0.0", "--port", "8003"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Check every 0.5 seconds for 3 seconds
            for i in range(6):
                time.sleep(0.5)
                if process.poll() is not None:
                    stdout, stderr = process.communicate()
                    issues.append(f"❌ Wiretap process died after {(i+1)*0.5}s")
                    if stderr:
                        issues.append(f"   Error: {stderr[-200:]}")
                    break
                
                # Check if port is bound
                port_status = self.check_port_status(8003)
                if port_status == "BOUND":
                    issues.append(f"✅ Wiretap bound to port after {(i+1)*0.5}s")
                    process.terminate()
                    process.wait()
                    break
            else:
                # Still running after 3 seconds
                if process.poll() is None:
                    issues.append("✅ Wiretap process still running after 3s")
                    process.terminate()
                    process.wait()
                
        except Exception as e:
            issues.append(f"❌ Port binding test failed: {e}")
        
        return {"issues": issues}

    def check_uvicorn_compatibility(self) -> dict:
        """Check if uvicorn can be imported and used"""
        try:
            import uvicorn
            print("   ✅ Uvicorn imports successfully")
            
            # Check uvicorn version
            version = getattr(uvicorn, '__version__', 'Unknown')
            print(f"   ✅ Uvicorn version: {version}")
            
            return {"status": "✅ SUCCESS", "version": version}
        except Exception as e:
            return {"status": "❌ FAILED", "error": str(e)}

    def run_full_diagnostic(self):
        """Run complete diagnostic suite"""
        print("🐙 INKTRACE SYSTEM DIAGNOSTIC")
        print("=" * 60)
        
        # 1. Check dependencies
        print("\n📦 DEPENDENCY CHECK:")
        deps = self.check_dependencies()
        for dep, status in deps.items():
            print(f"   {dep}: {status}")
        
        # 2. Check wiretap-specific dependencies
        print("\n🐙 WIRETAP DEPENDENCIES:")
        wiretap_deps = self.check_wiretap_dependencies()
        for dep, status in wiretap_deps.items():
            print(f"   {dep}: {status}")
        
        # 3. Check file structure
        print("\n📁 FILE STRUCTURE CHECK:")
        files = self.check_file_structure()
        for file, status in files.items():
            print(f"   {file}: {status}")
        
        # 4. Check template files specifically
        print("\n📋 TEMPLATE FILES CHECK:")
        templates = self.check_template_files()
        for file, status in templates.items():
            print(f"   {file}: {status}")
        
        # 5. Check uvicorn compatibility
        print("\n🌐 UVICORN CHECK:")
        uvicorn_status = self.check_uvicorn_compatibility()
        print(f"   Status: {uvicorn_status['status']}")
        if 'version' in uvicorn_status:
            print(f"   Version: {uvicorn_status['version']}")
        if 'error' in uvicorn_status:
            print(f"   Error: {uvicorn_status['error']}")
        
        # 6. Test wiretap startup capability
        print("\n🧪 WIRETAP STARTUP TEST:")
        startup_test = self.test_wiretap_startup()
        print(f"   {startup_test['status']}: {startup_test['details']}")
        
        # 7. Manual wiretap start test
        print("\n🚀 MANUAL WIRETAP START TEST:")
        manual_test = self.test_manual_wiretap_start()
        print(f"   {manual_test['status']}: {manual_test['details']}")
        if 'stdout' in manual_test:
            print(f"   STDOUT: {manual_test['stdout']}")
        if 'stderr' in manual_test:
            print(f"   STDERR: {manual_test['stderr']}")
        
        # 8. Check launch script behavior
        print("\n📋 LAUNCH SCRIPT ANALYSIS:")
        launch_analysis = self.check_launch_script_behavior()
        print(f"   {launch_analysis['status']}: {launch_analysis['details']}")
        if 'lines' in launch_analysis:
            for line in launch_analysis['lines'][:5]:  # Show first 5 lines
                print(f"   {line}")
        
        # 9. Test wiretap with launcher
        print("\n🎯 LAUNCHER TEST:")
        launcher_test = self.test_wiretap_with_launcher()
        print(f"   {launcher_test['status']}: {launcher_test['details']}")
        if 'launcher_stdout' in launcher_test and launcher_test['launcher_stdout']:
            print(f"   LAUNCHER OUTPUT: {launcher_test['launcher_stdout'][-300:]}")
        if 'launcher_stderr' in launcher_test and launcher_test['launcher_stderr']:
            print(f"   LAUNCHER ERROR: {launcher_test['launcher_stderr'][-300:]}")
        
        # 10. Port binding diagnosis
        print("\n🔍 PORT BINDING DIAGNOSIS:")
        port_diag = self.diagnose_port_binding_issue()
        for issue in port_diag['issues']:
            print(f"   {issue}")
        
        # 11. Check current processes (Docker-friendly)
        print("\n🔄 CURRENT PROCESSES:")
        processes = self.check_current_processes()
        if "processes" in processes:
            print(f"   Found {processes['count']} Python processes:")
            for proc in processes["processes"][:5]:  # Show first 5
                print(f"   🔸 {proc}")
        else:
            print(f"   ❌ Error checking processes: {processes.get('error', 'Unknown')}")
        
        # 12. Check service ports
        print("\n🔌 PORT STATUS CHECK:")
        for service, config in self.services.items():
            port_status = self.check_port_status(config["port"])
            print(f"   {service} (:{config['port']}): {port_status}")
        
        # 13. Check HTTP responses
        print("\n🌐 HTTP RESPONSE CHECK:")
        for service, config in self.services.items():
            http_status = self.check_http_response(config["port"], config["endpoint"])
            if "error" in http_status:
                print(f"   {service}: ❌ {http_status['error']}")
            else:
                status = "✅" if http_status["success"] else "❌"
                print(f"   {service}: {status} HTTP {http_status['status_code']} ({http_status['response_time']:.2f}s)")
        
        # 14. Quick A2A discovery test
        print("\n🔍 A2A DISCOVERY TEST:")
        for service, config in self.services.items():
            if config["endpoint"] == "/.well-known/agent.json":
                try:
                    url = f"http://localhost:{config['port']}/.well-known/agent.json"
                    response = requests.get(url, timeout=3)
                    if response.status_code == 200:
                        agent_data = response.json()
                        print(f"   {service}: ✅ {agent_data.get('name', 'Unknown Agent')}")
                        print(f"      Version: {agent_data.get('version', 'Unknown')}")
                        print(f"      Skills: {len(agent_data.get('skills', []))}")
                    else:
                        print(f"   {service}: ❌ HTTP {response.status_code}")
                except Exception as e:
                    print(f"   {service}: ❌ {str(e)}")
        
        print("\n🏁 DIAGNOSTIC COMPLETE")
        print("=" * 60)

    def quick_fix_suggestions(self):
        """Provide quick fix suggestions based on diagnostics"""
        print("\n🔧 QUICK FIX SUGGESTIONS:")
        print("=" * 60)
        
        # Check if any ports are bound but not responding
        bound_but_not_responding = []
        for service, config in self.services.items():
            port_status = self.check_port_status(config["port"])
            if port_status == "BOUND":
                http_status = self.check_http_response(config["port"], config["endpoint"])
                if "error" in http_status:
                    bound_but_not_responding.append(service)
        
        if bound_but_not_responding:
            print("📋 Ports bound but not responding properly:")
            for service in bound_but_not_responding:
                print(f"   • {service}: Try restarting this service")
            print("   💡 Fix: Stop all processes and restart with launch.py")
        
        # Check for missing dependencies
        deps = self.check_dependencies()
        missing_deps = [dep for dep, status in deps.items() if "MISSING" in status]
        if missing_deps:
            print("📋 Missing dependencies:")
            for dep in missing_deps:
                print(f"   • {dep}")
            print("   💡 Fix: pip install -r requirements.txt")
        
        # Check for missing files
        files = self.check_file_structure()
        missing_files = [file for file, status in files.items() if "MISSING" in status]
        if missing_files:
            print("📋 Missing files:")
            for file in missing_files:
                print(f"   • {file}")
            print("   💡 Fix: Ensure all agent and tentacle scripts are present")


def main():
    """Run diagnostic tool"""
    diagnostic = InktraceDiagnostic()
    diagnostic.run_full_diagnostic()
    diagnostic.quick_fix_suggestions()


if __name__ == "__main__":
    main()