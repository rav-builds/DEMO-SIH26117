import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncIterator
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.api.router import api_router
from app.models.registry import model_registry

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """
    Application lifecycle manager.
    Initializes resources and persistence directories on startup and cleanly closes
    connection pools on shutdown.
    """
    # Ensure local persistence and upload directories exist
    os.makedirs("data", exist_ok=True)
    os.makedirs("uploads", exist_ok=True)

    logger.info(
        "Starting %s v%s (Backend: %s, Endpoint: %s, Air-Gapped: True)",
        settings.app_name,
        settings.app_version,
        settings.active_backend,
        settings.active_model_endpoint,
    )
    yield
    logger.info("Shutting down %s; closing model client connections...", settings.app_name)
    await model_registry.aclose()


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend applications (Vite / Next.js)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.parsed_allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/", tags=["root"])
async def root_status() -> JSONResponse:
    return JSONResponse(
        content={
            "app": settings.app_name,
            "version": settings.app_version,
            "status": "online",
            "active_backend": settings.active_backend,
            "active_model": settings.active_model_name,
            "docs": "/docs",
        }
    )
