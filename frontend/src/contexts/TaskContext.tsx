"use client";

import {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { Task } from "@/types/task-schema";
import { MOCK_TASKS, delay } from "@/lib/mock-data";
import { getFromLocalStorage, setToLocalStorage } from "@/lib/utils";
import { v4 as uuidv4 } from "uuid";

const STORAGE_KEY = "todo_app_tasks";

interface TaskContextValue {
  tasks: Task[];
  isLoading: boolean;
  addTask: (input: Omit<Task, "id" | "created_at" | "updated_at">) => Promise<void>;
  updateTask: (id: string, updates: Partial<Task>) => Promise<void>;
  deleteTask: (id: string) => Promise<void>;
  completeTask: (id: string, completed: boolean) => Promise<void>;
}

const TaskContext = createContext<TaskContextValue | undefined>(undefined);

export function TaskProvider({ children }: { children: ReactNode }) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [isLoading, setIsLoading] = useState(true);

  // Load from localStorage on mount
  useEffect(() => {
    const loadTasks = async () => {
      await delay("initialLoad");
      const stored = getFromLocalStorage<Task[]>(STORAGE_KEY, []);
      if (stored.length > 0) {
        setTasks(stored);
      } else {
        setTasks(MOCK_TASKS);
      }
      setIsLoading(false);
    };

    loadTasks();
  }, []);

  // Sync to localStorage on tasks change
  useEffect(() => {
    if (!isLoading) {
      setToLocalStorage(STORAGE_KEY, tasks);
    }
  }, [tasks, isLoading]);

  const addTask = async (input: Omit<Task, "id" | "created_at" | "updated_at">) => {
    await delay("createTask");
    const now = new Date().toISOString();
    const newTask: Task = {
      ...input,
      id: uuidv4(),
      created_at: now,
      updated_at: now,
    };
    setTasks((prev) => [newTask, ...prev]);
  };

  const updateTask = async (id: string, updates: Partial<Task>) => {
    await delay("updateTask");
    setTasks((prev) =>
      prev.map((task) =>
        task.id === id
          ? { ...task, ...updates, updated_at: new Date().toISOString() }
          : task
      )
    );
  };

  const deleteTask = async (id: string) => {
    await delay("deleteTask");
    setTasks((prev) => prev.filter((task) => task.id !== id));
  };

  const completeTask = async (id: string, completed: boolean) => {
    await delay("updateTask");
    setTasks((prev) =>
      prev.map((task) =>
        task.id === id
          ? { ...task, completed, updated_at: new Date().toISOString() }
          : task
      )
    );
  };

  return (
    <TaskContext.Provider
      value={{ tasks, isLoading, addTask, updateTask, deleteTask, completeTask }}
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
