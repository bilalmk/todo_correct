"use client";

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

interface FilterContextValue extends FilterState {
  setStatus: (status: FilterState["status"]) => void;
  setPriority: (priority: FilterState["priority"]) => void;
  setSelectedTags: (tags: string[]) => void;
  setDateRange: (range: FilterState["dateRange"]) => void;
  setSearchQuery: (query: string) => void;
  setSortBy: (sortBy: FilterState["sortBy"]) => void;
  setSortOrder: (order: FilterState["sortOrder"]) => void;
  resetFilters: () => void;
}

const FilterContext = createContext<FilterContextValue | undefined>(undefined);

export function FilterProvider({ children }: { children: ReactNode }) {
  const [filterState, setFilterState] = useState<FilterState>(defaultFilterState);

  // Reset filters on component mount (page refresh)
  useEffect(() => {
    setFilterState(defaultFilterState);
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
