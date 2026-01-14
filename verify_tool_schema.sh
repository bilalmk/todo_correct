#!/bin/bash
# Verify that MCP tools expose advanced fields

echo "=== Verifying MCP Tool Schema ==="
echo ""

# Step 1: Initialize MCP session
echo "1. Initializing MCP session..."
INIT_RESPONSE=$(curl -s -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{"protocolVersion":"0.1.0","capabilities":{},"clientInfo":{"name":"test","version":"1.0"}}}')

if echo "$INIT_RESPONSE" | grep -q '"result"'; then
  echo "✅ MCP session initialized"
else
  echo "❌ Failed to initialize MCP session"
  echo "$INIT_RESPONSE"
  exit 1
fi

echo ""

# Step 2: List tools and check add_task schema
echo "2. Checking todo_add_task tool schema..."
TOOLS_RESPONSE=$(curl -s -X POST http://localhost:8001/mcp \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","id":2,"method":"tools/list"}')

# Extract property keys from add_task tool
PROPERTIES=$(echo "$TOOLS_RESPONSE" | python3 -c "
import json, sys
data = json.load(sys.stdin)
tools = data.get('result', {}).get('tools', [])
add_task = next((t for t in tools if t['name'] == 'todo_add_task'), None)
if add_task:
    props = list(add_task['inputSchema']['properties'].keys())
    print(','.join(props))
else:
    print('NOT_FOUND')
" 2>/dev/null)

if [ "$PROPERTIES" = "NOT_FOUND" ]; then
  echo "❌ todo_add_task tool not found"
  exit 1
fi

echo "   Available properties: $PROPERTIES"
echo ""

# Check for required fields
echo "3. Verifying advanced fields presence..."

REQUIRED_FIELDS=("priority" "due_date" "reminder_at" "recurrence_pattern" "recurrence_config")
ALL_PRESENT=true

for field in "${REQUIRED_FIELDS[@]}"; do
  if echo "$PROPERTIES" | grep -q "$field"; then
    echo "   ✅ $field"
  else
    echo "   ❌ $field - MISSING!"
    ALL_PRESENT=false
  fi
done

echo ""

if [ "$ALL_PRESENT" = true ]; then
  echo "🎉 SUCCESS! All advanced fields are exposed in the tool schema."
  echo ""
  echo "The AI can now:"
  echo "  - Extract priority from keywords (urgent → high)"
  echo "  - Parse due dates from natural language (tomorrow, January 31st)"
  echo "  - Set reminders (remind me 1 hour before)"
  echo "  - Detect recurrence patterns (every day, weekly)"
  echo ""
  echo "Try it out with:"
  echo '  "Finish the presentation by tomorrow at 5pm, it'"'"'s urgent"'
else
  echo "⚠️  WARNING: Some advanced fields are missing!"
  echo "The natural language parsing may not work correctly."
  echo ""
  echo "Troubleshooting:"
  echo "  1. Check that tools_registry.py has been updated"
  echo "  2. Restart the MCP server"
  echo "  3. Run this script again to verify"
fi

echo ""
echo "=== Verification Complete ==="
