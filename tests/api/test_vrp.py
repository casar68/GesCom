import pytest
from httpx import AsyncClient


async def get_token(client: AsyncClient) -> str:
    await client.post(
        "/auth/register",
        json={"email": "vrp@gescom.fr", "nom": "Vrp", "prenom": "User", "password": "Pass123!", "role": "admin"},
    )
    resp = await client.post("/auth/login", json={"email": "vrp@gescom.fr", "password": "Pass123!"})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_vrp(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/vrp",
        json={
            "code_vrp": "VRP-001",
            "nom": "Martin",
            "prenom": "Pierre",
            "email": "pierre.martin@nkf.fr",
            "secteur": "Île-de-France",
            "taux_commission": "5.00",
            "objectif_ca": "100000.00",
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code_vrp"] == "VRP-001"
    assert data["nom"] == "Martin"


@pytest.mark.asyncio
async def test_create_concession(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/vrp/concessions",
        json={
            "code": "CONC-001",
            "nom": "Concession Paris Nord",
            "adresse": "45 av de la Moto",
            "code_postal": "93000",
            "ville": "Bobigny",
        },
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["nom"] == "Concession Paris Nord"


@pytest.mark.asyncio
async def test_create_suivi_client(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Créer un client d'abord
    cli_resp = await client.post(
        "/api/v1/clients",
        json={"code_client": "VRP-CLI-001", "raison_sociale": "Client Suivi Test"},
        headers=headers,
    )
    client_id = cli_resp.json()["id"]

    response = await client.post(
        "/api/v1/vrp/suivis",
        json={
            "client_id": client_id,
            "type_action": "appel",
            "description": "Relance téléphonique - intéressé par les nouveaux casques",
        },
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["type_action"] == "appel"

    # Vérifier le suivi
    response = await client.get(f"/api/v1/vrp/suivis/{client_id}", headers=headers)
    assert response.status_code == 200
    assert len(response.json()) >= 1
