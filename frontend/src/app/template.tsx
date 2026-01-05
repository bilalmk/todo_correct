/**
 * App Template for Page Transitions
 * T021a: Implements page transition animations for all route changes
 * FR-037: Fade-in, slide-up, duration: 200ms-400ms
 *
 * Note: template.tsx is the Next.js recommended pattern for page transitions
 * Unlike layout.tsx, template creates a new instance on each navigation,
 * which allows animations to work correctly with Server Components
 */

'use client';

import { motion } from 'framer-motion';

export default function Template({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{
        duration: 0.3,
        ease: [0.22, 1, 0.36, 1]
      }}
    >
      {children}
    </motion.div>
  );
}
