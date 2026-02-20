"""Abstract base repository defining CRUD interface for Supabase."""

from __future__ import annotations

from abc import ABC
from typing import Any
from uuid import UUID


class BaseRepository(ABC):
    """Abstract base repository defining CRUD interface.

    Provides common data access methods for Supabase tables. Subclasses
    should call ``super().__init__`` with the appropriate table name and
    an authenticated Supabase client instance.
    """

    def __init__(self, table_name: str, supabase_client: Any) -> None:
        self.table_name = table_name
        self.client = supabase_client

    def get_by_id(self, id: UUID) -> dict | None:
        """Get a single record by ID.

        Args:
            id: Primary key UUID of the record.

        Returns:
            A dictionary representing the record, or ``None`` if not found.
        """
        response = (
            self.client.table(self.table_name)
            .select("*")
            .eq("id", str(id))
            .execute()
        )
        data = response.data
        return data[0] if data else None

    def get_all(
        self,
        page: int = 1,
        per_page: int = 20,
        **filters: Any,
    ) -> tuple[list[dict], int]:
        """Get paginated records with optional equality filters.

        Args:
            page: 1-based page number.
            per_page: Number of records per page.
            **filters: Column-name / value pairs used as equality filters.
                       ``None`` values are silently skipped.

        Returns:
            A tuple of (list-of-record-dicts, total-count).
        """
        query = self.client.table(self.table_name).select("*", count="exact")

        for key, value in filters.items():
            if value is not None:
                query = query.eq(key, value)

        offset = (page - 1) * per_page
        query = query.range(offset, offset + per_page - 1).order(
            "created_at", desc=True
        )

        response = query.execute()
        total = response.count if response.count is not None else len(response.data)
        return response.data or [], total

    def create(self, data: dict) -> dict:
        """Create a new record.

        Args:
            data: Column-name / value mapping for the new row.

        Returns:
            The newly created record as a dictionary.
        """
        response = self.client.table(self.table_name).insert(data).execute()
        return response.data[0]

    def update(self, id: UUID, data: dict) -> dict | None:
        """Update an existing record.

        Args:
            id: Primary key UUID of the record to update.
            data: Column-name / value mapping with fields to change.

        Returns:
            The updated record as a dictionary, or ``None`` if the record
            was not found.
        """
        response = (
            self.client.table(self.table_name)
            .update(data)
            .eq("id", str(id))
            .execute()
        )
        return response.data[0] if response.data else None

    def delete(self, id: UUID) -> bool:
        """Delete a record by ID.

        Args:
            id: Primary key UUID of the record to delete.

        Returns:
            ``True`` if a row was deleted, ``False`` otherwise.
        """
        response = (
            self.client.table(self.table_name)
            .delete()
            .eq("id", str(id))
            .execute()
        )
        return len(response.data) > 0
