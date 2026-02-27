from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.article import Article
from app.models.stock import (
    MouvementStock,
    LigneMouvementStock,
    Inventaire,
    LigneInventaire,
    TypeMouvement,
    StatutInventaire,
)
from app.schemas.stock import MouvementStockCreate, InventaireCreate

_mouvement_counter = 0
_inventaire_counter = 0


async def _next_numero_mouvement(db: AsyncSession) -> str:
    result = await db.execute(select(func.count(MouvementStock.id)))
    count = (result.scalar() or 0) + 1
    return f"MVT-{count:06d}"


async def _next_numero_inventaire(db: AsyncSession) -> str:
    result = await db.execute(select(func.count(Inventaire.id)))
    count = (result.scalar() or 0) + 1
    return f"INV-{count:06d}"


async def get_mouvements(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    type_mouvement: TypeMouvement | None = None,
) -> tuple[list[MouvementStock], int]:
    query = select(MouvementStock)
    if type_mouvement:
        query = query.where(MouvementStock.type_mouvement == type_mouvement)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = (
        query.options(selectinload(MouvementStock.lignes))
        .order_by(MouvementStock.date_mouvement.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_mouvement(db: AsyncSession, mouvement_id: int) -> MouvementStock | None:
    query = (
        select(MouvementStock)
        .where(MouvementStock.id == mouvement_id)
        .options(selectinload(MouvementStock.lignes))
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_mouvement(db: AsyncSession, data: MouvementStockCreate, user_id: int | None = None) -> MouvementStock:
    numero = await _next_numero_mouvement(db)
    mouvement = MouvementStock(
        numero=numero,
        type_mouvement=data.type_mouvement,
        depot_source=data.depot_source,
        depot_destination=data.depot_destination,
        reference_document=data.reference_document,
        notes=data.notes,
        user_id=user_id,
    )

    for ligne_data in data.lignes:
        ligne = LigneMouvementStock(**ligne_data.model_dump())
        mouvement.lignes.append(ligne)

        # Mettre à jour le stock de l'article
        article_result = await db.execute(select(Article).where(Article.id == ligne_data.article_id))
        article = article_result.scalar_one_or_none()
        if article:
            if data.type_mouvement in (TypeMouvement.ENTREE, TypeMouvement.RETOUR):
                article.stock_actuel += ligne_data.quantite
            elif data.type_mouvement == TypeMouvement.SORTIE:
                article.stock_actuel -= ligne_data.quantite

    db.add(mouvement)
    await db.flush()
    await db.refresh(mouvement, ["lignes"])
    return mouvement


async def create_inventaire(db: AsyncSession, data: InventaireCreate, user_id: int | None = None) -> Inventaire:
    numero = await _next_numero_inventaire(db)
    inventaire = Inventaire(
        numero=numero,
        depot=data.depot,
        notes=data.notes,
        user_id=user_id,
    )

    for ligne_data in data.lignes:
        ecart = ligne_data.stock_physique - ligne_data.stock_theorique
        ligne = LigneInventaire(**ligne_data.model_dump(), ecart=ecart)
        inventaire.lignes.append(ligne)

    db.add(inventaire)
    await db.flush()
    await db.refresh(inventaire, ["lignes"])
    return inventaire


async def valider_inventaire(db: AsyncSession, inventaire: Inventaire) -> Inventaire:
    for ligne in inventaire.lignes:
        article_result = await db.execute(select(Article).where(Article.id == ligne.article_id))
        article = article_result.scalar_one_or_none()
        if article:
            article.stock_actuel = ligne.stock_physique

    inventaire.statut = StatutInventaire.VALIDE
    await db.flush()
    await db.refresh(inventaire)
    return inventaire


async def get_articles_sous_stock(db: AsyncSession) -> list[Article]:
    query = select(Article).where(
        Article.actif == True,  # noqa: E712
        Article.stock_actuel <= Article.stock_minimum,
    ).order_by(Article.reference)
    result = await db.execute(query)
    return list(result.scalars().all())
