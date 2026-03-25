"""
CRM Corven — Auth module schemas.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class OTPRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr


class OTPVerify(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr
    code: str = Field(pattern=r"^\d{6}$")


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class RefreshRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    refresh_token: str = Field(min_length=20)


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
