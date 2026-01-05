'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import { Check } from 'lucide-react';

/**
 * Pricing Section Component
 *
 * Features (per tasks.md T023):
 * - Simple pricing structure: Free tier features (3-5 items)
 * - Premium tier with "Contact Us" CTA
 * - Styled with orange/coral accents
 * - Minimal actual content (hackathon requirement)
 *
 * Skills used:
 * - frontend-design-system: Card component patterns, responsive grid layout
 *   - Pattern: Pricing card with consistent border-radius (8px), borders (2px), shadows
 *   - Pattern: Button sizing (44px min-height for accessibility)
 *   - Pattern: Hover effects with elevation changes
 * - building-nextjs-apps: Framer Motion animations, responsive breakpoints
 */
export function Pricing() {
  const pricingTiers = [
    {
      name: 'Free',
      price: '$0',
      period: 'forever',
      description: 'Perfect for individuals getting started with task management',
      features: [
        'Unlimited tasks',
        'Drag & drop reordering',
        'Task priorities & tags',
        'Search & filtering',
        'Mobile responsive',
      ],
      cta: 'Get Started Free',
      ctaLink: '/auth/register',
      highlighted: false,
      gradient: 'from-gray-50 to-gray-100',
      borderColor: 'border-gray-200',
      buttonStyle: 'border-2 border-primary text-primary hover:bg-primary hover:text-white',
    },
    {
      name: 'Premium',
      price: 'Custom',
      period: '',
      description: 'Advanced features for teams and power users',
      features: [
        'Everything in Free',
        'Team collaboration',
        'Advanced analytics',
        'Priority support',
        'Custom integrations',
      ],
      cta: 'Contact Sales',
      ctaLink: '/contact',
      highlighted: true,
      gradient: 'from-primary/10 to-secondary/10',
      borderColor: 'border-primary',
      buttonStyle: 'bg-gradient-to-r from-primary to-secondary text-white hover:opacity-90',
    },
  ];

  return (
    <section id="pricing" className="py-20 bg-gradient-to-br from-orange-50 via-white to-coral-50">
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
            Simple, Transparent Pricing
          </h2>
          <p className="text-lg md:text-xl text-gray-600">
            Start for free, upgrade when you need more. No hidden fees, no surprises.
          </p>
        </motion.div>

        {/* Pricing Cards (frontend-design-system pattern: card grid with responsive breakpoints) */}
        <div className="grid md:grid-cols-2 gap-8 max-w-5xl mx-auto">
          {pricingTiers.map((tier, index) => (
            <motion.div
              key={tier.name}
              className={`relative rounded-2xl p-8 bg-gradient-to-br ${tier.gradient} border-2 ${tier.borderColor} shadow-lg hover:shadow-xl transition-all duration-300`}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true, amount: 0.2 }}
              transition={{ duration: 0.6, delay: index * 0.1 }}
              whileHover={{ y: -5 }}
              style={{
                // frontend-design-system pattern: Consistent card styling
                // - border-radius: 16px (rounded-2xl = 1rem = 16px)
                // - border: 2px solid
                // - shadow: lg (moderate), hover: xl (pronounced)
                // - hover elevation: translateY(-5px)
              }}
            >
              {/* Highlighted Badge (Premium tier) */}
              {tier.highlighted && (
                <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                  <span className="bg-gradient-to-r from-primary to-secondary text-white px-4 py-1 rounded-full text-sm font-semibold shadow-md">
                    Most Popular
                  </span>
                </div>
              )}

              {/* Tier Name */}
              <h3 className="text-2xl font-bold mb-2 text-gray-800">{tier.name}</h3>

              {/* Price */}
              <div className="mb-4">
                <span className="text-5xl font-bold bg-gradient-to-r from-primary to-secondary bg-clip-text text-transparent">
                  {tier.price}
                </span>
                {tier.period && (
                  <span className="text-gray-600 ml-2">/ {tier.period}</span>
                )}
              </div>

              {/* Description */}
              <p className="text-gray-600 mb-6">{tier.description}</p>

              {/* Features List */}
              <ul className="space-y-3 mb-8">
                {tier.features.map((feature) => (
                  <li key={feature} className="flex items-start gap-3">
                    <Check className="w-5 h-5 text-primary flex-shrink-0 mt-0.5" />
                    <span className="text-gray-700">{feature}</span>
                  </li>
                ))}
              </ul>

              {/* CTA Button (frontend-design-system pattern: 44px min-height, proper padding) */}
              <Link
                href={tier.ctaLink}
                className={`block w-full text-center px-6 py-3 rounded-lg font-semibold transition-all shadow-md hover:shadow-lg min-h-[44px] flex items-center justify-center ${tier.buttonStyle}`}
                style={{
                  // frontend-design-system pattern: Button sizing
                  // - min-height: 44px (WCAG touch target)
                  // - padding: px-6 (24px horizontal), py-3 (12px vertical)
                  // - transition: all 300ms for smooth hover effects
                }}
              >
                {tier.cta}
              </Link>
            </motion.div>
          ))}
        </div>

        {/* Trust Indicators */}
        <motion.div
          className="mt-16 text-center"
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true, amount: 0.2 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <p className="text-gray-600 mb-4">Trusted by productive teams worldwide</p>
          <div className="flex justify-center gap-8 flex-wrap">
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-sm text-gray-600">30-day money-back guarantee</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-sm text-gray-600">Cancel anytime</span>
            </div>
            <div className="flex items-center gap-2">
              <svg className="w-5 h-5 text-green-500" fill="currentColor" viewBox="0 0 20 20">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              <span className="text-sm text-gray-600">24/7 customer support</span>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
