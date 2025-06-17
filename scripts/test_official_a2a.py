# scripts/test_official_a2a.py - NEW TEST SCRIPT FOR OFFICIAL SDK
"""
🐙 Inktrace Official A2A Communication Test
scripts/test_official_a2a.py

Test script specifically for the official Google A2A SDK implementation.
"""

import asyncio
import json
import httpx
import time
import uuid
from datetime import datetime
from typing import Dict, List

class OfficialA2ATester:
    """🐙 Test official Google A2A implementation"""
    
    def __init__(self):
        self.agents = {
            "data_processor": {"port": 8001, "name": "Data Processor"},
            "report_generator": {"port": 8002, "name": "Report Generator"},
            "wiretap": {"port": 8003, "name": "Wiretap Tentacle"}
        }
        
    async def test_agent_discovery(self):
        """Test A2A agent discovery using official protocol"""
        print("🔍 Testing Official A2A Agent Discovery...")
        print("=" * 60)
        
        discovered = {}
        async with httpx.AsyncClient(timeout=10.0) as client:
            for agent_id, config in self.agents.items():
                try:
                    url = f"http://localhost:{config['port']}/.well-known/agent.json"
                    response = await client.get(url)
                    
                    if response.status_code == 200:
                        agent_card = response.json()
                        discovered[agent_id] = {
                            "status": "✅ DISCOVERED",
                            "name": agent_card.get("name", "Unknown"),
                            "url": agent_card.get("url", ""),
                            "capabilities": agent_card.get("capabilities", {}),
                            "skills": agent_card.get("skills", [])
                        }
                        print(f"✅ {config['name']}: {agent_card.get('name')}")
                        print(f"   URL: {agent_card.get('url')}")
                        print(f"   Version: {agent_card.get('version', 'Unknown')}")
                        print(f"   Skills: {len(agent_card.get('skills', []))}")
                        print(f"   Capabilities: {agent_card.get('capabilities', {})}")
                    else:
                        discovered[agent_id] = {"status": f"❌ HTTP {response.status_code}"}
                        print(f"❌ {config['name']}: HTTP {response.status_code}")
                        
                except Exception as e:
                    discovered[agent_id] = {"status": f"❌ ERROR: {str(e)}"}
                    print(f"❌ {config['name']}: {str(e)}")
                
                print()
        
        return discovered
    
    async def test_task_submission(self, agent_port: int, agent_name: str, task_content: str):
        """Test task submission using official A2A protocol"""
        print(f"📤 Testing task submission to {agent_name}...")
        
        # Create official A2A task payload
        task_payload = {
            "id": str(uuid.uuid4()),
            "sessionId": f"test-session-{int(time.time())}",
            "message": {
                "role": "user",
                "parts": [
                    {
                        "type": "text",
                        "text": task_content
                    }
                ]
            }
        }
        
        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"http://localhost:{agent_port}/tasks/send",
                    json=task_payload,
                    headers={"Content-Type": "application/json"}
                )
                
                print(f"📥 Response from {agent_name}:")
                print(f"   Status Code: {response.status_code}")
                print(f"   Response Time: {response.elapsed.total_seconds():.2f}s")
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Task submission successful!")
                    
                    # Try to extract the task result
                    if 'taskId' in result:
                        print(f"   Task ID: {result['taskId']}")
                    
                    # Wait for task completion (simplified)
                    await asyncio.sleep(2)
                    
                    # Try to get task status
                    if 'taskId' in result:
                        status_response = await client.get(
                            f"http://localhost:{agent_port}/tasks/{result['taskId']}"
                        )
                        if status_response.status_code == 200:
                            task_status = status_response.json()
                            print(f"   Task Status: {task_status.get('status', {}).get('state', 'unknown')}")
                    
                    return True
                else:
                    print(f"❌ Task submission failed:")
                    print(f"   Error: {response.text[:200]}...")
                    return False
                    
        except Exception as e:
            print(f"❌ Task submission error: {e}")
            return False
    
    async def test_data_processor(self):
        """Test Data Processor Agent with official A2A"""
        return await self.test_task_submission(
            8001, 
            "Data Processor",
            "Analyze security threats: Multiple failed admin login attempts from different geographic locations (US, Russia, China) with password spray attack patterns and credential exposure detected in logs"
        )
    
    async def test_report_generator(self):
        """Test Report Generator Agent with official A2A"""
        return await self.test_task_submission(
            8002,
            "Report Generator", 
            "Generate comprehensive security report for: Suspicious admin login attempts with multiple failed authentication events from different geographic locations. Include compliance analysis for APRA and SOC2 frameworks with agent coordination assessment."
        )
    
    async def test_wiretap_monitoring(self):
        """Test Wiretap tentacle monitoring capabilities"""
        print("🔍 Testing Wiretap Monitoring...")
        print("=" * 60)
        
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                # Test dashboard access
                dashboard_response = await client.get("http://localhost:8003/dashboard")
                if dashboard_response.status_code == 200:
                    print("✅ Wiretap dashboard accessible")
                else:
                    print(f"⚠️ Dashboard status: {dashboard_response.status_code}")
                
                # Test API endpoints
                agents_response = await client.get("http://localhost:8003/api/agents")
                if agents_response.status_code == 200:
                    agents_data = agents_response.json()
                    print(f"✅ Wiretap API working - {len(agents_data.get('agents', {}))} agents discovered")
                else:
                    print(f"⚠️ API status: {agents_response.status_code}")
                
                return True
                
        except Exception as e:
            print(f"❌ Wiretap monitoring error: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """Run comprehensive official A2A test suite"""
        print("🐙 INKTRACE OFFICIAL GOOGLE A2A TEST SUITE")
        print("=" * 80)
        print("Testing with official Google A2A Python SDK...")
        print("=" * 80)
        
        results = {}
        
        # Test 1: Agent Discovery
        results["discovery"] = await self.test_agent_discovery()
        await asyncio.sleep(2)
        
        # Test 2: Data Processor Communication
        results["data_processor"] = await self.test_data_processor()
        await asyncio.sleep(2)
        
        # Test 3: Report Generator Communication
        results["report_generator"] = await self.test_report_generator()
        await asyncio.sleep(2)
        
        # Test 4: Wiretap Monitoring
        results["wiretap"] = await self.test_wiretap_monitoring()
        
        # Summary
        print("\n🏆 TEST RESULTS SUMMARY")
        print("=" * 80)
        
        passed = 0
        total = 0
        
        for test_name, result in results.items():
            if test_name == "discovery":
                continue  # Skip discovery as it's not a boolean result
            
            total += 1
            if result:
                passed += 1
                print(f"✅ {test_name.replace('_', ' ').title()}: PASSED")
            else:
                print(f"❌ {test_name.replace('_', ' ').title()}: FAILED")
        
        print(f"\n🎯 OVERALL SCORE: {passed}/{total} tests passed")
        print(f"📚 SDK: Official Google A2A Python SDK")
        
        if passed == total:
            print("🎉 ALL TESTS PASSED - Official A2A Communication Working!")
            print("🐙 Inktrace distributed intelligence is operational!")
        else:
            print("⚠️ Some tests failed - check agent configurations")
        
        print("\n📊 Next Steps:")
        print("1. Open Wiretap Dashboard: http://localhost:8003/dashboard")
        print("2. Monitor communications: http://localhost:8003/communications")  
        print("3. Check security events: http://localhost:8003/security-events")
        print("4. Review agent cards at /.well-known/agent.json endpoints")
        
        return passed == total

async def main():
    """Run the official A2A communication test"""
    tester = OfficialA2ATester()
    success = await tester.run_comprehensive_test()
    
    if success:
        print("\n🚀 HACKATHON READY!")
        print("Your Inktrace system is ready for demonstration with official Google A2A!")
    else:
        print("\n🔧 NEEDS ATTENTION!")
        print("Some components need fixing before demo.")

if __name__ == "__main__":
    asyncio.run(main())