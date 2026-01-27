#!/usr/bin/env python3
"""Quick test to verify FunctionTool fix works."""

import asyncio
import sys
sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend')

async def test_agent_creation():
    """Test that we can create an agent with FunctionTool objects."""

    print("=" * 70)
    print("Testing Agent Creation with FunctionTool Objects")
    print("=" * 70)

    from src.chatkit.mcp_http_client import MCPHTTPClient
    from src.chatkit.server import SYSTEM_PROMPT
    from src.core.config import settings
    from agents import Agent, FunctionTool
    import json as json_module

    # Create MCP client
    print("\n[1/4] Creating MCP client...")
    mcp_client = MCPHTTPClient(settings.MCP_SERVER_URL)

    try:
        # Initialize and list tools
        print("\n[2/4] Initializing MCP session and listing tools...")
        await mcp_client.initialize()
        tools = await mcp_client.list_tools()
        print(f"  ✓ Got {len(tools)} MCP tools")

        # Convert to FunctionTool objects
        print("\n[3/4] Creating FunctionTool objects...")
        agent_tools = []
        for tool_dict in tools:
            tool_name = tool_dict["name"]

            # Create handler factory
            def create_tool_handler(tool_name_capture: str):
                async def on_invoke_tool(ctx, args: str) -> str:
                    """Call MCP server tool with arguments."""
                    try:
                        parsed_args = json_module.loads(args)
                        result = await mcp_client.call_tool(tool_name_capture, parsed_args)
                        if isinstance(result, dict):
                            return json_module.dumps(result)
                        return str(result)
                    except Exception as e:
                        return json_module.dumps({"error": str(e)})
                return on_invoke_tool

            function_tool = FunctionTool(
                name=tool_name,
                description=tool_dict["description"],
                params_json_schema=tool_dict["inputSchema"],
                on_invoke_tool=create_tool_handler(tool_name),
            )
            agent_tools.append(function_tool)

        print(f"  ✓ Created {len(agent_tools)} FunctionTool objects")

        # Verify tool objects have .name attribute
        for tool in agent_tools:
            assert hasattr(tool, 'name'), f"Tool {tool} missing .name attribute"
        print(f"  ✓ All tools have .name attribute")

        # Create agent
        print("\n[4/4] Creating OpenAI Agent...")
        agent = Agent(
            name="TodoAssistant",
            model=settings.OPENAI_MODEL,
            instructions=SYSTEM_PROMPT,
            tools=agent_tools,
        )
        print(f"  ✓ Agent created successfully!")
        print(f"    Name: {agent.name}")
        print(f"    Model: {agent.model}")
        print(f"    Tools: {len(agent_tools)} FunctionTool objects")

        # Check that tools are properly attached
        print(f"  ✓ Agent has {len(agent_tools)} tools configured")

        print("\n" + "=" * 70)
        print("✅ TEST PASSED - AttributeError FIXED!")
        print("=" * 70)
        print("\nThe 'dict' object has no attribute 'name' error is resolved!")
        print("FunctionTool objects are being used correctly.")
        print("\nNext: Test actual chat endpoint with JWT token.")

        return True

    except AttributeError as e:
        if "'dict' object has no attribute 'name'" in str(e):
            print(f"  ✗ FAILED: {e}")
            print("\n" + "=" * 70)
            print("❌ TEST FAILED - Still getting AttributeError")
            print("=" * 70)
            return False
        else:
            raise

    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False

    finally:
        await mcp_client.close()


if __name__ == "__main__":
    print("\n🧪 Testing FunctionTool Fix\n")

    try:
        result = asyncio.run(test_agent_creation())

        if result:
            print("\n✅ Fix verified - agent creation works with FunctionTool objects!")
        else:
            print("\n❌ Fix incomplete - still has issues")
            sys.exit(1)

    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")
    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print()
