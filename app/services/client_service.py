from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.client import Client, ContactClient, AdresseClient
from app.schemas.client import ClientCreate, ClientUpdate, ContactClientCreate, AdresseClientCreate


async def get_clients(
    db: AsyncSession,
    page: int = 1,
    page_size: int = 50,
    search: str | None = None,
    type_client: str | None = None,
    actif: bool | None = None,
) -> tuple[list[Client], int]:
    query = select(Client)

    if search:
        query = query.where(
            Client.code_client.ilike(f"%{search}%")
            | Client.raison_sociale.ilike(f"%{search}%")
            | Client.ville.ilike(f"%{search}%")
        )
    if type_client:
        query = query.where(Client.type_client == type_client)
    if actif is not None:
        query = query.where(Client.actif == actif)

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar() or 0

    query = query.order_by(Client.raison_sociale).offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)
    return list(result.scalars().all()), total


async def get_client(db: AsyncSession, client_id: int) -> Client | None:
    query = (
        select(Client)
        .where(Client.id == client_id)
        .options(selectinload(Client.contacts), selectinload(Client.adresses))
    )
    result = await db.execute(query)
    return result.scalar_one_or_none()


async def get_client_by_code(db: AsyncSession, code: str) -> Client | None:
    result = await db.execute(select(Client).where(Client.code_client == code))
    return result.scalar_one_or_none()


async def create_client(db: AsyncSession, data: ClientCreate) -> Client:
    client = Client(**data.model_dump(exclude={"contacts", "adresses"}))
    for c in data.contacts:
        client.contacts.append(ContactClient(**c.model_dump()))
    for a in data.adresses:
        client.adresses.append(AdresseClient(**a.model_dump()))
    db.add(client)
    await db.flush()
    await db.refresh(client, ["contacts", "adresses"])
    return client


async def update_client(db: AsyncSession, client: Client, data: ClientUpdate) -> Client:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(client, field, value)
    await db.flush()
    await db.refresh(client)
    return client


async def delete_client(db: AsyncSession, client: Client) -> None:
    await db.delete(client)
    await db.flush()


async def add_contact(db: AsyncSession, client_id: int, data: ContactClientCreate) -> ContactClient:
    contact = ContactClient(client_id=client_id, **data.model_dump())
    db.add(contact)
    await db.flush()
    await db.refresh(contact)
    return contact


async def add_adresse(db: AsyncSession, client_id: int, data: AdresseClientCreate) -> AdresseClient:
    adresse = AdresseClient(client_id=client_id, **data.model_dump())
    db.add(adresse)
    await db.flush()
    await db.refresh(adresse)
    return adresse
