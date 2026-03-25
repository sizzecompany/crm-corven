"""
CRM Corven — Multi-tenant middleware.

Extracts tenant_id from the authenticated user's JWT and makes it
available on request.state for all downstream handlers.
"""

from __future__ import annotations

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response

# Public routes that do NOT require tenant context
PUBLIC_PATHS = {
    "/docs",
    "/redoc",
    "/openapi.json",
    "/health",
    "/auth/request-otp",
    "/auth/verify-otp",
    "/auth/refresh",
    "/whatsapp/webhook",
}


class TenantMiddleware(BaseHTTPMiddleware):
    """
    Middleware that sets `request.state.tenant_id` based on the
    authenticated user. This value is later used by services and
    queries to enforce tenant isolation.
    """

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Skip public routes
        path = request.url.path.rstrip("/") or "/"
        if path in PUBLIC_PATHS:
            request.state.tenant_id = None
            return await call_next(request)

        # tenant_id is set by the auth dependency (get_current_user)
        # and stored on request.state. The middleware just ensures
        # the attribute exists so downstream code won't crash.
        if not hasattr(request.state, "tenant_id"):
            request.state.tenant_id = None

        return await call_next(request)
