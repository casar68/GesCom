"""Script de seed pour peupler la base avec des données de démonstration."""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import settings
from app.database import engine, async_session, Base
from app.models import *  # noqa
from app.auth.service import hash_password


ARTICLES_DEMO = [
    {"reference": "CASQ-INT-001", "designation": "Casque intégral Racing", "famille": "Casques", "gamme": "Moto", "marque": "NKF Racing", "prix_achat_ht": 85, "prix_vente_ht": 189.90, "stock_actuel": 45, "stock_minimum": 10, "tva": 20},
    {"reference": "CASQ-JET-001", "designation": "Casque jet urbain", "famille": "Casques", "gamme": "Scooter", "marque": "NKF City", "prix_achat_ht": 45, "prix_vente_ht": 99.90, "stock_actuel": 60, "stock_minimum": 15, "tva": 20},
    {"reference": "CASQ-MOD-001", "designation": "Casque modulable touring", "famille": "Casques", "gamme": "Touring", "marque": "NKF Travel", "prix_achat_ht": 120, "prix_vente_ht": 249.90, "stock_actuel": 25, "stock_minimum": 8, "tva": 20},
    {"reference": "GANT-CUI-001", "designation": "Gants cuir racing", "famille": "Gants", "gamme": "Moto", "marque": "NKF Racing", "prix_achat_ht": 35, "prix_vente_ht": 79.90, "stock_actuel": 80, "stock_minimum": 20, "tva": 20},
    {"reference": "GANT-TEX-001", "designation": "Gants textile été", "famille": "Gants", "gamme": "Été", "marque": "NKF City", "prix_achat_ht": 18, "prix_vente_ht": 39.90, "stock_actuel": 120, "stock_minimum": 30, "tva": 20},
    {"reference": "BLOU-CUI-001", "designation": "Blouson cuir sport", "famille": "Blousons", "gamme": "Moto", "marque": "NKF Racing", "prix_achat_ht": 150, "prix_vente_ht": 329.90, "stock_actuel": 20, "stock_minimum": 5, "tva": 20},
    {"reference": "BLOU-TEX-001", "designation": "Blouson textile 4 saisons", "famille": "Blousons", "gamme": "Touring", "marque": "NKF Travel", "prix_achat_ht": 95, "prix_vente_ht": 199.90, "stock_actuel": 35, "stock_minimum": 10, "tva": 20},
    {"reference": "BOTT-CUI-001", "designation": "Bottes racing", "famille": "Bottes", "gamme": "Moto", "marque": "NKF Racing", "prix_achat_ht": 80, "prix_vente_ht": 169.90, "stock_actuel": 30, "stock_minimum": 8, "tva": 20},
    {"reference": "PANT-CUI-001", "designation": "Pantalon cuir piste", "famille": "Pantalons", "gamme": "Moto", "marque": "NKF Racing", "prix_achat_ht": 110, "prix_vente_ht": 239.90, "stock_actuel": 15, "stock_minimum": 5, "tva": 20},
    {"reference": "ANTI-VOL-001", "designation": "Antivol U haute sécurité", "famille": "Accessoires", "gamme": "Sécurité", "marque": "NKF Lock", "prix_achat_ht": 25, "prix_vente_ht": 59.90, "stock_actuel": 100, "stock_minimum": 25, "tva": 20},
    {"reference": "VISI-GIL-001", "designation": "Gilet haute visibilité", "famille": "Accessoires", "gamme": "Sécurité", "marque": "NKF City", "prix_achat_ht": 5, "prix_vente_ht": 14.90, "stock_actuel": 200, "stock_minimum": 50, "tva": 20},
    {"reference": "ECRA-FUM-001", "designation": "Écran fumé universel", "famille": "Écrans", "gamme": "Accessoires", "marque": "NKF Vision", "prix_achat_ht": 12, "prix_vente_ht": 29.90, "stock_actuel": 3, "stock_minimum": 15, "tva": 20},
]

CLIENTS_DEMO = [
    {"code_client": "DAF-001", "raison_sociale": "Dafy Moto Paris", "type_client": "magasin", "telephone": "01 42 33 44 55", "email": "paris@dafymoto.fr", "adresse": "25 boulevard Voltaire", "code_postal": "75011", "ville": "Paris"},
    {"code_client": "DAF-002", "raison_sociale": "Dafy Moto Lyon", "type_client": "magasin", "telephone": "04 72 33 44 55", "email": "lyon@dafymoto.fr", "adresse": "12 rue de la République", "code_postal": "69002", "ville": "Lyon"},
    {"code_client": "MOT-001", "raison_sociale": "Moto Expert Marseille", "type_client": "magasin", "telephone": "04 91 22 33 44", "email": "contact@motoexpert13.fr", "adresse": "45 avenue du Prado", "code_postal": "13008", "ville": "Marseille"},
    {"code_client": "RAC-001", "raison_sociale": "Racing Center Toulouse", "type_client": "magasin", "telephone": "05 61 22 33 44", "email": "info@racingcenter31.fr", "adresse": "8 rue Alsace-Lorraine", "code_postal": "31000", "ville": "Toulouse"},
    {"code_client": "2ROU-001", "raison_sociale": "2 Roues Nantes", "type_client": "magasin", "telephone": "02 40 22 33 44", "email": "contact@2roues44.fr", "adresse": "15 quai de la Fosse", "code_postal": "44000", "ville": "Nantes"},
    {"code_client": "SPEED-001", "raison_sociale": "Speed Bike Bordeaux", "type_client": "magasin", "telephone": "05 56 22 33 44", "email": "contact@speedbike33.fr", "adresse": "22 cours de l'Intendance", "code_postal": "33000", "ville": "Bordeaux"},
    {"code_client": "BIKE-001", "raison_sociale": "Bike Land Lille", "type_client": "magasin", "telephone": "03 20 22 33 44", "email": "info@bikeland59.fr", "adresse": "5 rue Faidherbe", "code_postal": "59000", "ville": "Lille"},
    {"code_client": "MOTO-SHOP-001", "raison_sociale": "Moto Shop Strasbourg", "type_client": "magasin", "telephone": "03 88 22 33 44", "email": "contact@motoshop67.fr", "adresse": "18 rue du Fossé des Tanneurs", "code_postal": "67000", "ville": "Strasbourg"},
]

VRP_DEMO = [
    {"code_vrp": "VRP-IDF", "nom": "Martin", "prenom": "Pierre", "email": "p.martin@nkf.fr", "mobile": "06 12 34 56 78", "secteur": "Île-de-France", "departements": "75,77,78,91,92,93,94,95", "taux_commission": 5, "objectif_ca": 150000},
    {"code_vrp": "VRP-SE", "nom": "Dupont", "prenom": "Marie", "email": "m.dupont@nkf.fr", "mobile": "06 23 45 67 89", "secteur": "Sud-Est", "departements": "13,69,38,06,83,84", "taux_commission": 5.5, "objectif_ca": 120000},
    {"code_vrp": "VRP-SO", "nom": "Bernard", "prenom": "Luc", "email": "l.bernard@nkf.fr", "mobile": "06 34 56 78 90", "secteur": "Sud-Ouest", "departements": "31,33,34,64,65", "taux_commission": 5, "objectif_ca": 100000},
]


async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session() as db:
        # Admin user
        admin = User(
            email="admin@gescom.fr", nom="Admin", prenom="GesCom",
            hashed_password=hash_password("admin123"), role="admin", is_active=True,
        )
        db.add(admin)

        # Demo user
        demo = User(
            email="demo@gescom.fr", nom="Démo", prenom="Utilisateur",
            hashed_password=hash_password("demo123"), role="commercial", is_active=True,
        )
        db.add(demo)

        # Fournisseurs
        from app.models.fournisseur import Fournisseur
        fournisseur = Fournisseur(code="FOUR-NKF", raison_sociale="NKF Manufacturing", ville="Taïwan", pays="Taïwan")
        db.add(fournisseur)

        # Articles
        for art_data in ARTICLES_DEMO:
            article = Article(**art_data)
            db.add(article)

        # Clients
        for cli_data in CLIENTS_DEMO:
            client = Client(**cli_data)
            db.add(client)

        # VRPs
        for vrp_data in VRP_DEMO:
            vrp = VRP(**vrp_data)
            db.add(vrp)

        # Transport
        transport = Transport(code="CHRONO", nom="Chronopost", tarif_base=8.50, tarif_kg=0.35, delai_moyen_jours=2)
        db.add(transport)
        transport2 = Transport(code="TNT", nom="TNT Express", tarif_base=12.00, tarif_kg=0.28, delai_moyen_jours=1)
        db.add(transport2)

        await db.commit()
        print("Seed terminé : 2 users, 12 articles, 8 clients, 3 VRP, 1 fournisseur, 2 transporteurs")


if __name__ == "__main__":
    asyncio.run(seed())
