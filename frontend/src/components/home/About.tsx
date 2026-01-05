'use client';

import { motion } from 'framer-motion';

/**
 * About Section Component
 * 
 * Features (per tasks.md T022):
 * - Brief mission statement (2-3 sentences)
 * - Key value propositions (2-3 bullet points)
 * - Team/company placeholder
 * - Styled with orange/coral accents
 * 
 * Skills used:
 * - frontend-design-system: Component patterns, gradient usage
 * - building-nextjs-apps: Responsive design, accessibility
 */
export function About() {
  const valueProps = [
    {
      icon: '⚡',
      title: 'Fast & Reliable',
      description: 'Lightning-fast performance with 99.9% uptime guarantee',
      gradient: 'from-primary to-secondary',
    },
    {
      icon: '🔒',
      title: 'Secure & Private',
      description: 'Enterprise-grade security with end-to-end encryption',
      gradient: 'from-secondary to-accent',
    },
    {
      icon: '🎨',
      title: 'Beautiful & Intuitive',
      description: 'Thoughtfully designed interface for maximum productivity',
      gradient: 'from-accent to-primary',
    },
  ];

  return (
    <section id="about" className="py-20 bg-white">
      <div className="container mx-auto px-4">
        {/* Section Header */}
        <motion.div
          className="text-center max-w-3xl mx-auto mb-16"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.6 }}
        >
          <h2 className="text-4xl md:text-5xl font-bold mb-6 bg-gradient-to-r from-primary via-secondary to-accent bg-clip-text text-transparent">
            About TodoEvo
          </h2>
          <p className="text-lg md:text-xl text-gray-600 leading-relaxed">
            TodoEvo is a modern task management platform designed to help individuals and teams 
            stay organized and productive. Built with cutting-edge technology and a user-first 
            approach, we empower you to conquer your goals with intuitive drag-and-drop 
            task management, smart prioritization, and beautiful design.
          </p>
        </motion.div>

        {/* Value Propositions (T022) */}
        <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
          {valueProps.map((prop, index) => (
            <motion.div
              key={prop.title}
              className={`p-8 rounded-2xl bg-gradient-to-br ${prop.gradient} text-white shadow-lg hover:shadow-xl transition-shadow`}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
            >
              <div className="text-5xl mb-4">{prop.icon}</div>
              <h3 className="text-2xl font-bold mb-3">{prop.title}</h3>
              <p className="text-white/90 leading-relaxed">{prop.description}</p>
            </motion.div>
          ))}
        </div>

        {/* Team/Company Placeholder (T022) */}
        <motion.div
          className="mt-20 max-w-4xl mx-auto text-center"
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <h3 className="text-2xl md:text-3xl font-bold mb-4 text-gray-800">
            Built by productivity enthusiasts, for productivity enthusiasts
          </h3>
          <p className="text-lg text-gray-600 mb-8">
            Our team is passionate about creating tools that make a real difference in people's lives. 
            We believe in simplicity, performance, and delightful user experiences.
          </p>
          <div className="flex justify-center gap-4">
            <motion.div
              className="bg-gray-100 w-16 h-16 rounded-full"
              whileHover={{ scale: 1.1 }}
              transition={{ duration: 0.2 }}
            />
            <motion.div
              className="bg-gray-100 w-16 h-16 rounded-full"
              whileHover={{ scale: 1.1 }}
              transition={{ duration: 0.2 }}
            />
            <motion.div
              className="bg-gray-100 w-16 h-16 rounded-full"
              whileHover={{ scale: 1.1 }}
              transition={{ duration: 0.2 }}
            />
            <motion.div
              className="bg-gray-100 w-16 h-16 rounded-full"
              whileHover={{ scale: 1.1 }}
              transition={{ duration: 0.2 }}
            />
          </div>
          <p className="text-sm text-gray-500 mt-4">Team photos coming soon</p>
        </motion.div>
      </div>
    </section>
  );
}
