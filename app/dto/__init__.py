"""DTO (Data Transfer Object) package - Pydantic models for request/response validation."""

from app.dto.analytics import AnalyticsResponse, CategoryStats, SentimentStats
from app.dto.review import ReviewCreate, ReviewListResponse, ReviewResponse, ReviewUpdate
from app.dto.summary import SummaryCreate, SummaryResponse
from app.dto.user import TokenResponse, UserCreate, UserLogin, UserResponse

__all__ = [
    # Review DTOs
    "ReviewCreate",
    "ReviewUpdate",
    "ReviewResponse",
    "ReviewListResponse",
    # Summary DTOs
    "SummaryCreate",
    "SummaryResponse",
    # User DTOs
    "UserCreate",
    "UserLogin",
    "UserResponse",
    "TokenResponse",
    # Analytics DTOs
    "SentimentStats",
    "CategoryStats",
    "AnalyticsResponse",
]
