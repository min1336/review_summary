"""Review repository for Supabase data access."""

from __future__ import annotations

from typing import Any, List, Tuple
from uuid import UUID

from app.repositories.base import BaseRepository


class ReviewRepository(BaseRepository):
    """Data access layer for the ``reviews`` table."""

    def __init__(self, client: Any) -> None:
        super().__init__("reviews", client)

    def get_by_category(
        self,
        category: str,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[dict], int]:
        """Get paginated reviews filtered by category.

        Args:
            category: Review category to filter on.
            page: 1-based page number.
            per_page: Number of records per page.

        Returns:
            A tuple of (list-of-record-dicts, total-count).
        """
        return self.get_all(page=page, per_page=per_page, category=category)

    def get_by_author(
        self,
        author_id: UUID,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[dict], int]:
        """Get paginated reviews filtered by author.

        Args:
            author_id: UUID of the review author.
            page: 1-based page number.
            per_page: Number of records per page.

        Returns:
            A tuple of (list-of-record-dicts, total-count).
        """
        return self.get_all(page=page, per_page=per_page, author_id=str(author_id))

    def search(
        self,
        query: str,
        page: int = 1,
        per_page: int = 20,
    ) -> Tuple[List[dict], int]:
        """Full-text search across review title and content using ``ilike``.

        Args:
            query: Search string (case-insensitive partial match).
            page: 1-based page number.
            per_page: Number of records per page.

        Returns:
            A tuple of (list-of-record-dicts, total-count).
        """
        pattern = f"%{query}%"
        offset = (page - 1) * per_page

        search_query = (
            self.client.table(self.table_name)
            .select("*", count="exact")
            .or_(f"title.ilike.{pattern},content.ilike.{pattern}")
            .order("created_at", desc=True)
            .range(offset, offset + per_page - 1)
        )

        response = search_query.execute()
        total = response.count if response.count is not None else len(response.data)
        return response.data or [], total
