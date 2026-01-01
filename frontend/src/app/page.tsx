/**
 * Landing Page - First impression marketing page
 *
 * Uses components from @/components/home following responsive design patterns
 * and Tech Innovation theme (purple primary color).
 *
 * Built following skills:
 * - @.claude/skills/panaversity/theme-factory (Tech Innovation theme)
 * - @.claude/skills/custom/frontend-design-system (responsive patterns)
 * - @.claude/skills/mjs/building-nextjs-apps (Next.js 16 patterns)
 */

import { Metadata } from "next";
import { Hero } from "@/components/home/Hero";
import { Features } from "@/components/home/Features";
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
    <main className="min-h-screen">
      <Hero />
      <Features />
      <Footer />
    </main>
  );
}
