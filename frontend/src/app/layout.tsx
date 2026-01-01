/**
 * Root layout for Next.js App Router with context providers
 */
import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { AuthProvider } from "@/contexts/AuthContext";
import { TaskProvider } from "@/contexts/TaskContext";
import { TagProvider } from "@/contexts/TagContext";
import { FilterProvider } from "@/contexts/FilterContext";
import { Toaster } from "@/components/ui/sonner";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Todo Evolution - Modern Task Management",
  description: "A sophisticated todo application with powerful features",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={inter.className}>
        <AuthProvider>
          <TaskProvider>
            <TagProvider>
              <FilterProvider>
                {children}
                <Toaster />
              </FilterProvider>
            </TagProvider>
          </TaskProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
