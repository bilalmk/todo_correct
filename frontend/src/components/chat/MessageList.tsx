/**
 * Message List Component
 * Feature: 009-chatkit-frontend
 * Task: T034 [US4]
 *
 * Purpose: Display chat messages with streaming state
 * - User messages (right-aligned)
 * - Assistant messages (left-aligned)
 * - Streaming indicator (T038: typing animation)
 * - Auto-scroll to bottom
 * - Loading states
 * - Success indicators for tool calls (T050)
 *
 * Usage:
 * ```tsx
 * <MessageList
 *   messages={messages}
 *   isStreaming={isStreaming}
 *   streamingContent={partialContent}
 * />
 * ```
 */

'use client';

import { useEffect, useRef } from 'react';
import { CheckCircle2, Loader2, AlertCircle } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import ReactMarkdown from 'react-markdown';

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  metadata?: {
    toolCalls?: {
      toolName: string;
      status: 'start' | 'success' | 'error';
      result?: any;
      error?: string;
    }[];
    complete?: boolean; // T077: Stream completion status
    interrupted?: boolean; // T077: Stream interrupted flag
  };
}

interface MessageListProps {
  messages: ChatMessage[];
  isStreaming?: boolean;
  streamingContent?: string;
  onLoadMore?: () => void;
  hasMore?: boolean;
  isLoadingMore?: boolean; // T060: Loading state for pagination
}

export function MessageList({
  messages,
  isStreaming = false,
  streamingContent = '',
  onLoadMore,
  hasMore = false,
  isLoadingMore = false,
}: MessageListProps) {
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const scrollContainerRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent]);

  return (
    <div
      ref={scrollContainerRef}
      className="flex-1 overflow-y-auto p-4 space-y-4 bg-gray-50 dark:bg-gray-800"
    >
      {/* T058, T060: Load earlier messages button with loading state */}
      {hasMore && onLoadMore && (
        <div className="text-center">
          <button
            onClick={onLoadMore}
            disabled={isLoadingMore}
            className="
              text-sm text-orange-600 dark:text-orange-400
              hover:text-orange-700 dark:hover:text-orange-300
              hover:underline
              disabled:opacity-50 disabled:cursor-not-allowed
              flex items-center gap-2 mx-auto
            "
          >
            {isLoadingMore && <Loader2 className="h-3 w-3 animate-spin" />}
            {isLoadingMore ? 'Loading...' : 'Load earlier messages'}
          </button>
        </div>
      )}

      {/* Empty state */}
      {messages.length === 0 && !isStreaming && (
        <div className="flex items-center justify-center h-full text-center text-gray-400 dark:text-gray-600">
          <div>
            <p className="text-lg font-medium mb-2">Start a conversation</p>
            <p className="text-sm">
              Ask me to create, update, or complete tasks for you!
            </p>
          </div>
        </div>
      )}

      {/* Messages */}
      <AnimatePresence initial={false}>
        {messages.map((message) => (
          <motion.div
            key={message.id}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`
                max-w-[80%] rounded-lg px-4 py-3
                ${
                  message.role === 'user'
                    ? 'bg-orange-500 text-white'
                    : 'bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 border border-gray-200 dark:border-gray-600'
                }
              `}
            >
              {/* Message content */}
              <div className="whitespace-pre-wrap break-words text-sm">
                {message.role === 'assistant' ? (
                  <ReactMarkdown
                    components={{
                      // Style headings
                      h1: ({ children }) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
                      h2: ({ children }) => <h2 className="text-base font-bold mb-2">{children}</h2>,
                      h3: ({ children }) => <h3 className="text-sm font-bold mb-1">{children}</h3>,
                      // Style paragraphs
                      p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                      // Style bold text
                      strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                      // Style lists
                      ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                      li: ({ children }) => <li className="ml-2">{children}</li>,
                      // Style code blocks
                      code: ({ children }) => (
                        <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-xs font-mono">
                          {children}
                        </code>
                      ),
                      // Style horizontal rules
                      hr: () => <hr className="my-3 border-gray-300 dark:border-gray-600" />,
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                ) : (
                  message.content
                )}
              </div>

              {/* T050, T051c: Tool call indicators (success confirmation UI - PROMINENT) */}
              {message.metadata?.toolCalls && message.metadata.toolCalls.length > 0 && (
                <div className="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600 space-y-2">
                  {message.metadata.toolCalls.map((tool, idx) => (
                    <div
                      key={idx}
                      className={`flex items-start gap-2 px-3 py-2 rounded-md ${
                        tool.status === 'success'
                          ? 'bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800'
                          : 'bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800'
                      }`}
                    >
                      {tool.status === 'success' && (
                        <>
                          <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400 flex-shrink-0 mt-0.5" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-green-800 dark:text-green-200">
                              {tool.toolName === 'todo_add_task' && `Task created successfully`}
                              {tool.toolName === 'todo_update_task' && `Task updated successfully`}
                              {tool.toolName === 'todo_complete_task' && `Task marked as complete`}
                              {tool.toolName === 'todo_delete_task' && `Task deleted successfully`}
                              {tool.toolName === 'todo_list_tasks' && `Tasks retrieved`}
                            </p>
                            {tool.result?.task_id && (
                              <p className="text-xs text-green-700 dark:text-green-300 mt-0.5">
                                {tool.result.title && `"${tool.result.title}" `}
                                (ID: #{tool.result.task_id})
                              </p>
                            )}
                          </div>
                        </>
                      )}
                      {tool.status === 'error' && (
                        <>
                          <AlertCircle className="h-4 w-4 text-red-600 dark:text-red-400 flex-shrink-0 mt-0.5" />
                          <div className="flex-1 min-w-0">
                            <p className="text-sm font-medium text-red-800 dark:text-red-200">
                              Operation failed
                            </p>
                            <p className="text-xs text-red-700 dark:text-red-300 mt-0.5">
                              {tool.error || 'An error occurred'}
                            </p>
                          </div>
                        </>
                      )}
                    </div>
                  ))}
                </div>
              )}

              {/* T077: Incomplete message indicator */}
              {message.role === 'assistant' && message.metadata?.complete === false && (
                <div className="mt-2 flex items-center gap-2 text-xs text-yellow-600 dark:text-yellow-400">
                  <AlertCircle className="h-3 w-3" />
                  <span>
                    {message.metadata.interrupted
                      ? 'Response interrupted (partial message)'
                      : 'Incomplete response'}
                  </span>
                </div>
              )}

              {/* Timestamp */}
              <div className={`text-xs mt-1 ${
                message.role === 'user' ? 'text-white/70' : 'text-gray-400 dark:text-gray-500'
              }`}>
                {new Date(message.timestamp).toLocaleTimeString([], {
                  hour: '2-digit',
                  minute: '2-digit',
                })}
              </div>
            </div>
          </motion.div>
        ))}
      </AnimatePresence>

      {/* T038: Streaming message with typing indicator */}
      {isStreaming && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          className="flex justify-start"
        >
          <div className="max-w-[80%] rounded-lg px-4 py-3 bg-white dark:bg-gray-700 border border-gray-200 dark:border-gray-600">
            {streamingContent ? (
              <>
                <div className="whitespace-pre-wrap break-words text-sm text-gray-900 dark:text-gray-100">
                  <ReactMarkdown
                    components={{
                      h1: ({ children }) => <h1 className="text-lg font-bold mb-2">{children}</h1>,
                      h2: ({ children }) => <h2 className="text-base font-bold mb-2">{children}</h2>,
                      h3: ({ children }) => <h3 className="text-sm font-bold mb-1">{children}</h3>,
                      p: ({ children }) => <p className="mb-2 last:mb-0">{children}</p>,
                      strong: ({ children }) => <strong className="font-semibold">{children}</strong>,
                      ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1">{children}</ol>,
                      li: ({ children }) => <li className="ml-2">{children}</li>,
                      code: ({ children }) => (
                        <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-xs font-mono">
                          {children}
                        </code>
                      ),
                      hr: () => <hr className="my-3 border-gray-300 dark:border-gray-600" />,
                    }}
                  >
                    {streamingContent}
                  </ReactMarkdown>
                </div>
                {/* Typing cursor */}
                <span className="inline-block w-1 h-4 ml-1 bg-gray-900 dark:bg-gray-100 animate-pulse" />
              </>
            ) : (
              <div className="flex items-center gap-2 text-sm text-gray-500 dark:text-gray-400">
                <Loader2 className="h-4 w-4 animate-spin" />
                <span>AI is typing...</span>
              </div>
            )}
          </div>
        </motion.div>
      )}

      {/* Scroll anchor */}
      <div ref={messagesEndRef} />
    </div>
  );
}
