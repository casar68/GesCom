import pytest
from httpx import AsyncClient


async def get_token_and_article(client: AsyncClient) -> tuple[str, int]:
    await client.post(
        "/auth/register",
        json={"email": "stk@gescom.fr", "nom": "Stk", "prenom": "User", "password": "Pass123!", "role": "admin"},
    )
    resp = await client.post("/auth/login", json={"email": "stk@gescom.fr", "password": "Pass123!"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    art_resp = await client.post(
        "/api/v1/articles",
        json={
            "reference": f"STK-ART-{id(client)}",
            "designation": "Article stock test",
            "prix_vente_ht": "50.00",
            "stock_actuel": 100,
            "stock_minimum": 20,
        },
        headers=headers,
    )
    return token, art_resp.json()["id"]


@pytest.mark.asyncio
async def test_create_mouvement_entree(client: AsyncClient):
    token, article_id = await get_token_and_article(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/stock/mouvements",
        json={
            "type_mouvement": "entree",
            "depot_destination": "Principal",
            "reference_document": "BR-001",
            "lignes": [{"article_id": article_id, "quantite": 25, "prix_unitaire": "45.00"}],
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["numero"].startswith("MVT-")
    assert data["type_mouvement"] == "entree"
    assert len(data["lignes"]) == 1


@pytest.mark.asyncio
async def test_create_mouvement_sortie(client: AsyncClient):
    token, article_id = await get_token_and_article(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/stock/mouvements",
        json={
            "type_mouvement": "sortie",
            "depot_source": "Principal",
            "reference_document": "BL-001",
            "lignes": [{"article_id": article_id, "quantite": 10}],
        },
        headers=headers,
    )
    assert response.status_code == 201
    assert response.json()["type_mouvement"] == "sortie"


@pytest.mark.asyncio
async def test_list_mouvements(client: AsyncClient):
    token, article_id = await get_token_and_article(client)
    headers = {"Authorization": f"Bearer {token}"}

    await client.post(
        "/api/v1/stock/mouvements",
        json={
            "type_mouvement": "entree",
            "lignes": [{"article_id": article_id, "quantite": 5}],
        },
        headers=headers,
    )

    response = await client.get("/api/v1/stock/mouvements", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1


@pytest.mark.asyncio
async def test_create_inventaire(client: AsyncClient):
    token, article_id = await get_token_and_article(client)
    headers = {"Authorization": f"Bearer {token}"}

    response = await client.post(
        "/api/v1/stock/inventaires",
        json={
            "depot": "Principal",
            "lignes": [{"article_id": article_id, "stock_theorique": 100, "stock_physique": 97}],
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["numero"].startswith("INV-")
    assert data["lignes"][0]["ecart"] == -3


@pytest.mark.asyncio
async def test_alertes_stock(client: AsyncClient):
    token = (
        await client.post("/auth/login", json={"email": "stk@gescom.fr", "password": "Pass123!"})
    ).json().get("access_token")

    if not token:
        await client.post(
            "/auth/register",
            json={"email": "stk2@gescom.fr", "nom": "Stk", "prenom": "User", "password": "Pass123!", "role": "admin"},
        )
        token = (
            await client.post("/auth/login", json={"email": "stk2@gescom.fr", "password": "Pass123!"})
        ).json()["access_token"]

    headers = {"Authorization": f"Bearer {token}"}

    # Créer un article sous le seuil
    await client.post(
        "/api/v1/articles",
        json={
            "reference": "STK-ALERT-001",
            "designation": "Article en rupture",
            "prix_vente_ht": "10.00",
            "stock_actuel": 5,
            "stock_minimum": 20,
        },
        headers=headers,
    )

    response = await client.get("/api/v1/stock/alertes", headers=headers)
    assert response.status_code == 200
    assert any(a["reference"] == "STK-ALERT-001" for a in response.json())
