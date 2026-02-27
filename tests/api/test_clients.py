import pytest
from httpx import AsyncClient


async def get_token(client: AsyncClient) -> str:
    await client.post(
        "/auth/register",
        json={"email": "cli@gescom.fr", "nom": "Cli", "prenom": "User", "password": "Pass123!", "role": "admin"},
    )
    resp = await client.post("/auth/login", json={"email": "cli@gescom.fr", "password": "Pass123!"})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_client(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/clients",
        json={
            "code_client": "CLI-001",
            "raison_sociale": "Moto Center Paris",
            "type_client": "magasin",
            "telephone": "01 23 45 67 89",
            "email": "contact@motocenter.fr",
            "adresse": "12 rue de la Moto",
            "code_postal": "75001",
            "ville": "Paris",
            "contacts": [{"nom": "Dupont", "prenom": "Jean", "email": "jean@motocenter.fr", "principal": True}],
            "adresses": [
                {
                    "type_adresse": "livraison",
                    "adresse": "12 rue de la Moto",
                    "code_postal": "75001",
                    "ville": "Paris",
                    "par_defaut": True,
                }
            ],
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["code_client"] == "CLI-001"
    assert data["raison_sociale"] == "Moto Center Paris"
    assert len(data["contacts"]) == 1
    assert len(data["adresses"]) == 1


@pytest.mark.asyncio
async def test_list_clients(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/clients",
        json={"code_client": "CLI-LIST-001", "raison_sociale": "Test Client"},
        headers=headers,
    )

    response = await client.get("/api/v1/clients", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_search_clients(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/clients",
        json={"code_client": "CLI-SEARCH-001", "raison_sociale": "Boutique Lyon Moto"},
        headers=headers,
    )

    response = await client.get("/api/v1/clients?search=Lyon", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_update_client(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/clients",
        json={"code_client": "CLI-UPD-001", "raison_sociale": "Ancien nom"},
        headers=headers,
    )
    client_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/clients/{client_id}",
        json={"raison_sociale": "Nouveau nom", "ville": "Marseille"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["raison_sociale"] == "Nouveau nom"
    assert response.json()["ville"] == "Marseille"


@pytest.mark.asyncio
async def test_delete_client(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/clients",
        json={"code_client": "CLI-DEL-001", "raison_sociale": "À supprimer"},
        headers=headers,
    )
    client_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/clients/{client_id}", headers=headers)
    assert response.status_code == 204
