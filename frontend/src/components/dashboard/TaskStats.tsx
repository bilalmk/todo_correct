"use client";

/**
 * TaskStats Component
 *
 * Built following skills:
 * - @.claude/skills/custom/frontend-design-system (Card patterns, Badge usage)
 * - @.claude/skills/custom/frontend-design-system/references/shadcn-components (Card)
 * - @.claude/skills/custom/frontend-design-system/references/responsive-design-patterns (Mobile-first grid)
 *
 * Features:
 * - Display task statistics: total, completed, pending, overdue
 * - Responsive grid layout: 2 cols on mobile, 4 cols on desktop
 * - shadcn/ui Card components with icon indicators
 * - Icons from lucide-react with color coding
 * - Full dark mode support with semantic Tailwind colors
 * - Computed statistics from task list
 * - WCAG 2.1 AA compliant accessibility
 * - Motion animations on mount
 */

import { useMemo } from "react";
import { motion } from "framer-motion";
import {
  CheckCircle2,
  Circle,
  AlertTriangle,
  ListTodo,
} from "lucide-react";

import { Card, CardContent } from "@/components/ui/card";
import { Task } from "@/types/task-schema";
import { containerVariants, listItem } from "@/lib/animations";

interface TaskStatsProps {
  tasks: Task[];
}

interface StatCard {
  id: string;
  label: string;
  value: number;
  icon: React.ComponentType<React.SVGProps<SVGSVGElement>>;
  iconColor: string;
  bgColor: string;
  description?: string;
}

/**
 * Compute task statistics from the task list
 */
function computeStats(tasks: Task[]): {
  total: number;
  completed: number;
  pending: number;
  overdue: number;
} {
  const now = new Date();
  const today = now.toISOString().split("T")[0];

  let completed = 0;
  let overdue = 0;

  for (const task of tasks) {
    if (task.completed) {
      completed++;
    } else if (task.due_date && task.due_date < today) {
      overdue++;
    }
  }

  const pending = tasks.length - completed;

  return {
    total: tasks.length,
    completed,
    pending,
    overdue,
  };
}

export function TaskStats({ tasks }: TaskStatsProps) {
  const stats = useMemo(() => computeStats(tasks), [tasks]);

  // Build stat cards with icons and styling
  const statCards: StatCard[] = [
    {
      id: "total",
      label: "Total Tasks",
      value: stats.total,
      icon: ListTodo,
      iconColor: "text-blue-600 dark:text-blue-400",
      bgColor: "bg-blue-50 dark:bg-blue-950/30",
      description: "All tasks in your list",
    },
    {
      id: "completed",
      label: "Completed",
      value: stats.completed,
      icon: CheckCircle2,
      iconColor: "text-green-600 dark:text-green-400",
      bgColor: "bg-green-50 dark:bg-green-950/30",
      description: "Tasks you've finished",
    },
    {
      id: "pending",
      label: "Pending",
      value: stats.pending,
      icon: Circle,
      iconColor: "text-yellow-600 dark:text-yellow-400",
      bgColor: "bg-yellow-50 dark:bg-yellow-950/30",
      description: "Tasks waiting to be done",
    },
    {
      id: "overdue",
      label: "Overdue",
      value: stats.overdue,
      icon: AlertTriangle,
      iconColor: "text-red-600 dark:text-red-400",
      bgColor: "bg-red-50 dark:bg-red-950/30",
      description: "Tasks past their due date",
    },
  ];

  return (
    <motion.div
      variants={containerVariants}
      initial="initial"
      animate="animate"
      className="w-full"
    >
      {/* Grid: 2 cols on mobile, 3 cols on tablet, 4 cols on desktop */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-4 gap-3 md:gap-4">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <motion.div
              key={stat.id}
              variants={listItem}
              initial="initial"
              animate="animate"
            >
              <Card className="transition-all duration-200 hover:shadow-lg hover:border-purple-200 dark:hover:border-purple-800">
                <CardContent className="p-4 md:p-5 flex flex-col h-full">
                  {/* Icon container */}
                  <div className={`${stat.bgColor} rounded-lg p-2 md:p-3 w-fit mb-3 md:mb-4`}>
                    <Icon className={`h-5 w-5 md:h-6 md:w-6 ${stat.iconColor}`} />
                  </div>

                  {/* Label */}
                  <h3 className="text-xs md:text-sm font-medium text-gray-600 dark:text-gray-400 mb-1 md:mb-2">
                    {stat.label}
                  </h3>

                  {/* Value */}
                  <div className="mb-2 md:mb-3">
                    <p className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">
                      {stat.value}
                    </p>
                  </div>

                  {/* Description (optional, smaller on mobile) */}
                  {stat.description && (
                    <p className="text-xs text-gray-500 dark:text-gray-500 line-clamp-2">
                      {stat.description}
                    </p>
                  )}
                </CardContent>
              </Card>
            </motion.div>
          );
        })}
      </div>

      {/* Empty state message */}
      {tasks.length === 0 && (
        <motion.div
          variants={listItem}
          className="text-center py-8 md:py-12"
        >
          <p className="text-sm md:text-base text-gray-500 dark:text-gray-400">
            No tasks yet. Create one to get started!
          </p>
        </motion.div>
      )}
    </motion.div>
  );
}
