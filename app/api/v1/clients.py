import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.client import (
    ClientCreate,
    ClientUpdate,
    ClientRead,
    ClientList,
    ContactClientCreate,
    ContactClientRead,
    AdresseClientCreate,
    AdresseClientRead,
)
from app.schemas.common import PaginatedResponse
from app.services import client_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_clients(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: str | None = None,
    type_client: str | None = None,
    actif: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    clients, total = await client_service.get_clients(db, page, page_size, search, type_client, actif)
    return PaginatedResponse(
        items=[ClientList.model_validate(c) for c in clients],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{client_id}", response_model=ClientRead)
async def get_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    client = await client_service.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")
    return client


@router.post("", response_model=ClientRead, status_code=201)
async def create_client(
    data: ClientCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    existing = await client_service.get_client_by_code(db, data.code_client)
    if existing:
        raise HTTPException(status_code=400, detail="Code client déjà existant")
    return await client_service.create_client(db, data)


@router.put("/{client_id}", response_model=ClientRead)
async def update_client(
    client_id: int,
    data: ClientUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    client = await client_service.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")
    return await client_service.update_client(db, client, data)


@router.delete("/{client_id}", status_code=204)
async def delete_client(
    client_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    client = await client_service.get_client(db, client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client introuvable")
    await client_service.delete_client(db, client)


@router.post("/{client_id}/contacts", response_model=ContactClientRead, status_code=201)
async def add_contact(
    client_id: int,
    data: ContactClientCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await client_service.add_contact(db, client_id, data)


@router.post("/{client_id}/adresses", response_model=AdresseClientRead, status_code=201)
async def add_adresse(
    client_id: int,
    data: AdresseClientCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await client_service.add_adresse(db, client_id, data)
