"""Business logic for analytics and reporting."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from app.dto.analytics import AnalyticsResponse, CategoryStats, SentimentStats


class AnalyticsService:
    """Aggregates review and summary data for dashboard analytics."""

    def __init__(self, supabase_client: Any) -> None:
        self.client = supabase_client

    def get_overview(self) -> AnalyticsResponse:
        """Build a high-level analytics overview.

        Queries the ``reviews`` and ``summaries`` tables to compute
        sentiment distribution, per-category counts, and average
        ratings.

        Returns:
            An ``AnalyticsResponse`` DTO containing the aggregated data.
        """
        sentiment_stats = self._get_sentiment_stats()
        category_stats = self._get_category_stats()
        total_reviews = self._get_total_reviews()
        avg_rating = self._get_average_rating()

        return AnalyticsResponse(
            sentiment_stats=sentiment_stats,
            category_stats=category_stats,
            total_reviews=total_reviews,
            avg_rating=avg_rating,
        )

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _get_sentiment_stats(self) -> SentimentStats:
        """Count summaries grouped by sentiment label."""
        response = (
            self.client.table("summaries")
            .select("sentiment", count="exact")
            .execute()
        )
        summaries: List[Dict[str, Any]] = response.data or []

        counts: Dict[str, int] = {
            "positive": 0,
            "negative": 0,
            "neutral": 0,
            "mixed": 0,
        }

        for row in summaries:
            sentiment = row.get("sentiment", "neutral")
            if sentiment in counts:
                counts[sentiment] += 1

        total = sum(counts.values())

        return SentimentStats(
            positive=counts["positive"],
            negative=counts["negative"],
            neutral=counts["neutral"],
            mixed=counts["mixed"],
            total=total,
        )

    def _get_category_stats(self) -> List[CategoryStats]:
        """Compute per-category review counts and average ratings."""
        response = (
            self.client.table("reviews")
            .select("category, rating")
            .execute()
        )
        reviews: List[Dict[str, Any]] = response.data or []

        category_data: Dict[str, Dict[str, Any]] = {}

        for row in reviews:
            cat = row.get("category", "other")
            if cat not in category_data:
                category_data[cat] = {"count": 0, "rating_sum": 0.0, "rating_count": 0}
            category_data[cat]["count"] += 1

            rating = row.get("rating")
            if rating is not None:
                category_data[cat]["rating_sum"] += float(rating)
                category_data[cat]["rating_count"] += 1

        stats: List[CategoryStats] = []
        for cat, info in sorted(category_data.items()):
            avg: Optional[float] = None
            if info["rating_count"] > 0:
                avg = round(info["rating_sum"] / info["rating_count"], 2)
            stats.append(
                CategoryStats(category=cat, count=info["count"], avg_rating=avg)
            )

        return stats

    def _get_total_reviews(self) -> int:
        """Return the total number of reviews."""
        response = (
            self.client.table("reviews")
            .select("id", count="exact")
            .execute()
        )
        return response.count if response.count is not None else 0

    def _get_average_rating(self) -> Optional[float]:
        """Compute the overall average rating across all reviews."""
        response = (
            self.client.table("reviews")
            .select("rating")
            .not_("rating", "is", "null")
            .execute()
        )
        rows: List[Dict[str, Any]] = response.data or []

        if not rows:
            return None

        total = sum(float(r["rating"]) for r in rows)
        return round(total / len(rows), 2)
