/**
 * Environment variable validation and type-safe access
 */
import { z } from "zod";

const envSchema = z.object({
  // Public variables (accessible in browser)
  NEXT_PUBLIC_APP_URL: z.string().url().default("http://localhost:3000"),
  NEXT_PUBLIC_BACKEND_API_URL: z.string().url().default("http://localhost:8000"),

  // ChatKit configuration (Feature: 009-chatkit-frontend, Task: T002a)
  // Note: OPENAI_DOMAIN_KEY is a placeholder - real auth happens via backend JWT
  NEXT_PUBLIC_OPENAI_DOMAIN_KEY: z.string().optional().default("chatkit-placeholder"),
  NEXT_PUBLIC_BACKEND_URL: z.string().url().default("http://localhost:8000"),

  // Server-only variables
  DATABASE_URL: z.string().min(1),
  BETTER_AUTH_SECRET: z.string().min(32),
  NODE_ENV: z.enum(["development", "production", "test"]).default("development"),
});

type Env = z.infer<typeof envSchema>;

function validateEnv(): Env {
  try {
    return envSchema.parse({
      NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL,
      NEXT_PUBLIC_BACKEND_API_URL: process.env.NEXT_PUBLIC_BACKEND_API_URL,
      NEXT_PUBLIC_OPENAI_DOMAIN_KEY: process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY,
      NEXT_PUBLIC_BACKEND_URL: process.env.NEXT_PUBLIC_BACKEND_URL,
      DATABASE_URL: process.env.DATABASE_URL,
      BETTER_AUTH_SECRET: process.env.BETTER_AUTH_SECRET,
      NODE_ENV: process.env.NODE_ENV,
    });
  } catch (error) {
    if (error instanceof z.ZodError) {
      console.error("❌ Invalid environment variables:");
      console.error(error.flatten().fieldErrors);
      throw new Error("Invalid environment variables");
    }
    throw error;
  }
}

export const env = validateEnv();
