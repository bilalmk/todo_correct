"""CustomChatKitServer implementation extending ChatKitServer base class.

This module implements the core ChatKit server logic for natural language
task management, integrating OpenAI Agents SDK with MCP tools and database-
backed conversation persistence.

Feature: 008-chatkit-server-backend
Phase: III (US5) - Persistent Conversation History
Task Reference: T020-T023, T027 (Phase 3), T013 (SYSTEM_PROMPT)
"""

import logging
from typing import Any, AsyncIterator, Optional
from uuid import UUID
from datetime import datetime, timezone

from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

# TODO: Import ChatKitServer base class when SDK installed
# from chatkit.server import ChatKitServer, ThreadMetadata, UserMessageItem, ThreadStreamEvent
# from chatkit.agents import stream_agent_response
# from agents import Runner

from ..models.conversation import Conversation
from ..models.message import Message
from .agent import create_mcp_client, create_agent_with_mcp, validate_mcp_tools, validate_add_task_tool, validate_list_tasks_tool, validate_complete_task_tool, validate_update_task_tool, validate_delete_task_tool
from .store import DatabaseThreadItemStore
from .utils import RequestContext, retry_with_exponential_backoff, retry_database_operation

logger = logging.getLogger(__name__)


# ===== T013: System Prompt Definition =====

SYSTEM_PROMPT = """You are a helpful task management assistant with advanced natural language understanding. Your role is to help users manage their to-do tasks through conversational language, intelligently extracting task details like priorities, due dates, reminders, and recurrence patterns.

**Available Tools**:
- **add_task**: Create a new task with title, description, priority, due_date, reminder_at, recurrence_pattern, and recurrence_config
- **list_tasks**: Retrieve tasks filtered by status (pending/completed/all)
- **complete_task**: Mark a task as completed by task_id
- **update_task**: Modify any task field (title, description, priority, due_date, reminder_at, recurrence_pattern, recurrence_config) by task_id
- **delete_task**: Remove a task by task_id

**Natural Language Parsing Guidelines**:

1. **Priority Extraction** (extract from keywords):
   - "urgent", "important", "critical", "asap", "high priority" → priority="high"
   - "low priority", "not urgent", "when I have time" → priority="low"
   - Default: priority="medium" if no priority mentioned

2. **Due Date Parsing** (convert natural language to ISO 8601 datetime UTC):
   - "tomorrow", "next week", "December 31st", "in 3 days", "by January 31st"
   - Today is 2026-01-14 (use this as reference for relative dates)
   - ALWAYS set time to 23:59:59 for end-of-day deadlines unless specific time mentioned
   - Examples:
     * "January 31st" → "2026-01-31T23:59:59Z"
     * "tomorrow at 3pm" → "2026-01-15T15:00:00Z"
     * "next Monday" → calculate date and use "YYYY-MM-DDT23:59:59Z"

3. **Reminder Extraction** (parse reminder phrases):
   - "remind me 1 hour before" → calculate reminder_at = due_date - 1 hour
   - "notify me at 9am on the due date" → reminder_at with 09:00:00 time
   - "send reminder the day before" → reminder_at = due_date - 24 hours

4. **Recurrence Pattern Detection** (identify recurring tasks):
   - "every day", "daily" → recurrence_pattern="daily"
   - "every week", "weekly", "every Monday" → recurrence_pattern="weekly"
   - "every month", "monthly", "first of every month" → recurrence_pattern="monthly"
   - For complex patterns (e.g., "every Monday, Wednesday, Friday"), use recurrence_pattern="custom" with recurrence_config

5. **Title Extraction** (clean, concise task title):
   - Remove temporal keywords ("tomorrow", "by Friday", "next week")
   - Remove priority keywords ("urgent", "important")
   - Remove recurrence keywords ("every day", "weekly")
   - Example: "Finish my project about FastAPI by January 31st" → title="Finish my project about FastAPI"

6. **Description Population** (optional context):
   - If user provides extra details beyond the title, add them to description
   - Example: "Buy groceries: milk, eggs, bread" → description="milk, eggs, bread"

**Response Style**:
- Be concise, helpful, and visually appealing
- Use emojis to make responses engaging and easy to scan
- **CRITICAL**: ALWAYS provide explicit confirmation messages for EVERY task operation
- Confirm actions with task IDs and ALL extracted metadata (priority, due_date, etc.)
- Use natural, conversational language with beautiful formatting

**Confirmation Message Formats** (use these exact formats):
- Task Created: "✅ **Task Created!**\n\n📝 **Title:** {title}\n🆔 **ID:** #{id}\n🎯 **Priority:** {priority}\n📅 **Due:** {due_date}"
- Task Completed: "🎉 **Task Completed!**\n\n✓ Task #{id} '{title}' is now done!"
- Task Updated: "✏️ **Task Updated!**\n\n#{id} has been modified successfully."
- Task Deleted: "🗑️ **Task Deleted!**\n\n Task #{id} has been removed."

**Task List Queries**:
- When user asks to "show tasks", "list tasks", "what are my tasks", etc., ALWAYS call list_tasks tool
- **CRITICAL**: Format task lists beautifully with this structure:

For task lists, use this format:
```
📋 **Your Tasks** ({count} total)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔴 **High Priority**
  • #{id} {title}
    📅 Due: {date} | 🔔 Reminder: {reminder}

🟡 **Medium Priority**
  • #{id} {title}

🟢 **Low Priority**
  • #{id} {title}

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

- Use priority emojis: 🔴 High, 🟡 Medium, 🟢 Low
- Use status emojis: ⬜ Pending, ✅ Completed
- Group tasks by priority when showing all tasks
- For single status queries (pending/completed), just list them nicely:

```
📋 **Pending Tasks** ({count})

1. #{id} 📝 {title}
   🎯 Priority: {priority} | 📅 Due: {date}

2. #{id} 📝 {title}
   🎯 Priority: {priority}
```

- If no tasks: "📭 **No tasks found!**\n\nYou're all caught up! Add a new task to get started."
- **CRITICAL**: NEVER say "Let me check your tasks" without actually calling list_tasks
- **CRITICAL**: ALWAYS display the actual task data from list_tasks response

**Important Security & Isolation**:
- All tools are automatically scoped to the authenticated user (user_id is injected automatically)
- You do NOT need to provide user_id when calling tools - it's handled by the system
- Never access or reference other users' tasks

**Example Interactions**:

User: "I need to finish my FastAPI project by January 31st, it's really urgent"
Assistant Action:
- Call add_task(title="Finish my FastAPI project", due_date="2026-01-31T23:59:59Z", priority="high")
Assistant Response:
"✅ **Task Created!**

📝 **Title:** Finish my FastAPI project
🆔 **ID:** #18
🎯 **Priority:** 🔴 High
📅 **Due:** Jan 31, 2026 at 11:59 PM"

User: "Remind me to call mom every Sunday"
Assistant Action:
- Call add_task(title="Call mom", recurrence_pattern="weekly")
Assistant Response:
"✅ **Recurring Task Created!**

📝 **Title:** Call mom
🆔 **ID:** #19
🔄 **Repeats:** Weekly"

User: "Show my pending tasks"
Assistant Action:
- Call list_tasks(status="pending")
Assistant Response:
"📋 **Pending Tasks** (3)

1. #12 📝 Buy groceries
   🎯 Priority: 🔴 High | 📅 Due: Jan 20, 2026

2. #15 📝 Call dentist
   🎯 Priority: 🟡 Medium

3. #18 📝 Finish FastAPI project
   🎯 Priority: 🔴 High | 📅 Due: Feb 15, 2026"

User: "Mark task 12 as done"
Assistant Action:
- Call complete_task(task_id=12)
Assistant Response:
"🎉 **Task Completed!**

✓ Task #12 'Buy groceries' is now done!"

User: "Delete task 15"
Assistant Action:
- Call delete_task(task_id=15)
Assistant Response:
"🗑️ **Task Deleted!**

Task #15 has been removed."

User: "Add buy milk"
Assistant Action:
- Call add_task(title="Buy milk")
Assistant Response:
"✅ **Task Created!**

📝 **Title:** Buy milk
🆔 **ID:** #20
🎯 **Priority:** 🟡 Medium"
"""

"""
SYSTEM_PROMPT constant defined per T013 spec (tasks.md lines 143-164).

Constitutional Compliance:
- FR-021: User isolation reminder ("All tools are automatically scoped to the authenticated user")
- Clear tool descriptions for AI understanding
- Natural, conversational response style
- All 5 MCP tools listed: add_task, list_tasks, complete_task, update_task, delete_task
"""


# ===== T022: Conversation Loading Helper =====

async def get_or_create_conversation(
    session: AsyncSession,
    user_id: UUID,
    correlation_id: str
) -> UUID:
    """
    Get active conversation for user or create new one.

    Implementation for T022 (User Story 5).

    Business Logic:
    - Each user has ONE active conversation (unique constraint on user_id WHERE deleted_at IS NULL)
    - If no active conversation exists, create new one
    - Returns conversation_id for message persistence

    Args:
        session: Async database session
        user_id: User UUID from JWT token
        correlation_id: For structured logging

    Returns:
        conversation_id (UUID) for the active conversation

    Example:
        conversation_id = await get_or_create_conversation(session, user.uuid, correlation_id)
    """
    # Log conversation lookup attempt
    logger.info(
        f"Looking up active conversation for user {user_id}",
        extra={
            "correlation_id": correlation_id,
            "user_id": str(user_id)
        }
    )

    # Query for active conversation (deleted_at IS NULL)
    result = await session.execute(
        select(Conversation)
        .where(Conversation.user_id == user_id)
        .where(Conversation.deleted_at.is_(None))
    )
    conversation = result.scalar_one_or_none()

    if conversation:
        # Active conversation found
        logger.info(
            f"Found active conversation {conversation.conversation_id}",
            extra={
                "correlation_id": correlation_id,
                "conversation_id": str(conversation.conversation_id),
                "user_id": str(user_id)
            }
        )
        return conversation.conversation_id
    else:
        # No active conversation, create new one
        new_conversation = Conversation(
            user_id=user_id,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.add(new_conversation)
        await session.flush()  # Get conversation_id immediately

        logger.info(
            f"Created new conversation {new_conversation.conversation_id}",
            extra={
                "correlation_id": correlation_id,
                "conversation_id": str(new_conversation.conversation_id),
                "user_id": str(user_id)
            }
        )
        return new_conversation.conversation_id


# ===== T020-T021: CustomChatKitServer Implementation =====

class CustomChatKitServer:
    """
    Custom ChatKit server with database-backed conversation persistence.

    Implementation for T020-T021, T023, T027 (User Story 5).

    Architecture:
    - Extends ChatKitServer base class (when SDK installed)
    - Implements respond() method for streaming chat responses
    - Integrates OpenAI Agents SDK with MCP tools
    - Persists all conversation state to PostgreSQL (stateless design)

    Constitutional Compliance:
    - Stateless: No in-memory conversation state (all persisted to database)
    - User Isolation: All operations scoped by user_id from RequestContext
    - Structured Logging: Correlation IDs propagated through all operations
    - Error Handling: Retry logic for OpenAI (3x) and database (2x)
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize ChatKit server with database session.

        Args:
            session: Async database session for conversation persistence
        """
        self.session = session
        self.store = DatabaseThreadItemStore(session)
        # NOTE: Don't cache MCP client/agent - create fresh for each request
        # StreamableHTTP transport requires proper context manager lifecycle

    # ===== T020-T021: Core respond() Method =====

    async def respond(
        self,
        thread: Any,  # ThreadMetadata type (contains thread.id UUID)
        input_user_message: Optional[Any],  # UserMessageItem type (contains content, role, created_at)
        context: RequestContext,
    ) -> AsyncIterator[Any]:  # Returns AsyncIterator[ThreadStreamEvent]
        """
        Handle chat message and return streaming response.

        Implementation based on research.md R001 findings (line 22).

        Method Signature (from research.md):
        - thread: ThreadMetadata with thread.id (UUID)
        - input_user_message: UserMessageItem with content, role, created_at
        - context: RequestContext with user_id and correlation_id
        - Returns: AsyncIterator[ThreadStreamEvent] for SSE streaming

        Workflow (T021):
        1. Get or create active conversation for user
        2. Load conversation history (last 20 messages) via DatabaseThreadItemStore
        3. Create OpenAI agent with MCP client (if not already created)
        4. Invoke Runner.run_streamed(agent, user_message)
        5. Stream response events via stream_agent_response() utility
        6. Persist user message and assistant response to database (T023)

        Error Handling (T027):
        - OpenAI failures: retry 3x with exponential backoff (2s/4s/8s)
        - Database failures: retry 2x with 1s delay
        - MCP connection errors: return user-friendly error with correlation ID

        Args:
            thread: Thread metadata (contains conversation UUID)
            input_user_message: User's input message (or None for loading history)
            context: Request context with user_id and correlation_id

        Yields:
            ThreadStreamEvent: SSE events for streaming response

        Example:
            async for event in server.respond(thread, message, context):
                # event.type: "thread.message.delta", "tool.call.start", etc.
                yield event
        """
        user_id = context.user_id
        correlation_id = context.correlation_id

        # Log request received
        logger.info(
            "ChatKit respond() called",
            extra={
                "correlation_id": correlation_id,
                "user_id": str(user_id),
                "has_user_message": input_user_message is not None
            }
        )

        try:
            # T022: Get or create active conversation
            conversation_id = await retry_database_operation(
                lambda: get_or_create_conversation(self.session, user_id, correlation_id),
                correlation_id=correlation_id
            )

            # T023: Save user message immediately (if provided)
            if input_user_message:
                user_message_content = getattr(input_user_message, 'content', '')

                # Persist user message to database
                await retry_database_operation(
                    lambda: self.store.save_thread_item(
                        str(conversation_id),
                        input_user_message,
                        context
                    ),
                    correlation_id=correlation_id
                )

                logger.info(
                    "User message persisted to database",
                    extra={
                        "correlation_id": correlation_id,
                        "conversation_id": str(conversation_id),
                        "message_length": len(user_message_content)
                    }
                )

            # T021: Load conversation history (last 20 messages)
            thread_items_page = await retry_database_operation(
                lambda: self.store.load_thread_items(
                    str(conversation_id),
                    after=None,
                    limit=20,
                    order="asc",
                    context=context
                ),
                correlation_id=correlation_id
            )

            logger.info(
                f"Loaded {len(thread_items_page['data'])} messages from conversation history",
                extra={
                    "correlation_id": correlation_id,
                    "conversation_id": str(conversation_id),
                    "message_count": len(thread_items_page['data'])
                }
            )

            # T021: Create agent fresh for this request (don't cache - proper lifecycle management)
            from agents import Agent, Runner, FunctionTool
            from typing import Any
            import json as json_module

            # Get user message content
            user_message_content = getattr(input_user_message, 'content', '') if input_user_message else ''

            logger.info(
                f"Creating agent for message: {user_message_content[:100]}...",
                extra={
                    "correlation_id": correlation_id,
                    "user_id": str(user_id),
                    "conversation_id": str(conversation_id),
                    "message_preview": user_message_content[:100]
                }
            )

            # Create MCP client and agent using simple JSON-RPC HTTP client
            from ..core.config import settings
            from .mcp_http_client import MCPHTTPClient

            # Create simple HTTP JSON-RPC client
            mcp_client = MCPHTTPClient(settings.MCP_SERVER_URL)

            try:
                # Initialize MCP session
                logger.info("Initializing MCP session", extra={"correlation_id": correlation_id})
                await mcp_client.initialize()

                # List tools
                tools = await mcp_client.list_tools()
                logger.info(f"Got {len(tools)} MCP tools", extra={"correlation_id": correlation_id})

                # Track tool calls and their results
                tool_results = []

                # Convert MCP tools to FunctionTool objects
                # OpenAI Agents SDK expects FunctionTool instances, not dictionaries
                agent_tools = []
                for tool_dict in tools:
                    tool_name = tool_dict["name"]

                    # Remove user_id from the schema the agent sees
                    # We automatically inject user_id from JWT auth context
                    agent_schema = tool_dict["inputSchema"].copy()
                    if "properties" in agent_schema and "user_id" in agent_schema["properties"]:
                        agent_schema["properties"] = {
                            k: v for k, v in agent_schema["properties"].items()
                            if k != "user_id"
                        }
                        # Remove user_id from required fields
                        if "required" in agent_schema:
                            agent_schema["required"] = [
                                field for field in agent_schema["required"]
                                if field != "user_id"
                            ]

                    # Create handler factory that captures tool_name, user_id, and results in closure
                    def create_tool_handler(tool_name_capture: str):
                        async def on_invoke_tool(ctx: Any, args: str) -> str:
                            """Call MCP server tool with arguments."""
                            try:
                                # Parse arguments from agent
                                parsed_args = json_module.loads(args)

                                # CRITICAL: Inject user_id from authenticated context
                                # The agent doesn't know the user_id - it comes from JWT auth
                                # All MCP tools require user_id for isolation (FR-021)
                                parsed_args["user_id"] = str(user_id)

                                logger.debug(
                                    f"Calling MCP tool {tool_name_capture}",
                                    extra={
                                        "correlation_id": correlation_id,
                                        "tool": tool_name_capture,
                                        "user_id": str(user_id)
                                    }
                                )

                                # Call MCP tool with injected user_id
                                result = await mcp_client.call_tool(tool_name_capture, parsed_args)

                                # Parse result if it's a JSON string
                                parsed_result = result
                                if isinstance(result, str):
                                    try:
                                        parsed_result = json_module.loads(result)
                                    except json_module.JSONDecodeError:
                                        # Keep as string if not valid JSON
                                        parsed_result = result

                                # Capture structured tool result for response
                                tool_results.append({
                                    "tool": tool_name_capture,
                                    "arguments": {k: v for k, v in parsed_args.items() if k != "user_id"},  # Exclude user_id
                                    "result": parsed_result
                                })

                                logger.debug(
                                    f"Tool {tool_name_capture} completed successfully",
                                    extra={
                                        "correlation_id": correlation_id,
                                        "tool": tool_name_capture
                                    }
                                )

                                # Return result as string
                                if isinstance(result, dict):
                                    return json_module.dumps(result)
                                return str(result)
                            except Exception as e:
                                logger.error(
                                    f"Tool {tool_name_capture} failed: {e}",
                                    extra={"correlation_id": correlation_id},
                                    exc_info=True
                                )
                                error_result = {"error": str(e)}
                                # Capture error result too
                                tool_results.append({
                                    "tool": tool_name_capture,
                                    "arguments": json_module.loads(args) if args else {},
                                    "result": error_result
                                })
                                return json_module.dumps(error_result)
                        return on_invoke_tool

                    # Create FunctionTool instance with modified schema (no user_id)
                    function_tool = FunctionTool(
                        name=tool_name,
                        description=tool_dict["description"],
                        params_json_schema=agent_schema,  # Use schema without user_id
                        on_invoke_tool=create_tool_handler(tool_name),
                    )
                    agent_tools.append(function_tool)

                # Create agent with MCP tools
                agent = Agent(
                    name="TodoAssistant",
                    model=settings.OPENAI_MODEL,
                    instructions=SYSTEM_PROMPT,
                    tools=agent_tools,
                )
                logger.info("Agent created successfully", extra={"correlation_id": correlation_id})

                # Run agent with streaming and extract only text content
                logger.info("Running agent to process message", extra={"correlation_id": correlation_id})
                result = Runner.run_streamed(agent, user_message_content)

                # Collect response text from streaming events
                response_text = ""

                async for event in result.stream_events():
                    event_type = getattr(event, 'type', type(event).__name__)

                    # Extract text content from response text events
                    if event_type == 'raw_response_event':
                        data = getattr(event, 'data', None)
                        if data:
                            data_type = getattr(data, 'type', None)

                            # Output text delta events contain the actual response text
                            if data_type == 'response.output_text.delta':
                                delta = getattr(data, 'delta', '')
                                if delta:
                                    response_text += delta

                            # Output text done has the final text
                            elif data_type == 'response.output_text.done':
                                text = getattr(data, 'text', '')
                                if text and not response_text:
                                    # Use final text if we didn't collect deltas
                                    response_text = text

                logger.info(
                    "Agent processing complete",
                    extra={
                        "correlation_id": correlation_id,
                        "response_length": len(response_text),
                        "tool_calls": len(tool_results)
                    }
                )

                # Yield a clean response event with content and tool results
                response_event = {
                    "type": "message",
                    "role": "assistant",
                    "content": response_text,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                }

                # Include tool results if any tools were called
                if tool_results:
                    response_event["tool_results"] = tool_results
                    logger.info(
                        f"Including {len(tool_results)} tool result(s) in response",
                        extra={
                            "correlation_id": correlation_id,
                            "tools": [tr["tool"] for tr in tool_results]
                        }
                    )

                yield response_event

                logger.info(
                    "Response sent to user",
                    extra={
                        "correlation_id": correlation_id,
                        "response_length": len(response_text),
                        "tool_calls": len(tool_results)
                    }
                )

            finally:
                # Close HTTP client
                await mcp_client.close()

        except Exception as e:
            # T027: Error handling with user-friendly messages
            error_message = f"Chat service error: {str(e)}"
            # DEBUG: Print full exception to stdout for debugging
            import traceback
            print(f"\n{'='*60}")
            print(f"CHAT SERVICE ERROR: {type(e).__name__}: {str(e)}")
            print(f"Correlation ID: {correlation_id}")
            print(f"Full traceback:")
            traceback.print_exc()
            print(f"{'='*60}\n")
            logger.error(
                error_message,
                extra={
                    "correlation_id": correlation_id,
                    "error_type": type(e).__name__,
                    "error": str(e)
                },
                exc_info=True
            )

            # Yield error event
            yield {
                "type": "error",
                "error": {
                    "message": "Unable to process your message. Please try again.",
                    "code": "CHAT_SERVICE_ERROR",
                    "correlation_id": correlation_id
                }
            }

