/**
 * Login Page
 *
 * Built following skills:
 * - @.claude/skills/mjs/building-nextjs-apps (Next.js 16 App Router patterns)
 * - @.claude/skills/custom/frontend-design-system (Responsive layout patterns)
 *
 * Features:
 * - Server Component with proper metadata
 * - Responsive layout (centered card on desktop, full-screen on mobile)
 * - Brand consistency with landing page
 * - Accessible navigation and links
 */

import { Metadata } from "next";
import Link from "next/link";
import { LoginForm } from "@/components/auth/LoginForm";
import { ArrowLeft } from "lucide-react";

export const metadata: Metadata = {
  title: "Sign In - Todo Evolution",
  description: "Sign in to your Todo Evolution account to manage your tasks.",
};

export default function LoginPage() {
  return (
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-purple-50 via-white to-indigo-50 dark:from-gray-900 dark:via-gray-800 dark:to-purple-900">
      {/* Header */}
      <header className="w-full p-4 md:p-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-purple-600 dark:text-gray-400 dark:hover:text-purple-400 transition-colors"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to home
        </Link>
      </header>

      {/* Main content */}
      <main className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-md">
          {/* Card */}
          <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-xl p-6 md:p-8 border border-gray-200 dark:border-gray-700">
            {/* Logo/Brand */}
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-purple-600 to-indigo-600 dark:from-purple-400 dark:to-indigo-400 mb-2">
                Todo Evolution
              </h1>
              <p className="text-gray-600 dark:text-gray-400">
                Welcome back! Sign in to continue
              </p>
            </div>

            {/* Login Form */}
            <LoginForm />

            {/* Divider */}
            <div className="relative my-6">
              <div className="absolute inset-0 flex items-center">
                <div className="w-full border-t border-gray-300 dark:border-gray-600" />
              </div>
              <div className="relative flex justify-center text-sm">
                <span className="px-2 bg-white dark:bg-gray-800 text-gray-500 dark:text-gray-400">
                  Don't have an account?
                </span>
              </div>
            </div>

            {/* Sign up link */}
            <div className="text-center">
              <Link
                href="/auth/register"
                className="text-sm font-medium text-purple-600 hover:text-purple-700 dark:text-purple-400 dark:hover:text-purple-300 transition-colors"
              >
                Create a free account
              </Link>
            </div>
          </div>

          {/* Footer note */}
          <p className="text-center text-xs text-gray-500 dark:text-gray-400 mt-6">
            Protected by industry-standard encryption
          </p>
        </div>
      </main>
    </div>
  );
}
