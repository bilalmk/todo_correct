"use client";

/**
 * TaskStats Component
 *
 * Built following skills:
 * - @.claude/skills/custom/frontend-design-system (Card patterns, Badge usage, gradient patterns)
 * - @.claude/skills/mjs/building-nextjs-apps (Framer Motion patterns, count-up animations)
 * - @.claude/skills/custom/frontend-design-system/references/shadcn-components (Card)
 * - @.claude/skills/custom/frontend-design-system/references/responsive-design-patterns (Mobile-first grid)
 *
 * Features (T053):
 * - Display task statistics: total, completed, pending, overdue
 * - Responsive grid layout: 2 cols on mobile, 4 cols on desktop
 * - shadcn/ui Card components with icon indicators
 * - Gradient backgrounds with orange/coral theme
 * - Count-up animations using Framer Motion
 * - Full dark mode support with semantic Tailwind colors
 * - Computed statistics from task list
 * - WCAG 2.1 AA compliant accessibility
 * - Motion animations on mount
 */

import { useMemo, useEffect, useState } from "react";
import { motion, useAnimationControls } from "framer-motion";
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
  bgGradient: string; // T053: Gradient background instead of solid
  description?: string;
}

/**
 * T053: Count-up animation component using Framer Motion
 * Animates number from 0 to target value over 800ms
 */
function CountUp({ value }: { value: number }) {
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    const duration = 800; // 800ms animation
    const startTime = Date.now();
    const startValue = 0;

    const animate = () => {
      const now = Date.now();
      const progress = Math.min((now - startTime) / duration, 1);

      // Easing function (easeOutExpo)
      const easedProgress = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress);
      const currentValue = Math.floor(startValue + (value - startValue) * easedProgress);

      setDisplayValue(currentValue);

      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    animate();
  }, [value]);

  return <span>{displayValue}</span>;
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

  // T053: Build stat cards with gradient backgrounds (orange/coral theme)
  const statCards: StatCard[] = [
    {
      id: "total",
      label: "Total Tasks",
      value: stats.total,
      icon: ListTodo,
      iconColor: "text-orange-600 dark:text-orange-400",
      bgGradient: "bg-gradient-to-br from-orange-50 to-orange-100 dark:from-orange-950/30 dark:to-orange-900/20",
      description: "All tasks in your list",
    },
    {
      id: "completed",
      label: "Completed",
      value: stats.completed,
      icon: CheckCircle2,
      iconColor: "text-green-600 dark:text-green-400",
      bgGradient: "bg-gradient-to-br from-green-50 to-emerald-100 dark:from-green-950/30 dark:to-emerald-900/20",
      description: "Tasks you've finished",
    },
    {
      id: "pending",
      label: "Pending",
      value: stats.pending,
      icon: Circle,
      iconColor: "text-amber-600 dark:text-amber-400",
      bgGradient: "bg-gradient-to-br from-amber-50 to-yellow-100 dark:from-amber-950/30 dark:to-yellow-900/20",
      description: "Tasks waiting to be done",
    },
    {
      id: "overdue",
      label: "Overdue",
      value: stats.overdue,
      icon: AlertTriangle,
      iconColor: "text-red-600 dark:text-red-400",
      bgGradient: "bg-gradient-to-br from-red-50 to-rose-100 dark:from-red-950/30 dark:to-rose-900/20",
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
              <Card className="transition-all duration-300 hover:shadow-lg hover:border-orange-300/50 dark:hover:border-orange-600/50 overflow-hidden">
                <CardContent className="p-4 md:p-5 flex flex-col h-full">
                  {/* T053: Icon container with gradient background */}
                  <div className={`${stat.bgGradient} rounded-lg p-2 md:p-3 w-fit mb-3 md:mb-4 shadow-sm`}>
                    <Icon className={`h-5 w-5 md:h-6 md:w-6 ${stat.iconColor}`} />
                  </div>

                  {/* Label */}
                  <h3 className="text-xs md:text-sm font-medium text-gray-600 dark:text-gray-400 mb-1 md:mb-2">
                    {stat.label}
                  </h3>

                  {/* T053: Count-up animated value */}
                  <div className="mb-2 md:mb-3">
                    <p className="text-2xl md:text-3xl font-bold text-gray-900 dark:text-white">
                      <CountUp value={stat.value} />
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
