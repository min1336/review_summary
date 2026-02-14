"""Analytics API router."""

from __future__ import annotations

from fastapi import APIRouter, HTTPException, status

from app.api.deps import get_supabase_client
from app.dto.analytics import AnalyticsResponse, CategoryStats, SentimentStats

router = APIRouter()


@router.get("/overview", response_model=AnalyticsResponse)
async def get_analytics_overview() -> AnalyticsResponse:
    """Return sentiment stats, category stats, total reviews, and average rating."""
    supabase = get_supabase_client()

    try:
        # Fetch all reviews for aggregation
        reviews_response = (
            supabase.table("reviews")
            .select("id, category, rating, summary_id", count="exact")
            .execute()
        )
        reviews = reviews_response.data or []
        total_reviews = reviews_response.count if reviews_response.count is not None else len(reviews)

        # Calculate average rating
        ratings = [r["rating"] for r in reviews if r.get("rating") is not None]
        avg_rating = round(sum(ratings) / len(ratings), 2) if ratings else None

        # Category stats
        category_map: dict[str, list[int | None]] = {}
        for review in reviews:
            cat = review.get("category", "other")
            if cat not in category_map:
                category_map[cat] = []
            category_map[cat].append(review.get("rating"))

        category_stats = []
        for cat, cat_ratings in sorted(category_map.items()):
            valid_ratings = [r for r in cat_ratings if r is not None]
            cat_avg = round(sum(valid_ratings) / len(valid_ratings), 2) if valid_ratings else None
            category_stats.append(
                CategoryStats(
                    category=cat,
                    count=len(cat_ratings),
                    avg_rating=cat_avg,
                )
            )

        # Sentiment stats from summaries
        summary_ids = [r["summary_id"] for r in reviews if r.get("summary_id")]
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0, "mixed": 0}

        if summary_ids:
            summaries_response = (
                supabase.table("summaries")
                .select("id, sentiment")
                .in_("id", summary_ids)
                .execute()
            )
            for s in summaries_response.data or []:
                sentiment = s.get("sentiment", "neutral")
                if sentiment in sentiment_counts:
                    sentiment_counts[sentiment] += 1

        sentiment_total = sum(sentiment_counts.values())
        sentiment_stats = SentimentStats(
            positive=sentiment_counts["positive"],
            negative=sentiment_counts["negative"],
            neutral=sentiment_counts["neutral"],
            mixed=sentiment_counts["mixed"],
            total=sentiment_total,
        )

        return AnalyticsResponse(
            sentiment_stats=sentiment_stats,
            category_stats=category_stats,
            total_reviews=total_reviews,
            avg_rating=avg_rating,
        )

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch analytics: {str(exc)}",
        ) from exc
