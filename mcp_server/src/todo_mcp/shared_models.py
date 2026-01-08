"""
Shared models imported from backend.

This module handles the complex import path setup needed to import Task model
from the backend without triggering circular import issues.
"""

import sys
from pathlib import Path

# Add both backend root and backend/src to path
backend_root = Path("/mnt/e/giaic/learning/spec_kit_plus/todo_correct/backend")
backend_src = backend_root / "src"

if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))
if str(backend_src) not in sys.path:
    sys.path.insert(0, str(backend_src))

# Now import Task model - the backend's internal imports should work
from src.models.task import Task

__all__ = ["Task"]
