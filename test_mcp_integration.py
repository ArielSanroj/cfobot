#!/usr/bin/env python3
"""
Test script for CFO MCP integration.
This script tests the MCP server functionality without requiring the full Nanobot setup.
"""

import json
import subprocess
import sys
from pathlib import Path

def test_mcp_server():
    """Test the MCP server functionality."""
    print("🧪 Testing CFO MCP Server Integration...")
    print("=" * 50)
    
    # Test 1: Initialize
    print("1. Testing initialization...")
    result = send_mcp_request({
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {}
    })
    
    if result and "result" in result:
        print("   ✅ Initialization successful")
        print(f"   📋 Server: {result['result']['serverInfo']['name']} v{result['result']['serverInfo']['version']}")
    else:
        print("   ❌ Initialization failed")
        return False
    
    # Test 2: List tools
    print("\n2. Testing tools list...")
    result = send_mcp_request({
        "jsonrpc": "2.0",
        "id": 2,
        "method": "tools/list",
        "params": {}
    })
    
    if result and "result" in result and "tools" in result["result"]:
        tools = result["result"]["tools"]
        print(f"   ✅ Found {len(tools)} tools:")
        for tool in tools:
            print(f"      • {tool['name']}: {tool['description']}")
    else:
        print("   ❌ Tools list failed")
        return False
    
    # Test 3: Test available reports tool
    print("\n3. Testing available reports...")
    result = send_mcp_request({
        "jsonrpc": "2.0",
        "id": 3,
        "method": "tools/call",
        "params": {
            "name": "get_available_reports",
            "arguments": {}
        }
    })
    
    if result and "result" in result:
        if "success" in result["result"] and result["result"]["success"]:
            reports = result["result"].get("reports", [])
            print(f"   ✅ Found {len(reports)} available reports")
            if reports:
                print("   📄 Recent reports:")
                for report in reports[:3]:  # Show first 3
                    print(f"      • {report['name']} ({report['size']} bytes)")
            else:
                print("   ℹ️  No reports found in downloads directory")
        else:
            print(f"   ⚠️  Reports check completed with message: {result['result'].get('message', 'Unknown')}")
    else:
        print("   ❌ Available reports test failed")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 MCP Server Integration Test Complete!")
    print("\nNext steps:")
    print("1. Set your API key: export OPENAI_API_KEY=sk-...")
    print("2. Start the CFO Agent: python start_cfo_agent.py")
    print("3. Open http://localhost:8080 in your browser")
    print("4. Start chatting with the CFO Financial Analyst!")
    
    return True

def send_mcp_request(request):
    """Send a request to the MCP server and return the response."""
    try:
        process = subprocess.Popen(
            ["python", "cfo_mcp_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            cwd=Path(__file__).parent
        )
        
        stdout, stderr = process.communicate(input=json.dumps(request) + "\n")
        
        if stderr:
            print(f"   ⚠️  Server stderr: {stderr}")
        
        if stdout:
            return json.loads(stdout.strip())
        else:
            return None
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return None

if __name__ == "__main__":
    success = test_mcp_server()
    sys.exit(0 if success else 1)