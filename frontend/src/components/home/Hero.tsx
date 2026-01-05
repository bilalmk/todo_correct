'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import Image from 'next/image';

/**
 * Hero Component - Updated with Orange/Coral Theme
 * 
 * Features (per tasks.md T019-T021):
 * - Orange/coral gradients replacing purple/indigo (T019)
 * - Professional images with Next.js Image optimization (T020)
 * - Framer Motion entrance animations with viewport detection (T021)
 * - WebP format, lazy loading, responsive sizes
 * 
 * Skills used:
 * - building-nextjs-apps: Next.js 16 Image patterns, animations
 * - frontend-design-system: Gradient usage, responsive design
 */
export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-orange-50 via-white to-coral-50">
      {/* Background gradient overlay (T019) */}
      <div className="absolute inset-0 bg-gradient-orange-warm opacity-10" />

      {/* Decorative blobs */}
      <div className="absolute top-20 right-10 w-72 h-72 bg-primary/20 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob" />
      <div className="absolute bottom-20 left-10 w-72 h-72 bg-secondary/20 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-2000" />
      <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-72 h-72 bg-accent/20 rounded-full mix-blend-multiply filter blur-xl opacity-70 animate-blob animation-delay-4000" />

      <div className="container mx-auto px-4 py-32 relative z-10">
        <div className="grid lg:grid-cols-2 gap-12 items-center">
          {/* Left Column: Text Content with animations (T021) */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.6 }}
          >
            <motion.h1
              className="text-5xl md:text-6xl font-bold mb-6 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.6, delay: 0.1 }}
            >
              Organize Your Life with TodoEvo
            </motion.h1>

            <motion.p
              className="text-xl md:text-2xl text-gray-600 mb-8"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.6, delay: 0.2 }}
            >
              The modern task management platform designed for productivity. 
              Drag, drop, and conquer your goals.
            </motion.p>

            <motion.div
              className="flex flex-col sm:flex-row gap-4"
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.6, delay: 0.3 }}
            >
              <Link
                href="/auth/register"
                className="bg-gradient-to-r from-primary to-secondary text-white px-8 py-4 rounded-lg hover:opacity-90 transition-opacity shadow-lg hover:shadow-xl font-semibold text-center min-h-[44px] flex items-center justify-center"
              >
                Get Started Free
              </Link>
              <Link
                href="#features"
                className="border-2 border-primary text-primary px-8 py-4 rounded-lg hover:bg-primary hover:text-white transition-all shadow-md font-semibold text-center min-h-[44px] flex items-center justify-center"
              >
                Learn More
              </Link>
            </motion.div>

            <motion.div
              className="mt-12 flex items-center gap-8 text-sm text-gray-600"
              initial={{ opacity: 0 }}
              whileInView={{ opacity: 1 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.6, delay: 0.4 }}
            >
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>No credit card required</span>
              </div>
              <div className="flex items-center gap-2">
                <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
                </svg>
                <span>Free forever</span>
              </div>
            </motion.div>
          </motion.div>

          {/* Right Column: Hero Image with Next.js Image optimization (T020) */}
          <motion.div
            className="relative h-[400px] md:h-[500px] lg:h-[600px]"
            initial={{ opacity: 0, scale: 0.95 }}
            whileInView={{ opacity: 1, scale: 1 }}
            viewport={{ once: true, amount: 0.2 }}
            transition={{ duration: 0.8, delay: 0.2 }}
          >
            <div className="relative w-full h-full rounded-2xl overflow-hidden shadow-2xl">
              {/* Professional image from Unsplash (T020 - building-nextjs-apps pattern) */}
              <Image
                src="https://images.unsplash.com/photo-1555212697-194d092e3b8f?w=1920"
                alt="Modern minimalist workspace with wooden desk and laptop - Photo by Minh Pham on Unsplash"
                fill
                priority
                className="object-cover"
                sizes="(max-width: 768px) 100vw, (max-width: 1200px) 50vw, 600px"
                quality={90}
              />
            </div>

            {/* Decorative floating cards */}
            <motion.div
              className="absolute -top-4 -right-4 bg-white p-4 rounded-lg shadow-lg"
              animate={{ y: [0, -10, 0] }}
              transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
            >
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-green-500" />
                <span className="text-sm font-semibold">Task Complete!</span>
              </div>
            </motion.div>

            <motion.div
              className="absolute -bottom-4 -left-4 bg-white p-4 rounded-lg shadow-lg"
              animate={{ y: [0, 10, 0] }}
              transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut', delay: 1 }}
            >
              <div className="flex items-center gap-2">
                <div className="w-3 h-3 rounded-full bg-primary" />
                <span className="text-sm font-semibold">3 tasks today</span>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}

// Add blob animation to globals.css if not already present
