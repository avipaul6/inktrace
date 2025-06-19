#!/usr/bin/env python3
"""
Debug Policy Agent Startup
debug_policy_agent.py

Simple test to see what's preventing the policy agent from starting
"""

import sys
import traceback
from pathlib import Path

def test_basic_imports():
    """Test if we can import everything needed"""
    print("🔍 Testing basic imports...")
    
    try:
        import json
        print("✅ json")
    except Exception as e:
        print(f"❌ json: {e}")
        return False
    
    try:
        import uuid
        print("✅ uuid")
    except Exception as e:
        print(f"❌ uuid: {e}")
        return False
    
    try:
        import asyncio
        print("✅ asyncio")
    except Exception as e:
        print(f"❌ asyncio: {e}")
        return False
    
    try:
        from datetime import datetime
        print("✅ datetime")
    except Exception as e:
        print(f"❌ datetime: {e}")
        return False
    
    try:
        import argparse
        print("✅ argparse")
    except Exception as e:
        print(f"❌ argparse: {e}")
        return False
    
    return True

def test_a2a_imports():
    """Test A2A SDK imports"""
    print("\n🔍 Testing A2A SDK imports...")
    
    try:
        from a2a.server.apps import A2AStarletteApplication
        print("✅ A2AStarletteApplication")
    except Exception as e:
        print(f"❌ A2AStarletteApplication: {e}")
        return False
    
    try:
        from a2a.server.request_handlers import DefaultRequestHandler
        print("✅ DefaultRequestHandler")
    except Exception as e:
        print(f"❌ DefaultRequestHandler: {e}")
        return False
    
    try:
        from a2a.server.tasks import InMemoryTaskStore
        print("✅ InMemoryTaskStore")
    except Exception as e:
        print(f"❌ InMemoryTaskStore: {e}")
        return False
    
    try:
        from a2a.server.agent_execution import AgentExecutor, RequestContext
        print("✅ AgentExecutor, RequestContext")
    except Exception as e:
        print(f"❌ AgentExecutor, RequestContext: {e}")
        return False
    
    try:
        from a2a.server.events import EventQueue
        print("✅ EventQueue")
    except Exception as e:
        print(f"❌ EventQueue: {e}")
        return False
    
    try:
        from a2a.types import AgentCard, AgentSkill, AgentCapabilities
        print("✅ AgentCard, AgentSkill, AgentCapabilities")
    except Exception as e:
        print(f"❌ AgentCard, AgentSkill, AgentCapabilities: {e}")
        return False
    
    try:
        from a2a.utils import new_agent_text_message
        print("✅ new_agent_text_message")
    except Exception as e:
        print(f"❌ new_agent_text_message: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ uvicorn")
    except Exception as e:
        print(f"❌ uvicorn: {e}")
        return False
    
    return True

def test_minimal_agent():
    """Test creating a minimal agent"""
    print("\n🔍 Testing minimal agent creation...")
    
    try:
        from a2a.server.apps import A2AStarletteApplication
        from a2a.server.request_handlers import DefaultRequestHandler
        from a2a.server.tasks import InMemoryTaskStore
        from a2a.server.agent_execution import AgentExecutor, RequestContext
        from a2a.server.events import EventQueue
        from a2a.types import AgentCard, AgentSkill, AgentCapabilities
        from a2a.utils import new_agent_text_message
        
        class TestExecutor(AgentExecutor):
            async def execute(self, context: RequestContext, event_queue: EventQueue):
                event_queue.enqueue_event(new_agent_text_message("Test response"))
            
            async def cancel(self, context: RequestContext, event_queue: EventQueue):
                pass
        
        agent_card = AgentCard(
            name="Test Agent",
            description="Test agent for debugging",
            version="1.0.0",
            url="http://localhost:8999",
            capabilities=AgentCapabilities(streaming=True, pushNotifications=False),
            skills=[
                AgentSkill(
                    id="test_skill",
                    name="Test Skill",
                    description="Test skill for debugging",
                    tags=["test", "debugging"]
                )
            ],
            defaultInputModes=["text/plain"],
            defaultOutputModes=["text/markdown"]
        )
        
        agent_executor = TestExecutor()
        request_handler = DefaultRequestHandler(
            agent_executor=agent_executor,
            task_store=InMemoryTaskStore()
        )
        
        server_app_builder = A2AStarletteApplication(
            agent_card=agent_card,
            http_handler=request_handler
        )
        
        app = server_app_builder.build()
        print("✅ Minimal agent created successfully")
        return True
        
    except Exception as e:
        print(f"❌ Minimal agent creation failed: {e}")
        traceback.print_exc()
        return False

def test_uvicorn_import():
    """Test if uvicorn can be imported and used"""
    print("\n🔍 Testing uvicorn...")
    
    try:
        import uvicorn
        print("✅ uvicorn imported")
        
        # Test if we can create a simple app
        def simple_app(scope, receive, send):
            pass
        
        print("✅ uvicorn can be used")
        return True
        
    except Exception as e:
        print(f"❌ uvicorn error: {e}")
        return False

def test_policy_agent_file():
    """Test if policy agent file exists and is readable"""
    print("\n🔍 Testing policy agent file...")
    
    policy_agent_path = Path("agents/policy_agent.py")
    
    if not policy_agent_path.exists():
        print(f"❌ Policy agent file not found: {policy_agent_path}")
        return False
    
    print(f"✅ Policy agent file exists: {policy_agent_path}")
    
    try:
        with open(policy_agent_path, 'r') as f:
            content = f.read()
        print(f"✅ Policy agent file readable ({len(content)} chars)")
        
        # Check for basic Python syntax
        try:
            compile(content, str(policy_agent_path), 'exec')
            print("✅ Policy agent syntax is valid")
        except SyntaxError as e:
            print(f"❌ Policy agent syntax error: {e}")
            return False
        
    except Exception as e:
        print(f"❌ Error reading policy agent: {e}")
        return False
    
    return True

def run_policy_agent_test():
    """Try to import and run the policy agent main function"""
    print("\n🔍 Testing policy agent import and execution...")
    
    try:
        # Add agents directory to path
        agents_dir = Path("agents")
        if agents_dir.exists():
            sys.path.insert(0, str(agents_dir))
        
        # Try to import policy_agent
        import policy_agent
        print("✅ Policy agent imported successfully")
        
        # Check if main function exists
        if hasattr(policy_agent, 'main'):
            print("✅ Policy agent has main function")
        else:
            print("❌ Policy agent missing main function")
            return False
        
        # Try to create the components used in main
        try:
            if hasattr(policy_agent, 'create_agent_card'):
                print("✅ create_agent_card function exists")
            else:
                print("❌ create_agent_card function missing")
                return False
            
            if hasattr(policy_agent, 'InktracePolicyExecutor'):
                print("✅ InktracePolicyExecutor class exists")
            else:
                print("❌ InktracePolicyExecutor class missing")
                return False
        
        except Exception as e:
            print(f"❌ Error checking policy agent components: {e}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Policy agent import failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all diagnostic tests"""
    print("🐙 POLICY AGENT STARTUP DIAGNOSTIC")
    print("=" * 50)
    
    tests = [
        ("Basic Python imports", test_basic_imports),
        ("A2A SDK imports", test_a2a_imports),
        ("Minimal agent creation", test_minimal_agent),
        ("Uvicorn functionality", test_uvicorn_import),
        ("Policy agent file", test_policy_agent_file),
        ("Policy agent import", run_policy_agent_test),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            traceback.print_exc()
            results[test_name] = False
    
    print("\n" + "="*50)
    print("🔍 DIAGNOSTIC SUMMARY")
    print("="*50)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
    
    if all(results.values()):
        print("\n✅ All tests passed! Policy agent should work.")
        print("🎯 Try running the policy agent manually:")
        print("   python agents/policy_agent.py --port 8006")
    else:
        print(f"\n❌ {sum(1 for r in results.values() if not r)} tests failed.")
        print("🔧 Fix the failing tests before running the policy agent.")
    
    return all(results.values())

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)