"use client";

/**
 * TaskContext - Task State Management with Real API Integration
 * T022-T027: Updated to use real backend API calls
 * T008: Enhanced to emit TaskEvent after operations (Feature: 009-chatkit-frontend)
 *
 * Built following skills:
 * - @.claude/skills/custom/frontend-design-system (React Context API integration)
 *
 * Features:
 * - Real-time task synchronization with backend
 * - Better Auth session integration for user_id
 * - Loading states for all operations
 * - Error handling with correlation IDs
 * - Optimistic UI updates
 * - Event emission for chatbot-dashboard sync (T008)
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { toast } from "sonner";
import { Task } from "@/types/task-schema";
import { authClient } from "@/lib/auth-client";
import { apiClient } from "@/lib/api-client";
import { getUserUuidFromSession } from "@/lib/get-user-uuid";
import { BackendQueryParams } from "@/contexts/FilterContext";
import { emitTaskEvent } from "@/lib/events/task-events"; // T008: Event system

// T029: Paginated response interface
interface PaginatedTaskResponse {
  items: Task[];
  total: number;
  page: number;
  limit: number;
  total_pages: number;
}

interface TaskContextValue {
  tasks: Task[];
  isLoading: boolean;
  error: string | null;
  totalTasks: number; // T029: Total count for pagination
  totalPages: number; // T029: Total pages from backend
  currentPage: number; // T029: Current page number
  pageLimit: number; // T029: Items per page
  refreshTasks: (filters?: BackendQueryParams) => Promise<void>; // T029: Accept filter params
  addTask: (input: Omit<Task, "id" | "created_at" | "updated_at">) => Promise<Task>; // Returns created task
  updateTask: (id: number, updates: Partial<Task>) => Promise<void>;
  deleteTask: (id: number) => Promise<void>;
  completeTask: (id: number, completed: boolean) => Promise<void>;
}

const TaskContext = createContext<TaskContextValue | undefined>(undefined);

export function TaskProvider({ children }: { children: ReactNode }) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [totalTasks, setTotalTasks] = useState<number>(0); // T029: Total count
  const [totalPages, setTotalPages] = useState<number>(0); // T029: Total pages
  const [currentPage, setCurrentPage] = useState<number>(1); // T029: Current page
  const [pageLimit, setPageLimit] = useState<number>(50); // T029: Items per page

  // T029: Load tasks from API with optional filter/pagination parameters
  const refreshTasks = async (filters?: BackendQueryParams) => {
    try {
      setIsLoading(true);
      setError(null);

      // Get user UUID from JWT token
      const userId = await getUserUuidFromSession();

      if (!userId) {
        // No session = not logged in, clear tasks and return silently
        setTasks([]);
        setTotalTasks(0);
        setIsLoading(false);
        return;
      }

      // T029: Construct query string from filter parameters
      let endpoint = `/api/v1/${userId}/tasks`;
      if (filters) {
        const queryParams = new URLSearchParams();

        // Add each filter parameter if present
        if (filters.status) queryParams.append("status", filters.status);
        if (filters.priority) queryParams.append("priority", filters.priority);
        if (filters.tag && filters.tag.length > 0) {
          filters.tag.forEach((tag) => queryParams.append("tag", tag));
        }
        if (filters.search) queryParams.append("search", filters.search);
        if (filters.sort_by) queryParams.append("sort_by", filters.sort_by);
        if (filters.order) queryParams.append("order", filters.order);
        if (filters.page) queryParams.append("page", filters.page.toString());
        if (filters.limit) queryParams.append("limit", filters.limit.toString());
        if (filters.due_after) queryParams.append("due_after", filters.due_after);
        if (filters.due_before) queryParams.append("due_before", filters.due_before);

        const queryString = queryParams.toString();
        if (queryString) {
          endpoint += `?${queryString}`;
        }
      }

      // Fetch tasks from backend API with filters
      // FIXME: Backend currently returns plain array, not paginated response
      const response = await apiClient.get<Task[] | PaginatedTaskResponse>(endpoint);

      console.log('[TaskContext] API Response:', {
        endpoint,
        isArray: Array.isArray(response),
        response: response,
      });

      // Handle both array response (current backend) and paginated response (future)
      if (Array.isArray(response)) {
        // Backend returns plain array (current implementation)
        setTasks(response);
        setTotalTasks(response.length);
        setTotalPages(1);
        setCurrentPage(1);
        setPageLimit(50);
      } else {
        // Backend returns paginated response (future implementation)
        setTasks(response.items || []);
        setTotalTasks(response.total || 0);
        setTotalPages(response.total_pages || 0);
        setCurrentPage(response.page || 1);
        setPageLimit(response.limit || 50);
      }
    } catch (err: any) {
      const errorMessage = err.message || "Failed to load tasks";
      setError(errorMessage);
      console.error("Failed to fetch tasks:", err);

      // Show error toast with correlation ID if available
      if (err.correlationId) {
        toast.error(`${errorMessage} (ID: ${err.correlationId.slice(0, 8)})`);
      } else {
        toast.error(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Load tasks on mount
  useEffect(() => {
    refreshTasks();
  }, []);

  // T023: Create task via API - returns created task for tag assignment
  // T008: Emit TaskEvent after successful creation
  const addTask = async (input: Omit<Task, "id" | "created_at" | "updated_at" | "tags">): Promise<Task> => {
    try {
      setError(null);

      // Get user UUID from JWT token
      const userId = await getUserUuidFromSession();

      if (!userId) {
        throw new Error("Please log in to create tasks");
      }

      // Debug: Log what we're sending
      console.log('[TaskContext] Creating task with data:', JSON.stringify(input, null, 2));

      // Create task via backend API
      const createdTask = await apiClient.post<Task>(`/api/v1/${userId}/tasks`, input);

      // Optimistic UI update: add task to the beginning of the list
      setTasks((prev) => [createdTask, ...(Array.isArray(prev) ? prev : [])]);

      // T008: Emit task.created event for chatbot-dashboard sync
      emitTaskEvent({
        taskId: createdTask.id.toString(),
        operation: 'task.created',
        userId: userId,
        timestamp: new Date().toISOString(),
        metadata: {
          source: 'dashboard',
        },
      });

      return createdTask; // Return for tag assignment
    } catch (err: any) {
      const errorMessage = err.message || "Failed to create task";
      setError(errorMessage);
      console.error("Failed to create task:", err);

      // Show error toast with correlation ID
      if (err.correlationId) {
        toast.error(`${errorMessage} (ID: ${err.correlationId.slice(0, 8)})`);
      } else {
        toast.error(errorMessage);
      }

      throw err; // Re-throw to let caller handle
    }
  };

  // T024: Update task via API
  // T008: Emit TaskEvent after successful update
  const updateTask = async (id: number, updates: Partial<Task>) => {
    try {
      setError(null);

      // Get user UUID from JWT token
      const userId = await getUserUuidFromSession();

      if (!userId) {
        throw new Error("Please log in to update tasks");
      }

      // Update task via backend API
      const updatedTask = await apiClient.patch<Task>(`/api/v1/${userId}/tasks/${id}`, updates);

      // Update local state
      setTasks((prev) =>
        Array.isArray(prev) ? prev.map((task) => (task.id === id ? updatedTask : task)) : []
      );

      // T008: Emit task.updated event for chatbot-dashboard sync
      emitTaskEvent({
        taskId: id.toString(),
        operation: 'task.updated',
        userId: userId,
        timestamp: new Date().toISOString(),
        metadata: {
          source: 'dashboard',
        },
      });
    } catch (err: any) {
      const errorMessage = err.message || "Failed to update task";
      setError(errorMessage);
      console.error("Failed to update task:", err);

      // Show error toast with correlation ID
      if (err.correlationId) {
        toast.error(`${errorMessage} (ID: ${err.correlationId.slice(0, 8)})`);
      } else {
        toast.error(errorMessage);
      }

      throw err; // Re-throw to let caller handle
    }
  };

  // T025: Delete task via API
  // T008: Emit TaskEvent after successful deletion
  const deleteTask = async (id: number) => {
    try {
      setError(null);

      // Get user UUID from JWT token
      const userId = await getUserUuidFromSession();

      if (!userId) {
        throw new Error("Please log in to delete tasks");
      }

      // Delete task via backend API
      await apiClient.delete(`/api/v1/${userId}/tasks/${id}`);

      // Remove from local state
      setTasks((prev) => Array.isArray(prev) ? prev.filter((task) => task.id !== id) : []);

      // T008: Emit task.deleted event for chatbot-dashboard sync
      emitTaskEvent({
        taskId: id.toString(),
        operation: 'task.deleted',
        userId: userId,
        timestamp: new Date().toISOString(),
        metadata: {
          source: 'dashboard',
        },
      });
    } catch (err: any) {
      const errorMessage = err.message || "Failed to delete task";
      setError(errorMessage);
      console.error("Failed to delete task:", err);

      // Show error toast with correlation ID
      if (err.correlationId) {
        toast.error(`${errorMessage} (ID: ${err.correlationId.slice(0, 8)})`);
      } else {
        toast.error(errorMessage);
      }

      throw err; // Re-throw to let caller handle
    }
  };

  // T026: Toggle task completion via API
  // T008: Emit TaskEvent after successful completion toggle
  const completeTask = async (id: number, completed: boolean) => {
    try {
      setError(null);

      // Get user UUID from JWT token
      const userId = await getUserUuidFromSession();

      if (!userId) {
        throw new Error("Please log in to complete tasks");
      }

      // Toggle completion via backend API
      const updatedTask = await apiClient.patch<Task>(
        `/api/v1/${userId}/tasks/${id}/complete`,
        { completed }
      );

      // Update local state
      setTasks((prev) =>
        Array.isArray(prev) ? prev.map((task) => (task.id === id ? updatedTask : task)) : []
      );

      // T008: Emit task.completed event for chatbot-dashboard sync
      emitTaskEvent({
        taskId: id.toString(),
        operation: 'task.completed',
        userId: userId,
        timestamp: new Date().toISOString(),
        metadata: {
          source: 'dashboard',
        },
      });
    } catch (err: any) {
      const errorMessage = err.message || "Failed to update task status";
      setError(errorMessage);
      console.error("Failed to toggle task completion:", err);

      // Show error toast with correlation ID
      if (err.correlationId) {
        toast.error(`${errorMessage} (ID: ${err.correlationId.slice(0, 8)})`);
      } else {
        toast.error(errorMessage);
      }

      throw err; // Re-throw to let caller handle
    }
  };

  // T027/T029: Provider with error state, pagination, and refresh capability
  return (
    <TaskContext.Provider
      value={{
        tasks,
        isLoading,
        error,
        totalTasks, // T029: Expose total count for pagination
        totalPages, // T029: Expose total pages
        currentPage, // T029: Expose current page
        pageLimit, // T029: Expose page limit
        refreshTasks,
        addTask,
        updateTask,
        deleteTask,
        completeTask,
      }}
    >
      {children}
    </TaskContext.Provider>
  );
}

export function useTasks() {
  const context = useContext(TaskContext);
  if (!context) {
    throw new Error("useTasks must be used within TaskProvider");
  }
  return context;
}
