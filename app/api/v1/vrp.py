import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.vrp import (
    VRPCreate, VRPUpdate, VRPRead,
    ConcessionCreate, ConcessionRead,
    SuiviClientCreate, SuiviClientRead,
)
from app.schemas.common import PaginatedResponse
from app.services import vrp_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_vrps(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    actif: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    vrps, total = await vrp_service.get_vrps(db, page, page_size, actif)
    return PaginatedResponse(
        items=[VRPRead.model_validate(v) for v in vrps],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{vrp_id}", response_model=VRPRead)
async def get_vrp(
    vrp_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    vrp = await vrp_service.get_vrp(db, vrp_id)
    if not vrp:
        raise HTTPException(status_code=404, detail="VRP introuvable")
    return vrp


@router.post("", response_model=VRPRead, status_code=201)
async def create_vrp(
    data: VRPCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await vrp_service.create_vrp(db, data)


@router.put("/{vrp_id}", response_model=VRPRead)
async def update_vrp(
    vrp_id: int,
    data: VRPUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    vrp = await vrp_service.get_vrp(db, vrp_id)
    if not vrp:
        raise HTTPException(status_code=404, detail="VRP introuvable")
    return await vrp_service.update_vrp(db, vrp, data)


@router.post("/concessions", response_model=ConcessionRead, status_code=201)
async def create_concession(
    data: ConcessionCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await vrp_service.create_concession(db, data)


@router.get("/concessions/list", response_model=list[ConcessionRead])
async def list_concessions(
    vrp_id: int | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return [ConcessionRead.model_validate(c) for c in await vrp_service.get_concessions(db, vrp_id)]


@router.post("/suivis", response_model=SuiviClientRead, status_code=201)
async def create_suivi(
    data: SuiviClientCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await vrp_service.create_suivi(db, data)


@router.get("/suivis/{client_id}", response_model=list[SuiviClientRead])
async def get_suivis_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return [SuiviClientRead.model_validate(s) for s in await vrp_service.get_suivis_client(db, client_id)]
