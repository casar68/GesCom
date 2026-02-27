import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.stock import TypeMouvement
from app.models.user import User
from app.schemas.article import ArticleList
from app.schemas.stock import MouvementStockCreate, MouvementStockRead, InventaireCreate, InventaireRead
from app.schemas.common import PaginatedResponse
from app.services import stock_service

router = APIRouter()


@router.get("/mouvements", response_model=PaginatedResponse)
async def list_mouvements(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    type_mouvement: TypeMouvement | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    mouvements, total = await stock_service.get_mouvements(db, page, page_size, type_mouvement)
    return PaginatedResponse(
        items=[MouvementStockRead.model_validate(m) for m in mouvements],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/mouvements/{mouvement_id}", response_model=MouvementStockRead)
async def get_mouvement(
    mouvement_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    mouvement = await stock_service.get_mouvement(db, mouvement_id)
    if not mouvement:
        raise HTTPException(status_code=404, detail="Mouvement introuvable")
    return mouvement


@router.post("/mouvements", response_model=MouvementStockRead, status_code=201)
async def create_mouvement(
    data: MouvementStockCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await stock_service.create_mouvement(db, data, user.id)


@router.post("/inventaires", response_model=InventaireRead, status_code=201)
async def create_inventaire(
    data: InventaireCreate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return await stock_service.create_inventaire(db, data, user.id)


@router.post("/inventaires/{inventaire_id}/valider", response_model=InventaireRead)
async def valider_inventaire(
    inventaire_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    from sqlalchemy import select
    from sqlalchemy.orm import selectinload
    from app.models.stock import Inventaire

    query = select(Inventaire).where(Inventaire.id == inventaire_id).options(selectinload(Inventaire.lignes))
    result = await db.execute(query)
    inventaire = result.scalar_one_or_none()
    if not inventaire:
        raise HTTPException(status_code=404, detail="Inventaire introuvable")
    return await stock_service.valider_inventaire(db, inventaire)


@router.get("/alertes", response_model=list[ArticleList])
async def get_alertes_stock(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    articles = await stock_service.get_articles_sous_stock(db)
    return [ArticleList.model_validate(a) for a in articles]
