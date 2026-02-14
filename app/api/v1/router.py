"""Combined API v1 router."""

from fastapi import APIRouter

from app.api.v1 import analytics, auth, reviews, summaries

api_v1_router = APIRouter()

api_v1_router.include_router(reviews.router, prefix="/reviews", tags=["reviews"])
api_v1_router.include_router(summaries.router, prefix="/summaries", tags=["summaries"])
api_v1_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_v1_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
