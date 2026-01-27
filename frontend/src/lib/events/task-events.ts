/**
 * Custom event system for real-time task synchronization
 * Feature: 009-chatkit-frontend
 * Task: T005, T085 [Phase 10]
 *
 * Purpose: Enable chatbot-to-dashboard communication via CustomEvent API
 * - Chatbot emits TaskEvent after successful task operations
 * - Dashboard listens for TaskEvent and triggers refreshTasks()
 * - No polling or WebSocket overhead (same-page communication)
 * - T085: Sanitize event data before logging (no PII, truncated content)
 *
 * Architecture Decision (from plan.md):
 * - CustomEvent dispatch is synchronous within JavaScript execution context
 * - No network overhead for same-page component communication
 * - Event listener triggers immediate React state update in dashboard
 */

import { sanitize } from '../logging/sanitize';

/**
 * Task event types
 * Matches MCP tool names for consistency
 */
export type TaskEventType =
  | 'task.created'
  | 'task.updated'
  | 'task.completed'
  | 'task.deleted';

/**
 * Task event detail payload
 * Carried in CustomEvent.detail
 */
export interface TaskEventDetail {
  /**
   * UUID of the affected task
   */
  taskId: string;

  /**
   * Type of operation performed
   */
  operation: TaskEventType;

  /**
   * User who performed the operation (from JWT)
   */
  userId: string;

  /**
   * ISO 8601 timestamp of the operation
   */
  timestamp: string;

  /**
   * Optional metadata (e.g., correlation ID for tracing)
   */
  metadata?: {
    correlation_id?: string;
    source?: 'chatbot' | 'dashboard';
  };
}

/**
 * Custom event wrapper
 * Type-safe CustomEvent with TaskEventDetail payload
 */
export type TaskEvent = CustomEvent<TaskEventDetail>;

/**
 * Event name constant
 * Used for addEventListener/dispatchEvent
 */
const TASK_EVENT_NAME = 'taskUpdate';

/**
 * Emit a task event to notify listeners of task changes
 *
 * Called from:
 * - TaskContext after successful API operations (dashboard-initiated changes)
 * - ChatInterface after successful MCP tool.call.result (chatbot-initiated changes)
 *
 * @param detail - Task event payload
 *
 * @example
 * ```ts
 * // After creating a task
 * emitTaskEvent({
 *   taskId: newTask.id,
 *   operation: 'task.created',
 *   userId: currentUser.uuid,
 *   timestamp: new Date().toISOString(),
 *   metadata: {
 *     source: 'dashboard',
 *   },
 * });
 * ```
 */
export function emitTaskEvent(detail: TaskEventDetail): void {
  // Create custom event with detail payload
  const event = new CustomEvent<TaskEventDetail>(TASK_EVENT_NAME, {
    detail,
    bubbles: false, // Don't bubble up DOM tree (window-level event)
    cancelable: false, // Event cannot be canceled
  });

  // Dispatch event on window object for global listeners
  window.dispatchEvent(event);

  // Debug logging in development (T085: sanitized)
  if (process.env.NODE_ENV === 'development') {
    console.log('[TaskEvent] Emitted:', sanitize({
      operation: detail.operation,
      taskId: detail.taskId,
      source: detail.metadata?.source || 'unknown',
      timestamp: detail.timestamp,
    }));
  }
}

/**
 * Listen for task events and invoke callback
 *
 * Called from:
 * - Dashboard page (useEffect) to trigger task list refresh
 *
 * @param callback - Function to invoke when task event is received
 * @returns Cleanup function to remove event listener
 *
 * @example
 * ```ts
 * // In dashboard page
 * useEffect(() => {
 *   const cleanup = onTaskEvent((detail) => {
 *     console.log('Task event received:', detail.operation);
 *     refreshTasks(); // Re-fetch from API
 *   });
 *
 *   return cleanup; // Remove listener on unmount
 * }, [refreshTasks]);
 * ```
 */
export function onTaskEvent(
  callback: (detail: TaskEventDetail) => void
): () => void {
  // Create event handler wrapper
  const handler = (event: Event) => {
    const taskEvent = event as TaskEvent;
    callback(taskEvent.detail);
  };

  // Add event listener to window
  window.addEventListener(TASK_EVENT_NAME, handler as EventListener);

  // Debug logging in development
  if (process.env.NODE_ENV === 'development') {
    console.log('[TaskEvent] Listener registered');
  }

  // Return cleanup function
  return () => {
    window.removeEventListener(TASK_EVENT_NAME, handler as EventListener);

    if (process.env.NODE_ENV === 'development') {
      console.log('[TaskEvent] Listener removed');
    }
  };
}

/**
 * Helper function to create a task event detail from MCP tool result
 *
 * Used in ChatInterface when parsing tool.call.result SSE events
 *
 * @param toolName - MCP tool name (todo_add_task, todo_complete_task, etc.)
 * @param taskId - Task UUID from tool result
 * @param userId - Current user UUID
 * @param correlationId - Request correlation ID (optional)
 * @returns TaskEventDetail object ready for emitTaskEvent
 *
 * @example
 * ```ts
 * // In ChatInterface after receiving tool.call.result
 * const detail = createTaskEventFromTool(
 *   'todo_add_task',
 *   result.task_id,
 *   currentUser.uuid,
 *   correlationId
 * );
 * emitTaskEvent(detail);
 * ```
 */
export function createTaskEventFromTool(
  toolName: string,
  taskId: string,
  userId: string,
  correlationId?: string
): TaskEventDetail {
  // Map MCP tool names to event types
  // MCP tool names have 'todo_' prefix from MCP server
  const operationMap: Record<string, TaskEventType> = {
    todo_add_task: 'task.created',
    todo_update_task: 'task.updated',
    todo_complete_task: 'task.completed',
    todo_delete_task: 'task.deleted',
  };

  const operation = operationMap[toolName];

  if (!operation) {
    throw new Error(`Unknown MCP tool name: ${toolName}`);
  }

  return {
    taskId,
    operation,
    userId,
    timestamp: new Date().toISOString(),
    metadata: {
      correlation_id: correlationId,
      source: 'chatbot',
    },
  };
}
