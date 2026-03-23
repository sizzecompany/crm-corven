from __future__ import annotations

from types import SimpleNamespace
from uuid import uuid4

import pytest
from httpx import ASGITransport, AsyncClient

from app.database import get_db
from app.dependencies import get_current_user
from app.main import create_app
from app.modules.auth import router as auth_router
from app.modules.auth import service as auth_service


@pytest.fixture
def app():
    return create_app()


@pytest.fixture
def dummy_db_session():
    return SimpleNamespace()


@pytest.fixture
def override_db(app, dummy_db_session):
    async def _override_get_db():
        yield dummy_db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield
    app.dependency_overrides.pop(get_db, None)


@pytest.mark.asyncio
async def test_request_otp_does_not_return_code_in_production(app, override_db, monkeypatch):
    async def _mock_request_otp(db, email: str):
        return "123456"

    monkeypatch.setattr(auth_service, "request_otp", _mock_request_otp)
    monkeypatch.setattr(auth_router.settings, "APP_ENV", "production")

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.post(
            "/api/v1/auth/request-otp",
            json={"email": "qa@example.com"},
        )

    assert response.status_code == 200
    payload = response.json()
    assert payload["message"] == "OTP sent to email"
    assert "otp_code_dev_only" not in payload


@pytest.mark.asyncio
async def test_user_role_cannot_access_admin_dashboard(app, override_db):
    async def _override_current_user():
        return SimpleNamespace(
            id=uuid4(),
            tenant_id=uuid4(),
            role="user",
            custom_permissions=None,
            is_active=True,
        )

    app.dependency_overrides[get_current_user] = _override_current_user

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://testserver",
    ) as client:
        response = await client.get("/api/v1/dashboard/admin")

    app.dependency_overrides.pop(get_current_user, None)

    assert response.status_code == 403
    assert response.json()["detail"] == "Insufficient role"
