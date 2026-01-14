#!/usr/bin/env python3
"""Test MCP tool directly to see the validation error."""

import asyncio
import httpx
import json
from uuid import uuid4

MCP_URL = "http://localhost:8001/mcp"

async def test_add_task_with_advanced_fields():
    """Test the add_task tool with priority and due_date."""

    # Simulate what the AI is sending
    test_cases = [
        {
            "name": "With priority and due_date as strings",
            "arguments": {
                "user_id": str(uuid4()),
                "title": "Submit quarterly report",
                "priority": "high",
                "due_date": "2026-01-20T14:00:00Z"
            }
        },
        {
            "name": "Basic test - title only",
            "arguments": {
                "user_id": str(uuid4()),
                "title": "Test task"
            }
        }
    ]

    async with httpx.AsyncClient() as client:
        # Initialize session first
        print("1. Initializing MCP session...")
        init_response = await client.post(
            MCP_URL,
            json={
                "jsonrpc": "2.0",
                "id": 1,
                "method": "initialize",
                "params": {
                    "protocolVersion": "0.1.0",
                    "capabilities": {},
                    "clientInfo": {"name": "test", "version": "1.0"}
                }
            }
        )
        print(f"   Status: {init_response.status_code}")
        print(f"   Response: {init_response.json()}\n")

        # Test each case
        for i, test_case in enumerate(test_cases, 2):
            print(f"{i}. Testing: {test_case['name']}")
            print(f"   Arguments: {json.dumps(test_case['arguments'], indent=2)}")

            response = await client.post(
                MCP_URL,
                json={
                    "jsonrpc": "2.0",
                    "id": i,
                    "method": "tools/call",
                    "params": {
                        "name": "todo_add_task",
                        "arguments": test_case['arguments']
                    }
                }
            )

            print(f"   Status: {response.status_code}")
            result = response.json()

            if "error" in result:
                print(f"   ❌ ERROR: {result['error']}")
            else:
                print(f"   ✅ SUCCESS: {result.get('result', 'No result')}")

            print()

if __name__ == "__main__":
    asyncio.run(test_add_task_with_advanced_fields())
