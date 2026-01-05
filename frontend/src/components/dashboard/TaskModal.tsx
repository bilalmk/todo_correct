"use client";

/**
 * TaskModal Component - Create/Edit Task Dialog
 *
 * Built following skills:
 * - @.claude/skills/custom/frontend-design-system (Form patterns, Modal behavior FR-024a)
 * - @.claude/skills/mjs/building-nextjs-apps (Next.js patterns)
 * - @.claude/skills/custom/frontend-design-system/references/shadcn-components (Dialog, Form, Calendar)
 *
 * Features:
 * - React Hook Form + Zod validation
 * - Date picker with React Day Picker
 * - Tag multi-select
 * - Priority dropdown
 * - Recurrence options
 * - Reminder time picker (conditional on due date)
 * - ESC to close, no outside click dismiss (FR-024a)
 * - Loading states
 * - Built-in Radix UI animations
 */

import { useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { format } from "date-fns";
import { toast } from "sonner";
import { CalendarIcon, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog";
import {
  Form,
  FormControl,
  FormDescription,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Calendar } from "@/components/ui/calendar";
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from "@/components/ui/popover";
import { Checkbox } from "@/components/ui/checkbox";
import { taskSchema, TaskFormData } from "@/lib/validation-schemas";
import { Task } from "@/types/task-schema";
import { useTags } from "@/contexts/TagContext";
import { cn } from "@/lib/utils";

interface TaskModalProps {
  open: boolean;
  onClose: () => void;
  onSubmit: (data: TaskFormData) => Promise<void>;
  task?: Task | null;
  isLoading?: boolean;
}

export function TaskModal({
  open,
  onClose,
  onSubmit,
  task,
  isLoading = false,
}: TaskModalProps) {
  const { tags } = useTags();
  const activeTags = Array.isArray(tags) ? tags.filter((t) => !t.archived) : [];

  const form = useForm<TaskFormData>({
    resolver: zodResolver(taskSchema),
    defaultValues: {
      title: "",
      description: "",
      priority: "medium",
      due_date: "",
      reminder_at: "", // Match backend field name
      recurrence_pattern: undefined, // Optional field - undefined means no recurrence
      tags: [],
    },
  });

  // Convert ISO datetime to datetime-local format (YYYY-MM-DDTHH:mm)
  const toDatetimeLocal = (isoString?: string) => {
    if (!isoString) return "";
    try {
      // Remove timezone and seconds: "2024-12-20T10:00:00.000Z" -> "2024-12-20T10:00"
      return isoString.slice(0, 16);
    } catch {
      return "";
    }
  };

  // Populate form when editing
  useEffect(() => {
    if (task) {
      console.log('[TaskModal] Editing task:', task);
      console.log('[TaskModal] Reminder at:', task.reminder_at);
      console.log('[TaskModal] Recurrence pattern:', task.recurrence_pattern);

      const formData = {
        title: task.title,
        description: task.description || "",
        priority: task.priority || "medium", // Optional field, default to medium
        due_date: task.due_date || "",
        reminder_at: toDatetimeLocal(task.reminder_at), // Convert to datetime-local format
        recurrence_pattern: task.recurrence_pattern || undefined, // Backend field name is recurrence_pattern
        tags: Array.isArray(task.tags) ? task.tags.map((t) => t.id) : [], // Extract tag IDs from objects
        completed: task.completed, // Include completed status for edit mode
      };

      console.log('[TaskModal] Resetting form with:', formData);
      form.reset(formData);

      console.log('[TaskModal] Form values after reset:', form.getValues());
    } else {
      form.reset({
        title: "",
        description: "",
        priority: "medium",
        due_date: "",
        reminder_at: "",
        recurrence_pattern: undefined,
        tags: [],
      });
    }
  }, [task, form]);

  const handleSubmit = async (data: TaskFormData) => {
    try {
      await onSubmit(data);
      form.reset();
      onClose();
    } catch (error) {
      toast.error("Failed to save task. Please try again.");
    }
  };

  const dueDateValue = form.watch("due_date");

  return (
    <Dialog open={open} onOpenChange={onClose}>
      <DialogContent
        className="sm:max-w-[600px] max-h-[90vh] overflow-y-auto"
        onPointerDownOutside={(e) => e.preventDefault()} // No outside click dismiss (FR-024a)
      >
        <DialogHeader>
          <DialogTitle>{task ? "Edit Task" : "Create New Task"}</DialogTitle>
          <DialogDescription>
            {task
              ? "Update the task details below."
              : "Fill in the details to create a new task."}
          </DialogDescription>
        </DialogHeader>

        <Form {...form}>
          <form onSubmit={form.handleSubmit(handleSubmit)} className="space-y-4">
            {/* Title */}
            <FormField
              control={form.control}
              name="title"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Title *</FormLabel>
                  <FormControl>
                    <Input
                      placeholder="Enter task title..."
                      disabled={isLoading}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Description */}
            <FormField
              control={form.control}
              name="description"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Description</FormLabel>
                  <FormControl>
                    <Textarea
                      placeholder="Add more details about this task..."
                      rows={3}
                      disabled={isLoading}
                      {...field}
                    />
                  </FormControl>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Priority */}
            <FormField
              control={form.control}
              name="priority"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Priority</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    value={field.value}
                    disabled={isLoading}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select priority" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="low">Low</SelectItem>
                      <SelectItem value="medium">Medium</SelectItem>
                      <SelectItem value="high">High</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Due Date */}
            <FormField
              control={form.control}
              name="due_date"
              render={({ field }) => (
                <FormItem className="flex flex-col">
                  <FormLabel>Due Date</FormLabel>
                  <Popover>
                    <PopoverTrigger asChild>
                      <FormControl>
                        <Button
                          variant="outline"
                          className={cn(
                            "w-full justify-start text-left font-normal",
                            !field.value && "text-muted-foreground"
                          )}
                          disabled={isLoading}
                        >
                          <CalendarIcon className="mr-2 h-4 w-4" />
                          {field.value
                            ? format(new Date(field.value), "PPP")
                            : "Pick a date"}
                        </Button>
                      </FormControl>
                    </PopoverTrigger>
                    <PopoverContent className="w-auto p-0" align="start">
                      <Calendar
                        mode="single"
                        selected={field.value ? new Date(field.value) : undefined}
                        onSelect={(date) =>
                          field.onChange(date ? date.toISOString().split("T")[0] : "")
                        }
                        initialFocus
                      />
                    </PopoverContent>
                  </Popover>
                  <FormDescription>
                    Optional: Set a deadline for this task
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Reminder Time (only if due date is set) */}
            {dueDateValue && (
              <FormField
                control={form.control}
                name="reminder_at"
                render={({ field }) => (
                  <FormItem>
                    <FormLabel>Reminder Time</FormLabel>
                    <FormControl>
                      <Input
                        type="datetime-local"
                        disabled={isLoading}
                        {...field}
                      />
                    </FormControl>
                    <FormDescription>
                      Get notified at a specific time
                    </FormDescription>
                    <FormMessage />
                  </FormItem>
                )}
              />
            )}

            {/* Recurrence */}
            <FormField
              control={form.control}
              name="recurrence_pattern"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Recurrence</FormLabel>
                  <Select
                    onValueChange={field.onChange}
                    value={field.value}
                    disabled={isLoading}
                  >
                    <FormControl>
                      <SelectTrigger>
                        <SelectValue placeholder="Select recurrence" />
                      </SelectTrigger>
                    </FormControl>
                    <SelectContent>
                      <SelectItem value="daily">Daily</SelectItem>
                      <SelectItem value="weekly">Weekly</SelectItem>
                      <SelectItem value="monthly">Monthly</SelectItem>
                      <SelectItem value="custom">Custom</SelectItem>
                    </SelectContent>
                  </Select>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Tags */}
            <FormField
              control={form.control}
              name="tags"
              render={({ field }) => (
                <FormItem>
                  <FormLabel>Tags</FormLabel>
                  <div className="border rounded-md p-3 space-y-2 max-h-32 overflow-y-auto">
                    {activeTags.length === 0 ? (
                      <p className="text-sm text-gray-500 dark:text-gray-400">
                        No tags available. Create tags in the Tags page.
                      </p>
                    ) : (
                      activeTags.map((tag) => (
                        <div key={tag.id} className="flex items-center space-x-2">
                          <Checkbox
                            checked={field.value.includes(tag.id)}
                            onCheckedChange={(checked) => {
                              if (checked) {
                                field.onChange([...field.value, tag.id]);
                              } else {
                                field.onChange(
                                  field.value.filter((id) => id !== tag.id)
                                );
                              }
                            }}
                            disabled={isLoading}
                          />
                          <span
                            className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium text-white"
                            style={{ backgroundColor: tag.color }}
                          >
                            {tag.name}
                          </span>
                        </div>
                      ))
                    )}
                  </div>
                  <FormDescription>
                    Select tags to organize this task
                  </FormDescription>
                  <FormMessage />
                </FormItem>
              )}
            />

            {/* Footer */}
            <DialogFooter className="gap-2">
              <Button
                type="button"
                variant="outline"
                onClick={onClose}
                disabled={isLoading}
              >
                Cancel
              </Button>
              <Button type="submit" disabled={isLoading}>
                {isLoading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Saving...
                  </>
                ) : (
                  <>{task ? "Update Task" : "Create Task"}</>
                )}
              </Button>
            </DialogFooter>
          </form>
        </Form>
      </DialogContent>
    </Dialog>
  );
}
