"""Review DTOs for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    """DTO for creating a new review."""

    title: str = Field(..., min_length=1, max_length=200, description="Review title")
    content: str = Field(..., min_length=1, description="Review content")
    category: Literal["product", "book", "restaurant", "movie", "other"] = Field(
        ..., description="Review category"
    )
    rating: int | None = Field(None, ge=1, le=5, description="Rating from 1 to 5")
    source: str | None = Field(None, max_length=500, description="Source URL or reference")


class ReviewUpdate(BaseModel):
    """DTO for updating an existing review. All fields are optional."""

    title: str | None = Field(None, min_length=1, max_length=200, description="Review title")
    content: str | None = Field(None, min_length=1, description="Review content")
    category: Literal["product", "book", "restaurant", "movie", "other"] | None = Field(
        None, description="Review category"
    )
    rating: int | None = Field(None, ge=1, le=5, description="Rating from 1 to 5")
    source: str | None = Field(None, max_length=500, description="Source URL or reference")


class ReviewResponse(BaseModel):
    """DTO for review responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    content: str
    category: str
    rating: int | None = None
    source: str | None = None
    author_id: UUID | None = None
    summary_id: UUID | None = None
    created_at: datetime
    updated_at: datetime


class ReviewListResponse(BaseModel):
    """DTO for paginated review list responses."""

    items: list[ReviewResponse]
    total: int = Field(..., ge=0, description="Total number of reviews")
    page: int = Field(..., ge=1, description="Current page number")
    per_page: int = Field(..., ge=1, description="Number of items per page")
