"""Analytics DTOs for response validation."""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class SentimentStats(BaseModel):
    """DTO for sentiment distribution statistics."""

    positive: int = Field(..., ge=0, description="Count of positive reviews")
    negative: int = Field(..., ge=0, description="Count of negative reviews")
    neutral: int = Field(..., ge=0, description="Count of neutral reviews")
    mixed: int = Field(..., ge=0, description="Count of mixed-sentiment reviews")
    total: int = Field(..., ge=0, description="Total number of reviewed items")


class CategoryStats(BaseModel):
    """DTO for per-category statistics."""

    category: str = Field(..., description="Category name")
    count: int = Field(..., ge=0, description="Number of reviews in this category")
    avg_rating: Optional[float] = Field(None, description="Average rating for this category")


class AnalyticsResponse(BaseModel):
    """DTO for analytics dashboard response."""

    sentiment_stats: SentimentStats
    category_stats: list[CategoryStats]
    total_reviews: int = Field(..., ge=0, description="Total number of reviews")
    avg_rating: Optional[float] = Field(None, description="Overall average rating")
