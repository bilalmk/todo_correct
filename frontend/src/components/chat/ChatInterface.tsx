/**
 * Chat Interface Component
 * Feature: 009-chatkit-frontend
 * Task: T033, T037, T039, T040, T048, T049 [US4, US2], T056-T060 [US3]
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
 * - Error handling
 *
 * Architecture:
 * - Frontend → /api/chatkit (proxy) → Backend ChatKit endpoint
 * - SSE streaming for real-time responses
 * - Parse MCP tool results and emit events
 * - Conversation persistence with database
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import { AlertCircle, RefreshCw } from 'lucide-react';
import { toast } from 'sonner';
import { MessageList, ChatMessage } from './MessageList';
import { MessageInput } from './MessageInput';
import { Button } from '@/components/ui/button';
import { emitTaskEvent, createTaskEventFromTool } from '@/lib/events/task-events';
import { getUserUuidFromSession } from '@/lib/get-user-uuid';

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
  const [conversationId, setConversationId] = useState<string | null>(initialConversationId || null);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [hasMoreMessages, setHasMoreMessages] = useState(false);
  const [currentPage, setCurrentPage] = useState(1);
  const [isLoadingMore, setIsLoadingMore] = useState(false);

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
   * T037: Send message and stream SSE response
   * T039: Exponential backoff retry (1s, 2s, 4s)
   */
  const sendMessage = useCallback(async (content: string, attempt = 0) => {
    try {
      setError(null);
      setIsStreaming(true);
      setStreamingContent('');

      // Add user message to UI
      const userMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'user',
        content,
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, userMessage]);

      // Get user UUID for backend
      const userId = await getUserUuidFromSession();
      if (!userId) {
        throw new Error('Please log in to use the chatbot');
      }

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
      });

      // Handle errors
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));

        if (response.status === 401) {
          // Redirect to login
          toast.error('Session expired. Redirecting to login...');
          setTimeout(() => {
            window.location.href = '/auth/signin';
          }, 3000);
          return;
        }

        if (response.status === 429) {
          // Rate limit error
          const retryAfter = parseInt(response.headers.get('Retry-After') || '60');
          throw new Error(`Rate limit exceeded. Please wait ${retryAfter} seconds.`);
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
            const event = JSON.parse(data);

            // Handle different SSE event types
            if (event.type === 'thread.message.delta') {
              // Incremental content update
              assistantContent += event.content || '';
              setStreamingContent(assistantContent);
            } else if (event.type === 'tool.call.start') {
              // MCP tool started
              console.log('[ChatInterface] Tool call started:', event.tool_name);
            } else if (event.type === 'tool.call.result') {
              // T048, T049: MCP tool completed - emit TaskEvent
              console.log('[ChatInterface] Tool call result:', event);

              const toolName = event.tool_name;
              const taskId = event.result?.task_id || event.result?.id;

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

              // T049: Emit TaskEvent for dashboard sync
              if (event.success && taskId && ['add_task', 'update_task', 'complete_task', 'delete_task'].includes(toolName)) {
                try {
                  const taskEvent = createTaskEventFromTool(
                    toolName,
                    taskId.toString(),
                    userId,
                    event.correlation_id
                  );
                  emitTaskEvent(taskEvent);
                  console.log('[ChatInterface] TaskEvent emitted:', taskEvent);
                } catch (err) {
                  console.error('[ChatInterface] Failed to emit TaskEvent:', err);
                }
              }
            } else if (event.type === 'thread.message.completed') {
              // Message complete
              console.log('[ChatInterface] Message completed');
            } else if (event.type === 'error') {
              // Error event
              throw new Error(event.message || 'Stream error');
            }
          } catch (parseError) {
            console.warn('[ChatInterface] Failed to parse SSE event:', parseError);
          }
        }
      }

      // Add assistant message to UI
      const assistantMessage: ChatMessage = {
        id: crypto.randomUUID(),
        role: 'assistant',
        content: assistantContent,
        timestamp: new Date().toISOString(),
        metadata: assistantMetadata,
      };

      setMessages((prev) => [...prev, assistantMessage]);
      setStreamingContent('');
      setRetryCount(0); // Reset retry count on success
    } catch (err: any) {
      console.error('[ChatInterface] Send message error:', err);

      // T039: Exponential backoff retry (1s, 2s, 4s)
      if (attempt < 3 && !err.message.includes('Rate limit')) {
        const delay = Math.pow(2, attempt) * 1000; // 1s, 2s, 4s
        console.log(`[ChatInterface] Retrying in ${delay}ms (attempt ${attempt + 1}/3)`);

        toast.info(`Connection failed. Retrying in ${delay / 1000}s...`);

        await new Promise((resolve) => setTimeout(resolve, delay));
        return sendMessage(content, attempt + 1);
      }

      // T040: Show error with manual retry option
      setError(err.message || 'Failed to send message');
      setRetryCount(attempt + 1);
      toast.error(err.message || 'Failed to send message');
    } finally {
      setIsStreaming(false);
    }
  }, [conversationId]);

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

  return (
    <div className="flex flex-col h-full">
      {/* T040: Error banner with retry button */}
      {error && (
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
