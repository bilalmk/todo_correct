#!/usr/bin/env python3
"""Test that empty strings are handled correctly for datetime fields."""

import sys
sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/mcp_server/src')

from todo_mcp.models.inputs import AddTaskInput
from uuid import uuid4
import json

# Test case that simulates what the AI is sending
test_data = {
    "user_id": str(uuid4()),
    "title": "Submit quarterly report",
    "priority": "high",
    "due_date": "2026-01-20T14:00:00Z",
    "reminder_at": ""  # ← Empty string (this was causing the error)
}

print("Testing AddTaskInput with empty string for reminder_at...")
print(f"Input: {json.dumps(test_data, indent=2)}\n")

try:
    task_input = AddTaskInput(**test_data)
    print("✅ SUCCESS! Empty string converted to None")
    print(f"   Parsed data:")
    print(f"     - title: {task_input.title}")
    print(f"     - priority: {task_input.priority}")
    print(f"     - due_date: {task_input.due_date}")
    print(f"     - reminder_at: {task_input.reminder_at} (type: {type(task_input.reminder_at)})")
except Exception as e:
    print(f"❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)}")
