from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.vrp import VRP, Concession, SuiviClient
from app.schemas.vrp import VRPCreate, VRPUpdate, ConcessionCreate, SuiviClientCreate


async def get_vrps(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    actif: bool | None = None,
) -> tuple[list[VRP], int]:
    query = select(VRP)
    if actif is not None:
        query = query.where(VRP.actif == actif)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(VRP.nom).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_vrp(db: AsyncSession, vrp_id: int) -> VRP | None:
    query = select(VRP).where(VRP.id == vrp_id).options(selectinload(VRP.concessions))
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def create_vrp(db: AsyncSession, data: VRPCreate) -> VRP:
    vrp = VRP(**data.model_dump())
    db.add(vrp)
    await db.flush()
    await db.refresh(vrp)
    return vrp


async def update_vrp(db: AsyncSession, vrp: VRP, data: VRPUpdate) -> VRP:
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(vrp, field, value)
    await db.flush()
    await db.refresh(vrp)
    return vrp


async def create_concession(db: AsyncSession, data: ConcessionCreate) -> Concession:
    concession = Concession(**data.model_dump())
    db.add(concession)
    await db.flush()
    await db.refresh(concession)
    return concession


async def get_concessions(db: AsyncSession, vrp_id: int | None = None) -> list[Concession]:
    query = select(Concession)
    if vrp_id:
        query = query.where(Concession.vrp_id == vrp_id)
    query = query.order_by(Concession.nom)
    result = await db.execute(query)
    return list(result.scalars().all())


async def create_suivi(db: AsyncSession, data: SuiviClientCreate) -> SuiviClient:
    suivi = SuiviClient(**data.model_dump())
    db.add(suivi)
    await db.flush()
    await db.refresh(suivi)
    return suivi


async def get_suivis_client(db: AsyncSession, client_id: int) -> list[SuiviClient]:
    query = select(SuiviClient).where(SuiviClient.client_id == client_id).order_by(SuiviClient.date_action.desc())
    result = await db.execute(query)
    return list(result.scalars().all())
