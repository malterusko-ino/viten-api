"""FastAPI application entry point."""

import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.v1.analyze import router as analyze_router
from app.core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s – %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Manage startup and shutdown of shared resources."""
    logger.info("Starting %s …", settings.project_name)
    # Future: initialise httpx.AsyncClient, LLM client, vector DB, etc.
    yield
    logger.info("Shutting down %s …", settings.project_name)
    # Future: close clients and connections here.


app = FastAPI(
    title=settings.project_name,
    description=(
        "RAG-based backend for the scientific fact-checking of political claims "
        "in Germany."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(analyze_router)


@app.get("/health", tags=["monitoring"])
async def health() -> JSONResponse:
    """Liveness probe – returns 200 when the service is up."""
    return JSONResponse(content={"status": "ok", "service": settings.project_name})
