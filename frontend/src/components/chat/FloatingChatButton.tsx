/**
 * Floating Chat Button (FAB) Component
 * Feature: 009-chatkit-frontend
 * Task: T013 [US1], T068 [US6], T079 [Phase 10]
 *
 * Purpose: Floating action button to trigger chatbot popup overlay
 * - Fixed position in bottom-right corner of dashboard
 * - Mobile: 60px × 60px for better touch targets (T079)
 * - Desktop: 56px × 56px standard FAB size
 * - Z-index z-40 (below popup overlay at z-50)
 * - Accessible with aria-label and keyboard support
 * - Orange/coral theme matching dashboard design (from 006-ui-enhancement)
 * - T068: Respects prefers-reduced-motion for accessibility
 *
 * Usage:
 * ```tsx
 * <FloatingChatButton onClick={() => setPopupOpen(true)} />
 * ```
 */

'use client';

import { useMemo } from 'react';
import { MessageSquare } from 'lucide-react';
import { motion } from 'framer-motion';

interface FloatingChatButtonProps {
  onClick: () => void;
  className?: string;
}

export function FloatingChatButton({ onClick, className = '' }: FloatingChatButtonProps) {
  // T068: Detect prefers-reduced-motion for accessibility
  const prefersReducedMotion = useMemo(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, []);

  return (
    <motion.button
      onClick={onClick}
      className={`
        fixed bottom-6 right-6 z-40
        // Mobile: Larger touch target (T079)
        h-[60px] w-[60px]
        // Desktop: Standard FAB size
        md:h-14 md:w-14
        rounded-full
        bg-gradient-to-br from-orange-500 to-orange-600
        shadow-lg shadow-orange-500/50
        hover:shadow-xl hover:shadow-orange-500/60
        hover:scale-105
        active:scale-95
        transition-all duration-200
        flex items-center justify-center
        group
        ${className}
      `}
      aria-label="Open chatbot assistant"
      role="button"
      tabIndex={0}
      initial={prefersReducedMotion ? { scale: 1, opacity: 1 } : { scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={prefersReducedMotion ? { scale: 1, opacity: 1 } : { scale: 0.8, opacity: 0 }}
      transition={
        prefersReducedMotion
          ? { duration: 0 }
          : {
              type: 'spring',
              stiffness: 260,
              damping: 20,
            }
      }
      whileHover={prefersReducedMotion ? {} : { scale: 1.05 }}
      whileTap={prefersReducedMotion ? {} : { scale: 0.95 }}
    >
      {/* Icon */}
      <MessageSquare
        className="h-6 w-6 text-white group-hover:scale-110 transition-transform duration-200"
        strokeWidth={2}
      />

      {/* Notification badge (optional - for future feature) */}
      {/* <span className="absolute -top-1 -right-1 h-5 w-5 bg-red-500 rounded-full text-xs text-white flex items-center justify-center">
        3
      </span> */}
    </motion.button>
  );
}
