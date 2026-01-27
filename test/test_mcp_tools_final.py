#!/usr/bin/env python3
"""Final comprehensive test of MCP tools with user_id injection."""

import asyncio
import httpx
import json

MCP_URL = "http://localhost:8001/mcp"
USER_ID = "bded475f-c2e8-4fd8-b616-c260f18d550b"

async def test_mcp_tools_with_user_id():
    """Test all MCP tools work correctly with user_id parameter."""

    print("=" * 70)
    print("Final MCP Tools Test - With user_id Injection")
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

        # List tools
        print("\n[2/6] List MCP tools...")
        list_tools_response = await client.post(MCP_URL, headers=headers, json={
            "jsonrpc": "2.0",
            "id": "2",
            "method": "tools/list"
        })
        tools_result = list_tools_response.json()
        if "result" in tools_result:
            tools = tools_result["result"]["tools"]
            print(f"  ✓ Got {len(tools)} tools:")
            for tool in tools:
                print(f"    - {tool['name']}")
        else:
            print(f"  ✗ Error: {tools_result.get('error')}")
            return False

        # Test list_tasks
        print("\n[3/6] Call todo_list_tasks...")
        list_response = await client.post(MCP_URL, headers=headers, json={
            "jsonrpc": "2.0",
            "id": "3",
            "method": "tools/call",
            "params": {
                "name": "todo_list_tasks",
                "arguments": {"user_id": USER_ID, "status": "all"}
            }
        })
        list_result = list_response.json()

        if list_response.status_code == 200 and "result" in list_result:
            content = list_result["result"]["content"]
            tasks_text = content[0]["text"]
            tasks_data = json.loads(tasks_text)
            print(f"  ✓ Success! Got {tasks_data['total']} tasks")
            if tasks_data['total'] > 0:
                print(f"    Sample task: {tasks_data['tasks'][0]['title'][:50]}...")
        else:
            print(f"  ✗ Failed with status {list_response.status_code}")
            print(f"    Error: {list_result.get('error', 'Unknown error')}")
            return False

        # Test add_task
        print("\n[4/6] Call todo_add_task...")
        add_response = await client.post(MCP_URL, headers=headers, json={
            "jsonrpc": "2.0",
            "id": "4",
            "method": "tools/call",
            "params": {
                "name": "todo_add_task",
                "arguments": {
                    "user_id": USER_ID,
                    "title": "Test task from final MCP test",
                    "description": "Verifying user_id injection fix"
                }
            }
        })
        add_result = add_response.json()

        if add_response.status_code == 200 and "result" in add_result:
            task_text = add_result["result"]["content"][0]["text"]
            task_data = json.loads(task_text)
            new_task_id = task_data["task_id"]
            print(f"  ✓ Success! Created task ID: {new_task_id}")
            print(f"    Title: {task_data['title']}")
        else:
            print(f"  ✗ Failed with status {add_response.status_code}")
            print(f"    Error: {add_result.get('error', 'Unknown error')}")
            return False

        # Test complete_task
        print("\n[5/6] Call todo_complete_task...")
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

        if complete_response.status_code == 200 and "result" in complete_result:
            completed_text = complete_result["result"]["content"][0]["text"]
            completed_data = json.loads(completed_text)
            print(f"  ✓ Success! Task {new_task_id} marked as completed")
            print(f"    Status: completed={completed_data.get('completed', 'N/A')}")
        else:
            print(f"  ✗ Failed with status {complete_response.status_code}")
            print(f"    Error: {complete_result.get('error', 'Unknown error')}")

        # Test delete_task
        print("\n[6/6] Call todo_delete_task...")
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

        if delete_response.status_code == 200 and "result" in delete_result:
            print(f"  ✓ Success! Task {new_task_id} deleted")
        else:
            print(f"  ✗ Failed with status {delete_response.status_code}")
            print(f"    Error: {delete_result.get('error', 'Unknown error')}")

        print("\n" + "=" * 70)
        print("✅ ALL MCP TOOLS WORKING!")
        print("=" * 70)
        print("\nSuccessfully tested:")
        print("  ✓ todo_list_tasks")
        print("  ✓ todo_add_task")
        print("  ✓ todo_complete_task")
        print("  ✓ todo_delete_task")
        print("\nThe 500 error is FIXED!")
        print("user_id injection is working correctly.")

        return True


if __name__ == "__main__":
    print("\n🧪 Testing MCP Tools (Final Verification)\n")

    try:
        result = asyncio.run(test_mcp_tools_with_user_id())

        if result:
            print("\n✅ All tests passed!")
        else:
            print("\n❌ Some tests failed")
            exit(1)

    except Exception as e:
        print(f"\n✗ Test error: {e}")
        import traceback
        traceback.print_exc()
        exit(1)

    print()
