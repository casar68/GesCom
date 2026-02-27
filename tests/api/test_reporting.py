import pytest
from httpx import AsyncClient


async def get_token(client: AsyncClient) -> str:
    await client.post(
        "/auth/register",
        json={"email": "rpt@gescom.fr", "nom": "Rpt", "prenom": "User", "password": "Pass123!", "role": "admin"},
    )
    resp = await client.post("/auth/login", json={"email": "rpt@gescom.fr", "password": "Pass123!"})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_dashboard(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/reporting/dashboard", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert "ca_mois" in data
    assert "nb_commandes_mois" in data
    assert "factures_impayees_count" in data
    assert "nb_clients_actifs" in data
    assert "articles_en_alerte" in data


@pytest.mark.asyncio
async def test_ca_mensuel(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/reporting/ca-mensuel?annee=2026", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 12
    assert data[0]["mois"] == 1


@pytest.mark.asyncio
async def test_top_clients(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/reporting/top-clients", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_top_articles(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/reporting/top-articles", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_ca_par_famille(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/reporting/ca-par-famille", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_ca_par_region(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/reporting/ca-par-region", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)


@pytest.mark.asyncio
async def test_export_top_clients_excel(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/reporting/export/top-clients", headers=headers)
    assert response.status_code == 200
    assert "spreadsheetml" in response.headers["content-type"]


@pytest.mark.asyncio
async def test_export_top_articles_excel(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.get("/api/v1/reporting/export/top-articles", headers=headers)
    assert response.status_code == 200
    assert "spreadsheetml" in response.headers["content-type"]
