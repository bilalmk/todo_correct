"use client";

/**
 * EmptyState Component - Professional empty state with CTA
 *
 * Built following skills:
 * - @.claude/skills/custom/frontend-design-system (Empty state patterns, CTA patterns)
 * - @.claude/skills/mjs/building-nextjs-apps (Framer Motion animations)
 *
 * Features (T057):
 * - Illustrative icon with orange/coral theme
 * - Clear empty state message
 * - "Create Task" CTA button
 * - Smooth entrance animations
 * - Responsive design
 * - Dark mode support
 */

import { motion } from "framer-motion";
import { Inbox, Plus } from "lucide-react";
import { Button } from "@/components/ui/button";

interface EmptyStateProps {
  /** Main heading message */
  title?: string;
  /** Descriptive subtitle */
  description?: string;
  /** CTA button text */
  ctaText?: string;
  /** CTA button click handler */
  onCtaClick?: () => void;
  /** Custom icon component */
  icon?: React.ComponentType<React.SVGProps<SVGSVGElement>>;
}

export function EmptyState({
  title = "No tasks yet",
  description = "Create your first task to get started organizing your work.",
  ctaText = "Create Task",
  onCtaClick,
  icon: Icon = Inbox,
}: EmptyStateProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: "easeOut" }}
      className="flex flex-col items-center justify-center py-12 md:py-16 lg:py-20 px-4"
    >
      {/* T057: Illustrative icon with gradient background */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0 }}
        animate={{ scale: 1, opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.3 }}
        className="mb-6 md:mb-8"
      >
        <div className="relative">
          {/* Gradient background glow */}
          <div className="absolute inset-0 bg-gradient-to-br from-orange-200 to-coral-200 dark:from-orange-900/30 dark:to-coral-900/20 rounded-full blur-2xl opacity-50" />

          {/* Icon container */}
          <div className="relative bg-gradient-to-br from-orange-100 to-coral-100 dark:from-orange-950/50 dark:to-coral-950/30 rounded-full p-6 md:p-8 shadow-lg">
            <Icon className="h-12 w-12 md:h-16 md:w-16 text-orange-600 dark:text-orange-400" />
          </div>
        </div>
      </motion.div>

      {/* T057: Empty state message */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.2, duration: 0.3 }}
        className="text-center mb-6 md:mb-8 max-w-md"
      >
        <h2 className="text-xl md:text-2xl font-bold text-gray-900 dark:text-white mb-2 md:mb-3">
          {title}
        </h2>
        <p className="text-sm md:text-base text-gray-600 dark:text-gray-400">
          {description}
        </p>
      </motion.div>

      {/* T057: "Create Task" CTA button */}
      {onCtaClick && (
        <motion.div
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.3 }}
        >
          <Button
            onClick={onCtaClick}
            size="lg"
            className="bg-gradient-to-r from-orange-500 to-coral-500 hover:from-orange-600 hover:to-coral-600 text-white shadow-md hover:shadow-lg transition-all duration-200 gap-2"
          >
            <Plus className="h-5 w-5" />
            {ctaText}
          </Button>
        </motion.div>
      )}
    </motion.div>
  );
}
