import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_check(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert data["app"] == "GesCom"


@pytest.mark.asyncio
async def test_register_user(client: AsyncClient):
    response = await client.post(
        "/auth/register",
        json={
            "email": "admin@gescom.fr",
            "nom": "Admin",
            "prenom": "GesCom",
            "password": "SecurePass123!",
            "role": "admin",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "admin@gescom.fr"
    assert data["role"] == "admin"


@pytest.mark.asyncio
async def test_login_user(client: AsyncClient):
    # Créer l'utilisateur
    await client.post(
        "/auth/register",
        json={
            "email": "test@gescom.fr",
            "nom": "Test",
            "prenom": "User",
            "password": "TestPass123!",
        },
    )
    # Login
    response = await client.post(
        "/auth/login",
        json={"email": "test@gescom.fr", "password": "TestPass123!"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_invalid_credentials(client: AsyncClient):
    response = await client.post(
        "/auth/login",
        json={"email": "invalid@gescom.fr", "password": "wrong"},
    )
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_get_me(client: AsyncClient):
    # Créer et login
    await client.post(
        "/auth/register",
        json={
            "email": "me@gescom.fr",
            "nom": "Moi",
            "prenom": "User",
            "password": "MyPass123!",
        },
    )
    login_resp = await client.post(
        "/auth/login",
        json={"email": "me@gescom.fr", "password": "MyPass123!"},
    )
    token = login_resp.json()["access_token"]

    response = await client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    assert response.json()["email"] == "me@gescom.fr"
