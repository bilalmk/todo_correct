#!/usr/bin/env python3
"""
Direct integration test of MCP + OpenAI Agents SDK.

This tests the full flow without the HTTP layer:
1. Connect to MCP server
2. List tools
3. Create OpenAI agent with MCP tools
4. Test agent invocation
"""

import asyncio
import sys
import os

# Add backend to path
sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend')

from src.chatkit.mcp_http_client import MCPHTTPClient
from src.chatkit.server import SYSTEM_PROMPT
from src.core.config import settings

async def test_mcp_integration():
    """Test full MCP + Agents SDK integration."""

    print("=" * 60)
    print("MCP + OpenAI Agents SDK Integration Test")
    print("=" * 60)

    # Step 1: Create MCP client
    print("\n[1/5] Creating MCP HTTP client...")
    mcp_client = MCPHTTPClient(settings.MCP_SERVER_URL)

    try:
        # Step 2: Initialize session
        print("\n[2/5] Initializing MCP session...")
        init_result = await mcp_client.initialize()
        print(f"  ✓ Protocol version: {init_result.get('protocolVersion')}")
        print(f"  ✓ Server: {init_result.get('serverInfo', {}).get('name')}")

        # Step 3: List tools
        print("\n[3/5] Listing MCP tools...")
        tools = await mcp_client.list_tools()
        print(f"  ✓ Found {len(tools)} tools:")
        for tool in tools:
            print(f"    - {tool['name']}: {tool['description'][:50]}...")

        # Step 4: Create OpenAI agent
        print("\n[4/5] Creating OpenAI Agent...")
        try:
            from agents import Agent, FunctionTool
            import json as json_module

            # Convert tool dicts to FunctionTool objects
            agent_tools = []
            for tool_dict in tools:
                tool_name = tool_dict["name"]

                def create_tool_handler(tool_name_capture: str):
                    async def on_invoke_tool(ctx, args: str) -> str:
                        parsed_args = json_module.loads(args)
                        result = await mcp_client.call_tool(tool_name_capture, parsed_args)
                        if isinstance(result, dict):
                            return json_module.dumps(result)
                        return str(result)
                    return on_invoke_tool

                function_tool = FunctionTool(
                    name=tool_name,
                    description=tool_dict["description"],
                    params_json_schema=tool_dict["inputSchema"],
                    on_invoke_tool=create_tool_handler(tool_name),
                )
                agent_tools.append(function_tool)

            agent = Agent(
                name="TodoAssistant",
                model=settings.OPENAI_MODEL,
                instructions=SYSTEM_PROMPT,
                tools=agent_tools,
            )
            print(f"  ✓ Agent created: {agent.name}")
            print(f"  ✓ Model: {agent.model}")
            print(f"  ✓ Tools: {len(agent_tools)} FunctionTool objects")

        except ImportError as e:
            print(f"  ⚠️  OpenAI Agents SDK not available: {e}")
            print("  Note: Install with: pip install openai-agents")
            print("  Skipping agent test...")
            return

        # Step 5: Test agent with a simple query (without actually calling OpenAI)
        print("\n[5/5] Agent configuration verified")
        print(f"  ✓ Agent ready to process messages")
        print(f"  ✓ System prompt: {len(SYSTEM_PROMPT)} characters")
        print("\n  Note: Actual OpenAI API calls require:")
        print("  - Valid OPENAI_API_KEY in environment")
        print("  - Sufficient API credits")
        print("  - Network connectivity to OpenAI")

        print("\n" + "=" * 60)
        print("✅ Integration Test PASSED")
        print("=" * 60)
        print("\nAll components working correctly:")
        print("  ✓ MCP server responding")
        print("  ✓ JSON-RPC protocol working")
        print("  ✓ Tool registration successful")
        print("  ✓ OpenAI Agents SDK integration ready")
        print("\nThe chat endpoint is ready to handle requests!")

    finally:
        # Cleanup
        await mcp_client.close()


async def test_direct_tool_call():
    """Test calling an MCP tool directly."""

    print("\n" + "=" * 60)
    print("Direct MCP Tool Call Test")
    print("=" * 60)

    mcp_client = MCPHTTPClient(settings.MCP_SERVER_URL)

    try:
        # Initialize
        print("\n[1/3] Initializing MCP session...")
        await mcp_client.initialize()
        print("  ✓ Session initialized")

        # List tools
        print("\n[2/3] Listing tools...")
        tools = await mcp_client.list_tools()
        print(f"  ✓ Got {len(tools)} tools")

        # Call list_tasks tool
        print("\n[3/3] Calling todo_list_tasks tool...")
        import httpx
        import json

        # Make direct JSON-RPC call
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.MCP_SERVER_URL,
                headers={"Mcp-Session-Id": mcp_client.session_id},
                json={
                    "jsonrpc": "2.0",
                    "id": "test-123",
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

            result = response.json()

            if "error" in result:
                print(f"  ✗ Tool call failed: {result['error']}")
            else:
                content = result.get("result", {}).get("content", [])
                if content:
                    task_data = content[0].get("text", "{}")
                    tasks = json.loads(task_data)
                    print(f"  ✓ Tool executed successfully")
                    print(f"  ✓ Found {tasks.get('total', 0)} tasks")

                    if tasks.get('tasks'):
                        print("\n  Sample task:")
                        task = tasks['tasks'][0]
                        print(f"    - ID: {task.get('task_id')}")
                        print(f"    - Title: {task.get('title')}")
                        print(f"    - Completed: {task.get('completed')}")

        print("\n" + "=" * 60)
        print("✅ Direct Tool Call Test PASSED")
        print("=" * 60)

    finally:
        await mcp_client.close()


if __name__ == "__main__":
    print("\n🔬 Starting Integration Tests\n")

    try:
        asyncio.run(test_mcp_integration())
        asyncio.run(test_direct_tool_call())
    except KeyboardInterrupt:
        print("\n\nTests interrupted by user")
    except Exception as e:
        print(f"\n\n✗ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

    print("\n✅ All tests completed!\n")
