/**
 * Better Auth client configuration for client-side usage
 * T011: Updated with JWT plugin (EdDSA/Ed25519 algorithm)
 *
 * This is used in:
 * - Client components for authentication UI
 * - Middleware for session validation
 * - API client for getting JWT tokens
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
 *
 * Usage in API client:
 * ```ts
 * const session = await authClient.getSession();
 * const token = session?.session?.token; // JWT token for backend API
 * ```
 */
import { createAuthClient } from "better-auth/client";
import { jwtClient } from "better-auth/client/plugins";

// T011: Create Better Auth client with JWT plugin
export const authClient = createAuthClient({
  baseURL: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
  plugins: [
    jwtClient(), // Enable JWT token management (EdDSA/Ed25519)
  ],
});
