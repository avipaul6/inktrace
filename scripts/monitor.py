#!/usr/bin/env python3
"""
🐙 Real-time Inktrace System Monitor
scripts/monitor.py

Watch your Inktrace system in real-time to catch hangs as they happen
"""

import time
import os
import sys
import psutil
import socket
import requests
from datetime import datetime
from pathlib import Path


class InktraceMonitor:
    """Real-time monitoring for Inktrace system"""
    
    def __init__(self):
        self.services = {
            "Data Processor": 8001,
            "Report Generator": 8002,
            "Wiretap": 8003,
            "Policy Agent": 8006
        }
        self.last_check = {}
        self.alert_threshold = 5  # seconds
        
    def clear_screen(self):
        """Clear terminal screen"""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_process_info(self):
        """Get info about Inktrace processes"""
        processes = []
        
        for proc in psutil.process_iter(['pid', 'name', 'cmdline', 'status', 'cpu_percent', 'memory_info', 'create_time']):
            try:
                if proc.info['name'] in ['python', 'python3']:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if any(script in cmdline for script in ['data_processor', 'report_generator', 'wiretap', 'policy_agent', 'launch']):
                        
                        # Extract service name
                        service_name = "Unknown"
                        if 'data_processor' in cmdline:
                            service_name = "Data Processor"
                        elif 'report_generator' in cmdline:
                            service_name = "Report Generator"
                        elif 'wiretap' in cmdline:
                            service_name = "Wiretap"
                        elif 'policy_agent' in cmdline:
                            service_name = "Policy Agent"
                        elif 'launch' in cmdline:
                            service_name = "Launcher"
                        
                        processes.append({
                            'pid': proc.info['pid'],
                            'name': service_name,
                            'status': proc.info['status'],
                            'cpu_percent': proc.info['cpu_percent'],
                            'memory_mb': proc.info['memory_info'].rss / 1024 / 1024,
                            'age_minutes': (time.time() - proc.info['create_time']) / 60,
                            'cmdline': cmdline[:60] + "..." if len(cmdline) > 60 else cmdline
                        })
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        return processes
    
    def check_port_status(self, port):
        """Check if a port is responsive"""
        start_time = time.time()
        
        try:
            # Socket connection test
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(3)
            result = sock.connect_ex(('localhost', port))
            sock.close()
            
            if result == 0:
                # Try HTTP request
                try:
                    response = requests.get(f"http://localhost:{port}/", timeout=3)
                    response_time = time.time() - start_time
                    return {
                        'status': 'responsive',
                        'response_time': response_time,
                        'http_code': response.status_code
                    }
                except requests.exceptions.Timeout:
                    return {
                        'status': 'hanging',
                        'response_time': time.time() - start_time,
                        'error': 'HTTP timeout'
                    }
                except Exception as e:
                    return {
                        'status': 'bound_no_http',
                        'response_time': time.time() - start_time,
                        'error': str(e)[:50]
                    }
            else:
                return {
                    'status': 'unbound',
                    'response_time': 0,
                    'error': 'Port not bound'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'response_time': 0,
                'error': str(e)[:50]
            }
    
    def get_system_stats(self):
        """Get system resource statistics"""
        cpu_percent = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        load_avg = "N/A"
        if hasattr(os, 'getloadavg'):
            load_avg = f"{os.getloadavg()[0]:.2f}"
        
        return {
            'cpu_percent': cpu_percent,
            'memory_percent': memory.percent,
            'memory_used_gb': memory.used / 1024 / 1024 / 1024,
            'memory_total_gb': memory.total / 1024 / 1024 / 1024,
            'disk_percent': disk.percent,
            'load_average': load_avg
        }
    
    def detect_hangs(self, port_statuses):
        """Detect hanging services"""
        hangs = []
        current_time = time.time()
        
        for service, port in self.services.items():
            status = port_statuses.get(port, {})
            
            if status.get('status') == 'hanging':
                hangs.append(f"{service} (port {port}) - HTTP timeout")
            elif status.get('response_time', 0) > self.alert_threshold:
                hangs.append(f"{service} (port {port}) - Slow response ({status.get('response_time', 0):.1f}s)")
            
            # Track response times
            if port in self.last_check:
                time_since_last = current_time - self.last_check[port]
                if time_since_last > 30 and status.get('status') == 'unbound':
                    hangs.append(f"{service} (port {port}) - Service died")
            
            self.last_check[port] = current_time
        
        return hangs
    
    def format_status_indicator(self, status_info):
        """Format status with color indicators"""
        status = status_info.get('status', 'unknown')
        
        indicators = {
            'responsive': '🟢',
            'hanging': '🔴',
            'bound_no_http': '🟡',
            'unbound': '⚫',
            'error': '❌'
        }
        
        return indicators.get(status, '❓')
    
    def display_dashboard(self):
        """Display the monitoring dashboard"""
        self.clear_screen()
        
        print("🐙 INKTRACE REAL-TIME MONITOR")
        print("=" * 80)
        print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Press Ctrl+C to stop")
        print("=" * 80)
        
        # System stats
        stats = self.get_system_stats()
        print(f"💻 SYSTEM: CPU {stats['cpu_percent']:.1f}% | "
              f"RAM {stats['memory_percent']:.1f}% ({stats['memory_used_gb']:.1f}GB/"
              f"{stats['memory_total_gb']:.1f}GB) | "
              f"Load {stats['load_average']}")
        
        # Service status
        print("\\n🔌 SERVICE STATUS:")
        port_statuses = {}
        for service, port in self.services.items():
            status_info = self.check_port_status(port)
            port_statuses[port] = status_info
            
            indicator = self.format_status_indicator(status_info)
            status_text = status_info.get('status', 'unknown')
            response_time = status_info.get('response_time', 0)
            
            print(f"   {indicator} {service:<16} (:{port}) | "
                  f"{status_text:<12} | "
                  f"{response_time:.2f}s")
            
            if status_info.get('error'):
                print(f"      └─ {status_info['error']}")
        
        # Process information
        print("\\n🔄 PROCESSES:")
        processes = self.get_process_info()
        
        if not processes:
            print("   ❌ No Inktrace processes running")
        else:
            print(f"   {'PID':<8} {'Service':<16} {'Status':<12} {'CPU%':<6} {'RAM(MB)':<8} {'Age(min)':<8}")
            print("   " + "-" * 70)
            
            for proc in processes:
                status_emoji = {
                    'running': '🟢',
                    'sleeping': '🟡',
                    'disk-sleep': '🔴',
                    'zombie': '💀'
                }.get(proc['status'], '❓')
                
                print(f"   {proc['pid']:<8} {proc['name']:<16} "
                      f"{status_emoji}{proc['status']:<11} "
                      f"{proc['cpu_percent']:<6.1f} "
                      f"{proc['memory_mb']:<8.1f} "
                      f"{proc['age_minutes']:<8.1f}")
        
        # Hang detection
        hangs = self.detect_hangs(port_statuses)
        if hangs:
            print("\\n🚨 ALERTS:")
            for hang in hangs:
                print(f"   ⚠️ {hang}")
        
        # Instructions
        print("\\n💡 TIPS:")
        print("   🟢 Responsive | 🟡 Issues | 🔴 Hanging | ⚫ Dead | ❌ Error")
        print("   Watch for: High CPU, growing memory, hanging status, long response times")
        
        # Auto-refresh countdown
        print("\\n🔄 Refreshing in: ", end="", flush=True)
        for i in range(5, 0, -1):
            print(f"{i}... ", end="", flush=True)
            time.sleep(1)
        print("refreshing!")
    
    def run(self):
        """Run the monitoring loop"""
        try:
            while True:
                self.display_dashboard()
        except KeyboardInterrupt:
            print("\\n\\n🛑 Monitoring stopped")
            sys.exit(0)


def main():
    """Main entry point"""
    print("🐙 Starting Inktrace Real-time Monitor...")
    print("This will refresh every 5 seconds to show system status")
    print("Press Ctrl+C to stop")
    print()
    
    time.sleep(2)
    
    monitor = InktraceMonitor()
    monitor.run()


if __name__ == "__main__":
    main()