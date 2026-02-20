"""Summary DTOs for request/response validation."""

from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SummaryCreate(BaseModel):
    """DTO for creating a new AI-generated summary."""

    summary: str = Field(..., min_length=1, description="AI-generated summary text")
    sentiment: Literal["positive", "negative", "neutral", "mixed"] = Field(
        ..., description="Overall sentiment classification"
    )
    sentiment_score: float = Field(
        ..., ge=-1.0, le=1.0, description="Sentiment score from -1.0 (negative) to 1.0 (positive)"
    )
    keywords: list[str] = Field(default_factory=list, description="Extracted keywords")
    pros: list[str] = Field(default_factory=list, description="Identified pros/advantages")
    cons: list[str] = Field(default_factory=list, description="Identified cons/disadvantages")
    ai_model: str | None = Field(None, description="AI model used for summarization")

    @field_validator("sentiment_score")
    @classmethod
    def validate_sentiment_score_precision(cls, v: float) -> float:
        """Round sentiment score to 2 decimal places."""
        return round(v, 2)


class SummaryResponse(BaseModel):
    """DTO for summary responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    summary: str
    sentiment: str
    sentiment_score: float
    keywords: list[str]
    pros: list[str]
    cons: list[str]
    ai_model: str | None = None
    created_at: datetime
