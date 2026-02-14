"""Repository package - data access layer for Supabase."""

from app.repositories.base import BaseRepository
from app.repositories.review_repo import ReviewRepository
from app.repositories.summary_repo import SummaryRepository
from app.repositories.user_repo import UserRepository

__all__ = [
    "BaseRepository",
    "ReviewRepository",
    "SummaryRepository",
    "UserRepository",
]
