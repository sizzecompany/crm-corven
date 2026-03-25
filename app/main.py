"""
CRM Corven — FastAPI Application.

Main application factory with all routers, middleware, and startup events.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from pathlib import Path

import sentry_sdk
import structlog
from fastapi import FastAPI
from sentry_sdk.integrations.fastapi import FastApiIntegration
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import get_settings
from app.core.exceptions import register_exception_handlers
from app.core.rate_limit import limiter
from app.middleware.tenant import TenantMiddleware

# Module routers
from app.modules.agent.router import router as agent_router
from app.modules.auth.router import router as auth_router
from app.modules.admin.router import router as admin_router
from app.modules.automations.router import router as automations_router
from app.modules.calendar.router import router as calendar_router
from app.modules.campaigns.router import router as campaigns_router
from app.modules.dashboard.router import router as dashboard_router
from app.modules.documents.router import router as documents_router
from app.modules.leads.router import router as leads_router
from app.modules.settings.router import router as settings_router
from app.modules.actions.router import router as actions_router
from app.modules.simulator.router import router as simulator_router
from app.modules.tenants.router import router as tenants_router
from app.modules.users.router import router as users_router
from app.modules.whatsapp.router import router as whatsapp_router

settings = get_settings()

if settings.SENTRY_DSN:
    sentry_sdk.init(
        dsn=settings.SENTRY_DSN,
        integrations=[FastApiIntegration()],
    )

logger = structlog.get_logger()

# Frontend directory (relative to project root)
FRONTEND_DIR = Path(__file__).resolve().parent.parent / "frontend"


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    logger.info("CRM Corven starting up", env=settings.APP_ENV)
    yield
    logger.info("CRM Corven shutting down")


def create_app() -> FastAPI:
    app = FastAPI(
        title="CRM Corven",
        description="SaaS CRM platform for health insurance brokers — multi-tenant backend.",
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan,
    )

    # ── CORS ─────────────────────────────────────────────────────────────
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # ── Rate limiter ────────────────────────────────────────────────────
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)
    app.add_middleware(SlowAPIMiddleware)

    # ── Tenant Middleware ────────────────────────────────────────────────
    app.add_middleware(TenantMiddleware)

    # ── Exception Handlers ──────────────────────────────────────────────
    register_exception_handlers(app)

    # ── Health Check ────────────────────────────────────────────────────
    @app.get("/health", tags=["Health"])
    async def health_check():
        return {"status": "healthy", "service": "crm-corven"}

    # ── Register All Routers ────────────────────────────────────────────
    api_prefix = "/api/v1"

    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(tenants_router, prefix=api_prefix)
    app.include_router(users_router, prefix=api_prefix)
    app.include_router(leads_router, prefix=api_prefix)
    app.include_router(dashboard_router, prefix=api_prefix)
    app.include_router(campaigns_router, prefix=api_prefix)
    app.include_router(whatsapp_router, prefix=api_prefix)
    app.include_router(documents_router, prefix=api_prefix)
    app.include_router(calendar_router, prefix=api_prefix)
    app.include_router(agent_router, prefix=api_prefix)
    app.include_router(automations_router, prefix=api_prefix)
    app.include_router(settings_router, prefix=api_prefix)
    app.include_router(admin_router, prefix=api_prefix)
    app.include_router(actions_router, prefix=api_prefix)
    app.include_router(simulator_router, prefix=api_prefix)

    # ── Serve Frontend (must be LAST to not shadow API routes) ──────────
    if FRONTEND_DIR.exists():
        app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")

    return app


app = create_app()
