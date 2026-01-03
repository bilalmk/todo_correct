/**
 * API Type Definitions
 * T013: Frontend API types matching backend contracts (data-model.md)
 *
 * These types mirror the backend API responses and requests for type safety.
 */

// ============================================================================
// API Request Types
// ============================================================================

/**
 * Task Create Request
 * POST /api/v1/{user_id}/tasks
 */
export interface TaskCreateRequest {
  title: string;
  description?: string;
  priority?: "low" | "medium" | "high";
  due_date?: string; // ISO 8601 format
  tags?: string[]; // Tag IDs
  recurrence_pattern?: string; // daily, weekly, monthly
}

/**
 * Task Update Request
 * PATCH /api/v1/{user_id}/tasks/{id}
 */
export interface TaskUpdateRequest {
  title?: string;
  description?: string;
  priority?: "low" | "medium" | "high";
  due_date?: string; // ISO 8601 format
  completed?: boolean;
  recurrence_pattern?: string;
}

/**
 * Task Filter Parameters
 * Query parameters for GET /api/v1/{user_id}/tasks
 *
 * Maps frontend filter state to backend query parameters (FR-017)
 */
export interface TaskFilterParams {
  status?: "incomplete" | "complete"; // Map from frontend "active"/"completed"
  priority?: "low" | "medium" | "high";
  tag?: string[]; // Tag names or IDs
  search?: string; // Keyword search
  sort_by?: "due_date" | "created_at" | "priority" | "title";
  order?: "asc" | "desc";
  page?: number;
  limit?: number; // Default: 50 per page (FR-017a)
}

/**
 * Tag Create Request
 * POST /api/v1/{user_id}/tags
 */
export interface TagCreateRequest {
  name: string;
  color?: string; // Hex color code (default: #3B82F6)
}

/**
 * Tag Update Request
 * PUT /api/v1/{user_id}/tags/{id}
 */
export interface TagUpdateRequest {
  name?: string;
  color?: string; // Hex color code
}

// ============================================================================
// API Response Types
// ============================================================================

/**
 * API Error Response (from error-responses.contract.md)
 */
export interface ApiErrorResponse {
  error: string; // Human-readable error message
  code: string; // Machine-readable error code
  status: number; // HTTP status code
  request_id: string; // Correlation ID
  details?: Record<string, any>; // Additional error details (e.g., validation errors)
}

/**
 * Tag Response
 */
export interface Tag {
  id: string; // UUID
  user_id: string; // UUID
  name: string;
  color: string; // Hex color code
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
}

/**
 * Task Response
 */
export interface Task {
  id: string; // UUID
  user_id: string; // UUID
  title: string;
  description?: string;
  completed: boolean;
  priority: "low" | "medium" | "high";
  due_date?: string; // ISO 8601
  recurrence_pattern?: string; // daily, weekly, monthly
  created_at: string; // ISO 8601
  updated_at: string; // ISO 8601
  tags: Tag[]; // Associated tags
}

/**
 * Paginated Response
 * Generic pagination wrapper
 */
export interface PaginatedResponse<T> {
  items: T[]; // Array of items
  total: number; // Total count of items
  page: number; // Current page number
  limit: number; // Items per page
  total_pages: number; // Total number of pages
}

/**
 * User Response (from Better Auth session)
 */
export interface User {
  id: string; // UUID
  email: string;
  name?: string;
  emailVerified: boolean;
  image?: string;
  createdAt: string; // ISO 8601
  updatedAt: string; // ISO 8601
}

// ============================================================================
// Better Auth Session Types
// ============================================================================

/**
 * Better Auth Session (frontend)
 * From auth-client.getSession()
 */
export interface BetterAuthSession {
  user: {
    id: string; // Better Auth session ID (internal)
    uuid: string; // User UUID for API calls (from database user.uuid column)
    email: string;
    name?: string;
    emailVerified: boolean;
    image?: string;
  };
  session: {
    id: string; // Session ID
    userId: string; // Same as user.id (Better Auth internal ID)
    expiresAt: Date;
    createdAt: Date;
    token: string; // JWT token for backend API (EdDSA/Ed25519, includes uuid claim)
  };
}

// ============================================================================
// API Client Request Options
// ============================================================================

/**
 * API Request Options
 * Extended RequestInit with correlation ID support
 */
export interface ApiRequestOptions extends RequestInit {
  correlationId?: string; // Optional correlation ID (auto-generated if not provided)
}

// ============================================================================
// Helper Types
// ============================================================================

/**
 * Task Priority enum for type safety
 */
export enum TaskPriority {
  Low = "low",
  Medium = "medium",
  High = "high",
}

/**
 * Task Status enum for filtering
 */
export enum TaskStatus {
  Incomplete = "incomplete",
  Complete = "complete",
}

/**
 * Sort Order enum
 */
export enum SortOrder {
  Asc = "asc",
  Desc = "desc",
}

/**
 * Recurrence Pattern enum
 */
export enum RecurrencePattern {
  Daily = "daily",
  Weekly = "weekly",
  Monthly = "monthly",
}
