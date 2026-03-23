"""
CRM Corven — Auth module schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, EmailStr


class OTPRequest(BaseModel):
    email: EmailStr


class OTPVerify(BaseModel):
    email: EmailStr
    code: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    refresh_token: str


class UserProfile(BaseModel):
    id: str
    email: str
    name: str
    role: str
    tenant_id: str | None = None
    phone: str | None = None
    avatar_url: str | None = None

    class Config:
        from_attributes = True
