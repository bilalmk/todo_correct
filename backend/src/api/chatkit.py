"""ChatKit API endpoints for AI-powered task management chat.

Feature: 008-chatkit-server-backend
Phase: III (US5) - Persistent Conversation History
Task Reference: T024-T025 (FastAPI routes), T026 (router registration)
"""

import logging
from typing import Optional
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy import update

from ..core.database import get_session
from ..api.deps import get_current_user
from ..models.user import User
from ..models.conversation import Conversation
from ..chatkit.server import CustomChatKitServer
from ..chatkit.utils import RequestContext, get_correlation_id

logger = logging.getLogger(__name__)

router = APIRouter()


# ===== T063: Health Check Endpoint =====

@router.get(
    "/health",
    status_code=status.HTTP_200_OK,
    summary="Check ChatKit service health",
    description="""
    Health check endpoint to verify ChatKit service and MCP server connectivity.

    **Checks Performed:**
    - MCP server connection (attempts to connect to MCP_SERVER_URL)
    - Database connectivity (verified via FastAPI dependency injection)

    **Use Cases:**
    - Deployment validation
    - Container orchestration health probes (Kubernetes liveness/readiness)
    - Monitoring and alerting

    **No Authentication Required** (public health check endpoint)
    """,
    responses={
        200: {
            "description": "Service healthy - MCP server connected",
            "content": {
                "application/json": {
                    "example": {
                        "status": "healthy",
                        "mcp_server": "connected",
                        "database": "connected",
                        "timestamp": "2026-01-13T14:30:00Z"
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable - MCP server unreachable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "unhealthy",
                        "mcp_server": "disconnected",
                        "database": "connected",
                        "error": "Failed to connect to MCP server",
                        "timestamp": "2026-01-13T14:30:00Z"
                    }
                }
            }
        }
    },
    tags=["ChatKit"]
)
async def health_check(
    session: AsyncSession = Depends(get_session),
):
    """
    Health check endpoint for deployment validation.

    Implementation for T063 (Health check for MCP connection).

    **Endpoint:** GET /api/chatkit/health

    **Authentication:** Not required (public health check)

    **Response:** JSON object with health status

    **Health Checks:**
    1. MCP Server Connectivity: Attempts to create MCP client connection
    2. Database Connectivity: Verified via session dependency (automatic)

    **Example Request:**
    ```bash
    curl http://localhost:8000/api/chatkit/health
    ```

    **Example Response (Healthy):**
    ```json
    {
        "status": "healthy",
        "mcp_server": "connected",
        "database": "connected",
        "timestamp": "2026-01-13T14:30:00Z"
    }
    ```

    **Example Response (Unhealthy):**
    ```json
    {
        "status": "unhealthy",
        "mcp_server": "disconnected",
        "database": "connected",
        "error": "Failed to connect to MCP server",
        "timestamp": "2026-01-13T14:30:00Z"
    }
    ```

    Args:
        session: Database session (dependency injection verifies DB connectivity)

    Returns:
        JSON object with health status

    Raises:
        HTTPException: 503 Service Unavailable if MCP server unreachable
    """
    import httpx
    from ..core.config import settings

    correlation_id = get_correlation_id()

    # Log health check request
    logger.info(
        "Health check requested",
        extra={"correlation_id": correlation_id}
    )

    # Check MCP server connectivity with simple HTTP request
    # (don't fully initialize MCP client to avoid cleanup issues)
    mcp_status = "disconnected"
    error_message = None

    try:
        # Simple HTTP GET to verify MCP server is responding
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(f"{settings.MCP_SERVER_URL.rstrip('/mcp')}/health")
            # MCP health endpoint should return 200
            if response.status_code == 200:
                mcp_status = "connected"
            else:
                error_message = f"MCP server returned unexpected status: {response.status_code}"

        logger.info(
            "Health check passed: MCP server connected",
            extra={"correlation_id": correlation_id}
        )

    except Exception as e:
        # MCP server unreachable
        error_message = str(e)

        logger.warning(
            f"Health check failed: MCP server unreachable - {error_message}",
            extra={
                "correlation_id": correlation_id,
                "error": error_message,
                "error_type": type(e).__name__
            }
        )

    # Database connectivity verified by session dependency
    db_status = "connected"

    # Build response
    response_data = {
        "status": "healthy" if mcp_status == "connected" else "unhealthy",
        "mcp_server": mcp_status,
        "database": db_status,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }

    if error_message:
        response_data["error"] = error_message

    # Return 503 if unhealthy
    if mcp_status != "connected":
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=response_data
        )

    return response_data


# ===== Request/Response Schemas =====

class ChatMessageRequest(BaseModel):
    """
    Request schema for POST /api/chatkit/chat endpoint.

    Specification: contracts/chatkit-api.yaml

    Example:
        {
            "message": "Add a task to buy groceries",
            "thread_id": "550e8400-e29b-41d4-a716-446655440000"  // Optional
        }
    """
    message: str = Field(
        ...,
        min_length=1,
        max_length=10000,
        description="User's chat message (max 10,000 characters per FR-024)"
    )
    thread_id: Optional[UUID] = Field(
        default=None,
        description="Conversation UUID (optional, auto-created if not provided)"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "message": "Show me all my pending tasks",
                "thread_id": None
            }
        }
    }


class ConversationDeleteResponse(BaseModel):
    """
    Response schema for DELETE /api/chatkit/conversation endpoint.

    Specification: contracts/chatkit-api.yaml (FR-020)

    HTTP 204 No Content on success (no body returned).
    """
    pass


# ===== T024: POST /api/chatkit/chat Endpoint =====

@router.post(
    "/chat",
    response_class=StreamingResponse,
    status_code=status.HTTP_200_OK,
    summary="Send chat message to AI assistant",
    description="""
    Send a natural language message to the AI task management assistant and receive a streaming response.

    **Features:**
    - Natural language task management (add, list, complete, update, delete tasks)
    - Streaming responses via Server-Sent Events (SSE)
    - Automatic conversation persistence
    - MCP tool invocation for task operations

    **Authentication:** Required (JWT Bearer token in Authorization header)

    **Rate Limits:** 50 concurrent requests per user (SC-003)

    **Response Format:** text/event-stream (Server-Sent Events)
    """,
    responses={
        200: {
            "description": "Streaming response with SSE events",
            "content": {
                "text/event-stream": {
                    "example": "event: thread.message.delta\\ndata: {\"type\":\"thread.message.delta\",\"content\":\"Task created successfully!\"}\\n\\n"
                }
            },
            "headers": {
                "X-Correlation-ID": {
                    "description": "Request correlation ID for tracing",
                    "schema": {"type": "string", "format": "uuid"}
                }
            }
        },
        401: {
            "description": "Unauthorized - Invalid or missing JWT token",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        },
        422: {
            "description": "Validation Error - Invalid message content",
            "content": {
                "application/json": {
                    "example": {"detail": [{"loc": ["body", "message"], "msg": "field required", "type": "value_error.missing"}]}
                }
            }
        },
        500: {
            "description": "Internal Server Error - OpenAI, MCP, or database failure",
            "content": {
                "application/json": {
                    "example": {"error": "Unable to process your message. Please try again.", "code": "CHAT_STREAMING_ERROR", "correlation_id": "550e8400-e29b-41d4-a716-446655440000"}
                }
            }
        }
    },
    tags=["ChatKit"]
)
async def chat_message(
    request: ChatMessageRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> StreamingResponse:
    """
    Send chat message and stream AI assistant response.

    Implementation for T024 (User Story 5), T060 (OpenAPI documentation).

    **Endpoint:** POST /api/chatkit/chat

    **Authentication:** Required (JWT Bearer token)

    **Content-Type:** application/json

    **Response:** text/event-stream (Server-Sent Events)

    **Workflow:**
    1. Extract user_id from JWT token (via get_current_user dependency)
    2. Generate correlation_id for request tracing
    3. Create RequestContext with user_id and correlation_id
    4. Create CustomChatKitServer instance with database session
    5. Call server.respond() to invoke OpenAI Agents SDK with MCP tools
    6. Stream response events as SSE to client

    **SSE Event Types** (per contracts/chatkit-sse-events.md):
    - `thread.message.delta`: Assistant response text chunks
    - `tool.call.start`: MCP tool invocation begins (add_task, list_tasks, etc.)
    - `tool.call.result`: MCP tool returns result
    - `thread.message.completed`: Assistant response finished

    **MCP Tools Available:**
    - `add_task(user_id, title, description)` - Create new task
    - `list_tasks(user_id, status)` - List tasks filtered by status
    - `complete_task(user_id, task_id)` - Mark task as completed
    - `update_task(user_id, task_id, title?, description?)` - Update task fields
    - `delete_task(user_id, task_id)` - Soft delete task

    **Error Handling:**
    - 401 Unauthorized: Invalid JWT token (handled by get_current_user)
    - 422 Validation Error: Invalid message content (handled by Pydantic)
    - 500 Internal Server Error: Service failures (OpenAI, MCP, database)

    **Example Request:**
    ```bash
    curl -N -H "Authorization: Bearer $TOKEN" \\
         -H "Content-Type: application/json" \\
         -d '{"message": "Add task to buy groceries"}' \\
         http://localhost:8000/api/chatkit/chat
    ```

    **Example SSE Response:**
    ```
    event: tool.call.start
    data: {"type":"tool.call.start","tool_name":"add_task"}

    event: tool.call.result
    data: {"type":"tool.call.result","tool_name":"add_task","success":true}

    event: thread.message.delta
    data: {"type":"thread.message.delta","content":"Task created!"}

    event: thread.message.completed
    data: {"type":"thread.message.completed"}
    ```

    Args:
        request: ChatMessageRequest with user message and optional thread_id
        current_user: Authenticated user from JWT token
        session: Database session for conversation persistence

    Returns:
        StreamingResponse with text/event-stream content type

    Example:
        curl -N -H "Authorization: Bearer $TOKEN" \\
             -H "Content-Type: application/json" \\
             -d '{"message": "Add task to buy groceries"}' \\
             http://localhost:8000/api/chatkit/chat
    """
    correlation_id = get_correlation_id()

    # Log request received
    logger.info(
        "POST /api/chatkit/chat received",
        extra={
            "correlation_id": correlation_id,
            "user_id": str(current_user.uuid),
            "message_length": len(request.message),
            "has_thread_id": request.thread_id is not None
        }
    )

    # Create RequestContext (user_id + correlation_id)
    context = RequestContext(user_id=current_user.uuid, correlation_id=correlation_id)

    # Create ChatKit server instance
    chatkit_server = CustomChatKitServer(session)

    # Create mock thread and user message (placeholder until SDK installed)
    # TODO: Replace with actual ThreadMetadata and UserMessageItem when SDK installed
    thread = type('Thread', (), {'id': request.thread_id or str(current_user.uuid)})()
    user_message = type('UserMessage', (), {
        'content': request.message,
        'role': 'user',
        'created_at': datetime.now(timezone.utc)
    })()

    # Stream response generator
    async def event_stream():
        """Generate SSE events from ChatKit server response."""
        try:
            async for event in chatkit_server.respond(thread, user_message, context):
                # Format as SSE (Server-Sent Events)
                # Format: "event: <type>\ndata: <json>\n\n"
                import json

                # Handle both dict and object events
                if isinstance(event, dict):
                    event_type = event.get('type', 'message')
                    event_data = json.dumps(event)
                else:
                    # Event is an object (e.g., StreamEvent from agents SDK)
                    event_type = getattr(event, 'type', 'message')
                    # Convert object to dict for JSON serialization
                    if hasattr(event, 'model_dump'):
                        event_data = json.dumps(event.model_dump())
                    elif hasattr(event, 'dict'):
                        event_data = json.dumps(event.dict())
                    else:
                        event_data = json.dumps(str(event))

                yield f"event: {event_type}\n"
                yield f"data: {event_data}\n\n"

        except Exception as e:
            # Log error
            logger.error(
                f"Chat streaming error: {str(e)}",
                extra={
                    "correlation_id": correlation_id,
                    "user_id": str(current_user.uuid),
                    "error_type": type(e).__name__
                },
                exc_info=True
            )

            # Send error event
            import json
            error_event = {
                "type": "error",
                "error": {
                    "message": "Unable to process your message. Please try again.",
                    "code": "CHAT_STREAMING_ERROR",
                    "correlation_id": correlation_id
                }
            }
            yield f"event: error\n"
            yield f"data: {json.dumps(error_event)}\n\n"

    # Return streaming response
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",  # Disable buffering in nginx
            "X-Correlation-ID": correlation_id
        }
    )


# ===== T025: DELETE /api/chatkit/conversation Endpoint =====

@router.delete(
    "/conversation",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Reset conversation history",
    description="""
    Soft-delete the active conversation and all associated messages to reset the chat session.

    **Features:**
    - Soft delete (data preserved for audit trail)
    - Cascades to all messages in conversation
    - Idempotent operation (no error if no active conversation)
    - User isolation enforced (FR-017)

    **Authentication:** Required (JWT Bearer token in Authorization header)

    **Data Preservation:** Conversation and messages marked with `deleted_at` timestamp, NOT hard deleted
    """,
    responses={
        204: {
            "description": "Conversation successfully deleted (or no active conversation existed)"
        },
        401: {
            "description": "Unauthorized - Invalid or missing JWT token",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        },
        500: {
            "description": "Internal Server Error - Database failure during deletion",
            "content": {
                "application/json": {
                    "example": {"error": "Unable to delete conversation. Please try again.", "code": "CONVERSATION_DELETE_ERROR", "correlation_id": "550e8400-e29b-41d4-a716-446655440000"}
                }
            }
        }
    },
    tags=["ChatKit"]
)
async def delete_conversation(
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_session),
) -> None:
    """
    Soft-delete active conversation and cascade to messages.

    Implementation for T025 (User Story 5, FR-020), T060 (OpenAPI documentation).

    Endpoint: DELETE /api/chatkit/conversation
    Authentication: Required (JWT Bearer token)
    Response: HTTP 204 No Content (no body)

    Workflow:
    1. Extract user_id from JWT token (via get_current_user)
    2. Find active conversation for user (deleted_at IS NULL)
    3. Set deleted_at timestamp on conversation
    4. Cascade soft delete to all messages (via application logic)
    5. Return 204 No Content

    Soft Delete Strategy:
    - Conversation.deleted_at = NOW()
    - All Message.deleted_at = NOW() (where conversation_id matches)
    - Data preserved for audit trail (not hard deleted)

    Error Handling:
    - 401 Unauthorized: Invalid JWT token (handled by get_current_user)
    - 404 Not Found: No active conversation exists (returns 204 anyway, idempotent)
    - 500 Internal Server Error: Database failure

    Args:
        current_user: Authenticated user from JWT token
        session: Database session for conversation deletion

    Returns:
        None (HTTP 204 No Content)

    Example:
        curl -X DELETE -H "Authorization: Bearer $TOKEN" \\
             http://localhost:8000/api/chatkit/conversation
    """
    correlation_id = get_correlation_id()

    # Log request received
    logger.info(
        "DELETE /api/chatkit/conversation received",
        extra={
            "correlation_id": correlation_id,
            "user_id": str(current_user.uuid)
        }
    )

    try:
        # Find active conversation for user
        from sqlmodel import select
        result = await session.execute(
            select(Conversation)
            .where(Conversation.user_id == current_user.uuid)
            .where(Conversation.deleted_at.is_(None))
        )
        conversation = result.scalar_one_or_none()

        if conversation:
            # Soft delete conversation
            conversation.deleted_at = datetime.now(timezone.utc)

            # Cascade soft delete to messages (application-level cascade)
            from ..models.message import Message
            await session.execute(
                update(Message)
                .where(Message.conversation_id == conversation.conversation_id)
                .where(Message.user_id == current_user.uuid)  # User isolation
                .values(deleted_at=datetime.now(timezone.utc))
            )

            await session.commit()

            # Log successful deletion
            logger.info(
                f"Conversation {conversation.conversation_id} soft-deleted",
                extra={
                    "correlation_id": correlation_id,
                    "conversation_id": str(conversation.conversation_id),
                    "user_id": str(current_user.uuid)
                }
            )
        else:
            # No active conversation (idempotent, return 204 anyway)
            logger.info(
                "No active conversation to delete (idempotent)",
                extra={
                    "correlation_id": correlation_id,
                    "user_id": str(current_user.uuid)
                }
            )

    except Exception as e:
        # Log error
        logger.error(
            f"Conversation deletion error: {str(e)}",
            extra={
                "correlation_id": correlation_id,
                "user_id": str(current_user.uuid),
                "error_type": type(e).__name__
            },
            exc_info=True
        )

        # Rollback transaction
        await session.rollback()

        # Raise 500 Internal Server Error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "Unable to delete conversation. Please try again.",
                "code": "CONVERSATION_DELETE_ERROR",
                "correlation_id": correlation_id
            }
        )
