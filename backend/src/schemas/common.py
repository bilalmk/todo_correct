"""Common enums and base schemas used across the API."""

from enum import Enum
from pydantic import BaseModel, Field


class PriorityEnum(str, Enum):
    """Task priority levels."""

    low = "low"
    medium = "medium"
    high = "high"


class RecurrencePatternEnum(str, Enum):
    """Recurrence patterns for recurring tasks."""

    daily = "daily"
    weekly = "weekly"
    monthly = "monthly"
    custom = "custom"


class ErrorResponse(BaseModel):
    """Standard error response format."""

    error: str = Field(..., description="Human-readable error message")
    code: str = Field(..., description="Machine-readable error code")
    status: int = Field(..., description="HTTP status code")
    request_id: str = Field(..., description="Request ID for tracing")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "Task not found",
                "code": "TASK_NOT_FOUND",
                "status": 404,
                "request_id": "req_abc123xyz",
            }
        }
    }
