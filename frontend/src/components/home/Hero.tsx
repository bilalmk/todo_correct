"use client";

import { motion } from "framer-motion";
import { Button } from "@/components/ui/button";
import { fadeIn, slideUp } from "@/lib/animations";
import Link from "next/link";
import { CheckCircle2, Sparkles, Zap } from "lucide-react";

export function Hero() {
  return (
    <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-purple-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900">
      {/* Background decoration */}
      <div className="absolute inset-0 overflow-hidden">
        <div className="absolute -top-40 -right-40 w-80 h-80 bg-purple-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob" />
        <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-indigo-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-2000" />
        <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 w-80 h-80 bg-pink-300 rounded-full mix-blend-multiply filter blur-xl opacity-30 animate-blob animation-delay-4000" />
      </div>

      <div className="container mx-auto px-4 md:px-6 lg:px-8 max-w-7xl relative z-10">
        <div className="flex flex-col items-center text-center">
          {/* Badge */}
          <motion.div
            variants={fadeIn}
            initial="initial"
            animate="animate"
            className="mb-6"
          >
            <span className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 text-sm font-medium">
              <Sparkles className="h-4 w-4" />
              Evolution of Todo Management
            </span>
          </motion.div>

          {/* Headline */}
          <motion.h1
            variants={slideUp}
            initial="initial"
            animate="animate"
            className="text-4xl md:text-5xl lg:text-6xl xl:text-7xl font-bold tracking-tight mb-6 bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-indigo-600 dark:from-purple-400 dark:to-indigo-400"
          >
            Transform Your
            <br />
            Productivity
          </motion.h1>

          {/* Subheadline */}
          <motion.p
            variants={slideUp}
            initial="initial"
            animate="animate"
            transition={{ delay: 0.1 }}
            className="text-lg md:text-xl lg:text-2xl text-gray-600 dark:text-gray-300 mb-8 max-w-3xl"
          >
            Experience the next generation of task management with powerful
            features, intuitive design, and seamless organization. Your
            productivity journey starts here.
          </motion.p>

          {/* Feature highlights */}
          <motion.div
            variants={fadeIn}
            initial="initial"
            animate="animate"
            transition={{ delay: 0.2 }}
            className="flex flex-wrap justify-center gap-4 md:gap-6 mb-12"
          >
            {[
              "Smart Organization",
              "Beautiful UI",
              "Lightning Fast",
            ].map((feature, index) => (
              <div
                key={index}
                className="flex items-center gap-2 text-sm md:text-base text-gray-700 dark:text-gray-300"
              >
                <CheckCircle2 className="h-5 w-5 text-green-500" />
                <span>{feature}</span>
              </div>
            ))}
          </motion.div>

          {/* CTAs */}
          <motion.div
            variants={slideUp}
            initial="initial"
            animate="animate"
            transition={{ delay: 0.3 }}
            className="flex flex-col sm:flex-row gap-4 w-full sm:w-auto"
          >
            <Link href="/auth/register" className="w-full sm:w-auto">
              <Button
                size="lg"
                className="w-full sm:w-auto bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-700 hover:to-indigo-700 text-white shadow-lg hover:shadow-xl transition-all duration-300 min-h-[44px]"
              >
                <Zap className="h-5 w-5 mr-2" />
                Get Started Free
              </Button>
            </Link>
            <Link href="/auth/login" className="w-full sm:w-auto">
              <Button
                size="lg"
                variant="outline"
                className="w-full sm:w-auto border-2 border-purple-600 text-purple-600 hover:bg-purple-50 dark:border-purple-400 dark:text-purple-400 dark:hover:bg-purple-950 min-h-[44px]"
              >
                Sign In
              </Button>
            </Link>
          </motion.div>

          {/* Trust indicator */}
          <motion.p
            variants={fadeIn}
            initial="initial"
            animate="animate"
            transition={{ delay: 0.4 }}
            className="mt-8 text-sm text-gray-500 dark:text-gray-400"
          >
            No credit card required • Free forever • 2-minute setup
          </motion.p>
        </div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8, duration: 0.5, repeat: Infinity, repeatType: "reverse" }}
        className="absolute bottom-8 left-1/2 transform -translate-x-1/2 hidden md:block"
      >
        <div className="w-6 h-10 border-2 border-purple-600 rounded-full flex items-start justify-center p-2">
          <div className="w-1 h-3 bg-purple-600 rounded-full" />
        </div>
      </motion.div>
    </section>
  );
}
