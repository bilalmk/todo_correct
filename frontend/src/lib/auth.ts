/**
 * Better Auth configuration and utilities
 */
import { betterAuth } from "better-auth";
import { Pool } from "pg";

// Create PostgreSQL connection pool for Better Auth
const pool = new Pool({
  connectionString: process.env.DATABASE_URL,
  max: 10,
  idleTimeoutMillis: 30000,
  connectionTimeoutMillis: 2000,
});

// Initialize Better Auth
export const auth = betterAuth({
  database: {
    provider: "pg",
    pg: pool,
  },
  emailAndPassword: {
    enabled: true,
    requireEmailVerification: false, // Phase II: Disabled for simplicity
  },
  secret: process.env.BETTER_AUTH_SECRET!,
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  session: {
    expiresIn: 60 * 60 * 24 * 7, // 7 days
    updateAge: 60 * 60 * 24, // 1 day
    cookieCache: {
      enabled: true,
      maxAge: 60 * 5, // 5 minutes
    },
  },
  advanced: {
    cookiePrefix: "todo_auth",
    useSecureCookies: process.env.NODE_ENV === "production",
  },
});

/**
 * Get current session on the server side
 */
export async function getSession() {
  return await auth.api.getSession({
    headers: await import("next/headers").then((mod) => mod.headers()),
  });
}

/**
 * Sign out helper function
 */
export async function signOut() {
  await auth.api.signOut({
    headers: await import("next/headers").then((mod) => mod.headers()),
  });
}
