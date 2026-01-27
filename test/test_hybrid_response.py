#!/usr/bin/env python3
"""Test the hybrid response format with both text and structured data."""

import asyncio
import sys
import json
sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend')

async def test_hybrid_response():
    """Test hybrid response format."""

    print("=" * 70)
    print("Testing Hybrid Response Format (Text + Structured Data)")
    print("=" * 70)

    from src.chatkit.server import CustomChatKitServer
    from src.chatkit.utils import RequestContext
    from src.core.database import engine
    from sqlmodel.ext.asyncio.session import AsyncSession
    from uuid import UUID

    user_id = UUID("bded475f-c2e8-4fd8-b616-c260f18d550b")
    correlation_id = "test-hybrid-123"

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

        context = RequestContext(user_id=user_id, correlation_id=correlation_id)

        print("\nSending message: 'List all my tasks'")
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
                        print("\n\n🔧 Tool Results (Structured Data):")
                        print("-" * 70)
                        for tool_result in last_event['tool_results']:
                            print(f"\n  Tool: {tool_result['tool']}")
                            print(f"  Arguments: {json.dumps(tool_result['arguments'], indent=4)}")
                            print(f"  Result: {json.dumps(tool_result['result'], indent=4)}")
                        print("-" * 70)
                    else:
                        print("\n⚠️  No tool results found in response")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("\n🔍 Testing Hybrid Chat Response (Text + Structured Data)\n")
    asyncio.run(test_hybrid_response())
    print()
