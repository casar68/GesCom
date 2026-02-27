import pytest
from httpx import AsyncClient


async def setup_auth_and_data(client: AsyncClient) -> tuple[dict, int, int]:
    await client.post(
        "/auth/register",
        json={"email": "fac@gescom.fr", "nom": "Fac", "prenom": "User", "password": "Pass123!", "role": "admin"},
    )
    resp = await client.post("/auth/login", json={"email": "fac@gescom.fr", "password": "Pass123!"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    cli_resp = await client.post(
        "/api/v1/clients",
        json={"code_client": f"FAC-CLI-{id(client)}", "raison_sociale": "Client Test Fac"},
        headers=headers,
    )
    client_id = cli_resp.json()["id"]

    art_resp = await client.post(
        "/api/v1/articles",
        json={"reference": f"FAC-ART-{id(client)}", "designation": "Article Fac", "prix_vente_ht": "100.00"},
        headers=headers,
    )
    article_id = art_resp.json()["id"]

    return headers, client_id, article_id


@pytest.mark.asyncio
async def test_create_facture(client: AsyncClient):
    headers, client_id, article_id = await setup_auth_and_data(client)

    response = await client.post(
        "/api/v1/factures",
        json={
            "client_id": client_id,
            "mode_reglement": "virement",
            "lignes": [
                {"article_id": article_id, "designation": "Prestation", "quantite": 1, "prix_unitaire_ht": "500.00"}
            ],
        },
        headers=headers,
    )
    assert response.status_code == 201
    data = response.json()
    assert data["numero"].startswith("FAC-")
    assert float(data["total_ht"]) == 500.00
    assert float(data["total_ttc"]) == 600.00


@pytest.mark.asyncio
async def test_enregistrer_paiement(client: AsyncClient):
    headers, client_id, article_id = await setup_auth_and_data(client)

    fac_resp = await client.post(
        "/api/v1/factures",
        json={
            "client_id": client_id,
            "lignes": [
                {"article_id": article_id, "designation": "Service", "quantite": 1, "prix_unitaire_ht": "200.00"}
            ],
        },
        headers=headers,
    )
    fac_id = fac_resp.json()["id"]

    # Paiement partiel
    response = await client.post(
        f"/api/v1/factures/{fac_id}/paiement",
        json={"montant": "100.00"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["statut"] == "payee_partiellement"

    # Paiement complet
    response = await client.post(
        f"/api/v1/factures/{fac_id}/paiement",
        json={"montant": "140.00"},
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["statut"] == "payee"


@pytest.mark.asyncio
async def test_list_factures(client: AsyncClient):
    headers, client_id, article_id = await setup_auth_and_data(client)

    await client.post(
        "/api/v1/factures",
        json={
            "client_id": client_id,
            "lignes": [
                {"article_id": article_id, "designation": "Item", "quantite": 1, "prix_unitaire_ht": "50.00"}
            ],
        },
        headers=headers,
    )

    response = await client.get("/api/v1/factures", headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] >= 1
