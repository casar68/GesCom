from decimal import Decimal

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.commande import Commande, StatutCommande
from app.models.facture import Facture, LigneFacture, StatutFacture
from app.schemas.facture import FactureCreate, FactureUpdate


async def _next_numero(db: AsyncSession) -> str:
    result = await db.execute(select(func.count(Facture.id)))
    count = (result.scalar() or 0) + 1
    return f"FAC-{count:06d}"


def _calc_ligne(quantite: int, prix_unitaire: Decimal, remise_pct: Decimal) -> Decimal:
    montant = Decimal(str(quantite)) * prix_unitaire
    if remise_pct > 0:
        montant *= (1 - remise_pct / 100)
    return montant.quantize(Decimal("0.01"))


async def get_factures(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    client_id: int | None = None,
    statut: StatutFacture | None = None,
) -> tuple[list[Facture], int]:
    query = select(Facture)
    if client_id:
        query = query.where(Facture.client_id == client_id)
    if statut:
        query = query.where(Facture.statut == statut)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = (
        query.options(selectinload(Facture.lignes))
        .order_by(Facture.date_facture.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
    )
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_facture(db: AsyncSession, facture_id: int) -> Facture | None:
    query = select(Facture).where(Facture.id == facture_id).options(selectinload(Facture.lignes))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_facture(db: AsyncSession, data: FactureCreate) -> Facture:
    numero = await _next_numero(db)
    facture = Facture(
        numero=numero,
        client_id=data.client_id,
        commande_id=data.commande_id,
        vrp_id=data.vrp_id,
        date_echeance=data.date_echeance,
        mode_reglement=data.mode_reglement,
        reference_client=data.reference_client,
        notes=data.notes,
        adresse_facturation=data.adresse_facturation,
        cp_facturation=data.cp_facturation,
        ville_facturation=data.ville_facturation,
        remise_globale_pct=data.remise_globale_pct,
    )

    total_ht = Decimal("0")
    total_tva = Decimal("0")
    for i, ligne_data in enumerate(data.lignes, 1):
        montant_ht = _calc_ligne(ligne_data.quantite, ligne_data.prix_unitaire_ht, ligne_data.remise_pct)
        ligne = LigneFacture(
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
        facture.lignes.append(ligne)
        total_ht += montant_ht
        total_tva += (montant_ht * ligne_data.tva_pct / 100).quantize(Decimal("0.01"))

    if data.remise_globale_pct > 0:
        total_ht *= (1 - data.remise_globale_pct / 100)
        total_tva *= (1 - data.remise_globale_pct / 100)

    facture.total_ht = total_ht.quantize(Decimal("0.01"))
    facture.total_tva = total_tva.quantize(Decimal("0.01"))
    facture.total_ttc = (total_ht + total_tva).quantize(Decimal("0.01"))

    db.add(facture)
    await db.flush()
    await db.refresh(facture, ["lignes"])
    return facture


async def create_facture_from_commande(db: AsyncSession, commande: Commande, mode_reglement: str | None = None, date_echeance=None) -> Facture:
    numero = await _next_numero(db)
    facture = Facture(
        numero=numero,
        client_id=commande.client_id,
        commande_id=commande.id,
        vrp_id=commande.vrp_id,
        mode_reglement=mode_reglement,
        date_echeance=date_echeance,
        adresse_facturation=commande.adresse_livraison,
        cp_facturation=commande.cp_livraison,
        ville_facturation=commande.ville_livraison,
        total_ht=commande.total_ht,
        total_tva=commande.total_tva,
        total_ttc=commande.total_ttc,
        remise_globale_pct=commande.remise_globale_pct,
        statut=StatutFacture.EMISE,
    )

    for i, lc in enumerate(commande.lignes, 1):
        ligne = LigneFacture(
            ligne_numero=i,
            article_id=lc.article_id,
            designation=lc.designation,
            quantite=lc.quantite,
            prix_unitaire_ht=lc.prix_unitaire_ht,
            remise_pct=lc.remise_pct,
            tva_pct=lc.tva_pct,
            montant_ht=lc.montant_ht,
            taille=lc.taille,
            couleur=lc.couleur,
        )
        facture.lignes.append(ligne)

    commande.statut = StatutCommande.FACTUREE

    db.add(facture)
    await db.flush()
    await db.refresh(facture, ["lignes"])
    return facture


async def enregistrer_paiement(db: AsyncSession, facture: Facture, montant: Decimal) -> Facture:
    facture.montant_regle += montant
    if facture.montant_regle >= facture.total_ttc:
        facture.statut = StatutFacture.PAYEE
    else:
        facture.statut = StatutFacture.PAYEE_PARTIELLEMENT
    await db.flush()
    await db.refresh(facture)
    return facture
