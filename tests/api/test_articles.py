import pytest
from httpx import AsyncClient


async def get_token(client: AsyncClient) -> str:
    await client.post(
        "/auth/register",
        json={"email": "art@gescom.fr", "nom": "Art", "prenom": "User", "password": "Pass123!", "role": "admin"},
    )
    resp = await client.post("/auth/login", json={"email": "art@gescom.fr", "password": "Pass123!"})
    return resp.json()["access_token"]


@pytest.mark.asyncio
async def test_create_article(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/articles",
        json={
            "reference": "ART-001",
            "designation": "Casque moto intégral",
            "famille": "Casques",
            "gamme": "Moto",
            "prix_achat_ht": "45.00",
            "prix_vente_ht": "89.90",
            "stock_actuel": 50,
            "stock_minimum": 10,
            "tailles": [{"taille": "S", "stock": 10}, {"taille": "M", "stock": 20}, {"taille": "L", "stock": 20}],
            "couleurs": [{"couleur": "Noir", "code_hex": "#000000", "stock": 30}],
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["reference"] == "ART-001"
    assert data["designation"] == "Casque moto intégral"
    assert len(data["tailles"]) == 3
    assert len(data["couleurs"]) == 1


@pytest.mark.asyncio
async def test_list_articles(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    # Créer un article
    await client.post(
        "/api/v1/articles",
        json={"reference": "ART-LIST-001", "designation": "Test Article", "prix_vente_ht": "10.00"},
        headers=headers,
    )

    response = await client.get("/api/v1/articles", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] >= 1
    assert len(data["items"]) >= 1


@pytest.mark.asyncio
async def test_get_article(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/articles",
        json={"reference": "ART-GET-001", "designation": "Article à lire", "prix_vente_ht": "25.00"},
        headers=headers,
    )
    article_id = create_resp.json()["id"]

    response = await client.get(f"/api/v1/articles/{article_id}", headers=headers)
    assert response.status_code == 200
    assert response.json()["reference"] == "ART-GET-001"


@pytest.mark.asyncio
async def test_update_article(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/articles",
        json={"reference": "ART-UPD-001", "designation": "Avant modif", "prix_vente_ht": "10.00"},
        headers=headers,
    )
    article_id = create_resp.json()["id"]

    response = await client.put(
        f"/api/v1/articles/{article_id}",
        json={"designation": "Après modif", "prix_vente_ht": "15.00"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["designation"] == "Après modif"


@pytest.mark.asyncio
async def test_delete_article(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    create_resp = await client.post(
        "/api/v1/articles",
        json={"reference": "ART-DEL-001", "designation": "À supprimer", "prix_vente_ht": "5.00"},
        headers=headers,
    )
    article_id = create_resp.json()["id"]

    response = await client.delete(f"/api/v1/articles/{article_id}", headers=headers)
    assert response.status_code == 204

    response = await client.get(f"/api/v1/articles/{article_id}", headers=headers)
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_duplicate_reference_rejected(client: AsyncClient):
    token = await get_token(client)
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/articles",
        json={"reference": "ART-DUP-001", "designation": "Original", "prix_vente_ht": "10.00"},
        headers=headers,
    )
    response = await client.post(
        "/api/v1/articles",
        json={"reference": "ART-DUP-001", "designation": "Doublon", "prix_vente_ht": "10.00"},
        headers=headers,
    )
    assert response.status_code == 400
