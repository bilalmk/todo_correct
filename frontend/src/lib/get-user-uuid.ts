/**
 * Get User UUID from Better Auth Session
 *
 * Extracts the UUID from the JWT token's custom claims.
 * The UUID is included in the JWT by the server-side Better Auth configuration.
 *
 * Usage:
 * ```ts
 * const session = await authClient.getSession();
 * const uuid = getUserUuid(session);
 * if (!uuid) {
 *   throw new Error("Please log in");
 * }
 * ```
 */

import { authClient } from "./auth-client";

interface JWTPayload {
  uuid?: string;
  sub?: string;
  iat?: number;
  exp?: number;
  [key: string]: any;
}

/**
 * Decode JWT token and extract UUID
 */
function decodeJWT(token: string): JWTPayload | null {
  try {
    // JWT format: header.payload.signature
    const parts = token.split(".");
    if (parts.length !== 3) {
      console.error("[JWT Decode] Invalid JWT format - expected 3 parts, got:", parts.length);
      return null;
    }

    // Decode the payload (base64url)
    const payload = parts[1];
    const decoded = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    const parsed = JSON.parse(decoded);

    // T085: NEVER log JWT payloads - contains sensitive user data
    // Only log presence of UUID claim, not the actual data
    console.log("[JWT Decode] UUID claim present:", !!parsed.uuid);

    return parsed;
  } catch (error) {
    console.error("[JWT Decode] Failed to decode JWT:", error);
    return null;
  }
}

/**
 * Get user UUID from Better Auth session
 *
 * @returns UUID string or null if not available
 */
export async function getUserUuid(): Promise<string | null> {
  try {
    const session = await authClient.getSession();

    console.log("[getUserUuid] Session exists:", !!session?.data);

    if (!session?.data?.user) {
      console.error("[getUserUuid] No session found");
      return null;
    }

    // Get JWT token from Better Auth JWT plugin endpoint
    const response = await fetch(`${process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000"}/api/auth/get-token`, {
      credentials: 'include', // Include cookies for session
    });

    if (!response.ok) {
      console.error("[getUserUuid] Failed to get JWT token:", response.status);
      return null;
    }

    const data = await response.json();
    const token = data.token;

    console.log("[getUserUuid] JWT token fetched:", !!token);

    if (!token) {
      console.error("[getUserUuid] No JWT token in response");
      return null;
    }

    const payload = decodeJWT(token);
    return payload?.uuid || null;
  } catch (error) {
    console.error("[getUserUuid] Failed to get user UUID:", error);
    return null;
  }
}

/**
 * Get user UUID from Better Auth session (async version)
 * Use this when you already have checked for session existence
 *
 * This is just an alias to getUserUuid() for backwards compatibility
 * @returns UUID string or null if not available
 */
export async function getUserUuidFromSession(session?: any): Promise<string | null> {
  // Just call getUserUuid() which handles fetching the JWT token
  return getUserUuid();
}
