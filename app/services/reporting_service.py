from datetime import datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select, func, extract, case
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.facture import Facture, LigneFacture, StatutFacture
from app.models.commande import Commande, LigneCommande, StatutCommande
from app.models.article import Article
from app.models.client import Client


async def get_dashboard(db: AsyncSession) -> dict:
    now = datetime.now(timezone.utc)
    debut_mois = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)

    # CA du mois
    ca_mois = await db.execute(
        select(func.coalesce(func.sum(Facture.total_ttc), 0)).where(
            Facture.date_facture >= debut_mois,
            Facture.statut != StatutFacture.ANNULEE,
        )
    )

    # Nombre de commandes du mois
    nb_commandes = await db.execute(
        select(func.count(Commande.id)).where(Commande.date_commande >= debut_mois)
    )

    # Factures impayées
    impayees = await db.execute(
        select(
            func.count(Facture.id),
            func.coalesce(func.sum(Facture.total_ttc - Facture.montant_regle), 0),
        ).where(Facture.statut.in_([StatutFacture.EMISE, StatutFacture.ENVOYEE, StatutFacture.EN_RETARD, StatutFacture.PAYEE_PARTIELLEMENT]))
    )
    impayees_row = impayees.one()

    # Nombre de clients actifs
    nb_clients = await db.execute(select(func.count(Client.id)).where(Client.actif == True))  # noqa: E712

    # Articles sous seuil
    articles_alerte = await db.execute(
        select(func.count(Article.id)).where(
            Article.actif == True,  # noqa: E712
            Article.stock_actuel <= Article.stock_minimum,
        )
    )

    return {
        "ca_mois": float(ca_mois.scalar() or 0),
        "nb_commandes_mois": nb_commandes.scalar() or 0,
        "factures_impayees_count": impayees_row[0] or 0,
        "factures_impayees_montant": float(impayees_row[1] or 0),
        "nb_clients_actifs": nb_clients.scalar() or 0,
        "articles_en_alerte": articles_alerte.scalar() or 0,
    }


async def get_ca_par_mois(db: AsyncSession, annee: int) -> list[dict]:
    result = await db.execute(
        select(
            extract("month", Facture.date_facture).label("mois"),
            func.coalesce(func.sum(Facture.total_ht), 0).label("total_ht"),
            func.coalesce(func.sum(Facture.total_ttc), 0).label("total_ttc"),
            func.count(Facture.id).label("nb_factures"),
        )
        .where(
            extract("year", Facture.date_facture) == annee,
            Facture.statut != StatutFacture.ANNULEE,
        )
        .group_by(extract("month", Facture.date_facture))
        .order_by(extract("month", Facture.date_facture))
    )

    mois_data = {int(row.mois): {"total_ht": float(row.total_ht), "total_ttc": float(row.total_ttc), "nb_factures": row.nb_factures} for row in result}

    return [
        {
            "mois": m,
            "total_ht": mois_data.get(m, {}).get("total_ht", 0),
            "total_ttc": mois_data.get(m, {}).get("total_ttc", 0),
            "nb_factures": mois_data.get(m, {}).get("nb_factures", 0),
        }
        for m in range(1, 13)
    ]


async def get_top_clients(db: AsyncSession, limit: int = 10, annee: int | None = None) -> list[dict]:
    query = (
        select(
            Client.id,
            Client.code_client,
            Client.raison_sociale,
            Client.ville,
            func.coalesce(func.sum(Facture.total_ttc), 0).label("ca_total"),
            func.count(Facture.id).label("nb_factures"),
        )
        .join(Facture, Facture.client_id == Client.id)
        .where(Facture.statut != StatutFacture.ANNULEE)
    )
    if annee:
        query = query.where(extract("year", Facture.date_facture) == annee)

    query = query.group_by(Client.id, Client.code_client, Client.raison_sociale, Client.ville).order_by(func.sum(Facture.total_ttc).desc()).limit(limit)

    result = await db.execute(query)
    return [
        {
            "client_id": row.id,
            "code_client": row.code_client,
            "raison_sociale": row.raison_sociale,
            "ville": row.ville,
            "ca_total": float(row.ca_total),
            "nb_factures": row.nb_factures,
        }
        for row in result
    ]


async def get_top_articles(db: AsyncSession, limit: int = 10, annee: int | None = None) -> list[dict]:
    query = (
        select(
            Article.id,
            Article.reference,
            Article.designation,
            Article.famille,
            func.coalesce(func.sum(LigneFacture.quantite), 0).label("quantite_vendue"),
            func.coalesce(func.sum(LigneFacture.montant_ht), 0).label("ca_ht"),
        )
        .join(LigneFacture, LigneFacture.article_id == Article.id)
        .join(Facture, Facture.id == LigneFacture.facture_id)
        .where(Facture.statut != StatutFacture.ANNULEE)
    )
    if annee:
        query = query.where(extract("year", Facture.date_facture) == annee)

    query = query.group_by(Article.id, Article.reference, Article.designation, Article.famille).order_by(func.sum(LigneFacture.montant_ht).desc()).limit(limit)

    result = await db.execute(query)
    return [
        {
            "article_id": row.id,
            "reference": row.reference,
            "designation": row.designation,
            "famille": row.famille,
            "quantite_vendue": row.quantite_vendue,
            "ca_ht": float(row.ca_ht),
        }
        for row in result
    ]


async def get_ca_par_famille(db: AsyncSession, annee: int | None = None) -> list[dict]:
    query = (
        select(
            func.coalesce(Article.famille, "Non classé").label("famille"),
            func.coalesce(func.sum(LigneFacture.montant_ht), 0).label("ca_ht"),
            func.coalesce(func.sum(LigneFacture.quantite), 0).label("quantite"),
        )
        .join(LigneFacture, LigneFacture.article_id == Article.id)
        .join(Facture, Facture.id == LigneFacture.facture_id)
        .where(Facture.statut != StatutFacture.ANNULEE)
    )
    if annee:
        query = query.where(extract("year", Facture.date_facture) == annee)

    query = query.group_by(Article.famille).order_by(func.sum(LigneFacture.montant_ht).desc())

    result = await db.execute(query)
    return [
        {"famille": row.famille, "ca_ht": float(row.ca_ht), "quantite": row.quantite}
        for row in result
    ]


async def get_ca_par_region(db: AsyncSession, annee: int | None = None) -> list[dict]:
    query = (
        select(
            func.coalesce(func.substr(Client.code_postal, 1, 2), "??").label("departement"),
            func.coalesce(func.sum(Facture.total_ttc), 0).label("ca_total"),
            func.count(func.distinct(Client.id)).label("nb_clients"),
        )
        .join(Client, Client.id == Facture.client_id)
        .where(Facture.statut != StatutFacture.ANNULEE)
    )
    if annee:
        query = query.where(extract("year", Facture.date_facture) == annee)

    query = query.group_by(func.substr(Client.code_postal, 1, 2)).order_by(func.sum(Facture.total_ttc).desc())

    result = await db.execute(query)
    return [
        {"departement": row.departement, "ca_total": float(row.ca_total), "nb_clients": row.nb_clients}
        for row in result
    ]
