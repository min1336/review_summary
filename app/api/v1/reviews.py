"""Reviews REST API router."""

from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user, get_supabase_client
from app.dto.review import ReviewCreate, ReviewListResponse, ReviewResponse
from app.dto.summary import SummaryResponse

router = APIRouter()


@router.get("", response_model=ReviewListResponse)
async def list_reviews(
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(10, ge=1, le=100, description="Items per page"),
    category: str | None = Query(None, description="Filter by category"),
) -> ReviewListResponse:
    """List reviews with pagination and optional category filter."""
    supabase = get_supabase_client()

    offset = (page - 1) * per_page

    # Build query for items
    query = supabase.table("reviews").select("*", count="exact")
    if category:
        query = query.eq("category", category)

    query = query.order("created_at", desc=True)
    query = query.range(offset, offset + per_page - 1)

    response = query.execute()

    items = [ReviewResponse(**row) for row in (response.data or [])]
    total = response.count if response.count is not None else len(items)

    return ReviewListResponse(
        items=items,
        total=total,
        page=page,
        per_page=per_page,
    )


@router.get("/{review_id}", response_model=ReviewResponse)
async def get_review(review_id: UUID) -> ReviewResponse:
    """Get a single review by ID."""
    supabase = get_supabase_client()

    response = (
        supabase.table("reviews")
        .select("*")
        .eq("id", str(review_id))
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with id '{review_id}' not found",
        )

    return ReviewResponse(**response.data[0])


@router.post("", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user: dict = Depends(get_current_user),
) -> ReviewResponse:
    """Create a new review. Requires authentication."""
    supabase = get_supabase_client()

    insert_data = review_data.model_dump()
    insert_data["author_id"] = current_user["id"]

    response = (
        supabase.table("reviews")
        .insert(insert_data)
        .execute()
    )

    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create review",
        )

    return ReviewResponse(**response.data[0])


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
async def delete_review(
    review_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> None:
    """Delete a review. Requires authentication and must be the author."""
    supabase = get_supabase_client()

    # Fetch the review to verify ownership
    existing = (
        supabase.table("reviews")
        .select("*")
        .eq("id", str(review_id))
        .execute()
    )

    if not existing.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with id '{review_id}' not found",
        )

    review = existing.data[0]
    if review.get("author_id") != current_user["id"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own reviews",
        )

    supabase.table("reviews").delete().eq("id", str(review_id)).execute()


@router.post("/{review_id}/summarize", response_model=SummaryResponse)
async def summarize_review(
    review_id: UUID,
    current_user: dict = Depends(get_current_user),
) -> SummaryResponse:
    """Trigger AI summary generation for a review. Requires authentication."""
    supabase = get_supabase_client()

    # Fetch the review
    review_response = (
        supabase.table("reviews")
        .select("*")
        .eq("id", str(review_id))
        .execute()
    )

    if not review_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Review with id '{review_id}' not found",
        )

    review = review_response.data[0]

    # Check if summary already exists
    if review.get("summary_id"):
        existing_summary = (
            supabase.table("summaries")
            .select("*")
            .eq("id", review["summary_id"])
            .execute()
        )
        if existing_summary.data:
            return SummaryResponse(**existing_summary.data[0])

    # Placeholder AI summary generation
    # In production, this would call an AI service (OpenAI, Gemini, etc.)
    summary_data = {
        "summary": f"AI-generated summary of: {review['title']}. {review['content'][:200]}...",
        "sentiment": "neutral",
        "sentiment_score": 0.0,
        "keywords": [],
        "pros": [],
        "cons": [],
        "ai_model": "placeholder",
    }

    summary_response = (
        supabase.table("summaries")
        .insert(summary_data)
        .execute()
    )

    if not summary_response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create summary",
        )

    summary = summary_response.data[0]

    # Link summary to review
    supabase.table("reviews").update(
        {"summary_id": summary["id"]}
    ).eq("id", str(review_id)).execute()

    return SummaryResponse(**summary)
