"""User domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class User:
    """Domain model representing a user."""

    email: str
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> User:
        """Create a User instance from a dictionary.

        Args:
            data: Dictionary containing user fields. UUID and datetime
                  values can be strings or native types.

        Returns:
            A new User instance.
        """
        return cls(
            id=UUID(data["id"]) if isinstance(data.get("id"), str) else data.get("id", uuid4()),
            email=data["email"],
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if isinstance(data.get("created_at"), str)
                else data.get("created_at", datetime.now())
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the User instance to a dictionary.

        Returns:
            Dictionary with all user fields, UUIDs and datetimes as strings.
        """
        return {
            "id": str(self.id),
            "email": self.email,
            "created_at": self.created_at.isoformat(),
        }
