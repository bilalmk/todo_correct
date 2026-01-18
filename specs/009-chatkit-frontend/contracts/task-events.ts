/**
 * Task Event Types - Real-Time Sync Contract
 *
 * Feature: 009-chatkit-frontend
 * Purpose: Custom event system for real-time task synchronization between chatbot and dashboard
 * Date: 2026-01-15
 *
 * This file defines the TypeScript interfaces and helper functions for emitting and listening
 * to task change events across React components without tight coupling.
 *
 * Usage:
 *   - TaskContext emits events after API operations (add, update, delete, complete)
 *   - Dashboard page listens for events and triggers refreshTasks()
 *   - Chatbot (future) can emit events after MCP tool results
 */

// ============================================================================
// Event Types
// ============================================================================

/**
 * Task event types representing different task operations.
 *
 * These align with MCP tool names for consistency:
 * - 'task:created' → add_task()
 * - 'task:updated' → update_task()
 * - 'task:deleted' → delete_task()
 * - 'task:completed' → complete_task()
 */
export type TaskEventType =
  | 'task:created'
  | 'task:updated'
  | 'task:deleted'
  | 'task:completed';

/**
 * Source of the task event (where it originated).
 *
 * - 'dashboard' → User manually changed task in dashboard UI
 * - 'chatbot' → AI agent performed task operation via MCP tool
 */
export type TaskEventSource = 'dashboard' | 'chatbot';

/**
 * Task event payload.
 *
 * Emitted after successful task operation to notify other components to refresh.
 *
 * @property type - Type of task operation
 * @property taskId - ID of affected task (optional for bulk operations)
 * @property timestamp - ISO 8601 timestamp when event occurred
 * @property source - Component that triggered the operation
 * @property metadata - Optional additional context (e.g., tool_call_id for chatbot events)
 */
export interface TaskEvent {
  type: TaskEventType;
  taskId?: number;
  timestamp: string;
  source: TaskEventSource;
  metadata?: {
    toolCallId?: string;        // ChatKit tool call ID (for correlation)
    correlationId?: string;      // Backend correlation ID (for tracing)
    [key: string]: any;          // Extensible for future metadata
  };
}

// ============================================================================
// Event Emitter
// ============================================================================

/**
 * Emit a task event to notify listeners of task changes.
 *
 * This uses the native CustomEvent API to dispatch events via the window object.
 * All listeners registered via `onTaskEvent()` will receive this event.
 *
 * @param event - Task event to emit
 *
 * @example
 * // In TaskContext after creating a task
 * emitTaskEvent({
 *   type: 'task:created',
 *   taskId: 123,
 *   timestamp: new Date().toISOString(),
 *   source: 'dashboard',
 * });
 *
 * @example
 * // In chatbot after MCP tool result
 * emitTaskEvent({
 *   type: 'task:completed',
 *   taskId: 456,
 *   timestamp: new Date().toISOString(),
 *   source: 'chatbot',
 *   metadata: {
 *     toolCallId: 'call_xyz789',
 *     correlationId: '7f3d8c90-1234-5678-9abc-def012345678',
 *   },
 * });
 */
export const emitTaskEvent = (event: TaskEvent): void => {
  if (typeof window === 'undefined') {
    // Server-side rendering: skip event emission
    console.warn('[TaskEvents] Attempted to emit event on server. Ignoring.');
    return;
  }

  // Dispatch custom event
  window.dispatchEvent(new CustomEvent('taskChange', { detail: event }));

  // Log for debugging (only in development)
  if (process.env.NODE_ENV === 'development') {
    console.log('[TaskEvents] Event emitted:', event);
  }
};

// ============================================================================
// Event Listener
// ============================================================================

/**
 * Register a listener for task events.
 *
 * The callback will be invoked whenever a task event is emitted via `emitTaskEvent()`.
 * Returns an unsubscribe function to clean up the listener (call in useEffect cleanup).
 *
 * @param callback - Function to call when task event received
 * @returns Unsubscribe function to remove listener
 *
 * @example
 * // In Dashboard page
 * useEffect(() => {
 *   const unsubscribe = onTaskEvent((event) => {
 *     console.log('Task changed:', event);
 *
 *     // Refresh task list if event came from chatbot
 *     if (event.source === 'chatbot') {
 *       refreshTasks(toBackendQuery());
 *     }
 *   });
 *
 *   return unsubscribe; // Cleanup on unmount
 * }, [refreshTasks, toBackendQuery]);
 */
export const onTaskEvent = (callback: (event: TaskEvent) => void): (() => void) => {
  if (typeof window === 'undefined') {
    // Server-side rendering: return no-op cleanup
    console.warn('[TaskEvents] Attempted to register listener on server. Ignoring.');
    return () => {};
  }

  // Wrap callback to extract event detail
  const handler = (e: Event) => {
    const customEvent = e as CustomEvent<TaskEvent>;
    callback(customEvent.detail);
  };

  // Register listener
  window.addEventListener('taskChange', handler);

  // Log for debugging (only in development)
  if (process.env.NODE_ENV === 'development') {
    console.log('[TaskEvents] Listener registered');
  }

  // Return unsubscribe function
  return () => {
    window.removeEventListener('taskChange', handler);

    if (process.env.NODE_ENV === 'development') {
      console.log('[TaskEvents] Listener unregistered');
    }
  };
};

// ============================================================================
// Helper Utilities
// ============================================================================

/**
 * Create a task event with current timestamp.
 *
 * Convenience function to reduce boilerplate when emitting events.
 *
 * @param type - Task event type
 * @param source - Event source (dashboard or chatbot)
 * @param taskId - Optional task ID
 * @param metadata - Optional metadata
 * @returns Complete TaskEvent object
 *
 * @example
 * emitTaskEvent(
 *   createTaskEvent('task:created', 'dashboard', 123)
 * );
 */
export const createTaskEvent = (
  type: TaskEventType,
  source: TaskEventSource,
  taskId?: number,
  metadata?: TaskEvent['metadata']
): TaskEvent => {
  return {
    type,
    taskId,
    timestamp: new Date().toISOString(),
    source,
    metadata,
  };
};

/**
 * Check if a task event is task-modifying (excludes read-only operations).
 *
 * Useful for filtering events that require dashboard refresh.
 *
 * @param event - Task event to check
 * @returns true if event modifies task data (create, update, delete, complete)
 *
 * @example
 * onTaskEvent((event) => {
 *   if (isTaskModifyingEvent(event)) {
 *     refreshTasks(); // Only refresh on data changes
 *   }
 * });
 */
export const isTaskModifyingEvent = (event: TaskEvent): boolean => {
  // All current event types modify data
  // (Future: might add 'task:viewed' or 'task:selected' read-only events)
  return true;
};

/**
 * Debounce task event emissions to prevent excessive refresh triggers.
 *
 * Useful when multiple rapid operations occur (e.g., bulk delete, batch update).
 *
 * @param callback - Event listener callback
 * @param delayMs - Debounce delay in milliseconds (default: 500ms)
 * @returns Debounced callback
 *
 * @example
 * useEffect(() => {
 *   const unsubscribe = onTaskEvent(
 *     debounceTaskEvents((event) => {
 *       refreshTasks(); // Only triggers once after 500ms of silence
 *     }, 500)
 *   );
 *
 *   return unsubscribe;
 * }, []);
 */
export const debounceTaskEvents = (
  callback: (event: TaskEvent) => void,
  delayMs: number = 500
): ((event: TaskEvent) => void) => {
  let timeoutId: NodeJS.Timeout | null = null;

  return (event: TaskEvent) => {
    // Clear previous timeout
    if (timeoutId) {
      clearTimeout(timeoutId);
    }

    // Set new timeout
    timeoutId = setTimeout(() => {
      callback(event);
      timeoutId = null;
    }, delayMs);
  };
};

// ============================================================================
// Type Guards
// ============================================================================

/**
 * Type guard to check if an event is a TaskEvent.
 *
 * Useful for runtime validation when receiving events from window.addEventListener.
 *
 * @param event - Event to check
 * @returns true if event is a valid TaskEvent
 */
export const isTaskEvent = (event: any): event is TaskEvent => {
  return (
    event &&
    typeof event === 'object' &&
    typeof event.type === 'string' &&
    ['task:created', 'task:updated', 'task:deleted', 'task:completed'].includes(event.type) &&
    typeof event.timestamp === 'string' &&
    typeof event.source === 'string' &&
    ['dashboard', 'chatbot'].includes(event.source)
  );
};

// ============================================================================
// Testing Utilities
// ============================================================================

/**
 * Mock task event for testing.
 *
 * @param overrides - Partial TaskEvent to override defaults
 * @returns Complete TaskEvent with sensible defaults
 */
export const mockTaskEvent = (overrides?: Partial<TaskEvent>): TaskEvent => {
  return {
    type: 'task:created',
    taskId: 123,
    timestamp: new Date().toISOString(),
    source: 'dashboard',
    ...overrides,
  };
};

/**
 * Wait for a task event (for testing).
 *
 * Returns a promise that resolves when an event matching the predicate is received.
 *
 * @param predicate - Function to test if event matches
 * @param timeoutMs - Timeout in milliseconds (default: 5000ms)
 * @returns Promise that resolves with the matching event
 *
 * @example
 * // In Playwright test
 * const eventPromise = waitForTaskEvent((e) => e.type === 'task:created');
 * await page.click('[data-testid="create-task-button"]');
 * const event = await eventPromise;
 * expect(event.taskId).toBeDefined();
 */
export const waitForTaskEvent = (
  predicate: (event: TaskEvent) => boolean,
  timeoutMs: number = 5000
): Promise<TaskEvent> => {
  return new Promise((resolve, reject) => {
    let unsubscribe: (() => void) | null = null;
    let timeoutId: NodeJS.Timeout | null = null;

    // Timeout handler
    timeoutId = setTimeout(() => {
      if (unsubscribe) unsubscribe();
      reject(new Error(`waitForTaskEvent timeout after ${timeoutMs}ms`));
    }, timeoutMs);

    // Event listener
    unsubscribe = onTaskEvent((event) => {
      if (predicate(event)) {
        if (timeoutId) clearTimeout(timeoutId);
        if (unsubscribe) unsubscribe();
        resolve(event);
      }
    });
  });
};

// ============================================================================
// Exports
// ============================================================================

export default {
  emitTaskEvent,
  onTaskEvent,
  createTaskEvent,
  isTaskModifyingEvent,
  debounceTaskEvents,
  isTaskEvent,
  mockTaskEvent,
  waitForTaskEvent,
};
