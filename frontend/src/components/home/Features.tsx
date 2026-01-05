"use client";

import { motion } from "framer-motion";
import { fadeIn, listItem } from "@/lib/animations";
import {
  CheckSquare,
  Tag,
  Filter,
  Calendar,
  Repeat,
  Bell,
  Palette,
  Zap,
  Shield,
} from "lucide-react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

const features = [
  {
    icon: CheckSquare,
    title: "Smart Task Management",
    description:
      "Create, organize, and track your tasks with ease. Mark tasks complete with a single click and keep your workflow smooth.",
  },
  {
    icon: Tag,
    title: "Custom Tags & Categories",
    description:
      "Organize tasks your way with custom tags and color-coded categories. Find what you need instantly.",
  },
  {
    icon: Filter,
    title: "Advanced Filtering",
    description:
      "Filter tasks by status, priority, tags, or date range. Search across all your tasks in real-time.",
  },
  {
    icon: Calendar,
    title: "Due Dates & Reminders",
    description:
      "Never miss a deadline with visual due date indicators and customizable reminder notifications.",
  },
  {
    icon: Repeat,
    title: "Recurring Tasks",
    description:
      "Set tasks to repeat daily, weekly, or monthly. Perfect for habits and routine responsibilities.",
  },
  {
    icon: Bell,
    title: "Smart Notifications",
    description:
      "Get notified when tasks are due, completed, or need attention. Stay on top of your work.",
  },
  {
    icon: Palette,
    title: "Beautiful Design",
    description:
      "Enjoy a modern, clean interface with smooth animations and responsive design that works everywhere.",
  },
  {
    icon: Zap,
    title: "Lightning Fast",
    description:
      "Optimized performance ensures your task management is always snappy and responsive.",
  },
  {
    icon: Shield,
    title: "Privacy First",
    description:
      "Your data stays yours. All information is stored securely with industry-standard encryption.",
  },
];

export function Features() {
  return (
    <section className="py-16 md:py-24 lg:py-32 bg-white dark:bg-gray-900">
      <div className="container mx-auto px-4 md:px-6 lg:px-8 max-w-7xl">
        {/* Section header */}
        <motion.div
          initial="initial"
          whileInView="animate"
          viewport={{ once: true, amount: 0.3 }}
          variants={fadeIn}
          className="text-center mb-12 md:mb-16"
        >
          <h2 className="text-3xl md:text-4xl lg:text-5xl font-bold tracking-tight mb-4 bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent dark:from-primary dark:to-secondary">
            Everything You Need
          </h2>
          <p className="text-lg md:text-xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto">
            Powerful features designed to boost your productivity and keep you
            organized
          </p>
        </motion.div>

        {/* Features grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6 md:gap-8">
          {features.map((feature, index) => {
            const Icon = feature.icon;
            return (
              <motion.div
                key={index}
                variants={listItem}
                initial="initial"
                whileInView="animate"
                viewport={{ once: true, amount: 0.3 }}
                transition={{ delay: index * 0.1 }}
              >
                <Card className="h-full hover:shadow-lg transition-shadow duration-300 border-2 hover:border-primary/30 dark:hover:border-primary/60">
                  <CardHeader>
                    <div className="w-12 h-12 rounded-lg bg-gradient-to-br from-primary to-secondary flex items-center justify-center mb-4">
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <CardTitle className="text-xl">{feature.title}</CardTitle>
                  </CardHeader>
                  <CardContent>
                    <CardDescription className="text-base">
                      {feature.description}
                    </CardDescription>
                  </CardContent>
                </Card>
              </motion.div>
            );
          })}
        </div>

        {/* Bottom CTA */}
        <motion.div
          initial="initial"
          whileInView="animate"
          viewport={{ once: true, amount: 0.3 }}
          variants={fadeIn}
          className="mt-16 text-center"
        >
          <p className="text-gray-600 dark:text-gray-300 mb-4">
            Ready to transform your productivity?
          </p>
          <a
            href="/auth/register"
            className="inline-flex items-center justify-center px-6 py-3 text-base font-medium text-white bg-gradient-to-r from-primary to-secondary hover:opacity-90 rounded-lg shadow-lg hover:shadow-xl transition-all duration-300 min-h-[44px]"
          >
            Start Your Free Trial
          </a>
        </motion.div>
      </div>
    </section>
  );
}
