/**
 * ChatBot Popup Overlay Component
 * Feature: 009-chatkit-frontend
 * Task: T014, T016, T017, T018 [US1], T065-T068 [US6], T079 [Phase 10]
 *
 * Purpose: Modal dialog wrapper for chatbot interface
 * - Uses shadcn/ui Dialog for accessibility
 * - Desktop: 400px × 600px, bottom-right positioning (per spec.md FR-002)
 * - Mobile: 100vw × 100vh, full-screen (T079: responsive design)
 * - Framer Motion animations (<300ms per spec.md FR-012)
 * - Z-index z-50 (above FAB at z-40, below toasts at z-100)
 * - T068: Respects prefers-reduced-motion for accessibility
 *
 * Architecture:
 * - Dialog blocks background interaction (modal=true)
 * - Clicking backdrop closes popup (closeOnClickOutside=true)
 * - Escape key closes popup (closeOnEsc=true)
 * - Dashboard remains visible but dimmed (desktop)
 * - Full-screen takeover on mobile (<768px)
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

import { ReactNode, useMemo } from 'react';
import { X } from 'lucide-react';
import { motion, AnimatePresence, Transition } from 'framer-motion';
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
  // T068: Detect prefers-reduced-motion for accessibility
  const prefersReducedMotion = useMemo(() => {
    if (typeof window === 'undefined') return false;
    return window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  }, []);

  // T065, T068: Animation configuration with reduced motion support
  const contentTransition: Transition = prefersReducedMotion
    ? { duration: 0 } // No animation if user prefers reduced motion
    : {
        duration: 0.25, // 250ms (T065: optimized for smooth feel under 300ms threshold)
        ease: 'easeOut',
      };

  const backdropTransition: Transition = prefersReducedMotion
    ? { duration: 0 } // No animation if user prefers reduced motion
    : {
        duration: 0.2, // 200ms (T067: backdrop synced with content)
      };

  return (
    <Dialog open={open} onOpenChange={onOpenChange}>
      {/* Custom DialogContent with responsive positioning (T079) */}
      <DialogContent
        className="
          fixed
          p-0
          border-2 border-orange-200
          shadow-2xl shadow-orange-500/20
          overflow-hidden
          z-50
          bg-white dark:bg-gray-900

          // Mobile (<768px): Full-screen modal (T079)
          w-screen h-screen
          bottom-0 right-0
          rounded-none

          // Desktop (>=768px): Bottom-right popup
          md:w-[400px] md:h-[600px]
          md:bottom-4 md:right-4
          md:rounded-2xl
          md:max-w-[calc(100vw-2rem)]
          md:max-h-[calc(100vh-2rem)]
        "
        aria-describedby="chatbot-description"
        // Override default Dialog positioning (T079: responsive)
        style={{
          position: 'fixed',
          bottom: 0,
          right: 0,
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
          {/* T016, T066: AnimatePresence wrapper for smooth enter/exit animations */}
          <AnimatePresence mode="wait">
            {open && (
              <motion.div
                className="h-full"
                initial={prefersReducedMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={prefersReducedMotion ? { opacity: 1, y: 0 } : { opacity: 0, y: 20 }}
                transition={contentTransition}
              >
                {children}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </DialogContent>

      {/* T067: Custom backdrop with fade animation (synced with content) */}
      {open && (
        <motion.div
          className="fixed inset-0 bg-black/40 z-40"
          initial={prefersReducedMotion ? { opacity: 1 } : { opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={prefersReducedMotion ? { opacity: 1 } : { opacity: 0 }}
          transition={backdropTransition}
          onClick={() => onOpenChange(false)}
          aria-hidden="true"
        />
      )}
    </Dialog>
  );
}
