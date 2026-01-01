/**
 * Filter State Schema
 *
 * TypeScript type definition for filter and sort state (ephemeral UI state).
 * Not persisted to localStorage per spec.md FR-037a (resets on page refresh).
 *
 * Feature: 004-frontend-design
 * Phase: UI-only implementation
 */

/**
 * Filter Status Options
 */
export const FilterStatus = {
  ALL: "all",
  ACTIVE: "active",
  COMPLETED: "completed",
} as const

export type FilterStatusType = typeof FilterStatus[keyof typeof FilterStatus]

/**
 * Filter Priority Options
 */
export const FilterPriority = {
  ALL: "all",
  LOW: "low",
  MEDIUM: "medium",
  HIGH: "high",
} as const

export type FilterPriorityType = typeof FilterPriority[keyof typeof FilterPriority]

/**
 * Sort Field Options
 */
export const SortField = {
  CREATED: "created",
  DUE_DATE: "due_date",
  PRIORITY: "priority",
  TITLE: "title",
} as const

export type SortFieldType = typeof SortField[keyof typeof SortField]

/**
 * Sort Order Options
 */
export const SortOrder = {
  ASC: "asc",
  DESC: "desc",
} as const

export type SortOrderType = typeof SortOrder[keyof typeof SortOrder]

/**
 * Date Range Filter
 */
export interface DateRange {
  start?: Date
  end?: Date
}

/**
 * FilterState Interface
 *
 * Represents the current filter and search state for the task list.
 * Managed in FilterContext, resets to defaults on page refresh.
 */
export interface FilterState {
  // Filters
  status: FilterStatusType
  priority: FilterPriorityType
  selectedTags: string[]  // Array of tag IDs
  dateRange: DateRange
  searchQuery: string

  // Sort
  sortBy: SortFieldType
  sortOrder: SortOrderType
}

/**
 * Default Filter State
 *
 * Used on app initialization and when "Clear All Filters" is clicked.
 */
export const DEFAULT_FILTER_STATE: FilterState = {
  status: FilterStatus.ALL,
  priority: FilterPriority.ALL,
  selectedTags: [],
  dateRange: {},
  searchQuery: "",
  sortBy: SortField.CREATED,
  sortOrder: SortOrder.DESC,
}

/**
 * Helper: Check if any filters are active
 *
 * Used to show/hide "Clear All Filters" button and active filter count.
 */
export function hasActiveFilters(state: FilterState): boolean {
  return (
    state.status !== FilterStatus.ALL ||
    state.priority !== FilterPriority.ALL ||
    state.selectedTags.length > 0 ||
    state.dateRange.start !== undefined ||
    state.dateRange.end !== undefined ||
    state.searchQuery.trim().length > 0
  )
}

/**
 * Helper: Count active filters
 *
 * Used for badge displaying number of active filters.
 */
export function countActiveFilters(state: FilterState): number {
  let count = 0

  if (state.status !== FilterStatus.ALL) count++
  if (state.priority !== FilterPriority.ALL) count++
  if (state.selectedTags.length > 0) count++
  if (state.dateRange.start || state.dateRange.end) count++
  if (state.searchQuery.trim().length > 0) count++

  return count
}

/**
 * Helper: Reset filters to default
 *
 * Used when "Clear All Filters" is clicked or on page refresh.
 */
export function resetFilters(): FilterState {
  return { ...DEFAULT_FILTER_STATE }
}
