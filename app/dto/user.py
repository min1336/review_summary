"""User DTOs for request/response validation."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserCreate(BaseModel):
    """DTO for user registration."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., min_length=8, description="User password (min 8 characters)")


class UserLogin(BaseModel):
    """DTO for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="User password")


class UserResponse(BaseModel):
    """DTO for user responses."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    """DTO for authentication token responses."""

    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    user: UserResponse
