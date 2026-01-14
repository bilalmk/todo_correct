#!/usr/bin/env python3
"""Simple test to check where chat is getting stuck."""

import asyncio
import httpx
from uuid import UUID

# Your real user ID
USER_ID = "bded475f-c2e8-4fd8-b616-c260f18d550b"

async def test_health():
    """Test health endpoint first."""
    print("\n[1/3] Testing health endpoint...")
    async with httpx.AsyncClient() as client:
        response = await client.get("http://localhost:8000/api/chatkit/health")
        print(f"  Status: {response.status_code}")
        print(f"  Response: {response.json()}")

async def test_mcp_connection():
    """Test direct MCP connection."""
    print("\n[2/3] Testing MCP client connection...")
    import sys
    sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend')

    from src.chatkit.agent import create_mcp_client

    try:
        print("  Creating MCP client...")
        client = await create_mcp_client()
        print("  ✓ MCP client created")

        print("  Listing tools...")
        tools = await client.list_tools()
        print(f"  ✓ Found {len(tools.tools)} tools:")
        for tool in tools.tools:
            print(f"    - {tool.name}")

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

async def test_agent_creation():
    """Test agent creation."""
    print("\n[3/3] Testing agent creation...")
    import sys
    sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend')

    from src.chatkit.agent import create_mcp_client, create_agent_with_mcp
    from src.chatkit.server import SYSTEM_PROMPT

    try:
        print("  Creating MCP client...")
        client = await create_mcp_client()
        print("  ✓ MCP client created")

        print("  Creating agent with MCP tools...")
        agent = await create_agent_with_mcp(client, SYSTEM_PROMPT)
        print(f"  ✓ Agent created: {agent.name}")
        print(f"  Model: {agent.model}")

        # Try a simple streaming call with timeout
        print("\n  Testing agent streaming (with 10s timeout)...")
        from agents import Runner

        result = Runner.run_streamed(agent, "Say hello")

        try:
            event_count = 0
            async with asyncio.timeout(10):  # 10 second timeout
                async for event in result.stream_events():
                    event_count += 1
                    event_type = getattr(event, 'type', 'unknown')
                    print(f"    Event {event_count}: {event_type}")

                    if event_count >= 3:
                        print("    (stopping after 3 events)")
                        break

            print(f"  ✓ Streaming works! Got {event_count} events")

        except asyncio.TimeoutError:
            print(f"  ⚠️ Timeout after 10s (got {event_count} events)")
            print("  This means the agent is waiting for OpenAI API response")

    except Exception as e:
        print(f"  ✗ Error: {e}")
        import traceback
        traceback.print_exc()

async def main():
    print("=" * 60)
    print("ChatKit Diagnostics")
    print("=" * 60)

    await test_health()
    await test_mcp_connection()
    await test_agent_creation()

    print("\n" + "=" * 60)
    print("Diagnostics Complete")
    print("=" * 60)

if __name__ == "__main__":
    asyncio.run(main())
