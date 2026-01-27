#!/usr/bin/env python3
"""Debug event types from OpenAI Agents SDK."""

import asyncio
import sys
sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend')

async def test_event_types():
    from src.chatkit.server import CustomChatKitServer
    from src.chatkit.utils import RequestContext
    from src.core.database import engine
    from sqlmodel.ext.asyncio.session import AsyncSession
    from uuid import UUID

    user_id = UUID("bded475f-c2e8-4fd8-b616-c260f18d550b")

    async with AsyncSession(engine) as session:
        server = CustomChatKitServer(session)

        class MockThread:
            def __init__(self, thread_id):
                self.id = thread_id

        class MockMessage:
            def __init__(self, content):
                self.content = content
                self.role = "user"
                import datetime
                self.created_at = datetime.datetime.now(datetime.timezone.utc)

        thread = MockThread(UUID("00000000-0000-0000-0000-000000000001"))
        message = MockMessage("List all my tasks")
        context = RequestContext(user_id=user_id, correlation_id="test-events")

        # Intercept the streaming to see all events
        from src.chatkit.mcp_http_client import MCPHTTPClient
        from src.core.config import settings
        from agents import Agent, Runner, FunctionTool
        import json as json_module

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
                        return str(result) if result else ""
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

            event_types_seen = {}
            data_types_seen = {}

            async for event in result.stream_events():
                event_type = getattr(event, 'type', type(event).__name__)
                event_types_seen[event_type] = event_types_seen.get(event_type, 0) + 1

                if event_type == 'raw_response_event':
                    data = getattr(event, 'data', None)
                    if data:
                        data_type = getattr(data, 'type', None)
                        data_types_seen[data_type] = data_types_seen.get(data_type, 0) + 1

                        # Print first occurrence of each data type with details
                        if data_types_seen[data_type] == 1:
                            print(f"\n{'='*60}")
                            print(f"DATA TYPE: {data_type}")
                            print(f"{'='*60}")
                            print(f"Attributes: {[attr for attr in dir(data) if not attr.startswith('_')]}")

                            if hasattr(data, 'item'):
                                item = data.item
                                print(f"Item type: {type(item).__name__}")
                                print(f"Item attributes: {[attr for attr in dir(item) if not attr.startswith('_')]}")
                                if hasattr(item, 'output'):
                                    print(f"Output preview: {str(item.output)[:200]}")

            print(f"\n\n{'='*60}")
            print("EVENT TYPES SUMMARY")
            print(f"{'='*60}")
            for event_type, count in event_types_seen.items():
                print(f"{event_type}: {count}")

            print(f"\n{'='*60}")
            print("DATA TYPES SUMMARY")
            print(f"{'='*60}")
            for data_type, count in data_types_seen.items():
                print(f"{data_type}: {count}")

        finally:
            await mcp_client.close()


if __name__ == "__main__":
    print("\n🔍 Analyzing Event Types\n")
    asyncio.run(test_event_types())
    print()
