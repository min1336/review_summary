"""Review domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Optional
from uuid import UUID, uuid4


@dataclass
class Review:
    """Domain model representing a review."""

    title: str
    content: str
    category: str
    id: UUID = field(default_factory=uuid4)
    rating: Optional[int] = None
    source: Optional[str] = None
    author_id: Optional[UUID] = None
    summary_id: Optional[UUID] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Review:
        """Create a Review instance from a dictionary.

        Args:
            data: Dictionary containing review fields. UUID and datetime
                  values can be strings or native types.

        Returns:
            A new Review instance.
        """
        return cls(
            id=UUID(data["id"]) if isinstance(data.get("id"), str) else data.get("id", uuid4()),
            title=data["title"],
            content=data["content"],
            category=data["category"],
            rating=data.get("rating"),
            source=data.get("source"),
            author_id=(
                UUID(data["author_id"])
                if isinstance(data.get("author_id"), str)
                else data.get("author_id")
            ),
            summary_id=(
                UUID(data["summary_id"])
                if isinstance(data.get("summary_id"), str)
                else data.get("summary_id")
            ),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if isinstance(data.get("created_at"), str)
                else data.get("created_at", datetime.now())
            ),
            updated_at=(
                datetime.fromisoformat(data["updated_at"])
                if isinstance(data.get("updated_at"), str)
                else data.get("updated_at", datetime.now())
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the Review instance to a dictionary.

        Returns:
            Dictionary with all review fields, UUIDs and datetimes as strings.
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "content": self.content,
            "category": self.category,
            "rating": self.rating,
            "source": self.source,
            "author_id": str(self.author_id) if self.author_id else None,
            "summary_id": str(self.summary_id) if self.summary_id else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }
