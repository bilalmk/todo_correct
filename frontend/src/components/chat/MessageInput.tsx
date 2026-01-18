/**
 * Message Input Component
 * Feature: 009-chatkit-frontend
 * Task: T035 [US4]
 *
 * Purpose: Input field for sending chat messages
 * - Textarea with auto-resize
 * - Send button with keyboard shortcut (Enter to send, Shift+Enter for newline)
 * - Disabled state during streaming
 * - Character limit validation
 *
 * Usage:
 * ```tsx
 * <MessageInput
 *   onSend={(text) => sendMessage(text)}
 *   disabled={isStreaming}
 *   placeholder="Ask me to manage your tasks..."
 * />
 * ```
 */

'use client';

import { useState, useRef, KeyboardEvent } from 'react';
import { Send } from 'lucide-react';
import { Button } from '@/components/ui/button';

interface MessageInputProps {
  onSend: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
  maxLength?: number;
}

export function MessageInput({
  onSend,
  disabled = false,
  placeholder = 'Type a message...',
  maxLength = 1000,
}: MessageInputProps) {
  const [message, setMessage] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSend = () => {
    const trimmedMessage = message.trim();

    if (!trimmedMessage || disabled) {
      return;
    }

    // Send message
    onSend(trimmedMessage);

    // Clear input
    setMessage('');

    // Reset textarea height
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    // Enter without Shift = send message
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }

    // Shift+Enter = newline (default behavior, no action needed)
  };

  const handleChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    const newValue = e.target.value;

    // Enforce max length
    if (newValue.length <= maxLength) {
      setMessage(newValue);
    }

    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  };

  const characterCount = message.length;
  const isNearLimit = characterCount > maxLength * 0.8;
  const isAtLimit = characterCount >= maxLength;

  return (
    <div className="border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
      <div className="p-4">
        {/* Textarea */}
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={message}
            onChange={handleChange}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
            disabled={disabled}
            rows={1}
            className="
              w-full
              resize-none
              rounded-lg
              border border-gray-300 dark:border-gray-600
              bg-white dark:bg-gray-800
              px-4 py-3 pr-12
              text-sm
              placeholder:text-gray-400 dark:placeholder:text-gray-500
              focus:border-orange-500 focus:outline-none focus:ring-2 focus:ring-orange-500/20
              disabled:cursor-not-allowed disabled:bg-gray-100 dark:disabled:bg-gray-800/50
              disabled:text-gray-500
              max-h-32
              overflow-y-auto
            "
            style={{
              minHeight: '44px',
            }}
          />

          {/* Send button */}
          <Button
            onClick={handleSend}
            disabled={disabled || !message.trim()}
            size="sm"
            className="
              absolute right-2 bottom-2
              h-8 w-8 p-0
              rounded-lg
              bg-orange-500 hover:bg-orange-600
              disabled:bg-gray-300 dark:disabled:bg-gray-700
              disabled:cursor-not-allowed
            "
            aria-label="Send message"
          >
            <Send className="h-4 w-4 text-white" />
          </Button>
        </div>

        {/* Character count (show when near limit) */}
        {isNearLimit && (
          <div className="mt-2 text-xs text-right">
            <span className={isAtLimit ? 'text-red-500' : 'text-gray-500'}>
              {characterCount} / {maxLength}
            </span>
          </div>
        )}

        {/* Keyboard hint */}
        <div className="mt-2 text-xs text-gray-400 dark:text-gray-600">
          Press <kbd className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded">Enter</kbd> to send,{' '}
          <kbd className="px-1 py-0.5 bg-gray-100 dark:bg-gray-800 rounded">Shift+Enter</kbd> for new line
        </div>
      </div>
    </div>
  );
}
