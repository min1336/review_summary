"""Dependency injection module for FastAPI routes."""

from __future__ import annotations

from fastapi import HTTPException, Request
from supabase import Client, create_client

from app.core.config import get_settings


def get_supabase_client() -> Client:
    """Create and return a Supabase client using application settings."""
    settings = get_settings()
    return create_client(settings.supabase_url, settings.supabase_anon_key)


async def get_current_user(request: Request) -> dict:
    """Extract and validate JWT from the Authorization header.

    Returns the authenticated user information from Supabase.
    Raises HTTPException(401) if the token is missing or invalid.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Missing or invalid Authorization header",
        )

    token = auth_header.removeprefix("Bearer ").strip()
    if not token:
        raise HTTPException(
            status_code=401,
            detail="Empty bearer token",
        )

    try:
        supabase = get_supabase_client()
        user_response = supabase.auth.get_user(token)
        if user_response is None or user_response.user is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid or expired token",
            )
        user = user_response.user
        return {
            "id": str(user.id),
            "email": user.email,
            "created_at": str(user.created_at) if user.created_at else None,
        }
    except HTTPException:
        raise
    except Exception as exc:
        raise HTTPException(
            status_code=401,
            detail=f"Token validation failed: {str(exc)}",
        ) from exc


async def get_optional_user(request: Request) -> dict | None:
    """Extract and validate JWT from the Authorization header.

    Returns the authenticated user information, or None if the token
    is missing or invalid (does not raise on failure).
    """
    try:
        return await get_current_user(request)
    except HTTPException:
        return None
