"""Consistent error responses and exception handling."""
from typing import Any, Dict, Optional
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse


class APIError(HTTPException):
    """
    Base API error with consistent response format.

    Following fastapi-expert error handling patterns.
    """

    def __init__(
        self,
        status_code: int,
        error: str,
        code: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.status_code = status_code
        self.error = error
        self.code = code
        self.message = message or error
        self.details = details or {}
        super().__init__(status_code=status_code, detail=message or error)


class ValidationError(APIError):
    """Validation error (400)."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            error="Validation error",
            code="VALIDATION_ERROR",
            message=message,
            details=details,
        )


class UnauthorizedError(APIError):
    """Unauthorized error (401)."""

    def __init__(self, message: str = "Authentication required"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error="Unauthorized",
            code="UNAUTHORIZED",
            message=message,
        )


class ForbiddenError(APIError):
    """Forbidden error (403)."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            error="Forbidden",
            code="FORBIDDEN",
            message=message,
        )


class NotFoundError(APIError):
    """Not found error (404)."""

    def __init__(self, resource: str):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            error="Not found",
            code="NOT_FOUND",
            message=f"{resource} not found",
        )


class ConflictError(APIError):
    """Conflict error (409)."""

    def __init__(self, message: str):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            error="Conflict",
            code="CONFLICT",
            message=message,
        )


class RateLimitError(APIError):
    """Rate limit exceeded error (429)."""

    def __init__(self, message: str = "Rate limit exceeded"):
        super().__init__(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            error="Rate limit exceeded",
            code="RATE_LIMIT_EXCEEDED",
            message=message,
        )


class ServerError(APIError):
    """Internal server error (500)."""

    def __init__(self, message: str = "Internal server error"):
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            error="Internal server error",
            code="INTERNAL_SERVER_ERROR",
            message=message,
        )


def create_error_response(
    status_code: int,
    error: str,
    code: str,
    message: str,
    request_id: str = "",
    details: Optional[Dict[str, Any]] = None,
) -> JSONResponse:
    """
    Create consistent error response.

    Following fastapi-expert error response patterns.
    """
    content = {
        "error": error,
        "code": code,
        "status": status_code,
        "message": message,
        "request_id": request_id,
    }

    if details:
        content["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=content,
        headers={"X-Request-ID": request_id} if request_id else {},
    )
