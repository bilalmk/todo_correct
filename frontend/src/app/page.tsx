/**
 * Landing Page - First impression marketing page
 *
 * Features (per tasks.md T026-T027):
 * - Masthead with fixed navigation and mobile menu
 * - Hero section with orange/coral gradients and animations
 * - About section with mission statement and value props
 * - Features grid with icon cards
 * - Pricing section with Free and Premium tiers
 * - Footer with image attributions and links
 * - Smooth scroll behavior for anchor links (#features, #about, #pricing)
 *
 * Skills used:
 * - building-nextjs-apps: Next.js 16 App Router patterns, metadata, smooth scroll
 * - frontend-design-system: Responsive layout, component composition, orange/coral theme
 */

import { Metadata } from "next";
import { Masthead } from "@/components/home/Masthead";
import { Hero } from "@/components/home/Hero";
import { Features } from "@/components/home/Features";
import { About } from "@/components/home/About";
import { Pricing } from "@/components/home/Pricing";
import { Footer } from "@/components/home/Footer";

export const metadata: Metadata = {
  title: "Todo Evolution - Transform Your Productivity",
  description:
    "Experience the next generation of task management with powerful features, intuitive design, and seamless organization. Built with Next.js 16, TypeScript, and modern web technologies.",
  keywords: [
    "todo app",
    "task management",
    "productivity",
    "organization",
    "next.js",
    "typescript",
  ],
  authors: [{ name: "Todo Evolution Team" }],
  openGraph: {
    title: "Todo Evolution - Transform Your Productivity",
    description:
      "The next generation of task management with powerful features and beautiful design.",
    type: "website",
    locale: "en_US",
  },
  twitter: {
    card: "summary_large_image",
    title: "Todo Evolution - Transform Your Productivity",
    description:
      "Experience the next generation of task management with powerful features.",
  },
};

export default function HomePage() {
  return (
    <>
      {/* Fixed Masthead Navigation (T026) */}
      <Masthead />

      {/* Main Content with Smooth Scroll (T027) */}
      <main className="min-h-screen scroll-smooth">
        <Hero />
        <Features />
        <About />
        <Pricing />
        <Footer />
      </main>
    </>
  );
}
