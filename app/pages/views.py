"""Jinja2 page router for server-rendered HTML pages."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

pages_router = APIRouter(tags=["pages"])


@pages_router.get("/", response_class=HTMLResponse)
async def index(request: Request) -> HTMLResponse:
    """Landing / dashboard page."""
    templates = request.app.state.templates
    return templates.TemplateResponse("index.html", {"request": request})


@pages_router.get("/reviews", response_class=HTMLResponse)
async def reviews_list(request: Request) -> HTMLResponse:
    """Review list page."""
    templates = request.app.state.templates
    return templates.TemplateResponse("reviews/list.html", {"request": request})


@pages_router.get("/reviews/new", response_class=HTMLResponse)
async def reviews_create(request: Request) -> HTMLResponse:
    """Create review page."""
    templates = request.app.state.templates
    return templates.TemplateResponse("reviews/create.html", {"request": request})


@pages_router.get("/summaries/{summary_id}", response_class=HTMLResponse)
async def summary_detail(request: Request, summary_id: UUID) -> HTMLResponse:
    """Summary detail page."""
    templates = request.app.state.templates
    return templates.TemplateResponse(
        "summaries/detail.html",
        {"request": request, "summary_id": str(summary_id)},
    )


@pages_router.get("/analytics", response_class=HTMLResponse)
async def analytics_dashboard(request: Request) -> HTMLResponse:
    """Analytics dashboard page."""
    templates = request.app.state.templates
    return templates.TemplateResponse("analytics/dashboard.html", {"request": request})
