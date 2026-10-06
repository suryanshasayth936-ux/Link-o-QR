"""Domain exceptions and HTTP error handlers."""

from typing import Any, Dict
from fastapi import Request, status
from fastapi.responses import JSONResponse


class LinkOQRException(Exception):
    """Base exception for all application-specific errors."""

    def __init__(self, message: str, details: Dict[str, Any] | None = None):
        super().__init__(message)
        self.message = message
        self.details = details or {}


class InvalidURLError(LinkOQRException):
    """Raised when URL validation fails."""

    pass


class QRGenerationError(LinkOQRException):
    """Raised when QR code rendering or processing fails."""

    pass


async def linkoqr_exception_handler(request: Request, exc: LinkOQRException) -> JSONResponse:
    """Handle custom application exceptions and format standard JSON responses."""
    status_code = status.HTTP_400_BAD_REQUEST
    if isinstance(exc, QRGenerationError):
        status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error_type": exc.__class__.__name__,
            "message": exc.message,
            "details": exc.details,
        },
    )
