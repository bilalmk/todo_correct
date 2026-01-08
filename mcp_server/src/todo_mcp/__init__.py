"""
Todo MCP Server

A Model Context Protocol (MCP) server that exposes 5 stateless tools for AI chatbot task management:
- todo_add_task: Create new tasks
- todo_list_tasks: Retrieve tasks with optional status filter
- todo_complete_task: Mark tasks as completed
- todo_delete_task: Soft delete tasks
- todo_update_task: Update task title/description

All operations enforce user isolation and persist immediately to PostgreSQL database.
"""

import sys
from pathlib import Path

# Add backend to Python path for model imports
# This allows us to import Task and User models from backend/src/models/
# Use absolute path to avoid relative path issues
backend_src_path = Path("/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend/src")
if backend_src_path.exists() and str(backend_src_path) not in sys.path:
    sys.path.insert(0, str(backend_src_path))

__version__ = "0.1.0"
