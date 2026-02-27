import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.livraison import StatutLivraison
from app.models.user import User
from app.schemas.livraison import BonLivraisonCreate, BonLivraisonRead, BonLivraisonList
from app.schemas.common import PaginatedResponse
from app.services import livraison_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_bons_livraison(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    client_id: int | None = None,
    statut: StatutLivraison | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    bls, total = await livraison_service.get_bons_livraison(db, page, page_size, client_id, statut)
    return PaginatedResponse(
        items=[BonLivraisonList.model_validate(bl) for bl in bls],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{bl_id}", response_model=BonLivraisonRead)
async def get_bon_livraison(
    bl_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    bl = await livraison_service.get_bon_livraison(db, bl_id)
    if not bl:
        raise HTTPException(status_code=404, detail="Bon de livraison introuvable")
    return bl


@router.post("", response_model=BonLivraisonRead, status_code=201)
async def create_bon_livraison(
    data: BonLivraisonCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await livraison_service.create_bon_livraison(db, data)


@router.post("/{bl_id}/expedier", response_model=BonLivraisonRead)
async def expedier(
    bl_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    bl = await livraison_service.get_bon_livraison(db, bl_id)
    if not bl:
        raise HTTPException(status_code=404, detail="BL introuvable")
    return await livraison_service.changer_statut(db, bl, StatutLivraison.EXPEDIEE)


@router.post("/{bl_id}/livrer", response_model=BonLivraisonRead)
async def marquer_livre(
    bl_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    bl = await livraison_service.get_bon_livraison(db, bl_id)
    if not bl:
        raise HTTPException(status_code=404, detail="BL introuvable")
    return await livraison_service.changer_statut(db, bl, StatutLivraison.LIVREE)
