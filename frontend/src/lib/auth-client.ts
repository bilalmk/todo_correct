/**
 * Better Auth client configuration for client-side usage
 *
 * This is used in:
 * - Client components for authentication UI
 * - Middleware for session validation
 *
 * Usage in middleware:
 * ```ts
 * const session = await authClient.getSession({
 *   fetchOptions: {
 *     headers: {
 *       cookie: request.headers.get("cookie") || "",
 *     },
 *   },
 * });
 * ```
 */
import { createAuthClient } from "better-auth/client";

// Create Better Auth client
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
});
