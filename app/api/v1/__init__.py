from fastapi import APIRouter

from app.api.v1.articles import router as articles_router
from app.api.v1.clients import router as clients_router
from app.api.v1.stock import router as stock_router
from app.api.v1.commandes import router as commandes_router
from app.api.v1.factures import router as factures_router
from app.api.v1.livraisons import router as livraisons_router
from app.api.v1.vrp import router as vrp_router
from app.api.v1.reporting import router as reporting_router

router = APIRouter()

router.include_router(articles_router, prefix="/articles", tags=["Articles"])
router.include_router(clients_router, prefix="/clients", tags=["Clients"])
router.include_router(stock_router, prefix="/stock", tags=["Stock"])
router.include_router(commandes_router, prefix="/commandes", tags=["Commandes"])
router.include_router(factures_router, prefix="/factures", tags=["Factures"])
router.include_router(livraisons_router, prefix="/livraisons", tags=["Livraisons"])
router.include_router(vrp_router, prefix="/vrp", tags=["VRP"])
router.include_router(reporting_router, prefix="/reporting", tags=["Reporting"])
