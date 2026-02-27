import pytest
from httpx import AsyncClient


async def setup_auth_and_data(client: AsyncClient) -> tuple[dict, int, int]:
    """Crée un user, un client et un article pour les tests commande."""
    await client.post(
        "/auth/register",
        json={"email": "cmd@gescom.fr", "nom": "Cmd", "prenom": "User", "password": "Pass123!", "role": "admin"},
    )
    resp = await client.post("/auth/login", json={"email": "cmd@gescom.fr", "password": "Pass123!"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cli_resp = await client.post(
        "/api/v1/clients",
        json={"code_client": f"CMD-CLI-{id(client)}", "raison_sociale": "Client Test Cmd"},
        headers=headers,
    )
    client_id = cli_resp.json()["id"]

    art_resp = await client.post(
        "/api/v1/articles",
        json={"reference": f"CMD-ART-{id(client)}", "designation": "Article Cmd", "prix_vente_ht": "89.90"},
        headers=headers,
    )
    article_id = art_resp.json()["id"]

    return headers, client_id, article_id


@pytest.mark.asyncio
async def test_create_commande(client: AsyncClient):
    headers, client_id, article_id = await setup_auth_and_data(client)

    response = await client.post(
        "/api/v1/commandes",
        json={
            "client_id": client_id,
            "lignes": [
                {"article_id": article_id, "designation": "Casque intégral", "quantite": 2, "prix_unitaire_ht": "89.90"}
            ],
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["numero"].startswith("CMD-")
    assert data["statut"] == "brouillon"
    assert len(data["lignes"]) == 1
    assert float(data["total_ht"]) == 179.80


@pytest.mark.asyncio
async def test_valider_commande(client: AsyncClient):
    headers, client_id, article_id = await setup_auth_and_data(client)

    cmd_resp = await client.post(
        "/api/v1/commandes",
        json={
            "client_id": client_id,
            "lignes": [
                {"article_id": article_id, "designation": "Test", "quantite": 1, "prix_unitaire_ht": "50.00"}
            ],
        },
        headers=headers,
    )
    cmd_id = cmd_resp.json()["id"]

    response = await client.post(f"/api/v1/commandes/{cmd_id}/valider", headers=headers)
    assert response.status_code == 200
    assert response.json()["statut"] == "validee"


@pytest.mark.asyncio
async def test_facturer_commande(client: AsyncClient):
    headers, client_id, article_id = await setup_auth_and_data(client)

    cmd_resp = await client.post(
        "/api/v1/commandes",
        json={
            "client_id": client_id,
            "lignes": [
                {"article_id": article_id, "designation": "Test fact", "quantite": 3, "prix_unitaire_ht": "100.00"}
            ],
        },
        headers=headers,
    )
    cmd_id = cmd_resp.json()["id"]

    response = await client.post(f"/api/v1/commandes/{cmd_id}/facturer", headers=headers)
    assert response.status_code == 200
    assert response.json()["facture_numero"].startswith("FAC-")


@pytest.mark.asyncio
async def test_livrer_commande(client: AsyncClient):
    headers, client_id, article_id = await setup_auth_and_data(client)

    cmd_resp = await client.post(
        "/api/v1/commandes",
        json={
            "client_id": client_id,
            "adresse_livraison": "12 rue Test",
            "ville_livraison": "Paris",
            "lignes": [
                {"article_id": article_id, "designation": "Test livr", "quantite": 5, "prix_unitaire_ht": "20.00"}
            ],
        },
        headers=headers,
    )
    cmd_id = cmd_resp.json()["id"]

    response = await client.post(f"/api/v1/commandes/{cmd_id}/livrer", headers=headers)
    assert response.status_code == 200
    assert response.json()["bl_numero"].startswith("BL-")
