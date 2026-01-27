#!/usr/bin/env python3
"""
Test script for advanced natural language task parsing.

Tests the AI's ability to extract:
- Due dates from natural language
- Priority levels from keywords
- Recurrence patterns
- Reminders
"""

import asyncio
import httpx
import json
from datetime import datetime, timezone

API_BASE = "http://localhost:8000/api"

# You'll need to get a real token by logging in
# For now, this is a placeholder
TOKEN = "YOUR_TOKEN_HERE"  # Replace with actual JWT token

async def test_chat(message: str, description: str):
    """Send a message to the chat endpoint and display the response."""
    print(f"\n{'='*80}")
    print(f"TEST: {description}")
    print(f"MESSAGE: \"{message}\"")
    print(f"{'='*80}")

    async with httpx.AsyncClient() as client:
        try:
            async with client.stream(
                "POST",
                f"{API_BASE}/chatkit/chat",
                headers={
                    "Authorization": f"Bearer {TOKEN}",
                    "Content-Type": "application/json"
                },
                json={"message": message},
                timeout=30.0
            ) as response:
                print(f"Status: {response.status_code}")

                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"ERROR: {error_text.decode()}")
                    return

                # Read SSE events
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data = line[6:]  # Remove "data: " prefix
                        try:
                            event_data = json.loads(data)

                            # Display key event data
                            if event_data.get("type") == "message":
                                print(f"\n✅ RESPONSE:")
                                print(f"   Content: {event_data.get('content', 'N/A')}")

                                # Show tool results if present
                                tool_results = event_data.get("tool_results", [])
                                if tool_results:
                                    print(f"\n📋 TOOL CALLS:")
                                    for tr in tool_results:
                                        print(f"   - Tool: {tr.get('tool', 'unknown')}")
                                        print(f"     Args: {json.dumps(tr.get('arguments', {}), indent=6)}")
                                        result = tr.get('result', {})
                                        if isinstance(result, dict):
                                            print(f"     Result: {json.dumps(result, indent=6, default=str)}")
                                        else:
                                            print(f"     Result: {result}")
                        except json.JSONDecodeError:
                            # Skip non-JSON lines
                            pass

        except Exception as e:
            print(f"❌ ERROR: {e}")


async def main():
    """Run all test cases."""
    print("="*80)
    print("ADVANCED NATURAL LANGUAGE TASK PARSING TESTS")
    print(f"Current Date Reference: {datetime.now(timezone.utc).strftime('%Y-%m-%d')}")
    print("="*80)

    # Test 1: Due date + Priority
    await test_chat(
        "I will complete my project about FastAPI due date is 31st January",
        "Extract due date and infer priority"
    )

    await asyncio.sleep(1)

    # Test 2: Explicit priority + due date
    await test_chat(
        "Urgent: Finish the presentation by tomorrow at 5pm",
        "Extract priority (urgent) and specific due date/time"
    )

    await asyncio.sleep(1)

    # Test 3: Weekly recurring task
    await test_chat(
        "Remind me to call my mom every Sunday",
        "Extract weekly recurrence pattern"
    )

    await asyncio.sleep(1)

    # Test 4: Low priority task
    await test_chat(
        "Buy groceries when I have time, not urgent",
        "Extract low priority"
    )

    await asyncio.sleep(1)

    # Test 5: Daily recurring with time
    await test_chat(
        "Daily standup meeting at 9am every morning",
        "Extract daily recurrence"
    )

    await asyncio.sleep(1)

    # Test 6: Update task deadline
    await test_chat(
        "Change task 18's deadline to February 15th",
        "Update existing task's due date"
    )

    print("\n" + "="*80)
    print("✅ ALL TESTS COMPLETE")
    print("="*80)
    print("\nNOTE: Replace TOKEN in script with actual JWT token from login")
    print("      Get token by: POST /api/auth/login with valid credentials")


if __name__ == "__main__":
    asyncio.run(main())
