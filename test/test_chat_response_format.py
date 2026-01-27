#!/usr/bin/env python3
"""Test to see what the chat endpoint actually returns."""

import asyncio
import sys
sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend')

async def test_chat_response_format():
    """Check what the actual response format looks like."""

    print("=" * 70)
    print("Testing Chat Response Format")
    print("=" * 70)

    from src.chatkit.server import CustomChatKitServer
    from src.chatkit.utils import RequestContext
    from src.core.database import engine
    from sqlmodel.ext.asyncio.session import AsyncSession
    from uuid import UUID

    user_id = UUID("bded475f-c2e8-4fd8-b616-c260f18d550b")
    correlation_id = "test-format-123"

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

        print("\nCalling respond() and examining events...")
        print("-" * 70)

        event_count = 0
        content_events = []

        try:
            async for event in server.respond(thread, message, context):
                event_count += 1

                # Show first 10 events in detail
                if event_count <= 10:
                    event_type = getattr(event, 'type', type(event).__name__)
                    print(f"\nEvent {event_count}: {event_type}")

                    # Show event attributes
                    if hasattr(event, '__dict__'):
                        for key, value in event.__dict__.items():
                            if isinstance(value, str) and len(value) > 100:
                                print(f"  {key}: {value[:100]}...")
                            else:
                                print(f"  {key}: {value}")

                    # Check for content
                    if hasattr(event, 'content'):
                        content_events.append(event.content)
                    if hasattr(event, 'delta'):
                        content_events.append(str(event.delta))

            print("\n" + "-" * 70)
            print(f"\nTotal events: {event_count}")
            print(f"Content events: {len(content_events)}")

            if content_events:
                print("\nCombined content:")
                print("=" * 70)
                combined = "".join(str(c) for c in content_events if c)
                print(combined[:500])
                if len(combined) > 500:
                    print(f"... ({len(combined) - 500} more characters)")

        except Exception as e:
            print(f"\nError: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    print("\n🔍 Analyzing Chat Response Format\n")
    asyncio.run(test_chat_response_format())
    print()
