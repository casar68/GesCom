from contextlib import asynccontextmanager
from collections.abc import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.v1 import router as api_v1_router
from app.auth.router import router as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="GesCom - Gestion Commerciale NKF",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth", tags=["Authentification"])
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health")
async def health_check():
    return {"status": "ok", "app": settings.APP_NAME, "version": settings.APP_VERSION}
