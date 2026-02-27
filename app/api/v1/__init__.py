from fastapi import APIRouter

from app.api.v1.articles import router as articles_router
from app.api.v1.clients import router as clients_router
from app.api.v1.stock import router as stock_router

router = APIRouter()

router.include_router(articles_router, prefix="/articles", tags=["Articles"])
router.include_router(clients_router, prefix="/clients", tags=["Clients"])
router.include_router(stock_router, prefix="/stock", tags=["Stock"])
