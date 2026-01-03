/**
 * API Client for authenticated requests to FastAPI backend.
 *
 * This module provides utilities for making authenticated API requests
 * from Next.js frontend to FastAPI backend using Better Auth JWT tokens.
 *
 * Usage:
 *   Copy this file to: frontend/lib/api-client.ts
 *
 * Example:
 *   import { getTasks, createTask } from "@/lib/api-client"
 *
 *   const tasks = await getTasks(userId)
 *   const newTask = await createTask(userId, { title: "New task" })
 */

import { authClient } from "@/lib/auth-client"

// API base URL from environment variables
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000"

/**
 * Error thrown when API request fails
 */
export class APIError extends Error {
  constructor(
    public status: number,
    public statusText: string,
    message: string
  ) {
    super(message)
    this.name = "APIError"
  }
}

/**
 * Get JWT token from current Better Auth session.
 *
 * @returns JWT token string or null if not authenticated
 */
async function getAuthToken(): Promise<string | null> {
  const session = await authClient.getSession()

  // Better Auth client returns session in session.data.session
  if (!session?.data?.session) {
    return null
  }

  // Better Auth JWT plugin provides token in session
  return session.data.session.token
}

/**
 * Make authenticated API request to FastAPI backend.
 *
 * This function:
 * 1. Gets JWT token from Better Auth session
 * 2. Adds Authorization header with Bearer token
 * 3. Makes the API request
 * 4. Handles errors appropriately
 *
 * @param endpoint - API endpoint path (e.g., "/api/v1/user123/tasks")
 * @param options - Fetch options (method, body, headers, etc.)
 * @returns Response data as JSON
 * @throws APIError if request fails
 * @throws Error if not authenticated
 */
export async function apiRequest<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  // Get authentication token
  const token = await getAuthToken()

  if (!token) {
    throw new Error("No authentication token available. Please log in.")
  }

  // Build full URL
  const url = `${API_BASE_URL}${endpoint}`

  // Make request with Authorization header
  const response = await fetch(url, {
    ...options,
    headers: {
      "Authorization": `Bearer ${token}`,
      "Content-Type": "application/json",
      ...options.headers,
    },
  })

  // Handle errors
  if (!response.ok) {
    // Try to get error details from response
    let errorMessage = response.statusText
    try {
      const errorData = await response.json()
      errorMessage = errorData.detail || errorMessage
    } catch {
      // If response is not JSON, use statusText
    }

    throw new APIError(response.status, response.statusText, errorMessage)
  }

  // Return parsed JSON
  return response.json()
}

// ============================================================================
// Task API Functions
// ============================================================================

export interface Task {
  id: number
  user_id: string
  title: string
  description: string | null
  completed: boolean
  created_at: string
  updated_at: string
}

export interface TaskCreate {
  title: string
  description?: string
}

export interface TaskUpdate {
  title?: string
  description?: string
  completed?: boolean
}

/**
 * Get all tasks for a user.
 *
 * @param userId - User ID (must match authenticated user)
 * @returns Array of tasks
 */
export async function getTasks(userId: string): Promise<Task[]> {
  return apiRequest<Task[]>(`/api/v1/${userId}/tasks`)
}

/**
 * Get a specific task by ID.
 *
 * @param userId - User ID (must match authenticated user)
 * @param taskId - Task ID
 * @returns Task object
 */
export async function getTask(userId: string, taskId: number): Promise<Task> {
  return apiRequest<Task>(`/api/v1/${userId}/tasks/${taskId}`)
}

/**
 * Create a new task.
 *
 * @param userId - User ID (must match authenticated user)
 * @param taskData - Task data (title and optional description)
 * @returns Created task
 */
export async function createTask(
  userId: string,
  taskData: TaskCreate
): Promise<Task> {
  return apiRequest<Task>(`/api/v1/${userId}/tasks`, {
    method: "POST",
    body: JSON.stringify(taskData),
  })
}

/**
 * Update an existing task.
 *
 * @param userId - User ID (must match authenticated user)
 * @param taskId - Task ID
 * @param taskData - Task data to update
 * @returns Updated task
 */
export async function updateTask(
  userId: string,
  taskId: number,
  taskData: TaskUpdate
): Promise<Task> {
  return apiRequest<Task>(`/api/v1/${userId}/tasks/${taskId}`, {
    method: "PATCH",
    body: JSON.stringify(taskData),
  })
}

/**
 * Delete a task.
 *
 * @param userId - User ID (must match authenticated user)
 * @param taskId - Task ID
 */
export async function deleteTask(
  userId: string,
  taskId: number
): Promise<void> {
  return apiRequest(`/api/v1/${userId}/tasks/${taskId}`, {
    method: "DELETE",
  })
}

/**
 * Toggle task completion status.
 *
 * @param userId - User ID (must match authenticated user)
 * @param taskId - Task ID
 * @param completed - New completion status
 * @returns Updated task
 */
export async function toggleTaskCompletion(
  userId: string,
  taskId: number,
  completed: boolean
): Promise<Task> {
  return updateTask(userId, taskId, { completed })
}

// ============================================================================
// React Hook Example (Optional)
// ============================================================================

/**
 * Example React hook for using API client with error handling.
 *
 * Usage:
 *   const { data: tasks, loading, error } = useAPIData(() => getTasks(userId))
 *
 * Note: You can use libraries like SWR or React Query for more features.
 */
import { useState, useEffect } from "react"

export function useAPIData<T>(
  fetcher: () => Promise<T>,
  dependencies: any[] = []
) {
  const [data, setData] = useState<T | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<Error | null>(null)

  useEffect(() => {
    let cancelled = false

    async function fetchData() {
      try {
        setLoading(true)
        setError(null)
        const result = await fetcher()
        if (!cancelled) {
          setData(result)
        }
      } catch (err) {
        if (!cancelled) {
          setError(err instanceof Error ? err : new Error(String(err)))
        }
      } finally {
        if (!cancelled) {
          setLoading(false)
        }
      }
    }

    fetchData()

    return () => {
      cancelled = true
    }
  }, dependencies)

  return { data, loading, error }
}
