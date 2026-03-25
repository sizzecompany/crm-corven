from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.dependencies import get_current_user
from app.main import create_app


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def override_db(app):
    async def _override_get_db():
        yield SimpleNamespace()

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_user_role_cannot_list_users(app, override_db):
    async def _override_current_user():
        return SimpleNamespace(
            id=uuid4(),
            tenant_id=uuid4(),
            role="user",
            custom_permissions=None,
            is_active=True,
        )

    app.dependency_overrides[get_current_user] = _override_current_user

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/api/v1/users/")

    app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient role"


@pytest.mark.asyncio
async def test_verify_otp_rejects_non_numeric_code(app, override_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.post(
            "/api/v1/auth/verify-otp",
            json={"email": "qa@example.com", "code": "abc123"},
        )

    assert response.status_code == 422
