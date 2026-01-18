/**
 * ChatBot Popup Overlay Component
 * Feature: 009-chatkit-frontend
 * Task: T014, T016, T017, T018 [US1]
 *
 * Purpose: Modal dialog wrapper for chatbot interface
 * - Uses shadcn/ui Dialog for accessibility
 * - Fixed dimensions: 400px × 600px (per spec.md FR-002)
 * - Bottom-right positioning with backdrop
 * - Framer Motion animations (<300ms per spec.md FR-012)
 * - Z-index z-50 (above FAB at z-40, below toasts at z-100)
 *
 * Architecture:
 * - Dialog blocks background interaction (modal=true)
 * - Clicking backdrop closes popup (closeOnClickOutside=true)
 * - Escape key closes popup (closeOnEsc=true)
 * - Dashboard remains visible but dimmed
 *
 * Usage:
 * ```tsx
 * const [isOpen, setIsOpen] = useState(false);
 * <ChatBotPopup open={isOpen} onOpenChange={setIsOpen}>
 *   <ChatInterface />
 * </ChatBotPopup>
 * ```
 */

'use client';

import { ReactNode } from 'react';
import { X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface ChatBotPopupProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
  children: ReactNode;
  title?: string;
}

/**
 * ChatBot Popup Component
 *
 * @param open - Whether popup is open (controlled)
 * @param onOpenChange - Callback when open state changes
 * @param children - ChatInterface component or loading state
 * @param title - Optional custom title (defaults to "AI Assistant")
 */
export function ChatBotPopup({
  open,
  onOpenChange,
  children,
  title = 'AI Assistant',
}: ChatBotPopupProps) {
  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {/* Custom DialogContent with fixed positioning */}
      <DialogContent
        className="
          fixed bottom-4 right-4
          w-[400px] h-[600px]
          max-w-[calc(100vw-2rem)]
          max-h-[calc(100vh-2rem)]
          p-0
          border-2 border-orange-200
          shadow-2xl shadow-orange-500/20
          rounded-2xl
          overflow-hidden
          z-50
          bg-white dark:bg-gray-900
        "
        aria-describedby="chatbot-description"
        // Override default Dialog positioning
        style={{
          position: 'fixed',
          bottom: '1rem',
          right: '1rem',
          top: 'auto',
          left: 'auto',
          transform: 'none',
        }}
      >
        {/* Hidden description for screen readers */}
        <span id="chatbot-description" className="sr-only">
          AI-powered chatbot assistant for managing tasks via natural language
        </span>

        {/* Header with gradient background */}
        <DialogHeader className="
          bg-gradient-to-r from-orange-500 to-orange-600
          px-6 py-4
          border-b border-orange-700
        ">
          <div className="flex items-center justify-between">
            <DialogTitle className="text-white font-semibold text-lg">
              {title}
            </DialogTitle>

            {/* Close button (T018: Accessibility) */}
            <button
              onClick={() => onOpenChange(false)}
              className="
                text-white/80 hover:text-white
                hover:bg-white/10
                rounded-lg p-2
                transition-all duration-200
              "
              aria-label="Close chatbot"
              type="button"
            >
              <X className="h-5 w-5" />
            </button>
          </div>
        </DialogHeader>

        {/* Content area - ChatInterface will be rendered here */}
        <div className="flex-1 h-[calc(100%-4rem)] overflow-hidden">
          {/* T016: Animation wrapper */}
          <AnimatePresence mode="wait">
            {open && (
              <motion.div
                className="h-full"
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: 20 }}
                transition={{
                  duration: 0.25, // 250ms (below 300ms threshold per FR-012)
                  ease: 'easeOut',
                }}
              >
                {children}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </DialogContent>

      {/* Custom backdrop with fade animation */}
      {open && (
        <motion.div
          className="fixed inset-0 bg-black/40 z-40"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          transition={{ duration: 0.2 }}
          onClick={() => onOpenChange(false)}
          aria-hidden="true"
        />
      )}
    </Dialog>
  );
}
