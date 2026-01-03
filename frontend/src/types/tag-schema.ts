/**
 * Tag Entity Schema
 *
 * TypeScript type definition and Zod validation schema for Tag entity.
 * Used for type safety and runtime validation in the frontend application.
 *
 * Feature: 004-frontend-design
 * Phase: UI-only implementation (no backend integration)
 */

import { z } from "zod"

/**
 * Tag TypeScript Interface
 *
 * Represents a categorization label with custom color for organizing tasks.
 * Supports soft delete (archiving) to preserve tags on existing tasks while
 * hiding them from the tag selector.
 */
export interface Tag {
  // Identity
  id: number  // Backend returns integer ID

  // Core fields
  name: string      // Display name (unique)
  color?: string     // Hex color code (e.g., "#3B82F6") - optional in backend

  // Metadata
  usage_count: number  // Number of tasks using this tag (client-side calculated)
  archived: boolean    // Soft delete flag (default false) - not in backend schema
}

/**
 * Zod Validation Schema for Tag
 *
 * Used for runtime validation in forms and data management.
 */
export const tagSchema = z.object({
  id: z.number().int().positive(), // Backend returns integer ID

  name: z
    .string()
    .min(1, "Tag name is required")
    .max(50, "Tag name must be 50 characters or less")
    .refine((val) => val.trim().length > 0, "Tag name cannot be only whitespace"),

  color: z
    .string()
    .regex(/^#[0-9A-Fa-f]{6}$/, "Color must be a valid hex color code (e.g., #3B82F6)")
    .transform((val) => val.toUpperCase())
    .optional(), // Optional in backend

  usage_count: z
    .number()
    .int("Usage count must be an integer")
    .nonnegative("Usage count cannot be negative")
    .default(0),

  archived: z.boolean().default(false),
})

/**
 * Zod Schema for Tag Creation Form
 *
 * Omits auto-generated/computed fields (id, usage_count, archived).
 * ID is generated from name as a slug.
 */
export const createTagSchema = z.object({
  name: z
    .string()
    .min(1, "Tag name is required")
    .max(50, "Tag name must be 50 characters or less")
    .refine((val) => val.trim().length > 0, "Tag name cannot be only whitespace"),

  color: z
    .string()
    .regex(/^#[0-9A-Fa-f]{6}$/, "Color must be a valid hex color code (e.g., #3B82F6)")
    .transform((val) => val.toUpperCase())
    .optional(), // Match backend - color is optional
})

export type CreateTagInput = z.infer<typeof createTagSchema>

/**
 * Zod Schema for Tag Update Form
 *
 * Allows updating name and color only (not id, usage_count, archived).
 */
export const updateTagSchema = z.object({
  name: z
    .string()
    .min(1, "Tag name is required")
    .max(50, "Tag name must be 50 characters or less")
    .refine((val) => val.trim().length > 0, "Tag name cannot be only whitespace")
    .optional(),

  color: z
    .string()
    .regex(/^#[0-9A-Fa-f]{6}$/, "Color must be a valid hex color code (e.g., #3B82F6)")
    .transform((val) => val.toUpperCase())
    .optional(),
})

export type UpdateTagInput = z.infer<typeof updateTagSchema>

/**
 * Preset Color Palette
 *
 * Recommended colors for quick tag creation (color picker preset options).
 */
export const PRESET_TAG_COLORS = [
  "#EF4444", // Red
  "#F59E0B", // Orange
  "#10B981", // Green
  "#3B82F6", // Blue
  "#8B5CF6", // Purple
  "#EC4899", // Pink
  "#6366F1", // Indigo
  "#14B8A6", // Teal
  "#F97316", // Deep Orange
  "#A855F7", // Violet
] as const

/**
 * Helper: Generate slug from tag name
 *
 * Converts "Work Tasks" -> "work-tasks"
 */
export function generateTagSlug(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/[^a-z0-9]+/g, "-") // Replace non-alphanumeric with hyphens
    .replace(/^-+|-+$/g, "")     // Remove leading/trailing hyphens
}

/**
 * Helper: Create a new tag with auto-generated fields
 */
export function createTag(input: CreateTagInput): Tag {
  return {
    id: generateTagSlug(input.name),
    name: input.name,
    color: input.color,
    usage_count: 0,
    archived: false,
  }
}

/**
 * Helper: Update a tag
 *
 * Note: Updating name does NOT update id (slug) to avoid breaking
 * references in existing tasks.
 */
export function updateTag(tag: Tag, input: UpdateTagInput): Tag {
  return {
    ...tag,
    ...input,
  }
}

/**
 * Helper: Archive a tag (soft delete)
 *
 * Archived tags remain visible on existing task cards but are hidden
 * from the tag selector for new/edited tasks.
 */
export function archiveTag(tag: Tag): Tag {
  return {
    ...tag,
    archived: true,
  }
}

/**
 * Helper: Check if a tag is in use
 */
export function isTagInUse(tag: Tag): boolean {
  return tag.usage_count > 0
}

/**
 * Helper: Update tag usage counts
 *
 * Call this function when tasks are added/removed/updated to keep
 * usage_count accurate.
 */
export function updateTagUsageCounts(tags: Tag[], tasks: { tags: string[] }[]): Tag[] {
  // Count how many times each tag ID appears in tasks
  const usageCounts = new Map<string, number>()

  tasks.forEach((task) => {
    task.tags.forEach((tagId) => {
      usageCounts.set(tagId, (usageCounts.get(tagId) || 0) + 1)
    })
  })

  // Update usage_count for each tag
  return tags.map((tag) => ({
    ...tag,
    usage_count: usageCounts.get(tag.id) || 0,
  }))
}
