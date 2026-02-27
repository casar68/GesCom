import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.facture import StatutFacture
from app.models.user import User
from app.schemas.facture import FactureCreate, FactureRead, FactureList, PaiementCreate
from app.schemas.common import PaginatedResponse
from app.services import facture_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_factures(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    client_id: int | None = None,
    statut: StatutFacture | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    factures, total = await facture_service.get_factures(db, page, page_size, client_id, statut)
    return PaginatedResponse(
        items=[FactureList.model_validate(f) for f in factures],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{facture_id}", response_model=FactureRead)
async def get_facture(
    facture_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    facture = await facture_service.get_facture(db, facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture introuvable")
    return facture


@router.post("", response_model=FactureRead, status_code=201)
async def create_facture(
    data: FactureCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await facture_service.create_facture(db, data)


@router.post("/{facture_id}/paiement", response_model=FactureRead)
async def enregistrer_paiement(
    facture_id: int,
    data: PaiementCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    facture = await facture_service.get_facture(db, facture_id)
    if not facture:
        raise HTTPException(status_code=404, detail="Facture introuvable")
    return await facture_service.enregistrer_paiement(db, facture, data.montant)
