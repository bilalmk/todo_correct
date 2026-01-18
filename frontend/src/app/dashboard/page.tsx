"use client";

/**
 * Dashboard Page - Main Tasks View
 * T021: Updated to use Better Auth session for user_id
 * T032: Added URL query parameter synchronization for bookmarkable filter states
 *
 * Built following skills:
 * - @.claude/skills/mjs/building-nextjs-apps (Next.js 16 patterns)
 * - @.claude/skills/custom/frontend-design-system (Component composition)
 * - @.claude/skills/custom/betterauth-fastapi-jwt-bridge (Session integration)
 *
 * Features:
 * - Better Auth session integration
 * - FilterBar for search and filtering
 * - TaskList with all task cards
 * - TaskModal for creating new tasks
 * - Integration with TaskContext and FilterContext
 * - URL query parameter synchronization (T032)
 * - Pagination UI (T030)
 * - Responsive layout
 * - Loading states
 * - Empty states
 */

import { useState, useEffect } from "react";
import { useRouter, useSearchParams } from "next/navigation";
import { toast } from "sonner";
import { FilterBar } from "@/components/dashboard/FilterBar";
import { TaskList } from "@/components/dashboard/TaskList";
import { TaskModal } from "@/components/dashboard/TaskModal";
import { TaskStats } from "@/components/dashboard/TaskStats"; // T056
import { Pagination } from "@/components/Pagination"; // T030
import { FloatingChatButton } from "@/components/chat/FloatingChatButton"; // T015 [US1]
import { ChatBotPopup } from "@/components/chat/ChatBotPopup"; // T015 [US1]
import { ChatInterface } from "@/components/chat/ChatInterface"; // T036 [US4]
import { useTasks } from "@/contexts/TaskContext";
import { useFilter } from "@/contexts/FilterContext"; // T032
import { TaskFormData } from "@/lib/validation-schemas";
import { authClient } from "@/lib/auth-client";
import { getUserUuidFromSession } from "@/lib/get-user-uuid";
import { onTaskEvent } from "@/lib/events/task-events"; // T046 [US2]

export default function DashboardPage() {
  const { tasks, addTask, refreshTasks, totalTasks, totalPages: taskTotalPages, currentPage: taskCurrentPage, pageLimit: taskPageLimit } = useTasks(); // T056: Added tasks for TaskStats
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
    pagination,
    setPage,
    setLimit,
    toBackendQuery, // T032: Get current filter query
  } = useFilter(); // T032

  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [userId, setUserId] = useState<string | null>(null);
  const [isLoadingSession, setIsLoadingSession] = useState(true);
  const [isChatbotOpen, setIsChatbotOpen] = useState(false); // T015 [US1]: Chatbot popup state
  const router = useRouter();
  const searchParams = useSearchParams(); // T032

  // T021: Get user_id from Better Auth session for API calls
  useEffect(() => {
    async function loadSession() {
      try {
        const session = await authClient.getSession();

        if (!session?.data?.user) {
          // No session found, redirect to login
          router.push("/auth/login");
          return;
        }

        // Extract user UUID from JWT token for API calls
        const userIdFromSession = await getUserUuidFromSession();
        if (!userIdFromSession) {
          toast.error("Failed to get user ID. Please log in again.");
          router.push("/auth/login");
          return;
        }

        setUserId(userIdFromSession);

        // Store user_id in context/state for use in API calls
        // In Phase 5 (T022-T027), this user_id will be passed to TaskContext
        // for constructing API URLs like: /api/v1/{user_id}/tasks
      } catch (error) {
        console.error("Failed to load session:", error);
        toast.error("Session expired. Please log in again.");
        router.push("/auth/login");
      } finally {
        setIsLoadingSession(false);
      }
    }

    loadSession();
  }, [router]);

  // T032: Initialize filters from URL params on mount
  useEffect(() => {
    const urlStatus = searchParams.get("status");
    const urlPriority = searchParams.get("priority");
    const urlTags = searchParams.get("tags");
    const urlSearch = searchParams.get("search");
    const urlSortBy = searchParams.get("sort_by");
    const urlOrder = searchParams.get("order");
    const urlPage = searchParams.get("page");
    const urlLimit = searchParams.get("limit");

    if (urlStatus && ["all", "active", "completed"].includes(urlStatus)) {
      setStatus(urlStatus as any);
    }
    if (urlPriority && ["all", "low", "medium", "high"].includes(urlPriority)) {
      setPriority(urlPriority as any);
    }
    if (urlTags) {
      setSelectedTags(urlTags.split(","));
    }
    if (urlSearch) {
      setSearchQuery(urlSearch);
    }
    if (urlSortBy && ["created", "due_date", "priority", "title"].includes(urlSortBy)) {
      setSortBy(urlSortBy as any);
    }
    if (urlOrder && ["asc", "desc"].includes(urlOrder)) {
      setSortOrder(urlOrder as any);
    }
    if (urlPage && !isNaN(Number(urlPage))) {
      setPage(Number(urlPage));
    }
    if (urlLimit && !isNaN(Number(urlLimit))) {
      setLimit(Number(urlLimit));
    }
  }, []); // Run only once on mount

  // T032: Sync filters to URL params for bookmarkable states
  useEffect(() => {
    const params = new URLSearchParams();

    if (status !== "all") params.set("status", status);
    if (priority !== "all") params.set("priority", priority);
    if (selectedTags.length > 0) params.set("tags", selectedTags.join(","));
    if (searchQuery.trim()) params.set("search", searchQuery.trim());
    if (sortBy !== "created") params.set("sort_by", sortBy);
    if (sortOrder !== "desc") params.set("order", sortOrder);
    if (pagination.page !== 1) params.set("page", pagination.page.toString());
    if (pagination.limit !== 50) params.set("limit", pagination.limit.toString());

    const queryString = params.toString();
    const newUrl = queryString ? `/dashboard?${queryString}` : "/dashboard";

    // Update URL without triggering a full page reload
    router.replace(newUrl, { scroll: false });
  }, [status, priority, selectedTags, searchQuery, sortBy, sortOrder, pagination.page, pagination.limit]);

  // T046 [US2]: Listen for task events from chatbot and refresh task list
  useEffect(() => {
    const cleanup = onTaskEvent((detail) => {
      console.log('[Dashboard] Task event received:', detail);

      // Only refresh if event came from chatbot (avoid refresh loop)
      if (detail.metadata?.source === 'chatbot') {
        console.log('[Dashboard] Refreshing tasks due to chatbot operation');
        refreshTasks(toBackendQuery());
      }
    });

    return cleanup; // Cleanup event listener on unmount
  }, [refreshTasks, toBackendQuery]);

  const handleCreateTask = async (data: TaskFormData) => {
    if (!userId) {
      toast.error("Session not loaded. Please try again.");
      return;
    }

    setIsSubmitting(true);
    try {
      // T021: user_id is now available for API calls
      // Create task first (backend doesn't accept tags in TaskCreate)
      // Sanitize data: remove empty strings and convert to undefined
      const taskData: any = {
        title: data.title.trim(),
        completed: false,
      };

      // Only include optional fields if they have values
      if (data.description && data.description.trim()) {
        taskData.description = data.description.trim();
      }
      if (data.priority) {
        taskData.priority = data.priority;
      }
      if (data.due_date && data.due_date.trim()) {
        // Convert datetime-local (YYYY-MM-DDTHH:mm) to ISO 8601 (YYYY-MM-DDTHH:mm:ss.sssZ)
        taskData.due_date = new Date(data.due_date).toISOString();
      }
      if (data.reminder_at && data.reminder_at.trim()) {
        // Convert datetime-local (YYYY-MM-DDTHH:mm) to ISO 8601 (YYYY-MM-DDTHH:mm:ss.sssZ)
        taskData.reminder_at = new Date(data.reminder_at).toISOString();
      }
      if (data.recurrence_pattern) {
        taskData.recurrence_pattern = data.recurrence_pattern;
      }

      const createdTask = await addTask(taskData);

      // Assign tags if any were selected
      if (data.tags && data.tags.length > 0) {
        console.log(`[Dashboard] Assigning ${data.tags.length} tags to task ${createdTask.id}`);

        const { apiClient } = await import("@/lib/api-client");

        for (const tagId of data.tags) {
          try {
            await apiClient.post(`/api/v1/${userId}/tasks/${createdTask.id}/tags`, {
              tag_id: tagId,
            });
            console.log(`[Dashboard] Assigned tag ${tagId} to task ${createdTask.id}`);
          } catch (tagError: any) {
            console.error(`[Dashboard] Failed to assign tag ${tagId}:`, tagError);
            // Continue with other tags even if one fails
          }
        }
      }

      // Refresh task list to get the newly created task with tags
      await refreshTasks(toBackendQuery());

      toast.success("Task created successfully!");
      setIsCreateModalOpen(false);
    } catch (error) {
      console.error("[Dashboard] Failed to create task:", error);
      toast.error("Failed to create task. Please try again.");
    } finally {
      setIsSubmitting(false);
    }
  };

  // Show loading state while session is being loaded (T030 - frontend-design-system)
  if (isLoadingSession) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <p className="text-gray-600 dark:text-gray-400">Loading your tasks...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Page header */}
      <div className="space-y-2">
        <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
          My Tasks
        </h1>
        <p className="text-gray-600 dark:text-gray-400">
          Organize and track your tasks efficiently
        </p>
      </div>

      {/* T056: Task statistics section with clear spacing */}
      <section className="pb-6 border-b border-gray-200 dark:border-gray-800">
        <TaskStats tasks={Array.isArray(tasks) ? tasks : []} />
      </section>

      {/* T056: Filter section with clear spacing */}
      <section className="pb-6 border-b border-gray-200 dark:border-gray-800">
        <FilterBar onCreateTask={() => setIsCreateModalOpen(true)} />
      </section>

      {/* T056: Task list section with clear spacing */}
      <section className="min-h-[400px]">
        <TaskList />
      </section>

      {/* T030: Pagination */}
      <Pagination
        currentPage={taskCurrentPage || pagination.page}
        totalPages={taskTotalPages || pagination.totalPages}
        totalItems={totalTasks}
        pageSize={taskPageLimit || pagination.limit}
        onPageChange={setPage}
        onPageSizeChange={setLimit}
      />

      {/* Create task modal */}
      <TaskModal
        open={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateTask}
        isLoading={isSubmitting}
      />

      {/* T015 [US1]: Floating Chat Button (FAB) - triggers chatbot popup */}
      <FloatingChatButton onClick={() => setIsChatbotOpen(true)} />

      {/* T015 [US1], T036 [US4]: Chatbot Popup Overlay with ChatInterface */}
      <ChatBotPopup
        open={isChatbotOpen}
        onOpenChange={setIsChatbotOpen}
      >
        <ChatInterface />
      </ChatBotPopup>
    </div>
  );
}
