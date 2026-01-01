/**
 * Dashboard Layout
 *
 * Built following skills:
 * - @.claude/skills/mjs/building-nextjs-apps (Next.js 16 App Router layout pattern)
 * - @.claude/skills/custom/frontend-design-system/references/responsive-design-patterns
 *
 * Features:
 * - Server Component layout
 * - Responsive grid with sidebar
 * - Mobile-first design
 * - Sidebar integration
 */

import { Metadata } from "next";
import { DashboardSidebar } from "@/components/dashboard/DashboardSidebar";

export const metadata: Metadata = {
  title: "Dashboard - Todo Evolution",
  description: "Manage your tasks efficiently with Todo Evolution",
};

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex h-screen bg-gray-50 dark:bg-gray-900">
      <DashboardSidebar />
      <main className="flex-1 overflow-y-auto">
        <div className="container mx-auto px-4 py-6 md:px-6 md:py-8 lg:px-8 max-w-7xl">
          {children}
        </div>
      </main>
    </div>
  );
}
