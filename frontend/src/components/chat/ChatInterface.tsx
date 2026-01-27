/**
 * Chat Interface Component
 * Feature: 009-chatkit-frontend
 * Task: T033, T037, T039, T040, T048, T049 [US4, US2], T056-T060 [US3], T072-T077 [Phase 9]
 *
 * Purpose: Main chat interface with SSE streaming and conversation history
 * - Send messages to backend via API proxy
 * - Stream SSE responses incrementally
 * - Handle tool.call.result events from MCP (T048, T049)
 * - Emit TaskEvent for dashboard sync (T049)
 * - Exponential backoff retry (T039)
 * - Manual retry button (T040)
 * - Load conversation history on mount (T057)
 * - Pagination support (T056, T058, T059)
 * - Loading states (T060)
 * - Error handling (T072-T077)
 *
 * Architecture:
 * - Frontend → /api/chatkit (proxy) → Backend ChatKit endpoint
 * - SSE streaming for real-time responses
 * - Parse MCP tool results and emit events
 * - Conversation persistence with database
 */

'use client';

import { useState, useCallback, useEffect, useRef } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import { MessageList, ChatMessage } from './MessageList';
import { MessageInput } from './MessageInput';
import { Button } from '@/components/ui/button';
import { RateLimitError, AuthError, TimeoutError } from './ErrorState';
import { emitTaskEvent, createTaskEventFromTool } from '@/lib/events/task-events';
import { getUserUuidFromSession } from '@/lib/get-user-uuid';
import { sanitize } from '@/lib/logging/sanitize';

interface ChatInterfaceProps {
  conversationId?: string;
}

export function ChatInterface({ conversationId: initialConversationId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

  // T057, T060: Conversation history state
  const [conversationId] = useState<string | null>(initialConversationId || null);
  const [, setIsLoadingHistory] = useState(false);
  const [hasMoreMessages] = useState(false);
  const [currentPage] = useState(1);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

  // T072-T077: Enhanced error handling state
  const [rateLimitCountdown, setRateLimitCountdown] = useState<number | null>(null);
  const [authErrorCountdown, setAuthErrorCountdown] = useState<number | null>(null);
  const [showTimeoutDialog, setShowTimeoutDialog] = useState(false);
  const [, setIsWaitingForTimeout] = useState(false);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const abortControllerRef = useRef<AbortController | null>(null);

  // T084: Performance optimization - throttle SSE updates with requestAnimationFrame
  const rafRef = useRef<number | null>(null);
  const pendingStreamingContentRef = useRef<string>('');

  /**
   * T084: Throttled streaming content update
   * Uses requestAnimationFrame to batch UI updates and prevent excessive re-renders
   * when receiving >50 SSE events/second
   */
  const updateStreamingContent = useCallback((content: string) => {
    pendingStreamingContentRef.current = content;

    // If RAF is already scheduled, just update the pending content
    if (rafRef.current !== null) {
      return;
    }

    // Schedule RAF update
    rafRef.current = requestAnimationFrame(() => {
      setStreamingContent(pendingStreamingContentRef.current);
      rafRef.current = null;
    });
  }, []);

  /**
   * T057: Load conversation history on mount
   * Fetches user's single persistent conversation from backend
   * Creates new conversation if none exists (first-time user)
   */
  const loadConversationHistory = useCallback(async () => {
    try {
      setIsLoadingHistory(true);
      setError(null);

      const userId = await getUserUuidFromSession();
      if (!userId) {
        console.log('[ChatInterface] No user session, skipping history load');
        return;
      }

      // Backend endpoint: GET /api/v1/{user_id}/conversations (returns user's single conversation)
      // Note: Backend creates conversation on first message if none exists
      // For now, we'll load conversation history when first message is sent
      // This is a placeholder - actual implementation depends on backend API
      console.log('[ChatInterface] Conversation history loading deferred to first message send');

      // If conversationId is provided, we could load messages here
      // But per architecture, conversation is created on first message send
    } catch (err: any) {
      console.error('[ChatInterface] Failed to load conversation history:', err);
      // Don't show error to user - gracefully fallback to empty state
    } finally {
      setIsLoadingHistory(false);
    }
  }, []);

  /**
   * T059: Load more messages (pagination)
   * T056: Limit 50 messages per page, descending order
   */
  const loadMoreMessages = useCallback(async () => {
    if (!conversationId || isLoadingMore || !hasMoreMessages) {
      return;
    }

    try {
      setIsLoadingMore(true);

      const userId = await getUserUuidFromSession();
      if (!userId) {
        throw new Error('Please log in to load more messages');
      }

      // Backend endpoint: GET /api/v1/{user_id}/conversations/{conversation_id}/messages?page={page}&limit=50
      // Note: This is a placeholder - actual endpoint needs to be implemented in backend
      const nextPage = currentPage + 1;
      console.log(`[ChatInterface] Loading more messages (page ${nextPage})...`);

      // Placeholder: In real implementation, fetch from backend
      // const response = await fetch(`/api/chatkit/conversations/${conversationId}/messages?page=${nextPage}&limit=50`);
      // const data = await response.json();
      // setMessages(prev => [...data.messages, ...prev]); // Prepend older messages
      // setHasMoreMessages(data.has_more);
      // setCurrentPage(nextPage);

      toast.info('Loading earlier messages... (Backend endpoint pending)');
    } catch (err: any) {
      console.error('[ChatInterface] Failed to load more messages:', err);
      toast.error(err.message || 'Failed to load earlier messages');
    } finally {
      setIsLoadingMore(false);
    }
  }, [conversationId, isLoadingMore, hasMoreMessages, currentPage]);

  /**
   * T057, T060: Load conversation history on mount
   */
  useEffect(() => {
    loadConversationHistory();
  }, [loadConversationHistory]);

  /**
   * T072: Rate limit countdown timer
   */
  useEffect(() => {
    if (rateLimitCountdown === null || rateLimitCountdown <= 0) return;

    const timer = setInterval(() => {
      setRateLimitCountdown((prev) => {
        if (prev === null || prev <= 1) {
          setError(null); // Clear error when countdown finishes
          return null;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [rateLimitCountdown]);

  /**
   * T074: Auth error countdown and redirect
   */
  useEffect(() => {
    if (authErrorCountdown === null || authErrorCountdown <= 0) return;

    const timer = setInterval(() => {
      setAuthErrorCountdown((prev) => {
        if (prev === null || prev <= 1) {
          // Redirect to sign in
          window.location.href = '/auth/signin';
          return null;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [authErrorCountdown]);

  /**
   * T084: Cleanup RAF on unmount
   */
  useEffect(() => {
    return () => {
      if (rafRef.current !== null) {
        cancelAnimationFrame(rafRef.current);
        rafRef.current = null;
      }
    };
  }, []);

  /**
   * T037: Send message and stream SSE response
   * T039: Exponential backoff retry (1s, 2s, 4s)
   * T072-T077: Enhanced error handling
   * T078: Structured logging with performance metrics
   */
  const sendMessage = useCallback(async (content: string, attempt = 0) => {
    // T078: Performance metrics tracking (FR-020)
    const requestStartTime = performance.now();
    let firstTokenTime: number | null = null;
    const correlationId = crypto.randomUUID();
    let userId: string | null = null;

    try {
      setError(null);
      setIsStreaming(true);
      setStreamingContent('');
      setShowTimeoutDialog(false);
      setIsWaitingForTimeout(false);

      // Add user message to UI
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);

      // Get user UUID for backend
      userId = await getUserUuidFromSession();
      if (!userId) {
        throw new Error('Please log in to use the chatbot');
      }

      // T078: Log request with sanitized content (FR-020)
      console.log('[ChatInterface] Sending message:', sanitize({
        correlation_id: correlationId,
        user_id: userId,
        conversation_id: conversationId,
        message: content, // Will be truncated to 50 chars by sanitize()
        timestamp: new Date().toISOString(),
        attempt: attempt,
      }));

      // T075: Setup timeout handling (10 seconds)
      abortControllerRef.current = new AbortController();
      timeoutRef.current = setTimeout(() => {
        setShowTimeoutDialog(true);
        setIsWaitingForTimeout(true);
      }, 10000);

      // Send request to API proxy
      const response = await fetch('/api/chatkit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          message: content,
          conversation_id: conversationId,
          user_id: userId,
        }),
        signal: abortControllerRef.current.signal,
      });

      // Clear timeout if response arrives
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      setShowTimeoutDialog(false);
      setIsWaitingForTimeout(false);

      // Handle errors
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        // T074: Auth error with countdown
        if (response.status === 401) {
          setAuthErrorCountdown(3);
          toast.error('Session expired. Redirecting to login...');
          return;
        }

        // T072: Rate limit error with countdown
        if (response.status === 429) {
          const retryAfter = parseInt(response.headers.get('Retry-After') || '60');
          setRateLimitCountdown(retryAfter);
          toast.error(`Rate limit exceeded. Please wait ${retryAfter} seconds.`);
          return;
        }

        throw new Error(errorData.error || `Request failed (${response.status})`);
      }

      // T037: Stream SSE response
      const reader = response.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        throw new Error('Response body is not readable');
      }

      let assistantContent = '';
      let assistantMetadata: ChatMessage['metadata'] = {};

      while (true) {
        const { done, value } = await reader.read();

        if (done) break;

        const chunk = decoder.decode(value, { stream: true });
        const lines = chunk.split('\n');

        for (const line of lines) {
          if (!line.trim() || !line.startsWith('data: ')) continue;

          const data = line.slice(6); // Remove 'data: ' prefix

          if (data === '[DONE]') {
            // Stream complete
            break;
          }

          try {
            // DEBUG: Log raw SSE data
            console.log('[ChatInterface] Raw SSE data:', data);

            const event = JSON.parse(data);

            // DEBUG: Log parsed event
            console.log('[ChatInterface] Parsed event type:', event.type, 'role:', event.role);

            // Handle different SSE event types
            if (event.type === 'thread.message.delta') {
              // Incremental content update (streaming deltas)
              assistantContent += event.content || '';

              // T084: Use throttled update to prevent excessive re-renders
              updateStreamingContent(assistantContent);
            } else if (event.type === 'message' && event.role === 'assistant') {
              // Complete message from backend (non-streaming response)
              assistantContent = event.content || '';
              updateStreamingContent(assistantContent);

              // Handle tool_results if present in the message event
              if (event.tool_results && Array.isArray(event.tool_results)) {
                for (const toolResult of event.tool_results) {
                  const toolName = toolResult.tool;
                  const result = toolResult.result;
                  const taskId = result?.task_id || result?.id;
                  const taskTitle = result?.title;

                  // Track tool call in message metadata
                  if (!assistantMetadata.toolCalls) {
                    assistantMetadata.toolCalls = [];
                  }

                  assistantMetadata.toolCalls.push({
                    toolName,
                    status: result?.error ? 'error' : 'success',
                    result: result,
                    error: result?.error,
                  });

                  // Emit TaskEvent for dashboard sync
                  if (!result?.error && taskId && ['add_task', 'update_task', 'complete_task', 'delete_task'].includes(toolName)) {
                    try {
                      const taskEvent = createTaskEventFromTool(
                        `todo_${toolName}`,
                        taskId.toString(),
                        userId,
                        correlationId
                      );
                      emitTaskEvent(taskEvent);
                      console.log('[ChatInterface] TaskEvent emitted from message:', sanitize(taskEvent));
                    } catch (err) {
                      console.error('[ChatInterface] Failed to emit TaskEvent:', sanitize(err));
                    }
                  }
                }
              }

              // T078: Track time to first token (FR-020)
              if (firstTokenTime === null && assistantContent.length > 0) {
                firstTokenTime = performance.now();
                const timeToFirstToken = Math.round(firstTokenTime - requestStartTime);
                console.log('[ChatInterface] First token received:', {
                  correlation_id: correlationId,
                  time_to_first_token_ms: timeToFirstToken,
                  timestamp: new Date().toISOString(),
                });
              }
            } else if (event.type === 'tool.call.start') {
              // MCP tool started
              console.log('[ChatInterface] Tool call started:', event.tool_name);
            } else if (event.type === 'tool.call.result') {
              // T048, T049, T051b: MCP tool completed - emit TaskEvent and ensure confirmation message
              // T085: Sanitize tool result before logging
              console.log('[ChatInterface] Tool call result:', sanitize(event));

              const toolName = event.tool_name;
              const taskId = event.result?.task_id || event.result?.id;
              const taskTitle = event.result?.title;
              const taskStatus = event.result?.status;

              // Track tool call in message metadata
              if (!assistantMetadata.toolCalls) {
                assistantMetadata.toolCalls = [];
              }

              assistantMetadata.toolCalls.push({
                toolName,
                status: event.success ? 'success' : 'error',
                result: event.result,
                error: event.error,
              });

              // T051b: Generate explicit confirmation message (fallback if AI doesn't provide it)
              // This ensures 100% visibility of task operations per FR-021
              if (event.success && ['todo_add_task', 'todo_update_task', 'todo_complete_task', 'todo_delete_task'].includes(toolName)) {
                let confirmationMessage = '';

                if (toolName === 'todo_add_task' && taskTitle) {
                  confirmationMessage = `\n\n✓ Task '${taskTitle}' has been added successfully (ID: #${taskId})`;
                } else if (toolName === 'todo_update_task' && taskId) {
                  confirmationMessage = `\n\n✓ Task #${taskId}${taskTitle ? ` updated to '${taskTitle}'` : ' has been updated'}`;
                } else if (toolName === 'todo_complete_task' && taskId) {
                  confirmationMessage = `\n\n✓ Task #${taskId} marked as complete`;
                } else if (toolName === 'todo_delete_task' && taskId) {
                  confirmationMessage = `\n\n✓ Task #${taskId} has been deleted`;
                }

                // Append confirmation to streaming content if not already present
                // (AI should already include this, but this is a safety net)
                if (confirmationMessage && !assistantContent.includes('✓')) {
                  assistantContent += confirmationMessage;
                  updateStreamingContent(assistantContent);
                }
              }

              // T049, T051f: Emit TaskEvent for dashboard sync IMMEDIATELY after tool success
              // Tool names have 'todo_' prefix from MCP server
              if (event.success && taskId && ['todo_add_task', 'todo_update_task', 'todo_complete_task', 'todo_delete_task'].includes(toolName)) {
                try {
                  const taskEvent = createTaskEventFromTool(
                    toolName,
                    taskId.toString(),
                    userId,
                    event.correlation_id
                  );

                  // T051f: Emit event immediately (dashboard should update within 1 second per FR-024)
                  emitTaskEvent(taskEvent);

                  // T085: Sanitize task event before logging
                  console.log('[ChatInterface] TaskEvent emitted:', sanitize(taskEvent));
                  console.log('[ChatInterface] Dashboard refresh triggered at:', new Date().toISOString());
                } catch (err) {
                  // T085: Sanitize error before logging
                  console.error('[ChatInterface] Failed to emit TaskEvent:', sanitize(err));
                }
              }
            } else if (event.type === 'thread.message.completed') {
              // Message complete
              console.log('[ChatInterface] Message completed');
            } else if (event.type === 'error') {
              // Error event
              console.error('[ChatInterface] Error event received:', event);
              throw new Error(event.error?.message || event.message || 'Stream error');
            } else {
              // Unknown event type
              console.log('[ChatInterface] Unknown event type:', event.type);
            }
          } catch (parseError) {
            console.warn('[ChatInterface] Failed to parse SSE event:', parseError, 'Raw data:', data);
          }
        }
      }

      // T077: Add assistant message to UI (mark as complete)
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: assistantContent,
        timestamp: new Date().toISOString(),
        metadata: {
          ...assistantMetadata,
          complete: true, // Stream completed successfully
        },
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setStreamingContent('');
      setRetryCount(0); // Reset retry count on success

      // T078: Log response completion with performance metrics (FR-020)
      const totalResponseTime = Math.round(performance.now() - requestStartTime);
      console.log('[ChatInterface] Response completed:', sanitize({
        correlation_id: correlationId,
        user_id: userId,
        response: assistantContent, // Will be truncated to 50 chars
        time_to_first_token_ms: firstTokenTime ? Math.round(firstTokenTime - requestStartTime) : null,
        total_response_time_ms: totalResponseTime,
        tool_calls: assistantMetadata.toolCalls?.length || 0,
        timestamp: new Date().toISOString(),
      }))
    } catch (err: any) {
      // T078, T085: Log error with full context and performance metrics (FR-020)
      const errorTime = Math.round(performance.now() - requestStartTime);
      console.error('[ChatInterface] Send message error:', sanitize({
        correlation_id: correlationId,
        user_id: userId,
        error_message: err.message,
        error_stack: err.stack,
        time_elapsed_ms: errorTime,
        attempt: attempt,
        timestamp: new Date().toISOString(),
      }));

      // T075: Clear timeout on error
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
        timeoutRef.current = null;
      }
      setShowTimeoutDialog(false);
      setIsWaitingForTimeout(false);

      // T073, T039: Exponential backoff retry for network errors (1s, 2s, 4s)
      // Skip retry for rate limit, auth errors, or aborted requests
      if (
        attempt < 3 &&
        !err.message.includes('Rate limit') &&
        err.name !== 'AbortError'
      ) {
        const delay = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s
        console.log(`[ChatInterface] Retrying in ${delay}ms (attempt ${attempt + 1}/3)`);

        toast.info(`Connection failed. Retrying in ${delay / 1000}s...`);

        await new Promise((resolve) => setTimeout(resolve, delay));
        return sendMessage(content, attempt + 1);
      }

      // T077: Add partial message indicator if stream was interrupted
      if (streamingContent && err.name === 'AbortError') {
        const partialMessage: ChatMessage = {
          id: crypto.randomUUID(),
          role: 'assistant',
          content: streamingContent,
          timestamp: new Date().toISOString(),
          metadata: {
            complete: false, // Incomplete stream
            interrupted: true,
          },
        };
        setMessages((prev) => [...prev, partialMessage]);
        setStreamingContent('');
      }

      // T040: Show error with manual retry option
      setError(err.message || 'Failed to send message');
      setRetryCount(attempt + 1);
      toast.error(err.message || 'Failed to send message');
    } finally {
      setIsStreaming(false);
    }
  }, [conversationId, streamingContent]);

  /**
   * T040: Manual retry for failed messages
   */
  const handleRetry = () => {
    if (messages.length > 0) {
      const lastUserMessage = [...messages].reverse().find((m) => m.role === 'user');
      if (lastUserMessage) {
        sendMessage(lastUserMessage.content);
      }
    }
  };

  /**
   * T075: Timeout dialog handlers
   */
  const handleCancelRequest = () => {
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
      timeoutRef.current = null;
    }
    setShowTimeoutDialog(false);
    setIsWaitingForTimeout(false);
    setIsStreaming(false);
    toast.info('Request cancelled');
  };

  const handleKeepWaiting = () => {
    setShowTimeoutDialog(false);
    // Keep isWaitingForTimeout true to prevent showing dialog again
    toast.info('Continuing to wait for response...');
  };

  return (
    <div className="flex flex-col h-full">
      {/* T072-T077: Enhanced error handling UI */}
      {rateLimitCountdown !== null && rateLimitCountdown > 0 && (
        <div className="border-b border-orange-200 dark:border-orange-800">
          <RateLimitError retryAfter={rateLimitCountdown} countdown={rateLimitCountdown} />
        </div>
      )}

      {authErrorCountdown !== null && authErrorCountdown > 0 && (
        <div className="border-b border-red-200 dark:border-red-800">
          <AuthError countdown={authErrorCountdown} />
        </div>
      )}

      {showTimeoutDialog && (
        <div className="border-b border-yellow-200 dark:border-yellow-800">
          <TimeoutError onCancel={handleCancelRequest} onKeepWaiting={handleKeepWaiting} />
        </div>
      )}

      {/* T040: Generic error banner with retry button (for other errors) */}
      {error && !rateLimitCountdown && !authErrorCountdown && !showTimeoutDialog && (
        <div className="bg-red-50 dark:bg-red-900/20 border-b border-red-200 dark:border-red-800 p-3">
          <div className="flex items-start gap-3">
            <AlertCircle className="h-5 w-5 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
            <div className="flex-1 min-w-0">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
              {retryCount >= 3 && (
                <p className="text-xs text-red-600 dark:text-red-400 mt-1">
                  Auto-retry failed after 3 attempts. Please try again manually.
                </p>
              )}
            </div>
            <Button
              onClick={handleRetry}
              size="sm"
              variant="outline"
              className="flex-shrink-0 border-red-300 dark:border-red-700 text-red-700 dark:text-red-300 hover:bg-red-100 dark:hover:bg-red-900/40"
            >
              <RefreshCw className="h-4 w-4 mr-1" />
              Retry
            </Button>
          </div>
        </div>
      )}

      {/* T058, T059, T060: Message list with pagination support */}
      <MessageList
        messages={messages}
        isStreaming={isStreaming}
        streamingContent={streamingContent}
        onLoadMore={loadMoreMessages}
        hasMore={hasMoreMessages}
        isLoadingMore={isLoadingMore}
      />

      {/* Message input */}
      <MessageInput
        onSend={sendMessage}
        disabled={isStreaming}
        placeholder="Ask me to manage your tasks... (e.g., 'Add a task to buy groceries')"
      />
    </div>
  );
}
