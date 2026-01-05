'use client';

import { useState } from 'react';
import Link from 'next/link';
import { Menu, X } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

/**
 * Masthead Component - Fixed Navigation Header
 * 
 * Features (per tasks.md T016-T018):
 * - Fixed positioning with backdrop blur (building-nextjs-apps pattern)
 * - Mobile hamburger menu (<768px) with Framer Motion animations
 * - Sticky header behavior on scroll
 * - Orange/coral gradient CTA button
 * - Smooth scroll anchor links (#features, #about, #pricing)
 * 
 * Skills used:
 * - building-nextjs-apps: Next.js 16 patterns, responsive design
 * - frontend-design-system: Component patterns, accessibility
 */
export function Masthead() {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const [isScrolled, setIsScrolled] = useState(false);

  // Sticky header with backdrop blur on scroll (T018)
  useState(() => {
    if (typeof window !== 'undefined') {
      const handleScroll = () => {
        setIsScrolled(window.scrollY > 10);
      };
      window.addEventListener('scroll', handleScroll);
      return () => window.removeEventListener('scroll', handleScroll);
    }
  });

  return (
    <header
      className={`fixed top-0 left-0 right-0 z-50 transition-all duration-300 ${
        isScrolled
          ? 'backdrop-blur-md bg-white/80 border-b border-gray-200 shadow-sm'
          : 'bg-transparent'
      }`}
    >
      <nav className="container mx-auto px-4 py-4 flex items-center justify-between">
        {/* Logo (T016) */}
        <Link
          href="/"
          className="text-2xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent hover:opacity-80 transition-opacity"
        >
          TodoEvo
        </Link>

        {/* Desktop Navigation (T016) */}
        <div className="hidden md:flex items-center gap-8">
          <Link
            href="#features"
            className="text-gray-700 hover:text-primary transition-colors font-medium"
          >
            Features
          </Link>
          <Link
            href="#about"
            className="text-gray-700 hover:text-primary transition-colors font-medium"
          >
            About
          </Link>
          <Link
            href="#pricing"
            className="text-gray-700 hover:text-primary transition-colors font-medium"
          >
            Pricing
          </Link>
          <Link
            href="/auth/login"
            className="text-gray-700 hover:text-primary transition-colors font-medium"
          >
            Login
          </Link>
          <Link
            href="/auth/register"
            className="bg-gradient-to-r from-primary to-secondary text-white px-6 py-2 rounded-lg hover:opacity-90 transition-opacity shadow-md hover:shadow-lg font-semibold min-h-[44px] flex items-center"
          >
            Sign Up
          </Link>
        </div>

        {/* Mobile Menu Toggle (T017) */}
        <button
          className="md:hidden p-2 rounded-lg hover:bg-gray-100 transition-colors min-w-[44px] min-h-[44px] flex items-center justify-center"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label={mobileMenuOpen ? 'Close menu' : 'Open menu'}
          aria-expanded={mobileMenuOpen}
        >
          {mobileMenuOpen ? (
            <X className="w-6 h-6 text-gray-700" />
          ) : (
            <Menu className="w-6 h-6 text-gray-700" />
          )}
        </button>
      </nav>

      {/* Mobile Menu with Framer Motion animations (T017) */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            transition={{ duration: 0.3, ease: 'easeInOut' }}
            className="md:hidden bg-white border-t border-gray-200 shadow-lg"
          >
            <div className="container mx-auto px-4 py-4 flex flex-col gap-4">
              <Link
                href="#features"
                className="py-3 px-4 hover:bg-gray-50 rounded-lg transition-colors text-gray-700 hover:text-primary font-medium min-h-[44px] flex items-center"
                onClick={() => setMobileMenuOpen(false)}
              >
                Features
              </Link>
              <Link
                href="#about"
                className="py-3 px-4 hover:bg-gray-50 rounded-lg transition-colors text-gray-700 hover:text-primary font-medium min-h-[44px] flex items-center"
                onClick={() => setMobileMenuOpen(false)}
              >
                About
              </Link>
              <Link
                href="#pricing"
                className="py-3 px-4 hover:bg-gray-50 rounded-lg transition-colors text-gray-700 hover:text-primary font-medium min-h-[44px] flex items-center"
                onClick={() => setMobileMenuOpen(false)}
              >
                Pricing
              </Link>
              <Link
                href="/auth/login"
                className="py-3 px-4 hover:bg-gray-50 rounded-lg transition-colors text-gray-700 hover:text-primary font-medium min-h-[44px] flex items-center"
                onClick={() => setMobileMenuOpen(false)}
              >
                Login
              </Link>
              <Link
                href="/auth/register"
                className="bg-gradient-to-r from-primary to-secondary text-white px-6 py-3 rounded-lg hover:opacity-90 transition-opacity text-center font-semibold min-h-[44px] flex items-center justify-center shadow-md"
                onClick={() => setMobileMenuOpen(false)}
              >
                Sign Up
              </Link>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
