"""
CRM Corven — Auth router.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser
from app.modules.auth import service
from app.modules.auth.schemas import (
    OTPRequest,
    OTPVerify,
    RefreshRequest,
    TokenResponse,
    UserProfile,
)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/request-otp")
async def request_otp(
    body: OTPRequest,
    db: AsyncSession = Depends(get_db),
):
    """Request an OTP code sent to the user's email."""
    code = await service.request_otp(db, body.email)
    # In production, don't return the code — send via email.
    return {"message": "OTP sent to email", "otp_code_dev_only": code}


@router.post("/verify-otp", response_model=TokenResponse)
async def verify_otp(
    body: OTPVerify,
    db: AsyncSession = Depends(get_db),
):
    """Verify OTP and receive JWT tokens."""
    return await service.verify_otp(db, body.email, body.code)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    body: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    """Refresh access token using a valid refresh token."""
    return await service.refresh_tokens(db, body.refresh_token)


@router.get("/me", response_model=UserProfile)
async def get_me(user: CurrentUser):
    """Get current authenticated user's profile."""
    return UserProfile(
        id=str(user.id),
        email=user.email,
        name=user.name,
        role=user.role,
        tenant_id=str(user.tenant_id) if user.tenant_id else None,
        phone=user.phone,
        avatar_url=user.avatar_url,
    )
