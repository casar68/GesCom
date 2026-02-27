from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.commande import Commande, LigneCommande, StatutCommande
from app.schemas.commande import CommandeCreate, CommandeUpdate


async def _next_numero(db: AsyncSession) -> str:
    result = await db.execute(select(func.count(Commande.id)))
    count = (result.scalar() or 0) + 1
    return f"CMD-{count:06d}"


def _calc_ligne(quantite: int, prix_unitaire: Decimal, remise_pct: Decimal) -> Decimal:
    montant = Decimal(str(quantite)) * prix_unitaire
    if remise_pct > 0:
        montant *= (1 - remise_pct / 100)
    return montant.quantize(Decimal("0.01"))


async def get_commandes(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    client_id: int | None = None,
    statut: StatutCommande | None = None,
) -> tuple[list[Commande], int]:
    query = select(Commande)
    if client_id:
        query = query.where(Commande.client_id == client_id)
    if statut:
        query = query.where(Commande.statut == statut)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = (
        query.options(selectinload(Commande.lignes))
        .order_by(Commande.date_commande.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_commande(db: AsyncSession, commande_id: int) -> Commande | None:
    query = select(Commande).where(Commande.id == commande_id).options(selectinload(Commande.lignes))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_commande(db: AsyncSession, data: CommandeCreate) -> Commande:
    numero = await _next_numero(db)
    commande = Commande(
        numero=numero,
        client_id=data.client_id,
        vrp_id=data.vrp_id,
        date_livraison_souhaitee=data.date_livraison_souhaitee,
        reference_client=data.reference_client,
        notes=data.notes,
        adresse_livraison=data.adresse_livraison,
        cp_livraison=data.cp_livraison,
        ville_livraison=data.ville_livraison,
        pays_livraison=data.pays_livraison,
        remise_globale_pct=data.remise_globale_pct,
    )

    total_ht = Decimal("0")
    total_tva = Decimal("0")
    for i, ligne_data in enumerate(data.lignes, 1):
        montant_ht = _calc_ligne(ligne_data.quantite, ligne_data.prix_unitaire_ht, ligne_data.remise_pct)
        ligne = LigneCommande(
            ligne_numero=i,
            article_id=ligne_data.article_id,
            designation=ligne_data.designation,
            quantite=ligne_data.quantite,
            prix_unitaire_ht=ligne_data.prix_unitaire_ht,
            remise_pct=ligne_data.remise_pct,
            tva_pct=ligne_data.tva_pct,
            montant_ht=montant_ht,
            taille=ligne_data.taille,
            couleur=ligne_data.couleur,
        )
        commande.lignes.append(ligne)
        total_ht += montant_ht
        total_tva += (montant_ht * ligne_data.tva_pct / 100).quantize(Decimal("0.01"))

    if data.remise_globale_pct > 0:
        total_ht *= (1 - data.remise_globale_pct / 100)
        total_tva *= (1 - data.remise_globale_pct / 100)

    commande.total_ht = total_ht.quantize(Decimal("0.01"))
    commande.total_tva = total_tva.quantize(Decimal("0.01"))
    commande.total_ttc = (total_ht + total_tva).quantize(Decimal("0.01"))

    db.add(commande)
    await db.flush()
    await db.refresh(commande, ["lignes"])
    return commande


async def update_commande(db: AsyncSession, commande: Commande, data: CommandeUpdate) -> Commande:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(commande, field, value)
    await db.flush()
    await db.refresh(commande)
    return commande


async def changer_statut(db: AsyncSession, commande: Commande, statut: StatutCommande) -> Commande:
    commande.statut = statut
    await db.flush()
    await db.refresh(commande)
    return commande
