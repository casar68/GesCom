"""
Script de migration des données HyperFile (.fic) vers PostgreSQL.

Ce script est un template à adapter selon les fichiers .fic disponibles.
HyperFile étant un format propriétaire, l'extraction nécessite soit :
- WinDev pour exporter en CSV/JSON
- Un outil tiers de lecture HyperFile
- Export manuel depuis l'application WinDev existante

Usage :
    1. Exporter les données depuis WinDev en CSV (UTF-8, séparateur ;)
    2. Placer les fichiers CSV dans le dossier data/
    3. Exécuter : python scripts/migrate_hyperfile.py
"""
import asyncio
import csv
import sys
from pathlib import Path
from decimal import Decimal

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.database import engine, async_session, Base
from app.models import *  # noqa

DATA_DIR = Path(__file__).parent.parent / "data"


async def import_csv(filename: str, model_class, field_mapping: dict, transforms: dict | None = None):
    """Importe un fichier CSV dans une table SQLAlchemy."""
    filepath = DATA_DIR / filename
    if not filepath.exists():
        print(f"  [SKIP] {filename} non trouvé")
        return 0

    count = 0
    async with async_session() as db:
        with open(filepath, encoding="utf-8-sig") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                data = {}
                for csv_col, db_col in field_mapping.items():
                    value = row.get(csv_col, "").strip()
                    if transforms and db_col in transforms:
                        value = transforms[db_col](value)
                    if value != "":
                        data[db_col] = value
                obj = model_class(**data)
                db.add(obj)
                count += 1
        await db.commit()

    print(f"  [OK] {filename} : {count} enregistrements importés")
    return count


def to_decimal(v):
    try:
        return Decimal(v.replace(",", ".")) if v else Decimal("0")
    except Exception:
        return Decimal("0")


def to_int(v):
    try:
        return int(float(v.replace(",", "."))) if v else 0
    except Exception:
        return 0


def to_bool(v):
    return v.lower() in ("1", "true", "oui", "o", "yes")


async def migrate():
    print("=== Migration HyperFile -> PostgreSQL ===\n")
    print("Prérequis : exporter les tables HyperFile en CSV (UTF-8, séparateur ;)")
    print(f"Placer les fichiers dans : {DATA_DIR}\n")

    DATA_DIR.mkdir(exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    total = 0

    # Fournisseurs
    total += await import_csv("fournisseurs.csv", Fournisseur, {
        "CODE": "code", "RAISON_SOCIALE": "raison_sociale",
        "CONTACT": "contact", "TELEPHONE": "telephone", "EMAIL": "email",
        "ADRESSE": "adresse", "CODE_POSTAL": "code_postal", "VILLE": "ville",
    })

    # Articles
    total += await import_csv("articles.csv", Article, {
        "REFERENCE": "reference", "DESIGNATION": "designation",
        "FAMILLE": "famille", "SOUS_FAMILLE": "sous_famille",
        "GAMME": "gamme", "MARQUE": "marque",
        "PRIX_ACHAT_HT": "prix_achat_ht", "PRIX_VENTE_HT": "prix_vente_ht",
        "TVA": "tva", "STOCK": "stock_actuel", "STOCK_MIN": "stock_minimum",
        "CODE_BARRE": "code_barre", "POIDS": "poids", "UNITE": "unite",
    }, transforms={
        "prix_achat_ht": to_decimal, "prix_vente_ht": to_decimal,
        "tva": to_decimal, "stock_actuel": to_int, "stock_minimum": to_int,
        "poids": to_decimal,
    })

    # Clients
    total += await import_csv("clients.csv", Client, {
        "CODE_CLIENT": "code_client", "RAISON_SOCIALE": "raison_sociale",
        "TYPE": "type_client", "SIRET": "siret", "TVA_INTRA": "tva_intra",
        "TELEPHONE": "telephone", "FAX": "fax", "EMAIL": "email",
        "ADRESSE": "adresse", "CODE_POSTAL": "code_postal", "VILLE": "ville",
        "PAYS": "pays", "MODE_REGLEMENT": "mode_reglement",
        "DELAI_REGLEMENT": "delai_reglement",
    }, transforms={
        "delai_reglement": to_int,
    })

    # VRP
    total += await import_csv("vrp.csv", VRP, {
        "CODE_VRP": "code_vrp", "NOM": "nom", "PRENOM": "prenom",
        "TELEPHONE": "telephone", "MOBILE": "mobile", "EMAIL": "email",
        "SECTEUR": "secteur", "DEPARTEMENTS": "departements",
        "TAUX_COMMISSION": "taux_commission", "OBJECTIF_CA": "objectif_ca",
    }, transforms={
        "taux_commission": to_decimal, "objectif_ca": to_decimal,
    })

    print(f"\n=== Migration terminée : {total} enregistrements au total ===")
    print("\nPour les commandes, factures et BL historiques,")
    print("utilisez le même pattern avec les fichiers CSV correspondants.")


if __name__ == "__main__":
    asyncio.run(migrate())
