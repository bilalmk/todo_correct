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
  arrayMove,
} from "@dnd-kit/sortable";

import { TaskCard } from "./TaskCard";
import { TaskModal } from "./TaskModal";
import { DeleteDialog } from "./DeleteDialog";
import { EmptyState } from "./EmptyState"; // T057
import { Skeleton } from "@/components/ui/skeleton";
import { Task } from "@/types/task-schema";
import { useTasks } from "@/contexts/TaskContext";
import { useFilter } from "@/contexts/FilterContext";
import { TaskFormData } from "@/lib/validation-schemas";
import { toast } from "sonner";
import { reorderTasks } from "@/lib/api-client";
import { getUserUuidFromSession } from "@/lib/get-user-uuid";

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

  // T048: Optimistic UI state for drag-and-drop
  const [optimisticTasks, setOptimisticTasks] = useState<Task[] | null>(null);

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

  // T048: Check if filters are active (T050 requirement)
  const hasActiveFilters = useMemo(() => {
    return status !== "all" ||
      priority !== "all" ||
      selectedTags.length > 0 ||
      dateRange.start !== null ||
      dateRange.end !== null ||
      searchQuery !== "";
  }, [status, priority, selectedTags, dateRange, searchQuery]);

  // Filter and sort tasks (T048: use optimistic tasks during drag operations)
  const filteredTasks = useMemo(() => {
    console.log('[TaskList] Filtering tasks:', {
      tasksCount: Array.isArray(tasks) ? tasks.length : 'not array',
      status,
      priority,
      selectedTags,
      searchQuery,
      tasks: tasks,
    });

    // T048: Use optimistic tasks if available (during reorder operation)
    const sourceTasks = optimisticTasks || tasks;

    // Safety check: ensure tasks is an array
    if (!Array.isArray(sourceTasks)) {
      console.log('[TaskList] Tasks is not array, returning empty');
      return [];
    }

    let filtered = [...sourceTasks];

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
      originalCount: sourceTasks.length,
      filteredCount: filtered.length,
      filtered: filtered,
    });

    return filtered;
  }, [tasks, optimisticTasks, status, priority, selectedTags, dateRange, searchQuery, sortBy, sortOrder]);

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
    // T050: Prevent drag if filters are active
    if (hasActiveFilters) {
      toast.error("Task reordering is only available in the default unfiltered view", {
        description: "Please clear all filters to enable drag-and-drop reordering.",
      });
      return;
    }

    setActiveId(event.active.id as number);
  };

  const handleDragEnd = async (event: DragEndEvent) => {
    const { active, over } = event;
    setActiveId(null);

    // T050: Abort if filters are active
    if (hasActiveFilters) {
      return;
    }

    // Abort if dropped outside droppable area or same position
    if (!over || active.id === over.id) {
      return;
    }

    // Find indices
    const oldIndex = filteredTasks.findIndex((t) => t.id === active.id);
    const newIndex = filteredTasks.findIndex((t) => t.id === over.id);

    if (oldIndex === -1 || newIndex === -1) {
      return;
    }

    // T048: Optimistic UI update (immediate visual feedback)
    const reorderedTasks = arrayMove(filteredTasks, oldIndex, newIndex);
    setOptimisticTasks(reorderedTasks);

    try {
      // Get user ID for API call
      const userId = await getUserUuidFromSession();
      if (!userId) {
        throw new Error("User not authenticated");
      }

      // T046: Call reorder API with new task IDs order
      const taskIds = reorderedTasks.map((t) => t.id);

      // T049: Set timeout for API call (5 seconds)
      const timeoutPromise = new Promise((_, reject) =>
        setTimeout(() => reject(new Error("Request timeout")), 5000)
      );

      await Promise.race([
        reorderTasks(userId, taskIds),
        timeoutPromise,
      ]);

      // Success: refresh tasks from backend to confirm new order
      await refreshTasks();
      setOptimisticTasks(null); // Clear optimistic state

      toast.success("Tasks reordered successfully");
    } catch (error) {
      // T049: Error handling - revert optimistic UI and show error
      console.error("Failed to reorder tasks:", error);
      setOptimisticTasks(null); // Revert to original order

      toast.error("Failed to reorder tasks", {
        description: error instanceof Error ? error.message : "Please try again",
      });
    }
  };

  const handleDragCancel = () => {
    setActiveId(null);
    // T049: Revert optimistic update on cancel
    setOptimisticTasks(null);
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

  // T057: Professional empty state with CTA
  if (filteredTasks.length === 0) {
    const hasFilters = searchQuery || selectedTags.length > 0 || dateRange.start || dateRange.end || status !== "all" || priority !== "all";
    const isEmptyList = !tasks || tasks.length === 0;

    return (
      <EmptyState
        title={hasFilters ? "No tasks found" : isEmptyList ? "No tasks yet" : "No tasks match your filters"}
        description={
          hasFilters
            ? "Try adjusting your filters or search query to find what you're looking for."
            : isEmptyList
            ? "Create your first task to get started organizing your work."
            : "Try changing your filter settings to see more tasks."
        }
        ctaText="Create Task"
        onCtaClick={isEmptyList ? () => {
          // Trigger parent create task modal
          const createButton = document.querySelector('[data-create-task]') as HTMLButtonElement;
          createButton?.click();
        } : undefined}
      />
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

        {/* T047: Drag Overlay with lifted card shadow effect */}
        <DragOverlay>
          {activeTask ? (
            <div
              className="opacity-90 cursor-grabbing"
              style={{ boxShadow: '0 10px 25px rgba(0, 0, 0, 0.15)' }}
            >
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
