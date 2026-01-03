"""Custom middleware for FastAPI application."""
import time
import uuid
import logging
from typing import Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp

from .logging import set_correlation_id, get_correlation_id

logger = logging.getLogger(__name__)


class RequestIDMiddleware(BaseHTTPMiddleware):
    """
    Middleware to generate and track request IDs.

    Following fastapi-expert patterns for request tracking.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add request ID to all requests."""
        # Generate or extract request ID
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))

        # Set in context for logging
        set_correlation_id(request_id)

        # Store in request state
        request.state.request_id = request_id

        # Process request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers["X-Request-ID"] = request_id

        return response


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log all requests with timing information.

    Following fastapi-expert patterns for observability.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response with timing."""
        start_time = time.time()

        # Process request
        response = await call_next(request)

        # Calculate duration
        duration_ms = round((time.time() - start_time) * 1000, 2)

        # Log request
        logger.info(
            f"{request.method} {request.url.path} - {response.status_code}",
            extra={
                "endpoint": f"{request.method} {request.url.path}",
                "status_code": response.status_code,
                "duration_ms": duration_ms,
            },
        )

        # Add timing header
        response.headers["X-Response-Time"] = f"{duration_ms}ms"

        return response


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add security headers to all responses.

    Following fastapi-expert security best practices:
    - HSTS for HTTPS enforcement
    - X-Content-Type-Options to prevent MIME sniffing
    - X-Frame-Options to prevent clickjacking
    - X-XSS-Protection for XSS prevention
    - CSP for XSS prevention (FR-011)
    """

    def __init__(self, app: ASGIApp, environment: str = "development"):
        super().__init__(app)
        self.environment = environment

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Add security headers to response."""
        response = await call_next(request)

        # HSTS - only in production with HTTPS
        if self.environment == "production":
            response.headers["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        # Prevent MIME sniffing
        response.headers["X-Content-Type-Options"] = "nosniff"

        # Prevent clickjacking
        response.headers["X-Frame-Options"] = "DENY"

        # XSS Protection (legacy but still useful)
        response.headers["X-XSS-Protection"] = "1; mode=block"

        # Content Security Policy (FR-011)
        # Relaxed CSP for API docs (Swagger UI needs to load from CDN)
        if request.url.path in ["/docs", "/redoc", "/openapi.json"]:
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "style-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdn.jsdelivr.net; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )
        else:
            # Strict CSP for all other endpoints to prevent XSS attacks
            response.headers["Content-Security-Policy"] = (
                "default-src 'self'; "
                "script-src 'self'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self'; "
                "connect-src 'self'; "
                "frame-ancestors 'none'; "
                "base-uri 'self'; "
                "form-action 'self'"
            )

        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )

        return response


class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to handle exceptions and return consistent error responses.

    Following fastapi-expert error handling patterns.
    """

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Handle exceptions and return JSON error responses."""
        try:
            return await call_next(request)
        except Exception as exc:
            logger.error(
                f"Unhandled exception: {str(exc)}",
                exc_info=True,
                extra={"endpoint": f"{request.method} {request.url.path}"},
            )

            # Return consistent error format
            return JSONResponse(
                status_code=500,
                content={
                    "error": "Internal server error",
                    "code": "INTERNAL_SERVER_ERROR",
                    "status": 500,
                    "request_id": get_correlation_id(),
                    "message": "An unexpected error occurred. Please try again later.",
                },
                headers={"X-Request-ID": get_correlation_id()},
            )
