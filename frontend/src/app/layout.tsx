/**
 * Root layout for Next.js App Router with context providers
 * T019: Updated to use Better Auth (managed via authClient, no provider needed)
 * T021a: Page transitions moved to template.tsx (Next.js recommended pattern)
 * T004: ChatKit CDN script added (Feature: 009-chatkit-frontend)
 */
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import Script from "next/script";
import "./globals.css";
import { TaskProvider } from "@/contexts/TaskContext";
import { TagProvider } from "@/contexts/TagContext";
import { FilterProvider } from "@/contexts/FilterContext";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Todo Evolution - Modern Task Management",
  description: "A sophisticated todo application with powerful features powered by Better Auth",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <head>
        {/* T004: ChatKit Integration (Feature: 009-chatkit-frontend)
            - OpenAI ChatKit SDK doesn't exist as a CDN product
            - Instead: Building custom chat interface with React components
            - Backend handles OpenAI API communication via /api/chatkit proxy
            - No external SDK loading required
        */}
      </head>
      <body className={inter.className}>
        {/*
          T019: Better Auth integration
          - Authentication managed via authClient (no provider wrapper needed)
          - Session available via authClient.getSession()
          - JWT tokens handled automatically via httpOnly cookies

          T021a: Page transitions implemented in template.tsx
          - Fade-in/slide-up animations (200ms-400ms duration)
          - Applied to all route changes per FR-037
        */}
        <TaskProvider>
          <TagProvider>
            <FilterProvider>
              {children}
              <Toaster />
            </FilterProvider>
          </TagProvider>
        </TaskProvider>
      </body>
    </html>
  );
}
