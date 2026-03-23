"""
CRM Corven — Database seed script.

Creates initial SUPERADMIN user and a demo tenant.
Run: python -m app.seed
"""

import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.tenant import Tenant
from app.models.user import User


async def seed():
    async with AsyncSessionLocal() as db:
        # Check if superadmin already exists
        result = await db.execute(select(User).where(User.role == "superadmin"))
        if result.scalar_one_or_none():
            print("Seed data already exists. Skipping.")
            return

        # Create demo tenant
        tenant = Tenant(
            name="Corven Saúde",
            slug="corven-saude",
            plan="professional",
            settings={"theme": "dark", "language": "pt-BR"},
        )
        db.add(tenant)
        await db.flush()

        # Create superadmin (also assigned to tenant for data visibility)
        superadmin = User(
            email="admin@corven.com.br",
            name="Super Admin",
            role="superadmin",
            tenant_id=tenant.id,
        )
        db.add(superadmin)

        # Create demo admin user
        admin_user = User(
            email="gestor@corven.com.br",
            name="Gestor Demo",
            role="admin",
            tenant_id=tenant.id,
        )
        db.add(admin_user)

        # Create demo regular user
        regular_user = User(
            email="corretor@corven.com.br",
            name="Corretor Demo",
            role="user",
            tenant_id=tenant.id,
        )
        db.add(regular_user)

        await db.commit()
        print("✅ Seed data created successfully!")
        print(f"  Tenant: {tenant.name} (ID: {tenant.id})")
        print(f"  Superadmin: {superadmin.email}")
        print(f"  Admin: {admin_user.email}")
        print(f"  User: {regular_user.email}")


if __name__ == "__main__":
    asyncio.run(seed())
