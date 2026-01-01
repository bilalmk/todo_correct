"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { Tag } from "@/types/tag-schema";
import { MOCK_TAGS, delay } from "@/lib/mock-data";
import { getFromLocalStorage, setToLocalStorage } from "@/lib/utils";
import { useTasks } from "./TaskContext";

const STORAGE_KEY = "todo_app_tags";

interface TagContextValue {
  tags: Tag[];
  isLoading: boolean;
  addTag: (input: Omit<Tag, "id" | "usage_count" | "archived">) => Promise<void>;
  updateTag: (id: string, updates: Partial<Tag>) => Promise<void>;
  archiveTag: (id: string) => Promise<void>;
}

const TagContext = createContext<TagContextValue | undefined>(undefined);

export function TagProvider({ children }: { children: ReactNode }) {
  const [tags, setTags] = useState<Tag[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const { tasks } = useTasks();

  // Load from localStorage on mount
  useEffect(() => {
    const loadTags = async () => {
      await delay("initialLoad");
      const stored = getFromLocalStorage<Tag[]>(STORAGE_KEY, []);
      if (stored.length > 0) {
        setTags(stored);
      } else {
        setTags(MOCK_TAGS);
      }
      setIsLoading(false);
    };

    loadTags();
  }, []);

  // Update usage counts based on tasks
  useEffect(() => {
    if (!isLoading) {
      setTags((prevTags) =>
        prevTags.map((tag) => {
          const usage_count = tasks.filter((task) =>
            task.tags.includes(tag.id)
          ).length;
          return { ...tag, usage_count };
        })
      );
    }
  }, [tasks, isLoading]);

  // Sync to localStorage on tags change
  useEffect(() => {
    if (!isLoading) {
      setToLocalStorage(STORAGE_KEY, tags);
    }
  }, [tags, isLoading]);

  const addTag = async (input: Omit<Tag, "id" | "usage_count" | "archived">) => {
    await delay("createTask");
    const id = input.name.toLowerCase().replace(/\s+/g, "-");
    const newTag: Tag = {
      ...input,
      id,
      usage_count: 0,
      archived: false,
    };
    setTags((prev) => [...prev, newTag]);
  };

  const updateTag = async (id: string, updates: Partial<Tag>) => {
    await delay("updateTask");
    setTags((prev) =>
      prev.map((tag) => (tag.id === id ? { ...tag, ...updates } : tag))
    );
  };

  const archiveTag = async (id: string) => {
    await delay("deleteTask");
    setTags((prev) =>
      prev.map((tag) => (tag.id === id ? { ...tag, archived: true } : tag))
    );
  };

  return (
    <TagContext.Provider
      value={{ tags, isLoading, addTag, updateTag, archiveTag }}
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
