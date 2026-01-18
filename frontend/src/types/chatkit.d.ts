/**
 * TypeScript type definitions for OpenAI ChatKit SDK
 * Feature: 009-chatkit-frontend
 * Task: T003
 *
 * The ChatKit SDK is loaded via CDN script in layout.tsx
 * These types provide IDE support and type safety for the global ChatKit object
 */

// Declare global ChatKit SDK types
declare global {
  interface Window {
    ChatKit?: {
      // ChatKit SDK exports (if needed for direct access)
    };
  }
}

// Export to make this a module
export {};

/**
 * Chat message role types
 */
export type MessageRole = 'user' | 'assistant' | 'system';

/**
 * Tool call status from MCP events
 */
export type ToolCallStatus = 'start' | 'success' | 'error';

/**
 * MCP tool call information
 */
export interface ToolCall {
  tool_name: string;
  status: ToolCallStatus;
  result?: any;
  error?: string;
}

/**
 * Chat message structure
 * Matches the ChatKit SDK message format
 */
export interface ChatMessage {
  id: string;
  role: MessageRole;
  content: string;
  timestamp: string;
  metadata?: {
    correlation_id?: string;
    tool_calls?: ToolCall[];
  };
}

/**
 * Streaming state tracking
 */
export interface StreamingState {
  isStreaming: boolean;
  partialContent: string;
  startTime: string;
  firstTokenTime: string | null;
}

/**
 * Request context metadata
 */
export interface RequestContext {
  user_id: string;
  correlation_id: string;
  page_context: {
    url: string;
    title: string;
    referrer: string;
  };
  timestamp: string;
}

/**
 * ChatKit configuration options
 * Based on research.md ChatKit integration patterns
 */
export interface ChatKitConfig {
  api: {
    url: string;
    domainKey: string;
    fetch?: typeof fetch;
  };
  pagination?: {
    limit: number;
    order: 'asc' | 'desc';
  };
}

/**
 * ChatKit hook return type
 * Simplified interface for useChatKit hook
 */
export interface UseChatKitReturn {
  messages: ChatMessage[];
  sendMessage: (text: string) => Promise<void>;
  isStreaming: boolean;
  isLoading: boolean;
  error: string | null;
  loadMore: () => Promise<void>;
  hasMore: boolean;
}

/**
 * useChatKit hook type
 * Note: Actual implementation comes from ChatKit SDK loaded via CDN
 */
export type UseChatKit = (config: ChatKitConfig) => UseChatKitReturn;
