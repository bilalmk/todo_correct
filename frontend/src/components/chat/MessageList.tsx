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
                {message.content}
              </div>

              {/* Tool call indicators (T050: success confirmation UI) */}
              {message.metadata?.toolCalls && message.metadata.toolCalls.length > 0 && (
                <div className="mt-2 space-y-1">
                  {message.metadata.toolCalls.map((tool, idx) => (
                    <div
                      key={idx}
                      className="flex items-center gap-2 text-xs opacity-80"
                    >
                      {tool.status === 'success' && (
                        <>
                          <CheckCircle2 className="h-3 w-3 text-green-500" />
                          <span>
                            {tool.toolName === 'add_task' && 'Task created'}
                            {tool.toolName === 'update_task' && 'Task updated'}
                            {tool.toolName === 'complete_task' && 'Task completed'}
                            {tool.toolName === 'delete_task' && 'Task deleted'}
                          </span>
                        </>
                      )}
                      {tool.status === 'error' && (
                        <span className="text-red-500">
                          Error: {tool.error || 'Operation failed'}
                        </span>
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
                  {streamingContent}
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
