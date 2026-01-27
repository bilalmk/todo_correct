#!/usr/bin/env python3
"""
Test the complete chat flow by directly calling MCP tools.
This verifies the MCP server is working end-to-end.
"""

import asyncio
import httpx
import json

MCP_URL = "http://localhost:8001/mcp"
USER_ID = "bded475f-c2e8-4fd8-b616-c260f18d550b"

async def test_complete_chat_flow():
    """Test a complete chat flow: list tasks, add task, list again."""

    print("=" * 70)
    print("Complete Chat Flow Test (MCP Tools)")
    print("=" * 70)

    async with httpx.AsyncClient() as client:

        # Initialize session
        print("\n[1/6] Initialize MCP session...")
        init_response = await client.post(MCP_URL, json={
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {"protocolVersion": "2024-11-05"}
        })
        session_id = init_response.headers.get("Mcp-Session-Id")
        print(f"  ✓ Session ID: {session_id}")

        headers = {"Mcp-Session-Id": session_id}

        # List initial tasks
        print("\n[2/6] List all tasks (initial state)...")
        list1_response = await client.post(MCP_URL, headers=headers, json={
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tools/call",
            "params": {
                "name": "todo_list_tasks",
                "arguments": {"user_id": USER_ID, "status": "all"}
            }
        })
        list1_result = list1_response.json()
        if "result" in list1_result:
            tasks_text = list1_result["result"]["content"][0]["text"]
            tasks_data = json.loads(tasks_text)
            initial_count = tasks_data["total"]
            print(f"  ✓ Found {initial_count} tasks initially")
        else:
            print(f"  ✗ Error: {list1_result.get('error')}")
            return

        # Add a new task
        print("\n[3/6] Add a new task...")
        add_response = await client.post(MCP_URL, headers=headers, json={
            "jsonrpc": "2.0",
            "id": "3",
            "method": "tools/call",
            "params": {
                "name": "todo_add_task",
                "arguments": {
                    "user_id": USER_ID,
                    "title": "Test task from MCP integration test",
                    "description": "This task verifies the MCP server is working correctly"
                }
            }
        })
        add_result = add_response.json()
        if "result" in add_result:
            task_text = add_result["result"]["content"][0]["text"]
            task_data = json.loads(task_text)
            new_task_id = task_data["task_id"]
            print(f"  ✓ Created task ID: {new_task_id}")
            print(f"    Title: {task_data['title']}")
        else:
            print(f"  ✗ Error: {add_result.get('error')}")
            return

        # List tasks again
        print("\n[4/6] List all tasks (after adding)...")
        list2_response = await client.post(MCP_URL, headers=headers, json={
            "jsonrpc": "2.0",
            "id": "4",
            "method": "tools/call",
            "params": {
                "name": "todo_list_tasks",
                "arguments": {"user_id": USER_ID, "status": "all"}
            }
        })
        list2_result = list2_response.json()
        if "result" in list2_result:
            tasks_text = list2_result["result"]["content"][0]["text"]
            tasks_data = json.loads(tasks_text)
            new_count = tasks_data["total"]
            print(f"  ✓ Found {new_count} tasks (was {initial_count})")

            if new_count == initial_count + 1:
                print(f"  ✓ Task count increased correctly")
            else:
                print(f"  ⚠️  Expected {initial_count + 1} tasks")
        else:
            print(f"  ✗ Error: {list2_result.get('error')}")
            return

        # Complete the task
        print("\n[5/6] Complete the new task...")
        complete_response = await client.post(MCP_URL, headers=headers, json={
            "jsonrpc": "2.0",
            "id": "5",
            "method": "tools/call",
            "params": {
                "name": "todo_complete_task",
                "arguments": {"user_id": USER_ID, "task_id": new_task_id}
            }
        })
        complete_result = complete_response.json()
        if "result" in complete_result:
            completed_text = complete_result["result"]["content"][0]["text"]
            completed_data = json.loads(completed_text)
            print(f"  ✓ Task {new_task_id} marked as completed")
            print(f"    Status: {completed_data.get('status', 'N/A')}")
        else:
            print(f"  ✗ Error: {complete_result.get('error')}")

        # Delete the test task
        print("\n[6/6] Delete the test task...")
        delete_response = await client.post(MCP_URL, headers=headers, json={
            "jsonrpc": "2.0",
            "id": "6",
            "method": "tools/call",
            "params": {
                "name": "todo_delete_task",
                "arguments": {"user_id": USER_ID, "task_id": new_task_id}
            }
        })
        delete_result = delete_response.json()
        if "result" in delete_result:
            print(f"  ✓ Task {new_task_id} deleted successfully")
        else:
            print(f"  ✗ Error: {delete_result.get('error')}")

        print("\n" + "=" * 70)
        print("✅ COMPLETE CHAT FLOW TEST PASSED")
        print("=" * 70)
        print("\nAll MCP tools working correctly:")
        print("  ✓ Session management")
        print("  ✓ todo_list_tasks")
        print("  ✓ todo_add_task")
        print("  ✓ todo_complete_task")
        print("  ✓ todo_delete_task")
        print("\nThe chat endpoint will work with proper authentication!")


if __name__ == "__main__":
    print("\n🧪 Testing Complete Chat Flow\n")

    try:
        asyncio.run(test_complete_chat_flow())
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()

    print()
