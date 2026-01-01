/**
 * Task Entity Schema
 *
 * TypeScript type definition and Zod validation schema for Task entity.
 * Used for type safety and runtime validation in the frontend application.
 *
 * Feature: 004-frontend-design
 * Phase: UI-only implementation (no backend integration)
 */

import { z } from "zod"

/**
 * Task Priority Levels
 */
export const TaskPriority = {
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
} as const

export type TaskPriorityType = typeof TaskPriority[keyof typeof TaskPriority]

/**
 * Task Recurrence Patterns
 */
export const TaskRecurrence = {
  NONE: "none",
  DAILY: "daily",
  WEEKLY: "weekly",
  MONTHLY: "monthly",
} as const

export type TaskRecurrenceType = typeof TaskRecurrence[keyof typeof TaskRecurrence]

/**
 * Task TypeScript Interface
 *
 * Core entity representing a todo item with comprehensive task management features.
 */
export interface Task {
  // Identity
  id: string

  // Core fields
  title: string
  description?: string
  completed: boolean

  // Organization
  priority: TaskPriorityType
  tags: string[]  // Array of tag IDs

  // Scheduling
  due_date?: string       // ISO 8601 date string (YYYY-MM-DD)
  reminder_time?: string  // ISO 8601 datetime string
  recurrence: TaskRecurrenceType

  // Audit
  created_at: string  // ISO 8601 datetime string
  updated_at: string  // ISO 8601 datetime string
}

/**
 * Zod Validation Schema for Task
 *
 * Used for runtime validation in forms and API responses.
 */
export const taskSchema = z.object({
  id: z.string().uuid("Invalid task ID format"),

  title: z
    .string()
    .min(1, "Title is required")
    .max(200, "Title must be 200 characters or less")
    .refine((val) => val.trim().length > 0, "Title cannot be only whitespace"),

  description: z
    .string()
    .max(1000, "Description must be 1000 characters or less")
    .optional(),

  completed: z.boolean(),

  priority: z.enum([TaskPriority.LOW, TaskPriority.MEDIUM, TaskPriority.HIGH] as const, {
    errorMap: () => ({ message: "Priority must be low, medium, or high" }),
  }),

  tags: z.array(z.string()).default([]),

  due_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, "Due date must be in YYYY-MM-DD format")
    .optional(),

  reminder_time: z
    .string()
    .datetime("Reminder time must be a valid ISO 8601 datetime")
    .optional(),

  recurrence: z.enum(
    [TaskRecurrence.NONE, TaskRecurrence.DAILY, TaskRecurrence.WEEKLY, TaskRecurrence.MONTHLY] as const,
    {
      errorMap: () => ({ message: "Recurrence must be none, daily, weekly, or monthly" }),
    }
  ),

  created_at: z.string().datetime("Created at must be a valid ISO 8601 datetime"),
  updated_at: z.string().datetime("Updated at must be a valid ISO 8601 datetime"),
}).refine(
  (data) => {
    // If reminder_time is set, due_date must also be set
    if (data.reminder_time && !data.due_date) {
      return false
    }
    return true
  },
  {
    message: "Due date is required when reminder time is set",
    path: ["due_date"],
  }
)

/**
 * Zod Schema for Task Creation Form
 *
 * Omits auto-generated fields (id, created_at, updated_at).
 * Used in the task creation modal.
 */
export const createTaskSchema = taskSchema.omit({
  id: true,
  created_at: true,
  updated_at: true,
})

export type CreateTaskInput = z.infer<typeof createTaskSchema>

/**
 * Zod Schema for Task Update Form
 *
 * All fields except id are optional.
 * Used in the task edit modal.
 */
export const updateTaskSchema = taskSchema
  .omit({ id: true, created_at: true })
  .partial()

export type UpdateTaskInput = z.infer<typeof updateTaskSchema>

/**
 * Computed Task Fields
 *
 * These fields are derived from stored data, not persisted.
 */
export interface TaskComputed extends Task {
  isOverdue: boolean
  dueStatus: "overdue" | "today" | "upcoming" | "none"
}

/**
 * Helper: Compute derived fields for a task
 */
export function computeTaskFields(task: Task): TaskComputed {
  const now = new Date()
  const today = now.toISOString().split("T")[0]

  const isOverdue = !task.completed && task.due_date ? task.due_date < today : false

  let dueStatus: TaskComputed["dueStatus"] = "none"
  if (task.due_date) {
    if (isOverdue) {
      dueStatus = "overdue"
    } else if (task.due_date === today) {
      dueStatus = "today"
    } else {
      dueStatus = "upcoming"
    }
  }

  return {
    ...task,
    isOverdue,
    dueStatus,
  }
}

/**
 * Helper: Create a new task with auto-generated fields
 */
export function createTask(input: CreateTaskInput): Task {
  const now = new Date().toISOString()

  return {
    ...input,
    id: crypto.randomUUID(),
    created_at: now,
    updated_at: now,
  }
}

/**
 * Helper: Update a task with auto-updated fields
 */
export function updateTask(task: Task, input: UpdateTaskInput): Task {
  return {
    ...task,
    ...input,
    updated_at: new Date().toISOString(),
  }
}
