#!/usr/bin/env python3
"""Test ChatKit chat endpoint with authentication."""

import asyncio
import httpx
import json
import sys

# Test user credentials
USER_ID = "bded475f-c2e8-4fd8-b616-c260f18d550b"

async def test_chat_endpoint():
    """Test the chat endpoint with a simple message."""

    print("=" * 60)
    print("ChatKit Chat Endpoint Test")
    print("=" * 60)

    async with httpx.AsyncClient(timeout=30.0) as client:

        # Step 1: Get JWT token from frontend auth endpoint
        print("\n[1/3] Getting JWT token...")
        try:
            # Try to get token from the get-token endpoint
            token_response = await client.get(
                "http://localhost:3000/api/auth/get-token",
                headers={"Cookie": "better-auth.session_token=your-session"}  # This would come from browser
            )

            if token_response.status_code != 200:
                print(f"  ⚠️  Cannot get token from frontend (status: {token_response.status_code})")
                print("  Note: You need to be logged in to the frontend first")
                print("  Attempting to test without auth (will likely fail)...")
                jwt_token = None
            else:
                token_data = token_response.json()
                jwt_token = token_data.get("token")
                print(f"  ✓ Got JWT token: {jwt_token[:20]}...")

        except Exception as e:
            print(f"  ⚠️  Error getting token: {e}")
            print("  Testing without auth token (for debugging)...")
            jwt_token = None

        # Step 2: Test health check
        print("\n[2/3] Testing health endpoint...")
        health_response = await client.get("http://localhost:8000/api/chatkit/health")
        print(f"  Status: {health_response.status_code}")
        health_data = health_response.json()
        print(f"  MCP Server: {health_data.get('mcp_server', 'unknown')}")
        print(f"  Database: {health_data.get('database', 'unknown')}")

        if health_data.get('status') != 'healthy':
            print("  ✗ System is not healthy, aborting test")
            return

        # Step 3: Test chat endpoint
        print("\n[3/3] Testing chat endpoint...")

        headers = {"Content-Type": "application/json"}
        if jwt_token:
            headers["Authorization"] = f"Bearer {jwt_token}"
        else:
            print("  ⚠️  No JWT token - this will likely fail with 401 Unauthorized")

        chat_request = {
            "message": "List all my tasks"
        }

        print(f"  Sending message: '{chat_request['message']}'")
        print("  Waiting for response (streaming)...")

        try:
            async with client.stream(
                "POST",
                "http://localhost:8000/api/chatkit/chat",
                headers=headers,
                json=chat_request
            ) as response:
                print(f"  Response Status: {response.status_code}")

                if response.status_code == 401:
                    print("  ✗ Authentication required (401 Unauthorized)")
                    print("\n  To test properly:")
                    print("  1. Start the frontend: cd frontend && npm run dev")
                    print("  2. Login at http://localhost:3000")
                    print("  3. Get your JWT token from /api/auth/get-token")
                    print("  4. Update this script with your token")
                    return

                if response.status_code != 200:
                    error_text = await response.aread()
                    print(f"  ✗ Error: {error_text.decode()}")
                    return

                print("\n  Streaming events:")
                print("  " + "-" * 56)

                event_count = 0
                async for line in response.aiter_lines():
                    if line.strip():
                        if line.startswith("event:"):
                            event_type = line.split(":", 1)[1].strip()
                            print(f"\n  [{event_count}] Event: {event_type}")
                        elif line.startswith("data:"):
                            event_count += 1
                            data = line.split(":", 1)[1].strip()
                            try:
                                data_obj = json.loads(data)
                                # Pretty print the data
                                if isinstance(data_obj, dict):
                                    for key, value in data_obj.items():
                                        if isinstance(value, str) and len(value) > 60:
                                            print(f"      {key}: {value[:60]}...")
                                        else:
                                            print(f"      {key}: {value}")
                            except:
                                print(f"      {data[:100]}...")

                print("  " + "-" * 56)
                print(f"\n  ✓ Received {event_count} events")

        except httpx.TimeoutException:
            print("  ✗ Request timed out after 30 seconds")
        except Exception as e:
            print(f"  ✗ Error: {e}")
            import traceback
            traceback.print_exc()


async def test_with_mock_auth():
    """Test with a mock JWT token for the known user."""
    print("\n" + "=" * 60)
    print("Testing with Mock Authentication")
    print("=" * 60)
    print("\nNote: This is a simplified test without full auth.")
    print("For production testing, use proper JWT from frontend.\n")

    # This would need to be a real JWT token
    # For now, just show what the request would look like
    print("Example curl command to test with a real JWT token:")
    print("")
    print('curl -X POST http://localhost:8000/api/chatkit/chat \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -H "Authorization: Bearer YOUR_JWT_TOKEN" \\')
    print('  -d \'{"message": "List all my tasks"}\'')


if __name__ == "__main__":
    print("\n🔍 Starting ChatKit Chat Endpoint Test\n")

    try:
        asyncio.run(test_chat_endpoint())
        asyncio.run(test_with_mock_auth())
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user")

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60 + "\n")
