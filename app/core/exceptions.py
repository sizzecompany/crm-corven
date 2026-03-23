"""
CRM Corven — Custom exceptions and FastAPI error handlers.
"""

from __future__ import annotations

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse


class AppException(Exception):
    """Base application exception."""

    def __init__(self, message: str, status_code: int = 400, detail: str | None = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail or message
        super().__init__(self.message)


class NotFoundError(AppException):
    def __init__(self, resource: str = "Resource", identifier: str | None = None):
        msg = f"{resource} not found" + (f": {identifier}" if identifier else "")
        super().__init__(message=msg, status_code=404)


class UnauthorizedError(AppException):
    def __init__(self, message: str = "Not authenticated"):
        super().__init__(message=message, status_code=401)


class ForbiddenError(AppException):
    def __init__(self, message: str = "Permission denied"):
        super().__init__(message=message, status_code=403)


class ConflictError(AppException):
    def __init__(self, message: str = "Resource already exists"):
        super().__init__(message=message, status_code=409)


class TenantIsolationError(AppException):
    def __init__(self):
        super().__init__(
            message="Tenant isolation violation",
            status_code=403,
        )


class OTPExpiredError(AppException):
    def __init__(self):
        super().__init__(message="OTP has expired", status_code=400)


class OTPInvalidError(AppException):
    def __init__(self):
        super().__init__(message="Invalid OTP code", status_code=400)


def register_exception_handlers(app: FastAPI) -> None:
    """Register global exception handlers."""

    @app.exception_handler(AppException)
    async def app_exception_handler(_request: Request, exc: AppException):
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "detail": exc.detail},
        )

    @app.exception_handler(Exception)
    async def generic_exception_handler(_request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": "Internal server error", "detail": str(exc)},
        )
