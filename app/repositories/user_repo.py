"""User repository wrapping Supabase Auth."""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID


class UserRepository:
    """Data access layer for Supabase Auth users.

    Unlike other repositories this does **not** extend ``BaseRepository``
    because user records live in Supabase Auth rather than a regular
    database table.
    """

    def __init__(self, client: Any) -> None:
        self.client = client

    def get_by_id(self, user_id: UUID) -> Optional[dict]:
        """Retrieve a user from Supabase Auth by their UUID.

        Args:
            user_id: The UUID of the user to look up.

        Returns:
            A dictionary with ``id``, ``email`` and ``created_at`` keys,
            or ``None`` if the user could not be found.
        """
        try:
            response = self.client.auth.admin.get_user_by_id(str(user_id))
            if response is None or response.user is None:
                return None

            user = response.user
            return {
                "id": str(user.id),
                "email": user.email,
                "created_at": str(user.created_at) if user.created_at else None,
            }
        except Exception:
            return None
