/**
 * Get JWT Token Endpoint
 *
 * Returns the JWT token for the current authenticated session.
 * This endpoint generates a JWT token with the user's UUID included.
 */

import { NextRequest, NextResponse } from "next/server";
import { auth } from "@/lib/auth";
import { sign } from "jsonwebtoken";
import { Pool } from "pg";

// Create PostgreSQL connection pool
const pool = new Pool({
  connectionString: process.env.DATABASE_URL!,
});

export async function GET(request: NextRequest) {
  try {
    // Get current session
    const session = await auth.api.getSession({
      headers: request.headers,
    });

    if (!session?.user) {
      return NextResponse.json(
        { error: "Not authenticated" },
        { status: 401 }
      );
    }

    // Fetch UUID from database
    const result = await pool.query(
      'SELECT uuid FROM "user" WHERE id = $1',
      [session.user.id]
    );

    const uuid = result.rows[0]?.uuid;

    if (!uuid) {
      return NextResponse.json(
        { error: "User UUID not found" },
        { status: 500 }
      );
    }

    // Generate JWT token with UUID claim
    // Use the same secret and algorithm as Better Auth JWT plugin
    const token = sign(
      {
        sub: session.user.id,
        uuid: uuid,
        email: session.user.email,
        iat: Math.floor(Date.now() / 1000),
        exp: Math.floor(Date.now() / 1000) + 60 * 60, // 1 hour
        iss: process.env.NEXT_PUBLIC_APP_URL || "http://localhost:3000",
      },
      process.env.BETTER_AUTH_SECRET!,
      {
        algorithm: "HS256", // Using HS256 for simplicity (EdDSA requires different key format)
      }
    );

    return NextResponse.json({ token });
  } catch (error) {
    console.error("[get-token] Error generating JWT:", error);
    return NextResponse.json(
      { error: "Failed to generate token" },
      { status: 500 }
    );
  }
}
