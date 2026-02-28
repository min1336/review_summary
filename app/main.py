"""FastAPI application entry point."""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.api.v1.router import api_v1_router
from app.core.config import get_settings
from app.core.exceptions import AppException
from app.pages.views import pages_router


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Application lifespan handler."""
    settings = get_settings()
    print(f"Starting Review Summary Platform [{settings.app_env}]")
    yield
    print("Shutting down Review Summary Platform")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    settings = get_settings()

    app = FastAPI(
        title="Review Summary Platform",
        description="AI-powered review summary and analysis platform",
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs" if settings.is_development else None,
        redoc_url="/redoc" if settings.is_development else None,
    )

    # Static files
    app.mount("/static", StaticFiles(directory="app/static"), name="static")

    # Templates
    templates = Jinja2Templates(directory="app/templates")
    app.state.templates = templates

    # API routers
    app.include_router(api_v1_router, prefix="/api/v1")

    # Page routers
    app.include_router(pages_router)

    # Exception handler
    @app.exception_handler(AppException)
    async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
        return JSONResponse(
            status_code=exc.status_code,
            content={"error": exc.message, "detail": exc.detail},
        )

    return app


app = create_app()
