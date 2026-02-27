import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.schemas.article import (
    ArticleCreate,
    ArticleUpdate,
    ArticleRead,
    ArticleList,
    ArticleTailleCreate,
    ArticleTailleRead,
    ArticleCouleurCreate,
    ArticleCouleurRead,
    ArticleDepotCreate,
    ArticleDepotRead,
    ArticleTarifCreate,
    ArticleTarifRead,
)
from app.schemas.common import PaginatedResponse
from app.services import article_service

router = APIRouter()


@router.get("", response_model=PaginatedResponse)
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=200),
    search: str | None = None,
    famille: str | None = None,
    gamme: str | None = None,
    actif: bool | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    articles, total = await article_service.get_articles(db, page, page_size, search, famille, gamme, actif)
    return PaginatedResponse(
        items=[ArticleList.model_validate(a) for a in articles],
        total=total,
        page=page,
        page_size=page_size,
        pages=math.ceil(total / page_size) if total else 0,
    )


@router.get("/{article_id}", response_model=ArticleRead)
async def get_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    article = await article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return article


@router.post("", response_model=ArticleRead, status_code=201)
async def create_article(
    data: ArticleCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    existing = await article_service.get_article_by_ref(db, data.reference)
    if existing:
        raise HTTPException(status_code=400, detail="Référence article déjà existante")
    return await article_service.create_article(db, data)


@router.put("/{article_id}", response_model=ArticleRead)
async def update_article(
    article_id: int,
    data: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    article = await article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable")
    return await article_service.update_article(db, article, data)


@router.delete("/{article_id}", status_code=204)
async def delete_article(
    article_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    article = await article_service.get_article(db, article_id)
    if not article:
        raise HTTPException(status_code=404, detail="Article introuvable")
    await article_service.delete_article(db, article)


@router.post("/{article_id}/tailles", response_model=ArticleTailleRead, status_code=201)
async def add_taille(
    article_id: int,
    data: ArticleTailleCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await article_service.add_taille(db, article_id, data)


@router.post("/{article_id}/couleurs", response_model=ArticleCouleurRead, status_code=201)
async def add_couleur(
    article_id: int,
    data: ArticleCouleurCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await article_service.add_couleur(db, article_id, data)


@router.post("/{article_id}/depots", response_model=ArticleDepotRead, status_code=201)
async def add_depot(
    article_id: int,
    data: ArticleDepotCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await article_service.add_depot(db, article_id, data)


@router.post("/{article_id}/tarifs", response_model=ArticleTarifRead, status_code=201)
async def add_tarif(
    article_id: int,
    data: ArticleTarifCreate,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await article_service.add_tarif(db, article_id, data)
