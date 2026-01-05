"use client";

/**
 * FilterContext - Filter State Management with Backend Query Mapping
 * T028: Updated to map frontend filter state to backend query parameters
 *
 * Built following skills:
 * - @.claude/skills/custom/frontend-design-system (filter mapping patterns)
 *
 * Features:
 * - Frontend filter state management
 * - Backend query parameter mapping per FR-017
 * - URL synchronization support
 * - Pagination state management
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { FilterState } from "@/types/filter-schema";

const defaultFilterState: FilterState = {
  status: "all",
  priority: "all",
  selectedTags: [],
  dateRange: {},
  searchQuery: "",
  sortBy: "created",
  sortOrder: "desc",
};

// T028: Pagination state (FR-017a: default 50 per page)
interface PaginationState {
  page: number;
  limit: number;
  total: number;
  totalPages: number;
}

const defaultPaginationState: PaginationState = {
  page: 1,
  limit: 50, // FR-017a: default 50 per page
  total: 0,
  totalPages: 0,
};

// T028: Backend query parameters mapping per FR-017
export interface BackendQueryParams {
  status?: string; // "completed" | "active" | undefined (all)
  priority?: string; // "low" | "medium" | "high" | undefined (all)
  tag?: string[]; // array of tag names
  search?: string; // search query
  sort_by?: string; // "created" | "due_date" | "priority" | "title"
  order?: string; // "asc" | "desc"
  page?: number; // page number (1-indexed)
  limit?: number; // page size
  due_after?: string; // ISO 8601 date
  due_before?: string; // ISO 8601 date
}

interface FilterContextValue extends FilterState {
  // Filter setters
  setStatus: (status: FilterState["status"]) => void;
  setPriority: (priority: FilterState["priority"]) => void;
  setSelectedTags: (tags: string[]) => void;
  setDateRange: (range: FilterState["dateRange"]) => void;
  setSearchQuery: (query: string) => void;
  setSortBy: (sortBy: FilterState["sortBy"]) => void;
  setSortOrder: (order: FilterState["sortOrder"]) => void;
  resetFilters: () => void;

  // Pagination (T028)
  pagination: PaginationState;
  setPage: (page: number) => void;
  setLimit: (limit: number) => void;
  setPaginationMeta: (total: number, totalPages: number) => void;

  // Backend query mapping (T028)
  toBackendQuery: () => BackendQueryParams;
}

const FilterContext = createContext<FilterContextValue | undefined>(undefined);

export function FilterProvider({ children }: { children: ReactNode }) {
  const [filterState, setFilterState] = useState<FilterState>(defaultFilterState);
  const [pagination, setPagination] = useState<PaginationState>(defaultPaginationState);

  // Reset filters on component mount (page refresh)
  useEffect(() => {
    setFilterState(defaultFilterState);
    setPagination(defaultPaginationState);
  }, []);

  const setStatus = (status: FilterState["status"]) => {
    setFilterState((prev) => ({ ...prev, status }));
  };

  const setPriority = (priority: FilterState["priority"]) => {
    setFilterState((prev) => ({ ...prev, priority }));
  };

  const setSelectedTags = (selectedTags: string[]) => {
    setFilterState((prev) => ({ ...prev, selectedTags }));
  };

  const setDateRange = (dateRange: FilterState["dateRange"]) => {
    setFilterState((prev) => ({ ...prev, dateRange }));
  };

  const setSearchQuery = (searchQuery: string) => {
    setFilterState((prev) => ({ ...prev, searchQuery }));
  };

  const setSortBy = (sortBy: FilterState["sortBy"]) => {
    setFilterState((prev) => ({ ...prev, sortBy }));
  };

  const setSortOrder = (sortOrder: FilterState["sortOrder"]) => {
    setFilterState((prev) => ({ ...prev, sortOrder }));
  };

  const resetFilters = () => {
    setFilterState(defaultFilterState);
    setPagination({ ...defaultPaginationState }); // Also reset pagination
  };

  // T028: Pagination setters
  const setPage = (page: number) => {
    setPagination((prev) => ({ ...prev, page }));
  };

  const setLimit = (limit: number) => {
    setPagination((prev) => ({ ...prev, limit, page: 1 })); // Reset to page 1 when limit changes
  };

  const setPaginationMeta = (total: number, totalPages: number) => {
    setPagination((prev) => ({ ...prev, total, totalPages }));
  };

  // T028: Map frontend filter state to backend query parameters per FR-017
  const toBackendQuery = (): BackendQueryParams => {
    const params: BackendQueryParams = {};

    // Status filter (only send if not "all")
    if (filterState.status !== "all") {
      params.status = filterState.status;
    }

    // Priority filter (only send if not "all")
    if (filterState.priority !== "all") {
      params.priority = filterState.priority;
    }

    // Tags filter (array of tag names)
    if (filterState.selectedTags.length > 0) {
      params.tag = filterState.selectedTags;
    }

    // Search query
    if (filterState.searchQuery.trim()) {
      params.search = filterState.searchQuery.trim();
    }

    // Date range filters
    if (filterState.dateRange.start) {
      params.due_after = filterState.dateRange.start.toISOString();
    }
    if (filterState.dateRange.end) {
      params.due_before = filterState.dateRange.end.toISOString();
    }

    // Sort parameters - map frontend values to backend column names
    const sortByMapping: Record<string, string> = {
      created: "created_at",
      due_date: "due_date",
      priority: "priority",
      title: "title",
    };
    params.sort_by = sortByMapping[filterState.sortBy] || "created_at";
    params.order = filterState.sortOrder;

    // Pagination
    params.page = pagination.page;
    params.limit = pagination.limit;

    return params;
  };

  return (
    <FilterContext.Provider
      value={{
        ...filterState,
        setStatus,
        setPriority,
        setSelectedTags,
        setDateRange,
        setSearchQuery,
        setSortBy,
        setSortOrder,
        resetFilters,
        pagination,
        setPage,
        setLimit,
        setPaginationMeta,
        toBackendQuery,
      }}
    >
      {children}
    </FilterContext.Provider>
  );
}

export function useFilter() {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error("useFilter must be used within FilterProvider");
  }
  return context;
}
