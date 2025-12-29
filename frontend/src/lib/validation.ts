/**
 * Zod validation schemas for forms
 */
import { z } from "zod";

/**
 * Registration form validation schema
 */
export const registerSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required")
    .email("Invalid email address")
    .toLowerCase()
    .trim(),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .max(100, "Password is too long"),
  name: z
    .string()
    .min(1, "Name is required")
    .max(255, "Name is too long")
    .trim(),
});

export type RegisterFormData = z.infer<typeof registerSchema>;

/**
 * Login form validation schema
 */
export const loginSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required")
    .email("Invalid email address")
    .toLowerCase()
    .trim(),
  password: z
    .string()
    .min(8, "Password must be at least 8 characters")
    .max(100, "Password is too long"),
});

export type LoginFormData = z.infer<typeof loginSchema>;
