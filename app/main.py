"""Main FastAPI application entrypoint for TrustFin AI."""

from fastapi import FastAPI
from app.api.routes.health import router as health_router
from app.core.config import settings


def create_app() -> FastAPI:
    """Application factory for TrustFin AI."""
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.VERSION,
        debug=settings.DEBUG,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Include route modules
    app.include_router(health_router)

    return app


app = create_app()
