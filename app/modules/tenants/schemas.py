"""
CRM Corven — Tenants module: schemas, service, router.
"""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel


# ── Schemas ──────────────────────────────────────────────────────────────────

class TenantCreate(BaseModel):
    name: str
    slug: str
    plan: str = "free"


class TenantUpdate(BaseModel):
    name: str | None = None
    slug: str | None = None
    plan: str | None = None
    is_active: bool | None = None
    settings: dict | None = None
    logo_url: str | None = None


class TenantOut(BaseModel):
    id: str
    name: str
    slug: str
    plan: str
    is_active: bool
    settings: dict | None = None
    created_at: datetime

    class Config:
        from_attributes = True
