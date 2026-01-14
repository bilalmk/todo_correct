#!/usr/bin/env python3
"""Analyze tool call events to understand how to capture results."""

import asyncio
import sys
sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend')

async def test_tool_call_events():
    """Examine tool call events in detail."""
    from src.core.config import settings
    from src.chatkit.mcp_http_client import MCPHTTPClient
    from agents import Agent, Runner, FunctionTool
    import json as json_module
    from uuid import UUID

    user_id = UUID("bded475f-c2e8-4fd8-b616-c260f18d550b")
    correlation_id = "test-tool-calls"

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
                    parsed_args = json_module.loads(args)
                    parsed_args["user_id"] = str(user_id)
                    result = await mcp_client.call_tool(tool_name_capture, parsed_args)
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

        tool_call_events = []

        print("\n" + "="*70)
        print("Analyzing Tool Call Events")
        print("="*70)

        async for event in result.stream_events():
            event_type = getattr(event, 'type', type(event).__name__)

            if event_type == 'raw_response_event':
                data = getattr(event, 'data', None)
                if data:
                    data_type = getattr(data, 'type', None)

                    # Capture tool-related events
                    if 'function_tool_call' in str(data_type) or 'tool' in str(data_type).lower():
                        tool_call_events.append({
                            'data_type': data_type,
                            'event': event,
                            'data': data
                        })

                        print(f"\n{'='*70}")
                        print(f"Tool Event: {data_type}")
                        print(f"{'='*70}")

                        # Show all attributes
                        attrs = [attr for attr in dir(data) if not attr.startswith('_')]
                        print(f"Attributes: {attrs}")

                        # Show key attributes
                        for attr in ['name', 'call_id', 'arguments', 'output', 'result', 'item', 'content']:
                            if hasattr(data, attr):
                                value = getattr(data, attr)
                                if isinstance(value, str) and len(value) > 200:
                                    print(f"{attr}: {value[:200]}...")
                                else:
                                    print(f"{attr}: {value}")

        print(f"\n{'='*70}")
        print(f"Total tool-related events: {len(tool_call_events)}")
        print(f"{'='*70}")

    finally:
        await mcp_client.close()


if __name__ == "__main__":
    print("\n🔍 Analyzing Tool Call Events\n")
    asyncio.run(test_tool_call_events())
    print()
