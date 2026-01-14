#!/usr/bin/env python3
"""Test MCP server JSON-RPC endpoint."""

import httpx
import asyncio
import json


async def test_mcp_server():
    """Test MCP server via JSON-RPC."""

    async with httpx.AsyncClient() as client:
        # Step 1: Initialize
        print("\n[1/3] Testing initialize...")
        init_response = await client.post(
            "http://localhost:8001/mcp",
            json={
                "jsonrpc": "2.0",
                "id": "1",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"}
                }
            }
        )
        print(f"  Status: {init_response.status_code}")
        init_result = init_response.json()
        print(f"  Result: {json.dumps(init_result, indent=2)}")

        session_id = init_response.headers.get("Mcp-Session-Id")
        print(f"  Session ID: {session_id}")

        # Step 2: List tools
        print("\n[2/3] Testing tools/list...")
        list_response = await client.post(
            "http://localhost:8001/mcp",
            headers={"Mcp-Session-Id": session_id},
            json={
                "jsonrpc": "2.0",
                "id": "2",
                "method": "tools/list",
                "params": {}
            }
        )
        print(f"  Status: {list_response.status_code}")
        list_result = list_response.json()
        tools = list_result.get("result", {}).get("tools", [])
        print(f"  Found {len(tools)} tools:")
        for tool in tools:
            print(f"    - {tool['name']}: {tool['description'][:60]}...")

        # Step 3: Call a tool
        print("\n[3/3] Testing tools/call (todo_list_tasks)...")
        call_response = await client.post(
            "http://localhost:8001/mcp",
            headers={"Mcp-Session-Id": session_id},
            json={
                "jsonrpc": "2.0",
                "id": "3",
                "method": "tools/call",
                "params": {
                    "name": "todo_list_tasks",
                    "arguments": {
                        "user_id": "bded475f-c2e8-4fd8-b616-c260f18d550b",
                        "status": "all"
                    }
                }
            }
        )
        print(f"  Status: {call_response.status_code}")
        call_result = call_response.json()
        print(f"  Result: {json.dumps(call_result, indent=2)}")


if __name__ == "__main__":
    asyncio.run(test_mcp_server())
