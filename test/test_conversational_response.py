#!/usr/bin/env python3
"""Test conversational response (no tools called)."""

import asyncio
import sys
import json
sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend')

async def test_conversational():
    """Test response without tool calls."""

    print("=" * 70)
    print("Testing Conversational Response (No Tools)")
    print("=" * 70)

    from src.chatkit.server import CustomChatKitServer
    from src.chatkit.utils import RequestContext
    from src.core.database import engine
    from sqlmodel.ext.asyncio.session import AsyncSession
    from uuid import UUID

    user_id = UUID("bded475f-c2e8-4fd8-b616-c260f18d550b")
    correlation_id = "test-conversation-123"

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
        message = MockMessage("Hello! How are you?")

        context = RequestContext(user_id=user_id, correlation_id=correlation_id)

        print("\nSending message: 'Hello! How are you?'")
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
                        print("\n\n🔧 Tool Results:")
                        print("  (Tool results present - unexpected for conversational query)")
                    else:
                        print("\n\n✅ No tool results (expected for pure conversation)")

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("\n🔍 Testing Conversational Response\n")
    asyncio.run(test_conversational())
    print()
