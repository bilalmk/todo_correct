"use client";

/**
 * TaskList Component - Filtered and Sorted Task Display
 *
 * Built following skills:
 * - @.claude/skills/custom/frontend-design-system (List patterns, filtering logic)
 *
 * Features:
 * - Filters tasks by status, priority, tags, date range, search query
 * - Sorts tasks by various criteria (created_at, due_date, priority, title)
 * - Empty states with helpful messages
 * - Loading skeletons
 * - Animations with Framer Motion
 * - Task completion toggle
 * - Edit and delete handlers
 */

import { useState, useMemo } from "react";
import { AnimatePresence } from "framer-motion";
import { parseISO, isWithinInterval } from "date-fns";
import { Inbox } from "lucide-react";
import {
  DndContext,
  DragOverlay,
  closestCenter,
  PointerSensor,
  TouchSensor,
  useSensor,
  useSensors,
  DragStartEvent,
  DragEndEvent,
} from "@dnd-kit/core";
import {
  SortableContext,
  verticalListSortingStrategy,
} from "@dnd-kit/sortable";

import { TaskCard } from "./TaskCard";
import { TaskModal } from "./TaskModal";
import { DeleteDialog } from "./DeleteDialog";
import { Skeleton } from "@/components/ui/skeleton";
import { Task } from "@/types/task-schema";
import { useTasks } from "@/contexts/TaskContext";
import { useFilter } from "@/contexts/FilterContext";
import { TaskFormData } from "@/lib/validation-schemas";
import { toast } from "sonner";

export function TaskList() {
  const { tasks, isLoading, refreshTasks, updateTask, deleteTask, completeTask } = useTasks();
  const {
    status,
    priority,
    selectedTags,
    dateRange,
    searchQuery,
    sortBy,
    sortOrder,
  } = useFilter();

  const [editingTask, setEditingTask] = useState<Task | null>(null);
  const [deletingTask, setDeletingTask] = useState<Task | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [activeId, setActiveId] = useState<number | null>(null);

  // Drag and drop sensors
  const sensors = useSensors(
    useSensor(PointerSensor, {
      activationConstraint: {
        distance: 8, // 8px movement required to start drag
      },
    }),
    useSensor(TouchSensor, {
      activationConstraint: {
        delay: 200, // 200ms hold required for touch
        tolerance: 5,
      },
    })
  );

  // Filter and sort tasks
  const filteredTasks = useMemo(() => {
    console.log('[TaskList] Filtering tasks:', {
      tasksCount: Array.isArray(tasks) ? tasks.length : 'not array',
      status,
      priority,
      selectedTags,
      searchQuery,
      tasks: tasks,
    });

    // Safety check: ensure tasks is an array
    if (!Array.isArray(tasks)) {
      console.log('[TaskList] Tasks is not array, returning empty');
      return [];
    }

    let filtered = [...tasks];

    // Filter by status
    if (status === "active") {
      filtered = filtered.filter((t) => !t.completed);
    } else if (status === "completed") {
      filtered = filtered.filter((t) => t.completed);
    }

    // Filter by priority
    if (priority !== "all") {
      filtered = filtered.filter((t) => t.priority === priority);
    }

    // Filter by tags (tags are now objects with id, name, color)
    if (selectedTags.length > 0) {
      filtered = filtered.filter((t) =>
        Array.isArray(t.tags) && selectedTags.some((tagId) =>
          t.tags.some((tag) => tag.id.toString() === tagId || tag.name === tagId)
        )
      );
    }

    // Filter by date range
    if (dateRange.start || dateRange.end) {
      filtered = filtered.filter((t) => {
        if (!t.due_date) return false;
        const taskDate = parseISO(t.due_date);

        if (dateRange.start && dateRange.end) {
          return isWithinInterval(taskDate, {
            start: dateRange.start,
            end: dateRange.end,
          });
        } else if (dateRange.start) {
          return taskDate >= dateRange.start;
        } else if (dateRange.end) {
          return taskDate <= dateRange.end;
        }
        return true;
      });
    }

    // Filter by search query
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (t) =>
          t.title.toLowerCase().includes(query) ||
          (t.description && t.description.toLowerCase().includes(query))
      );
    }

    // Sort
    filtered.sort((a, b) => {
      let comparison = 0;

      switch (sortBy) {
        case "title":
          comparison = a.title.localeCompare(b.title);
          break;
        case "priority":
          const priorityOrder = { high: 3, medium: 2, low: 1 };
          const aPriority = a.priority ? priorityOrder[a.priority] : 0;
          const bPriority = b.priority ? priorityOrder[b.priority] : 0;
          comparison = bPriority - aPriority;
          break;
        case "due_date":
          if (!a.due_date && !b.due_date) comparison = 0;
          else if (!a.due_date) comparison = 1;
          else if (!b.due_date) comparison = -1;
          else comparison = parseISO(a.due_date).getTime() - parseISO(b.due_date).getTime();
          break;
        case "created":
        default:
          comparison = parseISO(b.created_at).getTime() - parseISO(a.created_at).getTime();
          break;
      }

      return sortOrder === "asc" ? comparison : -comparison;
    });

    console.log('[TaskList] After filtering and sorting:', {
      originalCount: tasks.length,
      filteredCount: filtered.length,
      filtered: filtered,
    });

    return filtered;
  }, [tasks, status, priority, selectedTags, dateRange, searchQuery, sortBy, sortOrder]);

  // Handlers
  const handleComplete = async (taskId: number, completed: boolean) => {
    try {
      await completeTask(taskId, completed);
      toast.success(completed ? "Task completed!" : "Task marked as incomplete");
    } catch (error) {
      toast.error("Failed to update task");
    }
  };

  const handleEdit = (task: Task) => {
    setEditingTask(task);
  };

  const handleDelete = (task: Task) => {
    setDeletingTask(task);
  };

  const handleTaskUpdate = async (data: TaskFormData) => {
    if (!editingTask) return;

    setIsSubmitting(true);
    try {
      // Update task fields
      await updateTask(editingTask.id, {
        title: data.title,
        description: data.description || undefined,
        priority: data.priority,
        due_date: data.due_date || undefined,
        reminder_at: data.reminder_at || undefined,
        recurrence_pattern: data.recurrence_pattern || undefined,
        tags: [], // Backend doesn't accept tags in update, must use separate endpoint
      });

      // Handle tag updates if changed
      if (data.tags) {
        const { getUserUuidFromSession } = await import("@/lib/get-user-uuid");
        const { apiClient } = await import("@/lib/api-client");
        const userId = await getUserUuidFromSession();

        if (userId) {
          // Get current tag IDs from task
          const currentTagIds = Array.isArray(editingTask.tags)
            ? editingTask.tags.map(t => t.id)
            : [];
          const newTagIds = data.tags;

          // Find tags to add and remove
          const tagsToAdd = newTagIds.filter(id => !currentTagIds.includes(id));
          const tagsToRemove = currentTagIds.filter(id => !newTagIds.includes(id));

          // Remove old tags
          for (const tagId of tagsToRemove) {
            try {
              await apiClient.delete(`/api/v1/${userId}/tasks/${editingTask.id}/tags/${tagId}`);
            } catch (err) {
              console.error(`Failed to remove tag ${tagId}:`, err);
            }
          }

          // Add new tags
          for (const tagId of tagsToAdd) {
            try {
              await apiClient.post(`/api/v1/${userId}/tasks/${editingTask.id}/tags`, {
                tag_id: tagId,
              });
            } catch (err) {
              console.error(`Failed to add tag ${tagId}:`, err);
            }
          }
        }
      }

      // Refresh task list to show updated tags
      await refreshTasks();

      toast.success("Task updated successfully");
      setEditingTask(null);
    } catch (error) {
      console.error("Failed to update task:", error);
      toast.error("Failed to update task");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleConfirmDelete = async () => {
    if (!deletingTask) return;

    setIsSubmitting(true);
    try {
      await deleteTask(deletingTask.id);
      toast.success("Task deleted successfully");
      setDeletingTask(null);
    } catch (error) {
      toast.error("Failed to delete task");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Drag and drop handlers
  const handleDragStart = (event: DragStartEvent) => {
    setActiveId(event.active.id as number);
  };

  const handleDragEnd = (_event: DragEndEvent) => {
    setActiveId(null);

    // Show toast notification that reordering is coming soon (FR-047)
    toast.info("Reordering functionality coming soon", {
      description: "Drag-and-drop visual feedback is enabled, but task reordering will be implemented in a future update.",
    });
  };

  const handleDragCancel = () => {
    setActiveId(null);
  };

  // Get the active task being dragged
  const activeTask = activeId ? tasks.find((t) => t.id === activeId) : null;

  // Loading state
  if (isLoading) {
    return (
      <div className="space-y-4">
        {[1, 2, 3, 4, 5].map((i) => (
          <div key={i} className="rounded-lg border p-5 space-y-3">
            <Skeleton className="h-5 w-2/3" />
            <Skeleton className="h-4 w-full" />
            <div className="flex gap-2">
              <Skeleton className="h-6 w-16" />
              <Skeleton className="h-6 w-20" />
              <Skeleton className="h-6 w-16" />
            </div>
          </div>
        ))}
      </div>
    );
  }

  // Empty state
  if (filteredTasks.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-16 px-4 text-center">
        <div className="w-16 h-16 rounded-full bg-gray-100 dark:bg-gray-800 flex items-center justify-center mb-4">
          <Inbox className="h-8 w-8 text-gray-400 dark:text-gray-600" />
        </div>
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
          {searchQuery || selectedTags.length > 0 || dateRange.start || dateRange.end
            ? "No tasks found"
            : (!tasks || tasks.length === 0)
            ? "No tasks yet"
            : "No tasks match your filters"}
        </h3>
        <p className="text-sm text-gray-600 dark:text-gray-400 max-w-sm">
          {searchQuery || selectedTags.length > 0 || dateRange.start || dateRange.end
            ? "Try adjusting your filters or search query"
            : (!tasks || tasks.length === 0)
            ? "Create your first task to get started"
            : "Try changing your filter settings"}
        </p>
      </div>
    );
  }

  return (
    <>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCenter}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
        onDragCancel={handleDragCancel}
      >
        <SortableContext
          items={filteredTasks.map((t) => t.id)}
          strategy={verticalListSortingStrategy}
        >
          <div className="space-y-4">
            <AnimatePresence mode="popLayout">
              {filteredTasks.map((task) => (
                <TaskCard
                  key={task.id}
                  task={task}
                  onComplete={(completed) => handleComplete(task.id, completed)}
                  onEdit={() => handleEdit(task)}
                  onDelete={() => handleDelete(task)}
                />
              ))}
            </AnimatePresence>
          </div>
        </SortableContext>

        {/* Drag Overlay */}
        <DragOverlay>
          {activeTask ? (
            <div className="opacity-90 cursor-grabbing">
              <TaskCard
                task={activeTask}
                onComplete={() => {}}
                onEdit={() => {}}
                onDelete={() => {}}
              />
            </div>
          ) : null}
        </DragOverlay>
      </DndContext>

      {/* Edit Modal */}
      <TaskModal
        open={!!editingTask}
        onClose={() => setEditingTask(null)}
        onSubmit={handleTaskUpdate}
        task={editingTask}
        isLoading={isSubmitting}
      />

      {/* Delete Confirmation */}
      <DeleteDialog
        open={!!deletingTask}
        onClose={() => setDeletingTask(null)}
        onConfirm={handleConfirmDelete}
        taskTitle={deletingTask?.title || ""}
        isLoading={isSubmitting}
      />
    </>
  );
}
