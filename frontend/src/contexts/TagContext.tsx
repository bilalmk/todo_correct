"use client";

/**
 * TagContext - Tag State Management with Real API Integration
 * T033-T037: Updated to use real backend API calls
 *
 * Built following skills:
 * - @.claude/skills/custom/frontend-design-system (React Context API patterns)
 *
 * Features:
 * - Real-time tag synchronization with backend
 * - Better Auth session integration for user_id
 * - Loading states for all operations
 * - Error handling with correlation IDs (T037)
 * - Usage count tracking
 */

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { toast } from "sonner";
import { Tag } from "@/types/tag-schema";
import { authClient } from "@/lib/auth-client";
import { apiClient } from "@/lib/api-client";
import { getUserUuidFromSession } from "@/lib/get-user-uuid";
import { useTasks } from "./TaskContext";

interface TagContextValue {
  tags: Tag[];
  isLoading: boolean;
  error: string | null; // T037
  refreshTags: () => Promise<void>; // T033
  addTag: (input: Omit<Tag, "id" | "usage_count" | "archived">) => Promise<void>;
  updateTag: (id: number, updates: Partial<Tag>) => Promise<void>;
  archiveTag: (id: number) => Promise<void>;
}

const TagContext = createContext<TagContextValue | undefined>(undefined);

export function TagProvider({ children }: { children: ReactNode }) {
  const [tags, setTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { tasks } = useTasks();

  // T033: Load tags from API using Better Auth session
  const refreshTags = async () => {
    try {
      setIsLoading(true);
      setError(null);

      // Get user UUID from JWT token
      const userId = await getUserUuidFromSession();

      console.log('[TagContext] Fetching tags for user:', userId);

      if (!userId) {
        // No session = not logged in, clear tags and return silently
        console.log('[TagContext] No user ID, clearing tags');
        setTags([]);
        setIsLoading(false);
        return;
      }

      // Fetch tags from backend API
      const fetchedTags = await apiClient.get<Tag[]>(`/api/v1/${userId}/tags`);
      console.log('[TagContext] Fetched tags:', fetchedTags);

      // Add usage_count and archived fields (client-side only)
      const tagsWithMetadata = Array.isArray(fetchedTags)
        ? fetchedTags.map(tag => ({
            ...tag,
            usage_count: tag.usage_count || 0,
            archived: tag.archived || false,
          }))
        : [];

      setTags(tagsWithMetadata);
    } catch (err: any) {
      const errorMessage = err.message || "Failed to load tags";
      setError(errorMessage);
      console.error("[TagContext] Failed to fetch tags:", err);

      // T037: Show error toast with correlation ID if available
      if (err.correlationId) {
        toast.error(`${errorMessage} (ID: ${err.correlationId.slice(0, 8)})`);
      } else {
        toast.error(errorMessage);
      }
    } finally {
      setIsLoading(false);
    }
  };

  // Load tags on mount
  useEffect(() => {
    refreshTags();
  }, []);

  // Update usage counts based on tasks (client-side calculation)
  // Backend returns task.tags as array of tag objects, not IDs
  useEffect(() => {
    if (!isLoading && tags.length > 0 && Array.isArray(tasks)) {
      setTags((prevTags) =>
        prevTags.map((tag) => {
          const usage_count = tasks.filter((task) =>
            Array.isArray(task.tags) && task.tags.some((t) => t.id === tag.id)
          ).length;
          return { ...tag, usage_count };
        })
      );
    }
  }, [tasks]);

  // T034: Create tag via API
  const addTag = async (input: Omit<Tag, "id" | "usage_count" | "archived">) => {
    try {
      setError(null);

      // Get user UUID from JWT token
      const userId = await getUserUuidFromSession();

      // DEBUG: Log UUID extraction
      console.log("DEBUG - Extracted UUID:", userId);

      if (!userId) {
        throw new Error("Please log in to create tags");
      }

      // Create tag via backend API
      const createdTag = await apiClient.post<Tag>(`/api/v1/${userId}/tags`, input);

      // Add tag to local state
      setTags((prev) => [...(Array.isArray(prev) ? prev : []), createdTag]);
    } catch (err: any) {
      const errorMessage = err.message || "Failed to create tag";
      setError(errorMessage);
      console.error("Failed to create tag:", err);

      // T037: Show error toast with correlation ID
      if (err.correlationId) {
        toast.error(`${errorMessage} (ID: ${err.correlationId.slice(0, 8)})`);
      } else {
        toast.error(errorMessage);
      }

      throw err; // Re-throw to let caller handle
    }
  };

  // T035: Update tag via API
  const updateTag = async (id: number, updates: Partial<Tag>) => {
    try {
      setError(null);

      // Get user UUID from JWT token
      const userId = await getUserUuidFromSession();

      if (!userId) {
        throw new Error("Please log in to update tags");
      }

      // Update tag via backend API
      const updatedTag = await apiClient.put<Tag>(`/api/v1/${userId}/tags/${id}`, updates);

      // Update local state
      setTags((prev) =>
        Array.isArray(prev) ? prev.map((tag) => (tag.id === id ? updatedTag : tag)) : []
      );
    } catch (err: any) {
      const errorMessage = err.message || "Failed to update tag";
      setError(errorMessage);
      console.error("Failed to update tag:", err);

      // T037: Show error toast with correlation ID
      if (err.correlationId) {
        toast.error(`${errorMessage} (ID: ${err.correlationId.slice(0, 8)})`);
      } else {
        toast.error(errorMessage);
      }

      throw err; // Re-throw to let caller handle
    }
  };

  // T036: Delete tag via API
  const archiveTag = async (id: number) => {
    try {
      setError(null);

      // Get user UUID from JWT token
      const userId = await getUserUuidFromSession();

      if (!userId) {
        throw new Error("Please log in to delete tags");
      }

      // Delete tag via backend API
      await apiClient.delete(`/api/v1/${userId}/tags/${id}`);

      // Remove from local state
      setTags((prev) => Array.isArray(prev) ? prev.filter((tag) => tag.id !== id) : []);
    } catch (err: any) {
      const errorMessage = err.message || "Failed to delete tag";
      setError(errorMessage);
      console.error("Failed to delete tag:", err);

      // T037: Show error toast with correlation ID
      if (err.correlationId) {
        toast.error(`${errorMessage} (ID: ${err.correlationId.slice(0, 8)})`);
      } else {
        toast.error(errorMessage);
      }

      throw err; // Re-throw to let caller handle
    }
  };

  // T037: Provider with error state and refresh capability
  return (
    <TagContext.Provider
      value={{
        tags,
        isLoading,
        error,
        refreshTags,
        addTag,
        updateTag,
        archiveTag,
      }}
    >
      {children}
    </TagContext.Provider>
  );
}

export function useTags() {
  const context = useContext(TagContext);
  if (!context) {
    throw new Error("useTags must be used within TagProvider");
  }
  return context;
}
