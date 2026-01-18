/**
 * Floating Chat Button (FAB) Component
 * Feature: 009-chatkit-frontend
 * Task: T013 [US1]
 *
 * Purpose: Floating action button to trigger chatbot popup overlay
 * - Fixed position in bottom-right corner of dashboard
 * - Z-index z-40 (below popup overlay at z-50)
 * - Accessible with aria-label and keyboard support
 * - Orange/coral theme matching dashboard design (from 006-ui-enhancement)
 *
 * Usage:
 * ```tsx
 * <FloatingChatButton onClick={() => setPopupOpen(true)} />
 * ```
 */

'use client';

import { MessageSquare } from 'lucide-react';
import { motion } from 'framer-motion';

interface FloatingChatButtonProps {
  onClick: () => void;
  className?: string;
}

export function FloatingChatButton({ onClick, className = '' }: FloatingChatButtonProps) {
  return (
    <motion.button
      onClick={onClick}
      className={`
        fixed bottom-6 right-6 z-40
        h-14 w-14
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
      initial={{ scale: 0.8, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
      exit={{ scale: 0.8, opacity: 0 }}
      transition={{
        type: 'spring',
        stiffness: 260,
        damping: 20,
      }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
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
