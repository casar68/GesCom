import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.commande import StatutCommande
from app.models.user import User
from app.schemas.commande import CommandeCreate, CommandeUpdate, CommandeRead, CommandeList
from app.schemas.common import PaginatedResponse, MessageResponse
from app.services import commande_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_commandes(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    client_id: int | None = None,
    statut: StatutCommande | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    commandes, total = await commande_service.get_commandes(db, page, page_size, client_id, statut)
    return PaginatedResponse(
        items=[CommandeList.model_validate(c) for c in commandes],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{commande_id}", response_model=CommandeRead)
async def get_commande(
    commande_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    commande = await commande_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    return commande


@router.post("", response_model=CommandeRead, status_code=201)
async def create_commande(
    data: CommandeCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await commande_service.create_commande(db, data)


@router.put("/{commande_id}", response_model=CommandeRead)
async def update_commande(
    commande_id: int,
    data: CommandeUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    commande = await commande_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    return await commande_service.update_commande(db, commande, data)


@router.post("/{commande_id}/valider", response_model=CommandeRead)
async def valider_commande(
    commande_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    commande = await commande_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    return await commande_service.changer_statut(db, commande, StatutCommande.VALIDEE)


@router.post("/{commande_id}/facturer", response_model=dict)
async def facturer_commande(
    commande_id: int,
    mode_reglement: str | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    from app.services import facture_service

    commande = await commande_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    facture = await facture_service.create_facture_from_commande(db, commande, mode_reglement)
    return {"message": "Facture créée", "facture_numero": facture.numero, "facture_id": facture.id}


@router.post("/{commande_id}/livrer", response_model=dict)
async def livrer_commande(
    commande_id: int,
    transport_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    from app.services import livraison_service

    commande = await commande_service.get_commande(db, commande_id)
    if not commande:
        raise HTTPException(status_code=404, detail="Commande introuvable")
    bl = await livraison_service.create_bl_from_commande(db, commande, transport_id)
    return {"message": "Bon de livraison créé", "bl_numero": bl.numero, "bl_id": bl.id}
