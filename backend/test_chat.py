#!/usr/bin/env python3
"""Test script to debug chat endpoint."""

import asyncio
import sys
from uuid import uuid4

# Add src to path
sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend')

from src.chatkit.server import CustomChatKitServer
from src.chatkit.utils import RequestContext
from src.core.database import get_session


async def test_chat():
    """Test the chat endpoint directly."""
    print("=" * 60)
    print("Testing ChatKit Server")
    print("=" * 60)

    # Create test context with REAL user from database
    from uuid import UUID
    user_id = UUID('bded475f-c2e8-4fd8-b616-c260f18d550b')  # Real user from DB
    correlation_id = str(uuid4())
    context = RequestContext(user_id=user_id, correlation_id=correlation_id)

    print(f"\nTest Parameters:")
    print(f"  User ID: {user_id}")
    print(f"  Correlation ID: {correlation_id}")
    print(f"  Message: 'List all my tasks'")

    # Get database session
    async for session in get_session():
        try:
            # Create server
            print("\n[1/5] Creating ChatKit server...")
            server = CustomChatKitServer(session)
            print("✓ Server created")

            # Create mock thread and message
            print("\n[2/5] Creating mock thread and message...")
            thread = type('Thread', (), {'id': str(user_id)})()
            user_message = type('UserMessage', (), {
                'content': 'List all my tasks',
                'role': 'user'
            })()
            print("✓ Thread and message created")

            # Call respond method
            print("\n[3/5] Calling server.respond()...")
            event_count = 0

            try:
                async for event in server.respond(thread, user_message, context):
                    event_count += 1
                    print(f"\n[4/5] Event #{event_count} received:")
                    print(f"  Type: {type(event)}")

                    # Try to extract event type
                    if hasattr(event, 'type'):
                        print(f"  Event Type: {event.type}")
                    elif isinstance(event, dict) and 'type' in event:
                        print(f"  Event Type: {event['type']}")

                    # Print event details
                    if hasattr(event, 'model_dump'):
                        print(f"  Data: {event.model_dump()}")
                    elif isinstance(event, dict):
                        print(f"  Data: {event}")
                    else:
                        print(f"  Data: {str(event)[:200]}")

                    # Only show first 5 events
                    if event_count >= 5:
                        print(f"\n  ... (showing first 5 events only)")
                        break

            except Exception as e:
                print(f"\n✗ Error during streaming: {e}")
                import traceback
                traceback.print_exc()
                return

            print(f"\n[5/5] Streaming completed!")
            print(f"  Total events: {event_count}")

            if event_count == 0:
                print("\n⚠️  WARNING: No events were yielded!")
                print("  This means the agent is not producing any output.")

        except Exception as e:
            print(f"\n✗ Error: {e}")
            import traceback
            traceback.print_exc()
        finally:
            await session.close()
            break


if __name__ == "__main__":
    asyncio.run(test_chat())
