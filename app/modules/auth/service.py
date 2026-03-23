"""
CRM Corven — Auth service.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import OTPExpiredError, OTPInvalidError, NotFoundError
from app.core.security import create_access_token, create_refresh_token, decode_token, generate_otp
from app.models.user import OTPCode, User
from app.modules.auth.schemas import TokenResponse

OTP_EXPIRY_MINUTES = 10


async def request_otp(db: AsyncSession, email: str) -> str:
    """
    Generate and store an OTP for the given email.
    Returns the OTP code (in production, send via email instead).
    """
    # Find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundError("User", email)

    # Generate OTP
    code = generate_otp()
    otp = OTPCode(
        user_id=user.id,
        code=code,
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES),
    )
    db.add(otp)
    await db.flush()

    # TODO: Send email with OTP code via SMTP
    # For development, we return the code in the response
    return code


async def verify_otp(db: AsyncSession, email: str, code: str) -> TokenResponse:
    """
    Verify OTP and return JWT tokens.
    """
    # Find user
    result = await db.execute(select(User).where(User.email == email))
    user = result.scalar_one_or_none()
    if user is None:
        raise NotFoundError("User", email)

    # Find latest valid OTP
    result = await db.execute(
        select(OTPCode)
        .where(
            OTPCode.user_id == user.id,
            OTPCode.code == code,
            OTPCode.used == False,
        )
        .order_by(OTPCode.created_at.desc())
        .limit(1)
    )
    otp = result.scalar_one_or_none()

    if otp is None:
        raise OTPInvalidError()

    if otp.expires_at < datetime.now(timezone.utc):
        raise OTPExpiredError()

    # Mark OTP as used
    otp.used = True
    await db.flush()

    # Generate tokens
    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "tenant_id": str(user.tenant_id) if user.tenant_id else None,
    }

    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )


async def refresh_tokens(db: AsyncSession, refresh_token: str) -> TokenResponse:
    """
    Validate refresh token and issue new access + refresh tokens.
    """
    payload = decode_token(refresh_token)
    if payload.get("type") != "refresh":
        raise OTPInvalidError()

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise NotFoundError("User")

    token_data = {
        "sub": str(user.id),
        "email": user.email,
        "role": user.role,
        "tenant_id": str(user.tenant_id) if user.tenant_id else None,
    }

    return TokenResponse(
        access_token=create_access_token(token_data),
        refresh_token=create_refresh_token(token_data),
    )
