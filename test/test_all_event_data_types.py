#!/usr/bin/env python3
"""Show all event data types and their contents."""

import asyncio
import sys
sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend')

async def test_all_events():
    """Show all event types in detail."""
    from src.core.config import settings
    from src.chatkit.mcp_http_client import MCPHTTPClient
    from agents import Agent, Runner, FunctionTool
    import json as json_module
    from uuid import UUID

    user_id = UUID("bded475f-c2e8-4fd8-b616-c260f18d550b")

    mcp_client = MCPHTTPClient(settings.MCP_SERVER_URL)

    try:
        await mcp_client.initialize()
        tools = await mcp_client.list_tools()

        agent_tools = []
        for tool_dict in tools:
            tool_name = tool_dict["name"]

            agent_schema = tool_dict["inputSchema"].copy()
            if "properties" in agent_schema and "user_id" in agent_schema["properties"]:
                agent_schema["properties"] = {k: v for k, v in agent_schema["properties"].items() if k != "user_id"}
                if "required" in agent_schema:
                    agent_schema["required"] = [field for field in agent_schema["required"] if field != "user_id"]

            def create_tool_handler(tool_name_capture: str):
                async def on_invoke_tool(ctx, args: str) -> str:
                    print(f"\n🔧 TOOL CALLED: {tool_name_capture}")
                    parsed_args = json_module.loads(args)
                    parsed_args["user_id"] = str(user_id)
                    result = await mcp_client.call_tool(tool_name_capture, parsed_args)
                    print(f"🔧 TOOL RESULT: {result}")
                    if isinstance(result, dict):
                        return json_module.dumps(result)
                    return str(result)
                return on_invoke_tool

            function_tool = FunctionTool(
                name=tool_name,
                description=tool_dict["description"],
                params_json_schema=agent_schema,
                on_invoke_tool=create_tool_handler(tool_name),
            )
            agent_tools.append(function_tool)

        agent = Agent(
            name="TodoAssistant",
            model=settings.OPENAI_MODEL,
            instructions="You are a task assistant",
            tools=agent_tools,
        )

        result = Runner.run_streamed(agent, "List all my tasks")

        event_count = 0
        data_types_seen = {}

        async for event in result.stream_events():
            event_count += 1
            event_type = getattr(event, 'type', type(event).__name__)

            if event_type == 'raw_response_event':
                data = getattr(event, 'data', None)
                if data:
                    data_type = getattr(data, 'type', None)

                    if data_type not in data_types_seen:
                        data_types_seen[data_type] = 0
                    data_types_seen[data_type] += 1

                    # Show first occurrence of each type
                    if data_types_seen[data_type] == 1:
                        print(f"\n{'='*70}")
                        print(f"DATA TYPE: {data_type}")
                        print(f"{'='*70}")
                        attrs = [attr for attr in dir(data) if not attr.startswith('_')]
                        print(f"Attributes: {attrs}")

                        # Check for common tool-related attributes
                        for attr in attrs:
                            if 'tool' in attr.lower() or attr in ['name', 'arguments', 'output', 'content', 'item']:
                                value = getattr(data, attr, None)
                                if value is not None:
                                    if isinstance(value, str) and len(value) > 200:
                                        print(f"  {attr}: {value[:200]}...")
                                    else:
                                        print(f"  {attr}: {value}")

        print(f"\n{'='*70}")
        print("Summary")
        print(f"{'='*70}")
        print(f"Total events: {event_count}")
        print(f"\nData types:")
        for data_type, count in sorted(data_types_seen.items()):
            print(f"  {data_type}: {count}")

    finally:
        await mcp_client.close()


if __name__ == "__main__":
    print("\n🔍 Showing All Event Data Types\n")
    asyncio.run(test_all_events())
    print()
