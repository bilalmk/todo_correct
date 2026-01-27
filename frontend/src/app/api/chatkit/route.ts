/**
 * ChatKit API Proxy Route
 * Feature: 009-chatkit-frontend
 * Task: T007, T023-T025 (JWT extraction, Authorization header, error handling)
 *
 * Purpose:
 * - Extract JWT from Better Auth session (httpOnly cookie)
 * - Forward requests to backend ChatKit endpoint with Authorization header
 * - Stream SSE responses back to client
 * - Maintain security: No API keys exposed in frontend
 *
 * Architecture (from plan.md):
 * Frontend (ChatKit SDK) → API Proxy (this file) → Backend (/api/chatkit/chat)
 *
 * Why needed:
 * - Better Auth stores JWT in httpOnly cookies (not accessible via JavaScript)
 * - ChatKit SDK runs client-side and cannot access httpOnly cookies
 * - This server-side route extracts JWT and adds Authorization header
 */

import { NextRequest, NextResponse } from 'next/server';
import { auth } from '@/lib/auth';
import { sign } from 'jsonwebtoken';
import { Pool } from 'pg';

// PostgreSQL connection pool for user UUID lookup
const pool = new Pool({
  connectionString: process.env.DATABASE_URL!,
});

/**
 * POST /api/chatkit
 *
 * Proxy ChatKit requests to backend with JWT authentication
 *
 * Request body (from ChatKit SDK via custom fetch):
 * ```json
 * {
 *   "message": "Add a task to buy groceries",
 *   "thread_id": "550e8400-e29b-41d4-a716-446655440000",
 *   "context": {
 *     "correlation_id": "...",
 *     "page_context": {...},
 *     "timestamp": "..."
 *   }
 * }
 * ```
 *
 * Response: SSE stream from backend (text/event-stream)
 *
 * Error responses:
 * - 401: Not authenticated (no valid session)
 * - 502: Backend unavailable
 */
export async function POST(request: NextRequest) {
  try {
    // ===== T023: JWT Extraction from Better Auth Session =====

    // Get current session from Better Auth
    // Session is managed via httpOnly cookies (secure)
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    // Check if user is authenticated
    if (!session?.user) {
      console.warn('[ChatKit Proxy] Unauthorized: No valid session');
      return NextResponse.json(
        {
          error: 'Authentication required',
          code: 'AUTHENTICATION_ERROR',
          message: 'Please sign in to use the chatbot',
        },
        { status: 401 }
      );
    }

    // Fetch user UUID from database (required for backend API)
    const result = await pool.query(
      'SELECT uuid FROM "user" WHERE id = $1',
      [session.user.id]
    );

    const uuid = result.rows[0]?.uuid;

    if (!uuid) {
      console.error('[ChatKit Proxy] User UUID not found:', session.user.id);
      return NextResponse.json(
        {
          error: 'User configuration error',
          code: 'USER_UUID_NOT_FOUND',
        },
        { status: 500 }
      );
    }

    // Generate JWT token with user UUID
    // Backend expects JWT with 'uuid' claim for user identification
    const token = sign(
      {
        sub: session.user.id,
        uuid: uuid,
        email: session.user.email,
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + 60 * 60, // 1 hour expiry
        iss: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
      },
      process.env.BETTER_AUTH_SECRET!,
      {
        algorithm: 'HS256',
      }
    );

    // ===== T024: Forward Request to Backend with Authorization Header =====

    // Extract correlation ID from request headers (added by custom fetch)
    const correlationId = request.headers.get('X-Correlation-ID') || crypto.randomUUID();

    // Read request body
    const body = await request.json();

    // Build backend request URL
    const backendUrl = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';
    const targetUrl = `${backendUrl}/api/chatkit/chat`;

    console.log(`[ChatKit Proxy] Forwarding request to backend: ${targetUrl}`, {
      correlation_id: correlationId,
      user_uuid: uuid,
    });

    // Forward request to backend with Authorization header
    const backendResponse = await fetch(targetUrl, {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
        'Content-Type': 'application/json',
        'X-Correlation-ID': correlationId,
      },
      body: JSON.stringify(body),
    });

    // ===== T025: Error Handling =====

    // Handle backend unavailable (502)
    if (!backendResponse.ok) {
      const errorText = await backendResponse.text();
      console.error('[ChatKit Proxy] Backend error:', {
        status: backendResponse.status,
        statusText: backendResponse.statusText,
        error: errorText,
        correlation_id: correlationId,
      });

      // If backend returns 401, it means JWT is invalid (shouldn't happen)
      if (backendResponse.status === 401) {
        return NextResponse.json(
          {
            error: 'Backend authentication failed',
            code: 'BACKEND_AUTH_ERROR',
            correlation_id: correlationId,
          },
          { status: 502 } // Return 502 to frontend (backend issue)
        );
      }

      // For other errors, return 502 Bad Gateway
      return NextResponse.json(
        {
          error: 'Backend service unavailable',
          code: 'BACKEND_UNAVAILABLE',
          status: backendResponse.status,
          correlation_id: correlationId,
        },
        { status: 502 }
      );
    }

    // ===== T037: Stream SSE Response =====

    // Backend returns SSE stream (text/event-stream)
    // We need to preserve the stream and forward it to the client

    // Create a new Response with the backend's body stream
    // This preserves SSE events without buffering
    const response = new NextResponse(backendResponse.body, {
      status: backendResponse.status,
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'X-Correlation-ID': correlationId,
      },
    });

    console.log(`[ChatKit Proxy] Streaming response to client`, {
      correlation_id: correlationId,
      content_type: backendResponse.headers.get('content-type'),
    });

    return response;
  } catch (error) {
    // Catch-all error handler
    console.error('[ChatKit Proxy] Unexpected error:', error);

    return NextResponse.json(
      {
        error: 'Internal server error',
        code: 'INTERNAL_ERROR',
        message: error instanceof Error ? error.message : 'Unknown error',
      },
      { status: 500 }
    );
  }
}

/**
 * OPTIONS /api/chatkit
 *
 * CORS preflight handler (if needed for external domains)
 * Currently not required as frontend and API proxy are same-origin
 */
export async function OPTIONS() {
  return new NextResponse(null, {
    status: 200,
    headers: {
      'Access-Control-Allow-Origin': '*',
      'Access-Control-Allow-Methods': 'POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Authorization, X-Correlation-ID',
    },
  });
}
