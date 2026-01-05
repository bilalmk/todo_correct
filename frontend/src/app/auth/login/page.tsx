/**
 * Login Page - Updated with Orange/Coral Theme
 *
 * Features (per tasks.md T028):
 * - Orange/coral gradient background (from-orange-50 to-coral-50)
 * - Consistent design tokens from frontend-design-system skill
 * - Card styling: rounded-lg (8px), 2px borders, shadows
 * - Responsive layout (centered card on desktop, full-screen on mobile)
 * - 44px min touch targets for mobile accessibility
 *
 * Skills used:
 * - frontend-design-system: Card patterns, gradient backgrounds, responsive layout
 *   - Pattern: Card with 8px border-radius, 2px border, shadow-xl
 *   - Pattern: Gradient background (orange-50 to coral-50 in light mode)
 *   - Pattern: Consistent spacing and typography
 * - building-nextjs-apps: Next.js 16 App Router patterns, metadata
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
    <div className="min-h-screen flex flex-col bg-gradient-to-br from-orange-50 via-white to-coral-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-950">
      {/* Header */}
      <header className="w-full p-4 md:p-6">
        <Link
          href="/"
          className="inline-flex items-center gap-2 text-sm text-gray-600 hover:text-primary dark:text-gray-400 dark:hover:text-primary transition-colors duration-300"
        >
          <ArrowLeft className="h-4 w-4" />
          Back to home
        </Link>
      </header>

      {/* Main content */}
      <main className="flex-1 flex items-center justify-center px-4 py-8">
        <div className="w-full max-w-md">
          {/* Card (frontend-design-system pattern: 8px border-radius, 2px border) */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-xl p-6 md:p-8 border-2 border-gray-200 dark:border-gray-700">
            {/* Logo/Brand */}
            <div className="text-center mb-8">
              <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary via-secondary to-accent dark:from-primary dark:to-secondary mb-2">
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
                className="text-sm font-medium text-primary hover:text-secondary dark:text-primary dark:hover:text-secondary transition-colors duration-300"
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
