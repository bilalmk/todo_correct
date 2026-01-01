"use client";

/**
 * Dashboard Page - Main Tasks View
 *
 * Built following skills:
 * - @.claude/skills/mjs/building-nextjs-apps (Next.js 16 patterns)
 * - @.claude/skills/custom/frontend-design-system (Component composition)
 *
 * Features:
 * - FilterBar for search and filtering
 * - TaskList with all task cards
 * - TaskModal for creating new tasks
 * - Integration with TaskContext and FilterContext
 * - Responsive layout
 * - Loading states
 * - Empty states
 */

import { useState } from "react";
import { toast } from "sonner";
import { FilterBar } from "@/components/dashboard/FilterBar";
import { TaskList } from "@/components/dashboard/TaskList";
import { TaskModal } from "@/components/dashboard/TaskModal";
import { useTasks } from "@/contexts/TaskContext";
import { TaskFormData } from "@/lib/validation-schemas";

export default function DashboardPage() {
  const { addTask } = useTasks();
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);

  const handleCreateTask = async (data: TaskFormData) => {
    setIsSubmitting(true);
    try {
      await addTask({
        title: data.title,
        description: data.description || undefined,
        completed: false,
        priority: data.priority,
        due_date: data.due_date || undefined,
        reminder_time: data.reminder_time || undefined,
        recurrence: data.recurrence,
        tags: data.tags,
      });
      toast.success("Task created successfully!");
      setIsCreateModalOpen(false);
    } catch (error) {
      toast.error("Failed to create task. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Page header */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-2">
          My Tasks
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Organize and track your tasks efficiently
        </p>
      </div>

      {/* Filter bar */}
      <FilterBar onCreateTask={() => setIsCreateModalOpen(true)} />

      {/* Task list */}
      <TaskList />

      {/* Create task modal */}
      <TaskModal
        open={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateTask}
        isLoading={isSubmitting}
      />
    </div>
  );
}
