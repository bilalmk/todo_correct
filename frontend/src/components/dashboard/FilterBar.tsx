"use client";

/**
 * FilterBar Component - Task Filtering and Search Controls
 * T031: Updated to integrate with TaskContext.fetchTasks and trigger API calls
 *
 * Built following skills:
 * - @.claude/skills/custom/frontend-design-system (Form controls, responsive design)
 * - @.claude/skills/custom/frontend-design-system/references/responsive-design-patterns
 *
 * Features:
 * - Search input with real-time filtering
 * - Status filter tabs (All, Active, Completed)
 * - Priority dropdown filter
 * - Tag multi-select filter
 * - Sort controls (by field and order)
 * - Reset filters button
 * - Responsive layout (stacks on mobile)
 * - Filter count indicator
 * - Real-time API integration (T031)
 */

import { useState, useEffect } from "react";
import { Search, X, SlidersHorizontal, Plus } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import { useFilter } from "@/contexts/FilterContext";
import { useTags } from "@/contexts/TagContext";
import { useTasks } from "@/contexts/TaskContext";

interface FilterBarProps {
  onCreateTask: () => void;
}

export function FilterBar({ onCreateTask }: FilterBarProps) {
  const {
    status,
    setStatus,
    priority,
    setPriority,
    selectedTags,
    setSelectedTags,
    searchQuery,
    setSearchQuery,
    sortBy,
    setSortBy,
    sortOrder,
    setSortOrder,
    resetFilters,
    pagination,
    setPaginationMeta,
    toBackendQuery,
  } = useFilter();

  const { tags } = useTags();
  const activeTags = tags.filter((t) => !t.archived);

  const { refreshTasks } = useTasks();

  const [showFilters, setShowFilters] = useState(false);

  // T031: Trigger API call when filters change
  useEffect(() => {
    const fetchWithFilters = async () => {
      const filters = toBackendQuery();
      await refreshTasks(filters);
    };

    // Debounce search query (wait 300ms after typing stops)
    const timeoutId = setTimeout(() => {
      fetchWithFilters();
    }, searchQuery ? 300 : 0);

    return () => clearTimeout(timeoutId);
  }, [status, priority, selectedTags, searchQuery, sortBy, sortOrder, pagination.page, pagination.limit]);

  // Count active filters
  const activeFilterCount =
    (priority !== "all" ? 1 : 0) +
    selectedTags.length +
    (searchQuery ? 1 : 0);

  return (
    <div className="space-y-4">
      {/* Top row: Search and Create button */}
      <div className="flex flex-col sm:flex-row gap-3">
        {/* Search */}
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-400" />
          <Input
            type="text"
            placeholder="Search tasks..."
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="pl-10 pr-10"
          />
          {searchQuery && (
            <button
              onClick={() => setSearchQuery("")}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-200"
              aria-label="Clear search"
            >
              <X className="h-4 w-4" />
            </button>
          )}
        </div>

        {/* Create Task button (frontend-design-system: 44px min-height, gradient) */}
        <Button
          onClick={onCreateTask}
          data-create-task
          className="bg-gradient-to-r from-primary to-secondary hover:opacity-90 transition-opacity duration-300 min-h-[44px] sm:min-h-0"
        >
          <Plus className="h-4 w-4 mr-2" />
          New Task
        </Button>

        {/* Filter toggle (mobile) */}
        <Button
          variant="outline"
          onClick={() => setShowFilters(!showFilters)}
          className="sm:hidden min-h-[44px]"
        >
          <SlidersHorizontal className="h-4 w-4 mr-2" />
          Filters
          {activeFilterCount > 0 && (
            <Badge className="ml-2 h-5 w-5 rounded-full p-0 flex items-center justify-center bg-primary">
              {activeFilterCount}
            </Badge>
          )}
        </Button>
      </div>

      {/* Filter controls */}
      <div className={`space-y-4 ${showFilters ? "block" : "hidden sm:block"}`}>
        {/* Status tabs */}
        <Tabs value={status} onValueChange={setStatus as any}>
          <TabsList className="w-full sm:w-auto">
            <TabsTrigger value="all" className="flex-1 sm:flex-none">
              All
            </TabsTrigger>
            <TabsTrigger value="active" className="flex-1 sm:flex-none">
              Active
            </TabsTrigger>
            <TabsTrigger value="completed" className="flex-1 sm:flex-none">
              Completed
            </TabsTrigger>
          </TabsList>
        </Tabs>

        {/* Advanced filters row */}
        <div className="flex flex-wrap gap-3">
          {/* Priority filter */}
          <Select value={priority} onValueChange={setPriority as any}>
            <SelectTrigger className="w-full sm:w-[150px]">
              <SelectValue placeholder="Priority" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priorities</SelectItem>
              <SelectItem value="high">High</SelectItem>
              <SelectItem value="medium">Medium</SelectItem>
              <SelectItem value="low">Low</SelectItem>
            </SelectContent>
          </Select>

          {/* Sort by */}
          <Select value={sortBy} onValueChange={setSortBy as any}>
            <SelectTrigger className="w-full sm:w-[150px]">
              <SelectValue placeholder="Sort by" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="created_at">Date Created</SelectItem>
              <SelectItem value="due_date">Due Date</SelectItem>
              <SelectItem value="priority">Priority</SelectItem>
              <SelectItem value="title">Title</SelectItem>
            </SelectContent>
          </Select>

          {/* Sort order */}
          <Select value={sortOrder} onValueChange={setSortOrder as any}>
            <SelectTrigger className="w-full sm:w-[120px]">
              <SelectValue placeholder="Order" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="asc">Ascending</SelectItem>
              <SelectItem value="desc">Descending</SelectItem>
            </SelectContent>
          </Select>

          {/* Tag filter */}
          <Popover>
            <PopoverTrigger asChild>
              <Button variant="outline" className="w-full sm:w-auto">
                Tags
                {selectedTags.length > 0 && (
                  <Badge className="ml-2 h-5 min-w-[20px] rounded-full px-1 bg-primary">
                    {selectedTags.length}
                  </Badge>
                )}
              </Button>
            </PopoverTrigger>
            <PopoverContent className="w-64" align="start">
              <div className="space-y-2">
                <h4 className="font-medium text-sm mb-3">Filter by tags</h4>
                {activeTags.length === 0 ? (
                  <p className="text-sm text-gray-500 dark:text-gray-400">
                    No tags available
                  </p>
                ) : (
                  <div className="space-y-2 max-h-48 overflow-y-auto">
                    {activeTags.map((tag) => (
                      <div key={tag.id} className="flex items-center space-x-2">
                        <Checkbox
                          checked={selectedTags.includes(tag.id.toString()) || selectedTags.includes(tag.id as any)}
                          onCheckedChange={(checked) => {
                            if (checked) {
                              setSelectedTags([...selectedTags, tag.id.toString()]);
                            } else {
                              setSelectedTags(
                                selectedTags.filter((id) => id !== tag.id.toString() && id !== tag.id)
                              );
                            }
                          }}
                        />
                        <span
                          className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium text-white"
                          style={{ backgroundColor: tag.color || "#3B82F6" }}
                        >
                          {tag.name}
                        </span>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </PopoverContent>
          </Popover>

          {/* Reset filters (frontend-design-system: orange/coral hover) */}
          {activeFilterCount > 0 && (
            <Button
              variant="ghost"
              onClick={resetFilters}
              className="w-full sm:w-auto text-primary hover:text-secondary dark:text-primary transition-colors duration-300"
            >
              <X className="h-4 w-4 mr-2" />
              Reset Filters
            </Button>
          )}
        </div>

        {/* Active filters summary */}
        {activeFilterCount > 0 && (
          <div className="flex flex-wrap gap-2 items-center text-sm">
            <span className="text-gray-600 dark:text-gray-400">Active filters:</span>
            {priority !== "all" && (
              <Badge variant="secondary">
                Priority: {priority}
                <button
                  onClick={() => setPriority("all")}
                  className="ml-1 hover:text-red-600"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )}
            {selectedTags.map((tagId) => {
              const tag = tags.find((t) => t.id.toString() === tagId.toString());
              if (!tag) return null;
              return (
                <Badge
                  key={tagId}
                  style={{ backgroundColor: tag.color || "#3B82F6", color: "white" }}
                >
                  {tag.name}
                  <button
                    onClick={() =>
                      setSelectedTags(selectedTags.filter((id) => id !== tagId))
                    }
                    className="ml-1 hover:opacity-80"
                  >
                    <X className="h-3 w-3" />
                  </button>
                </Badge>
              );
            })}
            {searchQuery && (
              <Badge variant="secondary">
                Search: "{searchQuery}"
                <button
                  onClick={() => setSearchQuery("")}
                  className="ml-1 hover:text-red-600"
                >
                  <X className="h-3 w-3" />
                </button>
              </Badge>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
