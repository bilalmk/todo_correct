/**
 * User Entity Schema
 *
 * TypeScript type definition and Zod validation schema for User entity.
 * Used for type safety and runtime validation in the frontend application.
 *
 * Feature: 004-frontend-design
 * Phase: UI-only implementation (mock authentication only)
 */

import { z } from "zod"

/**
 * User TypeScript Interface
 *
 * Represents the authenticated user profile (mock data for UI-only phase).
 * Authentication is simulated with no real JWT validation.
 */
export interface User {
  // Identity
  id: string

  // Profile
  name: string
  email: string
  avatar_url?: string | null  // Optional profile picture URL
}

/**
 * Zod Validation Schema for User
 *
 * Used for runtime validation of user profile data.
 */
export const userSchema = z.object({
  id: z.string().min(1, "User ID is required"),

  name: z
    .string()
    .min(1, "Name is required")
    .max(100, "Name must be 100 characters or less")
    .refine((val) => val.trim().length > 0, "Name cannot be only whitespace"),

  email: z
    .string()
    .email("Invalid email address")
    .min(1, "Email is required"),

  avatar_url: z
    .string()
    .url("Avatar URL must be a valid URL")
    .nullable()
    .optional(),
})

/**
 * AuthState Interface
 *
 * Represents the mock authentication state managed in AuthContext.
 */
export interface AuthState {
  isAuthenticated: boolean
  user: User | null
}

/**
 * Zod Schema for Login Form
 *
 * Used in the login page for form validation.
 */
export const loginSchema = z.object({
  email: z
    .string()
    .email("Invalid email address")
    .min(1, "Email is required"),

  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .max(100, "Password must be 100 characters or less"),
})

export type LoginInput = z.infer<typeof loginSchema>

/**
 * Zod Schema for Registration Form
 *
 * Used in the registration page for form validation.
 * Includes password strength validation.
 */
export const registerSchema = z
  .object({
    name: z
      .string()
      .min(1, "Name is required")
      .max(100, "Name must be 100 characters or less")
      .refine((val) => val.trim().length > 0, "Name cannot be only whitespace"),

    email: z
      .string()
      .email("Invalid email address")
      .min(1, "Email is required"),

    password: z
      .string()
      .min(8, "Password must be at least 8 characters")
      .max(100, "Password must be 100 characters or less")
      .regex(/[A-Z]/, "Password must contain at least one uppercase letter")
      .regex(/[0-9]/, "Password must contain at least one number"),

    confirmPassword: z
      .string()
      .min(1, "Please confirm your password"),
  })
  .refine((data) => data.password === data.confirmPassword, {
    message: "Passwords do not match",
    path: ["confirmPassword"],
  })

export type RegisterInput = z.infer<typeof registerSchema>

/**
 * Password Strength Levels
 */
export const PasswordStrength = {
  WEAK: "weak",
  MEDIUM: "medium",
  STRONG: "strong",
} as const

export type PasswordStrengthType = typeof PasswordStrength[keyof typeof PasswordStrength]

/**
 * Helper: Calculate password strength
 *
 * Used for real-time password strength indicator in registration form.
 */
export function calculatePasswordStrength(password: string): PasswordStrengthType {
  if (password.length < 8) {
    return PasswordStrength.WEAK
  }

  let strength = 0

  // Length check
  if (password.length >= 12) strength++
  if (password.length >= 16) strength++

  // Complexity checks
  if (/[a-z]/.test(password)) strength++  // Lowercase
  if (/[A-Z]/.test(password)) strength++  // Uppercase
  if (/[0-9]/.test(password)) strength++  // Numbers
  if (/[^a-zA-Z0-9]/.test(password)) strength++  // Special characters

  if (strength <= 2) return PasswordStrength.WEAK
  if (strength <= 4) return PasswordStrength.MEDIUM
  return PasswordStrength.STRONG
}

/**
 * Helper: Get password strength color
 *
 * Used for visual feedback in password strength indicator.
 */
export function getPasswordStrengthColor(strength: PasswordStrengthType): string {
  switch (strength) {
    case PasswordStrength.WEAK:
      return "#EF4444" // Red
    case PasswordStrength.MEDIUM:
      return "#F59E0B" // Orange
    case PasswordStrength.STRONG:
      return "#10B981" // Green
  }
}

/**
 * Mock User Data
 *
 * Default user profile for UI-only implementation.
 */
export const MOCK_USER: User = {
  id: "user_demo_123",
  name: "Demo User",
  email: "demo@todoapp.com",
  avatar_url: null,
}

/**
 * Helper: Mock login (simulate async authentication)
 *
 * In UI-only phase, this validates form input and returns mock user.
 * Replace with real API call in integration phase.
 */
export async function mockLogin(input: LoginInput): Promise<User> {
  // Validate input
  loginSchema.parse(input)

  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 500))

  // Mock: any valid email/password returns demo user
  return MOCK_USER
}

/**
 * Helper: Mock registration (simulate async user creation)
 *
 * In UI-only phase, this validates form input and returns mock user.
 * Replace with real API call in integration phase.
 */
export async function mockRegister(input: RegisterInput): Promise<User> {
  // Validate input (including password confirmation)
  registerSchema.parse(input)

  // Simulate API delay
  await new Promise((resolve) => setTimeout(resolve, 800))

  // Mock: return demo user with provided name/email
  return {
    id: `user_${Date.now()}`,
    name: input.name,
    email: input.email,
    avatar_url: null,
  }
}

/**
 * Helper: Mock logout
 *
 * Clears authentication state (no API call needed in UI-only phase).
 */
export function mockLogout(): void {
  // In integration phase, this would call the logout endpoint
  // For now, just return (AuthContext handles state clearing)
}
