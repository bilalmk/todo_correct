#!/bin/bash

# Test ChatKit chat endpoint

# Get JWT token for user
USER_ID="bded475f-c2e8-4fd8-b616-c260f18d550b"

# Generate a simple JWT token (this is mock - normally you'd get from auth)
# For testing, we'll send a chat request directly

echo "Testing ChatKit chat endpoint..."
echo ""

# Test 1: Health check
echo "[1/2] Health check..."
curl -s http://localhost:8000/api/chatkit/health | python3 -m json.tool
echo ""

# Test 2: Chat request (this will need proper auth, but let's try)
echo "[2/2] Testing chat endpoint (needs auth)..."
echo "To test chat, you need a valid JWT token from the frontend."
echo "Visit: http://localhost:3000 and use the /get-token endpoint"
