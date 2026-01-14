#!/usr/bin/env python3
"""Test if Pydantic can parse datetime strings in AddTaskInput."""

import sys
sys.path.insert(0, '/mnt/e/giaic/learning/spec_kit_plus/todo_correct/mcp_server/src')

from todo_mcp.models.inputs import AddTaskInput
from uuid import uuid4
import json

# Test cases
test_cases = [
    {
        "name": "With string datetime",
        "data": {
            "user_id": str(uuid4()),
            "title": "Submit quarterly report",
            "priority": "high",
            "due_date": "2026-01-20T14:00:00Z"
        }
    },
    {
        "name": "Without advanced fields",
        "data": {
            "user_id": str(uuid4()),
            "title": "Test task"
        }
    }
]

for test in test_cases:
    print(f"\n{'='*60}")
    print(f"Test: {test['name']}")
    print(f"Input: {json.dumps(test['data'], indent=2)}")
    print(f"{'='*60}")

    try:
        # Try to create AddTaskInput instance
        task_input = AddTaskInput(**test['data'])
        print(f"✅ SUCCESS!")
        print(f"   Parsed data:")
        print(f"     - title: {task_input.title}")
        print(f"     - priority: {task_input.priority}")
        print(f"     - due_date: {task_input.due_date}")
        print(f"     - due_date type: {type(task_input.due_date)}")

    except Exception as e:
        print(f"❌ ERROR: {type(e).__name__}")
        print(f"   {str(e)}")
