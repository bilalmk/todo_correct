/**
 * Next.js Middleware for Protected Routes
 * T020: Auth middleware using Better Auth session validation
 *
 * Features:
 * - Checks for active Better Auth session
 * - Redirects unauthenticated users to login
 * - Protects dashboard and other authenticated routes
 * - Allows public routes (/, /auth/*)
 */

import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";
import { authClient } from "@/lib/auth-client";

/**
 * Protected routes that require authentication
 */
const protectedRoutes = ["/dashboard", "/settings", "/profile"];

/**
 * Public routes that don't require authentication
 */
const publicRoutes = [
  "/",
  "/auth/login",
  "/auth/register",
  "/about",
  "/features",
];

/**
 * Auth routes (redirect to dashboard if already logged in)
 */
const authRoutes = ["/auth/login", "/auth/register"];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if the current path is protected
  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  );
  const isPublicRoute = publicRoutes.includes(pathname);
  const isAuthRoute = authRoutes.includes(pathname);

  try {
    // Get Better Auth session
    const session = await authClient.getSession({
      fetchOptions: {
        headers: {
          cookie: request.headers.get("cookie") || "",
        },
      },
    });

    const isAuthenticated = !!session?.data?.session;

    // T020: Redirect to login if accessing protected route without session
    if (isProtectedRoute && !isAuthenticated) {
      const loginUrl = new URL("/auth/login", request.url);
      loginUrl.searchParams.set("from", pathname); // Save redirect path
      return NextResponse.redirect(loginUrl);
    }

    // Redirect to dashboard if accessing auth routes while logged in
    if (isAuthRoute && isAuthenticated) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }

    // Allow the request to proceed
    return NextResponse.next();
  } catch (error) {
    console.error("Middleware auth check error:", error);

    // On error, allow public routes, redirect protected routes to login
    if (isProtectedRoute) {
      return NextResponse.redirect(new URL("/auth/login", request.url));
    }

    return NextResponse.next();
  }
}

/**
 * Matcher configuration
 * Run middleware on all routes except static files and API routes
 */
export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api (API routes)
     * - _next/static (static files)
     * - _next/image (image optimization files)
     * - favicon.ico (favicon file)
     * - public folder
     */
    "/((?!api|_next/static|_next/image|favicon.ico|.*\\..*|public).*)",
  ],
};
