#!/usr/bin/env python3
"""
Test script to debug MCP connection issues.
"""

import asyncio
import json
import subprocess
import sys
import os

async def test_mcp_connection():
    """Test MCP connection step by step."""
    
    print("🔍 Testing MCP connection...")
    
    # Step 1: Start the MCP server
    print("\n1️⃣ Starting MCP server...")
    try:
        process = subprocess.Popen(
            ["python", "math_server.py"],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        print("✅ MCP server started")
    except Exception as e:
        print(f"❌ Failed to start MCP server: {e}")
        return False
    
    try:
        # Step 2: Send initialization request
        print("\n2️⃣ Sending initialization request...")
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {},
                    "resources": {},
                    "prompts": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        init_str = json.dumps(init_request) + "\n"
        process.stdin.write(init_str)
        process.stdin.flush()
        
        # Read initialization response
        init_response = process.stdout.readline()
        print(f"📥 Init response: {init_response.strip()}")
        
        if not init_response:
            print("❌ No initialization response")
            return False
        
        init_data = json.loads(init_response.strip())
        if "error" in init_data:
            print(f"❌ Initialization error: {init_data['error']}")
            return False
        
        print("✅ Initialization successful")
        
        # Step 3: Send initialized notification
        print("\n3️⃣ Sending initialized notification...")
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized",
            "params": {}
        }
        
        notif_str = json.dumps(initialized_notification) + "\n"
        process.stdin.write(notif_str)
        process.stdin.flush()
        print("✅ Initialized notification sent")
        
        # Step 4: List tools
        print("\n4️⃣ Listing tools...")
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        tools_str = json.dumps(tools_request) + "\n"
        process.stdin.write(tools_str)
        process.stdin.flush()
        
        tools_response = process.stdout.readline()
        print(f"📥 Tools response: {tools_response.strip()}")
        
        if tools_response:
            tools_data = json.loads(tools_response.strip())
            if "result" in tools_data and "tools" in tools_data["result"]:
                tools = tools_data["result"]["tools"]
                print(f"✅ Found {len(tools)} tools: {[t.get('name', 'unknown') for t in tools]}")
            else:
                print("❌ No tools found")
                return False
        
        # Step 5: Test tool call
        print("\n5️⃣ Testing tool call...")
        tool_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "add",
                "arguments": {
                    "a": 5,
                    "b": 12
                }
            }
        }
        
        tool_str = json.dumps(tool_request) + "\n"
        process.stdin.write(tool_str)
        process.stdin.flush()
        
        tool_response = process.stdout.readline()
        print(f"📥 Tool response: {tool_response.strip()}")
        
        if tool_response:
            tool_data = json.loads(tool_response.strip())
            if "result" in tool_data:
                result = tool_data["result"]
                print(f"✅ Tool call successful: {result}")
            elif "error" in tool_data:
                print(f"❌ Tool call error: {tool_data['error']}")
                return False
        
        print("\n🎉 MCP connection test successful!")
        return True
        
    except Exception as e:
        print(f"❌ Error during MCP test: {e}")
        return False
    
    finally:
        # Clean up
        print("\n🧹 Cleaning up...")
        try:
            process.terminate()
            process.wait(timeout=5)
            print("✅ Process terminated")
        except:
            process.kill()
            print("⚠️ Process killed")

if __name__ == "__main__":
    # Run the test
    success = asyncio.run(test_mcp_connection())
    sys.exit(0 if success else 1)
