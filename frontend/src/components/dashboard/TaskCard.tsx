"use client";

/**
 * TaskCard Component
 *
 * Built following skills:
 * - @.claude/skills/custom/frontend-design-system (Card patterns, Badge usage)
 * - @.claude/skills/custom/frontend-design-system/references/shadcn-components (Card, Badge, Checkbox)
 * - @.claude/skills/custom/frontend-design-system/references/responsive-design-patterns (Mobile-first)
 *
 * Features:
 * - Visual priority indicators (color + icon)
 * - Due date status badges (overdue, today, upcoming)
 * - Tag pills with custom colors
 * - Checkbox for completion toggle
 * - Edit and delete action buttons
 * - Responsive layout (stacks on mobile)
 * - Hover effects and transitions
 * - WCAG 2.1 AA compliant
 */

import { useState } from "react";
import { motion } from "framer-motion";
import { format, parseISO } from "date-fns";
import {
  Calendar,
  Tag as TagIcon,
  MoreVertical,
  Edit,
  Trash2,
  AlertCircle,
  Clock,
  CheckCircle2,
  Repeat,
  GripVertical,
} from "lucide-react";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";

import { Card, CardContent } from "@/components/ui/card";
import { Checkbox } from "@/components/ui/checkbox";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Button } from "@/components/ui/button";
import { Task } from "@/types/task-schema";
import { useTags } from "@/contexts/TagContext";
import { getDueStatus } from "@/lib/utils";
import { listItem } from "@/lib/animations";

interface TaskCardProps {
  task: Task;
  onComplete: (completed: boolean) => void;
  onEdit: () => void;
  onDelete: () => void;
}

export function TaskCard({ task, onComplete, onEdit, onDelete }: TaskCardProps) {
  const { tags } = useTags();
  const [isHovered, setIsHovered] = useState(false);

  // Drag and drop setup
  const {
    attributes,
    listeners,
    setNodeRef,
    transform,
    transition,
    isDragging,
  } = useSortable({ id: task.id });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.5 : 1,
  };

  const dueStatus = getDueStatus(task.due_date, task.completed);

  // Task tags come as full objects from backend
  const taskTags = Array.isArray(task.tags) ? task.tags : [];

  // Priority badge config (priority is optional in backend)
  const priorityConfig = {
    high: {
      color: "bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400",
      icon: AlertCircle,
    },
    medium: {
      color: "bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400",
      icon: Clock,
    },
    low: {
      color: "bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400",
      icon: CheckCircle2,
    },
  };

  const priorityInfo = task.priority ? priorityConfig[task.priority] : priorityConfig.low;
  const PriorityIcon = priorityInfo.icon;

  return (
    <motion.div
      ref={setNodeRef}
      style={style}
      variants={listItem}
      initial="initial"
      animate="animate"
      exit="exit"
      onHoverStart={() => setIsHovered(true)}
      onHoverEnd={() => setIsHovered(false)}
      // T054: Enhanced hover effects with translateY and increased shadow
      whileHover={{ y: -2 }}
      transition={{ duration: 0.2 }}
    >
      <Card
        className={`transition-all duration-300 ${
          task.completed ? "opacity-60" : ""
        } ${
          isHovered
            ? "shadow-xl border-orange-300/50 dark:border-orange-600/50"
            : "shadow-sm"
        }`}
      >
        <CardContent className="p-4 md:p-5">
          <div className="flex gap-3 md:gap-4">
            {/* Drag Handle */}
            <div
              {...attributes}
              {...listeners}
              className="pt-0.5 cursor-grab active:cursor-grabbing touch-none min-w-[44px] min-h-[44px] flex items-center justify-center -ml-2"
              aria-label="Drag to reorder task"
            >
              <GripVertical className="h-5 w-5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 transition-colors" />
            </div>

            {/* Checkbox */}
            <div className="pt-0.5">
              <Checkbox
                checked={task.completed}
                onCheckedChange={onComplete}
                className="h-5 w-5"
                aria-label={`Mark "${task.title}" as ${task.completed ? "incomplete" : "complete"}`}
              />
            </div>

            {/* Main content */}
            <div className="flex-1 min-w-0">
              {/* Title */}
              <h3
                className={`font-semibold text-base md:text-lg mb-2 ${
                  task.completed
                    ? "line-through text-gray-500 dark:text-gray-400"
                    : "text-gray-900 dark:text-white"
                }`}
              >
                {task.title}
              </h3>

              {/* Description */}
              {task.description && (
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-3 line-clamp-2">
                  {task.description}
                </p>
              )}

              {/* Metadata row */}
              <div className="flex flex-wrap gap-2 items-center">
                {/* Priority badge (optional field) */}
                {task.priority && (
                  <Badge className={`${priorityInfo.color} gap-1`}>
                    <PriorityIcon className="h-3 w-3" />
                    {task.priority.charAt(0).toUpperCase() + task.priority.slice(1)}
                  </Badge>
                )}

                {/* Due date badge */}
                {task.due_date && (
                  <Badge
                    variant="outline"
                    className={`gap-1 ${
                      dueStatus === "overdue"
                        ? "border-red-300 text-red-700 dark:border-red-800 dark:text-red-400"
                        : dueStatus === "today"
                        ? "border-yellow-300 text-yellow-700 dark:border-yellow-800 dark:text-yellow-400"
                        : "border-gray-300 text-gray-700 dark:border-gray-600 dark:text-gray-400"
                    }`}
                  >
                    <Calendar className="h-3 w-3" />
                    {format(parseISO(task.due_date), "MMM d")}
                    {dueStatus === "overdue" && " (Overdue)"}
                    {dueStatus === "today" && " (Today)"}
                  </Badge>
                )}

                {/* Recurrence badge */}
                {task.recurrence_pattern && (
                  <Badge variant="secondary" className="gap-1">
                    <Repeat className="h-3 w-3" />
                    {task.recurrence_pattern.charAt(0).toUpperCase() + task.recurrence_pattern.slice(1)}
                  </Badge>
                )}

                {/* Tags */}
                {taskTags.length > 0 && (
                  <div className="flex flex-wrap gap-1.5">
                    {taskTags.slice(0, 3).map((tag) => (
                      <span
                        key={tag.id}
                        className="inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium text-white"
                        style={{ backgroundColor: tag.color || "#888888" }}
                      >
                        <TagIcon className="h-2.5 w-2.5" />
                        {tag.name}
                      </span>
                    ))}
                    {taskTags.length > 3 && (
                      <span className="text-xs text-gray-500 dark:text-gray-400">
                        +{taskTags.length - 3} more
                      </span>
                    )}
                  </div>
                )}
              </div>
            </div>

            {/* Actions menu */}
            <div>
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    size="icon"
                    className="h-8 w-8"
                    aria-label="Task actions"
                  >
                    <MoreVertical className="h-4 w-4" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end">
                  <DropdownMenuItem onClick={onEdit} className="gap-2">
                    <Edit className="h-4 w-4" />
                    Edit
                  </DropdownMenuItem>
                  <DropdownMenuItem
                    onClick={onDelete}
                    className="gap-2 text-red-600 dark:text-red-400"
                  >
                    <Trash2 className="h-4 w-4" />
                    Delete
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            </div>
          </div>
        </CardContent>
      </Card>
    </motion.div>
  );
}
