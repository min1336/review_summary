"""Auth API router using Supabase Auth."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import get_current_user, get_supabase_client
from app.dto.user import TokenResponse, UserCreate, UserLogin, UserResponse

router = APIRouter()


@router.post("/signup", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
async def signup(user_data: UserCreate) -> TokenResponse:
    """Register a new user with email and password via Supabase Auth."""
    supabase = get_supabase_client()

    try:
        response = supabase.auth.sign_up(
            {
                "email": user_data.email,
                "password": user_data.password,
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Signup failed: {str(exc)}",
        ) from exc

    if response.user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signup failed: could not create user",
        )

    if response.session is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Signup succeeded but email confirmation may be required",
        )

    user = response.user
    return TokenResponse(
        access_token=response.session.access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email or "",
            created_at=user.created_at,
        ),
    )


@router.post("/login", response_model=TokenResponse)
async def login(user_data: UserLogin) -> TokenResponse:
    """Login with email and password via Supabase Auth."""
    supabase = get_supabase_client()

    try:
        response = supabase.auth.sign_in_with_password(
            {
                "email": user_data.email,
                "password": user_data.password,
            }
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Login failed: {str(exc)}",
        ) from exc

    if response.user is None or response.session is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    user = response.user
    return TokenResponse(
        access_token=response.session.access_token,
        token_type="bearer",
        user=UserResponse(
            id=user.id,
            email=user.email or "",
            created_at=user.created_at,
        ),
    )


@router.post("/logout", status_code=status.HTTP_200_OK)
async def logout(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Logout the current user. Requires authentication."""
    supabase = get_supabase_client()

    try:
        supabase.auth.sign_out()
    except Exception:
        # Sign out is best-effort; the client should discard the token regardless
        pass

    return {"message": "Successfully logged out"}


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: dict = Depends(get_current_user),
) -> dict:
    """Get the current authenticated user's information."""
    return current_user
