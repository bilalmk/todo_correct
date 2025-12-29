/**
 * Next.js middleware for route protection
 *
 * Protects authenticated routes and redirects unauthenticated users to login
 */
import { NextRequest, NextResponse } from "next/server";
import { authClient } from "./src/lib/auth-client";

// Define protected routes
const protectedRoutes = ["/dashboard"];
const authRoutes = ["/auth/login", "/auth/register"];

export async function middleware(request: NextRequest) {
  const { pathname } = request.nextUrl;

  // Check if route requires authentication
  const isProtectedRoute = protectedRoutes.some((route) =>
    pathname.startsWith(route)
  );
  const isAuthRoute = authRoutes.some((route) => pathname.startsWith(route));

  try {
    // Get session from Better Auth with cookies from the request
    const session = await authClient.getSession({
      fetchOptions: {
        headers: {
          cookie: request.headers.get("cookie") || "",
        },
      },
    });

    const isAuthenticated = !!session?.data?.session;

    // Redirect unauthenticated users away from protected routes
    if (isProtectedRoute && !isAuthenticated) {
      const loginUrl = new URL("/auth/login", request.url);
      loginUrl.searchParams.set("redirect", pathname);
      return NextResponse.redirect(loginUrl);
    }

    // Redirect authenticated users away from auth routes
    if (isAuthRoute && isAuthenticated) {
      return NextResponse.redirect(new URL("/dashboard", request.url));
    }

    return NextResponse.next();
  } catch (error) {
    // On error, allow request to proceed (fail open for now)
    console.error("Middleware error:", error);
    return NextResponse.next();
  }
}

export const config = {
  matcher: [
    /*
     * Match all request paths except:
     * - api routes
     * - _next/static (static files)
     * - _next/image (image optimization)
     * - favicon.ico
     */
    "/((?!api|_next/static|_next/image|favicon.ico).*)",
  ],
};
