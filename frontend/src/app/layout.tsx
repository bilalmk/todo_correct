/**
 * Root layout for Next.js App Router with context providers
 * T019: Updated to use Better Auth (managed via authClient, no provider needed)
 */
import type { Metadata } from "next";
import { Inter } from "next/font/google";
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
      <body className={inter.className}>
        {/*
          T019: Better Auth integration
          - Authentication managed via authClient (no provider wrapper needed)
          - Session available via authClient.getSession()
          - JWT tokens handled automatically via httpOnly cookies
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
