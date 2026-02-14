"""Summary repository for Supabase data access."""

from __future__ import annotations

from typing import Any, List, Tuple

from app.repositories.base import BaseRepository


class SummaryRepository(BaseRepository):
    """Data access layer for the ``summaries`` table."""

    def __init__(self, client: Any) -> None:
        super().__init__("summaries", client)

    def get_by_sentiment(
        self,
        sentiment: str,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[dict], int]:
        """Get paginated summaries filtered by sentiment.

        Args:
            sentiment: Sentiment classification to filter on
                       (``positive``, ``negative``, ``neutral``, or ``mixed``).
            page: 1-based page number.
            per_page: Number of records per page.

        Returns:
            A tuple of (list-of-record-dicts, total-count).
        """
        return self.get_all(page=page, per_page=per_page, sentiment=sentiment)
