#!/usr/bin/env python3
"""Test response with multiple tool calls."""

import asyncio
import sys
import json
sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend')

async def test_multiple_tools():
    """Test response with multiple tool calls."""

    print("=" * 70)
    print("Testing Multiple Tool Calls")
    print("=" * 70)

    from src.chatkit.server import CustomChatKitServer
    from src.chatkit.utils import RequestContext
    from src.core.database import engine
    from sqlmodel.ext.asyncio.session import AsyncSession
    from uuid import UUID

    user_id = UUID("bded475f-c2e8-4fd8-b616-c260f18d550b")
    correlation_id = "test-multiple-123"

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
        message = MockMessage("Add a task 'Test multiple tools' then list all my tasks")

        context = RequestContext(user_id=user_id, correlation_id=correlation_id)

        print("\nSending message: 'Add a task \"Test multiple tools\" then list all my tasks'")
        print("Waiting for response...\n")

        try:
            events = []
            async for event in server.respond(thread, message, context):
                events.append(event)

            print("=" * 70)
            print(f"✅ SUCCESS - Received {len(events)} event(s)")
            print("=" * 70)

            if events:
                last_event = events[-1]
                print("\n📦 Full Response:")
                print(json.dumps(last_event, indent=2, default=str))

                if isinstance(last_event, dict):
                    if 'content' in last_event:
                        print("\n\n💬 AI Response (Text):")
                        print("-" * 70)
                        print(last_event['content'])
                        print("-" * 70)

                    if 'tool_results' in last_event:
                        print(f"\n\n🔧 Tool Results ({len(last_event['tool_results'])} tool calls):")
                        print("-" * 70)
                        for i, tool_result in enumerate(last_event['tool_results'], 1):
                            print(f"\n  [{i}] Tool: {tool_result['tool']}")
                            print(f"      Arguments: {json.dumps(tool_result['arguments'], indent=10)}")

                            # Show result summary (not full content)
                            result = tool_result['result']
                            if isinstance(result, dict):
                                if 'tasks' in result:
                                    print(f"      Result: {result.get('total', len(result['tasks']))} tasks")
                                elif 'task_id' in result:
                                    print(f"      Result: Created task ID {result['task_id']}")
                                else:
                                    print(f"      Result: {list(result.keys())}")
                            else:
                                print(f"      Result: {str(result)[:100]}")
                        print("-" * 70)
                    else:
                        print("\n\n⚠️  No tool results found")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("\n🔍 Testing Multiple Tool Calls\n")
    asyncio.run(test_multiple_tools())
    print()
