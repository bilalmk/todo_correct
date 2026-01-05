/**
 * Better Auth API route handler
 *
 * This catch-all route handles all Better Auth endpoints:
 * - POST /api/auth/sign-up
 * - POST /api/auth/sign-in/email
 * - POST /api/auth/sign-out
 * - GET /api/auth/session
 */
import { auth } from "@/lib/auth";
import { toNextJsHandler } from "better-auth/next-js";

export const { GET, POST } = toNextJsHandler(auth);
