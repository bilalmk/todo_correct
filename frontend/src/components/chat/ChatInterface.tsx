/**
 * Chat Interface Component
 * Feature: 009-chatkit-frontend
 * Task: T033, T037, T039, T040, T048, T049 [US4, US2]
 *
 * Purpose: Main chat interface with SSE streaming
 * - Send messages to backend via API proxy
 * - Stream SSE responses incrementally
 * - Handle tool.call.result events from MCP (T048, T049)
 * - Emit TaskEvent for dashboard sync (T049)
 * - Exponential backoff retry (T039)
 * - Manual retry button (T040)
 * - Error handling
 *
 * Architecture:
 * - Frontend → /api/chatkit (proxy) → Backend ChatKit endpoint
 * - SSE streaming for real-time responses
 * - Parse MCP tool results and emit events
 */

'use client';

import { useState, useCallback } from 'react';
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

export function ChatInterface({ conversationId }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [error, setError] = useState<string | null>(null);
  const [retryCount, setRetryCount] = useState(0);

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

      {/* Message list */}
      <MessageList
        messages={messages}
        isStreaming={isStreaming}
        streamingContent={streamingContent}
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
