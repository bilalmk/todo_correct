#!/bin/bash

# Simple chatbot test script
# Tests the backend ChatKit endpoint directly

echo "=============================="
echo "Testing Backend ChatKit API"
echo "=============================="
echo ""

# You need to replace this with a real JWT token from your session
# To get it:
# 1. Log in to the app in browser
# 2. Open DevTools > Application > Cookies
# 3. Copy the 'better-auth.session_token' value
# 4. Paste it below

JWT_TOKEN="YOUR_JWT_TOKEN_HERE"

if [ "$JWT_TOKEN" == "YOUR_JWT_TOKEN_HERE" ]; then
    echo "❌ ERROR: Please edit this script and add your JWT token"
    echo ""
    echo "To get your JWT:"
    echo "1. Log in to the app"
    echo "2. Press F12 (DevTools)"
    echo "3. Go to Application > Cookies"
    echo "4. Copy 'better-auth.session_token' value"
    echo "5. Paste it in this script as JWT_TOKEN"
    exit 1
fi

# Test the ChatKit endpoint
echo "Sending test message: 'Add a task to test chatbot'"
echo ""

curl -N -H "Authorization: Bearer $JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -H "X-Correlation-ID: test-$(uuidgen)" \
     -d '{"message":"Add a task to test chatbot"}' \
     http://localhost:8000/api/chatkit/chat

echo ""
echo ""
echo "✅ If you saw streaming events above, the backend works!"
echo "❌ If you got an error, check the backend logs"
