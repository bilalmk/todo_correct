/**
 * Zod validation schemas for ChatKit message validation
 * Feature: 009-chatkit-frontend
 * Task: T003a
 *
 * Purpose: Runtime validation of ChatKit SDK messages and responses
 */

import { z } from 'zod';

/**
 * Message role schema
 */
export const MessageRoleSchema = z.enum(['user', 'assistant', 'system']);

/**
 * Tool call status schema
 */
export const ToolCallStatusSchema = z.enum(['start', 'success', 'error']);

/**
 * MCP tool call schema
 */
export const ToolCallSchema = z.object({
  tool_name: z.string(),
  status: ToolCallStatusSchema,
  result: z.any().optional(),
  error: z.string().optional(),
});

/**
 * Chat message metadata schema
 */
export const MessageMetadataSchema = z.object({
  correlation_id: z.string().uuid().optional(),
  tool_calls: z.array(ToolCallSchema).optional(),
});

/**
 * Chat message schema
 * Validates incoming messages from ChatKit SDK
 */
export const MessageSchema = z.object({
  id: z.string().uuid(),
  role: MessageRoleSchema,
  content: z.string().min(1).max(10000, 'Message content exceeds 10,000 character limit'),
  timestamp: z.string().datetime(),
  metadata: MessageMetadataSchema.optional(),
});

/**
 * Conversation schema
 * Validates conversation data from backend API
 */
export const ConversationSchema = z.object({
  conversation_id: z.string().uuid(),
  user_id: z.string().uuid(),
  created_at: z.string().datetime(),
  updated_at: z.string().datetime(),
  deleted_at: z.string().datetime().nullable(),
});

/**
 * Tool result schema
 * Validates MCP tool.call.result events
 */
export const ToolResultSchema = z.object({
  type: z.literal('tool.call.result'),
  tool_name: z.string(),
  success: z.boolean(),
  result: z.any().optional(),
  error: z.string().optional(),
});

/**
 * Request context schema
 * Validates request metadata sent to backend
 */
export const RequestContextSchema = z.object({
  user_id: z.string().uuid(),
  correlation_id: z.string().uuid(),
  page_context: z.object({
    url: z.string().url(),
    title: z.string(),
    referrer: z.string(),
  }),
  timestamp: z.string().datetime(),
});

/**
 * ChatKit configuration schema
 * Validates useChatKit hook configuration
 */
export const ChatKitConfigSchema = z.object({
  api: z.object({
    url: z.string().url(),
    domainKey: z.string().min(1, 'OpenAI domain key is required'),
    fetch: z.function().optional(),
  }),
  pagination: z.object({
    limit: z.number().int().min(1).max(100),
    order: z.enum(['asc', 'desc']),
  }).optional(),
});

// Type exports inferred from schemas
export type MessageInput = z.input<typeof MessageSchema>;
export type MessageOutput = z.output<typeof MessageSchema>;
export type ConversationInput = z.input<typeof ConversationSchema>;
export type ConversationOutput = z.output<typeof ConversationSchema>;
export type ToolResultInput = z.input<typeof ToolResultSchema>;
export type ToolResultOutput = z.output<typeof ToolResultSchema>;
export type RequestContextInput = z.input<typeof RequestContextSchema>;
export type RequestContextOutput = z.output<typeof RequestContextSchema>;
export type ChatKitConfigInput = z.input<typeof ChatKitConfigSchema>;
export type ChatKitConfigOutput = z.output<typeof ChatKitConfigSchema>;
