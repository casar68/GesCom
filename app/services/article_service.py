from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.article import Article, ArticleTaille, ArticleCouleur, ArticleDepot, ArticleTarif
from app.schemas.article import ArticleCreate, ArticleUpdate, ArticleTailleCreate, ArticleCouleurCreate, ArticleDepotCreate, ArticleTarifCreate


async def get_articles(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    search: str | None = None,
    famille: str | None = None,
    gamme: str | None = None,
    actif: bool | None = None,
) -> tuple[list[Article], int]:
    query = select(Article)

    if search:
        query = query.where(
            Article.reference.ilike(f"%{search}%")
            | Article.designation.ilike(f"%{search}%")
            | Article.code_barre.ilike(f"%{search}%")
        )
    if famille:
        query = query.where(Article.famille == famille)
    if gamme:
        query = query.where(Article.gamme == gamme)
    if actif is not None:
        query = query.where(Article.actif == actif)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(Article.reference).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_article(db: AsyncSession, article_id: int) -> Article | None:
    query = (
        select(Article)
        .where(Article.id == article_id)
        .options(
            selectinload(Article.tailles),
            selectinload(Article.couleurs),
            selectinload(Article.depots),
            selectinload(Article.tarifs),
        )
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_article_by_ref(db: AsyncSession, reference: str) -> Article | None:
    result = await db.execute(select(Article).where(Article.reference == reference))
    return result.scalar_one_or_none()


async def create_article(db: AsyncSession, data: ArticleCreate) -> Article:
    article = Article(**data.model_dump(exclude={"tailles", "couleurs"}))
    for t in data.tailles:
        article.tailles.append(ArticleTaille(**t.model_dump()))
    for c in data.couleurs:
        article.couleurs.append(ArticleCouleur(**c.model_dump()))
    db.add(article)
    await db.flush()
    await db.refresh(article, ["tailles", "couleurs", "depots", "tarifs"])
    return article


async def update_article(db: AsyncSession, article: Article, data: ArticleUpdate) -> Article:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(article, field, value)
    await db.flush()
    await db.refresh(article)
    return article


async def delete_article(db: AsyncSession, article: Article) -> None:
    await db.delete(article)
    await db.flush()


async def add_taille(db: AsyncSession, article_id: int, data: ArticleTailleCreate) -> ArticleTaille:
    taille = ArticleTaille(article_id=article_id, **data.model_dump())
    db.add(taille)
    await db.flush()
    await db.refresh(taille)
    return taille


async def add_couleur(db: AsyncSession, article_id: int, data: ArticleCouleurCreate) -> ArticleCouleur:
    couleur = ArticleCouleur(article_id=article_id, **data.model_dump())
    db.add(couleur)
    await db.flush()
    await db.refresh(couleur)
    return couleur


async def add_depot(db: AsyncSession, article_id: int, data: ArticleDepotCreate) -> ArticleDepot:
    depot = ArticleDepot(article_id=article_id, **data.model_dump())
    db.add(depot)
    await db.flush()
    await db.refresh(depot)
    return depot


async def add_tarif(db: AsyncSession, article_id: int, data: ArticleTarifCreate) -> ArticleTarif:
    tarif = ArticleTarif(article_id=article_id, **data.model_dump())
    db.add(tarif)
    await db.flush()
    await db.refresh(tarif)
    return tarif
