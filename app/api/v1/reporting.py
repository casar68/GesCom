from datetime import datetime, timezone

from fastapi import APIRouter, Depends, Query
from fastapi.responses import Response
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.dependencies import get_current_user
from app.database import get_db
from app.models.user import User
from app.services import reporting_service, export_service

router = APIRouter()


@router.get("/dashboard")
async def get_dashboard(
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await reporting_service.get_dashboard(db)


@router.get("/ca-mensuel")
async def get_ca_par_mois(
    annee: int = Query(default_factory=lambda: datetime.now(timezone.utc).year),
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await reporting_service.get_ca_par_mois(db, annee)


@router.get("/top-clients")
async def get_top_clients(
    limit: int = Query(10, ge=1, le=100),
    annee: int | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await reporting_service.get_top_clients(db, limit, annee)


@router.get("/top-articles")
async def get_top_articles(
    limit: int = Query(10, ge=1, le=100),
    annee: int | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await reporting_service.get_top_articles(db, limit, annee)


@router.get("/ca-par-famille")
async def get_ca_par_famille(
    annee: int | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await reporting_service.get_ca_par_famille(db, annee)


@router.get("/ca-par-region")
async def get_ca_par_region(
    annee: int | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    return await reporting_service.get_ca_par_region(db, annee)


@router.get("/export/top-clients")
async def export_top_clients_excel(
    limit: int = Query(50, ge=1, le=500),
    annee: int | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    data = await reporting_service.get_top_clients(db, limit, annee)
    excel_bytes = export_service.generate_excel_report(data, "Top Clients")
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=top_clients.xlsx"},
    )


@router.get("/export/top-articles")
async def export_top_articles_excel(
    limit: int = Query(50, ge=1, le=500),
    annee: int | None = None,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    data = await reporting_service.get_top_articles(db, limit, annee)
    excel_bytes = export_service.generate_excel_report(data, "Top Articles")
    return Response(
        content=excel_bytes,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=top_articles.xlsx"},
    )


@router.get("/export/facture/{facture_id}/pdf")
async def export_facture_pdf(
    facture_id: int,
    db: AsyncSession = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    from app.services.facture_service import get_facture
    from app.services.client_service import get_client

    facture = await get_facture(db, facture_id)
    if not facture:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Facture introuvable")

    client = await get_client(db, facture.client_id)
    client_name = client.raison_sociale if client else "Client inconnu"

    pdf_bytes = export_service.generate_facture_pdf(facture, client_name)
    return Response(
        content=pdf_bytes,
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=facture_{facture.numero}.pdf"},
    )
