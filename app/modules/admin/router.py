from __future__ import annotations

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field, field_validator
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.dependencies import CurrentUser, require_role
from app.core.permissions import Role
from app.models.broker_config import BrokerConfig
from app.models.user import User


ALLOWED_SKILLS = {"PF", "PME", "PJ", "hot", "warm", "cold"}


class BrokerConfigIn(BaseModel):
    skills: list[str] = Field(default_factory=lambda: ["PF", "hot", "warm", "cold"])
    max_capacity: int = Field(default=50, ge=1, le=1000)
    sla_minutes: int = Field(default=15, ge=1, le=1440)
    working_hours: dict = Field(default_factory=lambda: {"start": "08:00", "end": "18:00"})
    is_active: bool = True

    @field_validator("skills")
    @classmethod
    def validate_skills(cls, value: list[str]) -> list[str]:
        if not value:
            raise ValueError("skills cannot be empty")
        invalid = [s for s in value if s not in ALLOWED_SKILLS]
        if invalid:
            raise ValueError(f"invalid skills: {invalid}")
        return value


class BrokerConfigOut(BaseModel):
    user_id: str
    user_name: str
    skills: list[str]
    max_capacity: int
    active_leads: int
    sla_minutes: int
    working_hours: dict
    is_active: bool
    updated_at: datetime


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/brokers", response_model=list[BrokerConfigOut])
async def list_broker_configs(
    current_user: CurrentUser,
    _user=require_role(Role.SUPERADMIN, Role.ADMIN),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(BrokerConfig, User)
        .join(User, BrokerConfig.user_id == User.id)
        .where(BrokerConfig.tenant_id == current_user.tenant_id)
    )
    return [
        BrokerConfigOut(
            user_id=str(cfg.user_id),
            user_name=user.name,
            skills=cfg.skills,
            max_capacity=cfg.max_capacity,
            active_leads=cfg.active_leads,
            sla_minutes=cfg.sla_minutes,
            working_hours=cfg.working_hours,
            is_active=cfg.is_active,
            updated_at=cfg.updated_at,
        )
        for cfg, user in result.all()
    ]


@router.post("/brokers/{broker_id}/config", response_model=BrokerConfigOut)
async def upsert_broker_config(
    broker_id: UUID,
    body: BrokerConfigIn,
    current_user: CurrentUser,
    _user=require_role(Role.SUPERADMIN, Role.ADMIN),
    db: AsyncSession = Depends(get_db),
):
    user_result = await db.execute(
        select(User).where(
            User.id == broker_id,
            User.tenant_id == current_user.tenant_id,
            User.role == "user",
        )
    )
    broker = user_result.scalar_one()

    cfg_result = await db.execute(
        select(BrokerConfig).where(
            BrokerConfig.tenant_id == current_user.tenant_id,
            BrokerConfig.user_id == broker_id,
        )
    )
    cfg = cfg_result.scalar_one_or_none()
    if not cfg:
        cfg = BrokerConfig(
            tenant_id=current_user.tenant_id,
            user_id=broker_id,
            skills=body.skills,
            max_capacity=body.max_capacity,
            sla_minutes=body.sla_minutes,
            working_hours=body.working_hours,
            is_active=body.is_active,
            updated_by=current_user.id,
        )
        db.add(cfg)
    else:
        cfg.skills = body.skills
        cfg.max_capacity = body.max_capacity
        cfg.sla_minutes = body.sla_minutes
        cfg.working_hours = body.working_hours
        cfg.is_active = body.is_active
        cfg.updated_by = current_user.id

    await db.flush()
    await db.refresh(cfg)
    return BrokerConfigOut(
        user_id=str(cfg.user_id),
        user_name=broker.name,
        skills=cfg.skills,
        max_capacity=cfg.max_capacity,
        active_leads=cfg.active_leads,
        sla_minutes=cfg.sla_minutes,
        working_hours=cfg.working_hours,
        is_active=cfg.is_active,
        updated_at=cfg.updated_at,
    )
