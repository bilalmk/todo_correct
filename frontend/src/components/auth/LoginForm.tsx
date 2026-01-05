"use client";

/**
 * LoginForm Component
 *
 * Built following skills:
 * - @.claude/skills/custom/frontend-design-system (Form patterns with React Hook Form + Zod)
 * - @.claude/skills/custom/frontend-design-system/references/shadcn-components (Form components)
 *
 * Features:
 * - Real-time validation with error messages
 * - Accessible form labels and error announcements
 * - Responsive design (mobile-first)
 * - Loading states during submission
 * - Password visibility toggle
 */

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { useRouter } from "next/navigation";
import { toast } from "sonner";
import { Eye, EyeOff, Loader2 } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Form,
  FormControl,
  FormField,
  FormItem,
  FormLabel,
  FormMessage,
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";
import { loginSchema, LoginFormData } from "@/lib/validation-schemas";
import { authClient } from "@/lib/auth-client";

export function LoginForm() {
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const router = useRouter();

  const form = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
    defaultValues: {
      email: "",
      password: "",
    },
  });

  const onSubmit = async (data: LoginFormData) => {
    setIsLoading(true);
    try {
      // T017: Use Better Auth signIn.email with error handling
      const result = await authClient.signIn.email({
        email: data.email,
        password: data.password,
      });

      if (result.error) {
        // Handle Better Auth errors
        toast.error(result.error.message || "Invalid email or password. Please try again.");
        return;
      }

      // Success - Better Auth sets JWT cookie automatically
      toast.success("Welcome back! Redirecting to dashboard...");
      router.push("/dashboard");
      router.refresh(); // Refresh to update session
    } catch (error) {
      console.error("Login error:", error);
      toast.error("An unexpected error occurred. Please try again.");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <Form {...form}>
      <form onSubmit={form.handleSubmit(onSubmit)} className="space-y-6">
        {/* Email field */}
        <FormField
          control={form.control}
          name="email"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-sm font-medium">
                Email Address
              </FormLabel>
              <FormControl>
                <Input
                  type="email"
                  placeholder="you@example.com"
                  autoComplete="email"
                  disabled={isLoading}
                  className="h-11"
                  {...field}
                />
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Password field */}
        <FormField
          control={form.control}
          name="password"
          render={({ field }) => (
            <FormItem>
              <FormLabel className="text-sm font-medium">Password</FormLabel>
              <FormControl>
                <div className="relative">
                  <Input
                    type={showPassword ? "text" : "password"}
                    placeholder="Enter your password"
                    autoComplete="current-password"
                    disabled={isLoading}
                    className="h-11 pr-10"
                    {...field}
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 transition-colors"
                    aria-label={showPassword ? "Hide password" : "Show password"}
                  >
                    {showPassword ? (
                      <EyeOff className="h-4 w-4" />
                    ) : (
                      <Eye className="h-4 w-4" />
                    )}
                  </button>
                </div>
              </FormControl>
              <FormMessage />
            </FormItem>
          )}
        />

        {/* Forgot password link (frontend-design-system: 44px touch target) */}
        <div className="flex items-center justify-end">
          <button
            type="button"
            className="text-sm text-primary hover:text-secondary dark:text-primary dark:hover:text-secondary transition-colors duration-300 min-h-[44px] flex items-center"
            onClick={() => toast.info("Password reset feature coming soon!")}
          >
            Forgot password?
          </button>
        </div>

        {/* Submit button (frontend-design-system: 44px height, gradient from primary to secondary) */}
        <Button
          type="submit"
          disabled={isLoading}
          className="w-full h-11 bg-gradient-to-r from-primary to-secondary hover:opacity-90 text-white transition-opacity duration-300"
        >
          {isLoading ? (
            <>
              <Loader2 className="mr-2 h-4 w-4 animate-spin" />
              Signing in...
            </>
          ) : (
            "Sign In"
          )}
        </Button>
      </form>
    </Form>
  );
}
