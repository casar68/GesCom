from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.commande import Commande, StatutCommande
from app.models.livraison import BonLivraison, LigneBonLivraison, StatutLivraison
from app.schemas.livraison import BonLivraisonCreate


async def _next_numero(db: AsyncSession) -> str:
    result = await db.execute(select(func.count(BonLivraison.id)))
    count = (result.scalar() or 0) + 1
    return f"BL-{count:06d}"


async def get_bons_livraison(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    client_id: int | None = None,
    statut: StatutLivraison | None = None,
) -> tuple[list[BonLivraison], int]:
    query = select(BonLivraison)
    if client_id:
        query = query.where(BonLivraison.client_id == client_id)
    if statut:
        query = query.where(BonLivraison.statut == statut)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = (
        query.options(selectinload(BonLivraison.lignes))
        .order_by(BonLivraison.date_bl.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_bon_livraison(db: AsyncSession, bl_id: int) -> BonLivraison | None:
    query = select(BonLivraison).where(BonLivraison.id == bl_id).options(selectinload(BonLivraison.lignes))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_bon_livraison(db: AsyncSession, data: BonLivraisonCreate) -> BonLivraison:
    numero = await _next_numero(db)
    bl = BonLivraison(
        numero=numero,
        client_id=data.client_id,
        commande_id=data.commande_id,
        vrp_id=data.vrp_id,
        transport_id=data.transport_id,
        adresse_livraison=data.adresse_livraison,
        cp_livraison=data.cp_livraison,
        ville_livraison=data.ville_livraison,
        pays_livraison=data.pays_livraison,
        poids_total=data.poids_total,
        nb_colis=data.nb_colis,
        notes=data.notes,
    )

    for i, ligne_data in enumerate(data.lignes, 1):
        ligne = LigneBonLivraison(
            ligne_numero=i,
            article_id=ligne_data.article_id,
            designation=ligne_data.designation,
            quantite=ligne_data.quantite,
            taille=ligne_data.taille,
            couleur=ligne_data.couleur,
            emplacement=ligne_data.emplacement,
        )
        bl.lignes.append(ligne)

    db.add(bl)
    await db.flush()
    await db.refresh(bl, ["lignes"])
    return bl


async def create_bl_from_commande(db: AsyncSession, commande: Commande, transport_id: int | None = None) -> BonLivraison:
    numero = await _next_numero(db)
    bl = BonLivraison(
        numero=numero,
        client_id=commande.client_id,
        commande_id=commande.id,
        vrp_id=commande.vrp_id,
        transport_id=transport_id,
        adresse_livraison=commande.adresse_livraison,
        cp_livraison=commande.cp_livraison,
        ville_livraison=commande.ville_livraison,
        pays_livraison=commande.pays_livraison,
    )

    for i, lc in enumerate(commande.lignes, 1):
        quantite_restante = lc.quantite - lc.quantite_livree
        if quantite_restante <= 0:
            continue
        ligne = LigneBonLivraison(
            ligne_numero=i,
            article_id=lc.article_id,
            designation=lc.designation,
            quantite=quantite_restante,
            taille=lc.taille,
            couleur=lc.couleur,
        )
        bl.lignes.append(ligne)
        lc.quantite_livree = lc.quantite

    commande.statut = StatutCommande.EXPEDIEE

    db.add(bl)
    await db.flush()
    await db.refresh(bl, ["lignes"])
    return bl


async def changer_statut(db: AsyncSession, bl: BonLivraison, statut: StatutLivraison) -> BonLivraison:
    bl.statut = statut
    await db.flush()
    await db.refresh(bl)
    return bl
