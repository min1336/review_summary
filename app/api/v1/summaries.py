"""Summaries REST API router."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status

from app.api.deps import get_supabase_client
from app.dto.summary import SummaryResponse

router = APIRouter()


@router.get("/{summary_id}", response_model=SummaryResponse)
async def get_summary(summary_id: UUID) -> SummaryResponse:
    """Get a single summary by ID."""
    supabase = get_supabase_client()

    response = (
        supabase.table("summaries")
        .select("*")
        .eq("id", str(summary_id))
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Summary with id '{summary_id}' not found",
        )

    return SummaryResponse(**response.data[0])


@router.get("", response_model=list[SummaryResponse])
async def list_summaries(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
) -> list[SummaryResponse]:
    """List recent summaries with pagination."""
    supabase = get_supabase_client()

    offset = (page - 1) * per_page

    response = (
        supabase.table("summaries")
        .select("*")
        .order("created_at", desc=True)
        .range(offset, offset + per_page - 1)
        .execute()
    )

    return [SummaryResponse(**row) for row in (response.data or [])]
