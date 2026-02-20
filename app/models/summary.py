"""Summary domain model."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any
from uuid import UUID, uuid4


@dataclass
class Summary:
    """Domain model representing an AI-generated review summary."""

    summary: str
    sentiment: str
    sentiment_score: float
    id: UUID = field(default_factory=uuid4)
    keywords: list[str] = field(default_factory=list)
    pros: list[str] = field(default_factory=list)
    cons: list[str] = field(default_factory=list)
    ai_model: str | None = None
    created_at: datetime = field(default_factory=datetime.now)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Summary:
        """Create a Summary instance from a dictionary.

        Args:
            data: Dictionary containing summary fields. UUID and datetime
                  values can be strings or native types.

        Returns:
            A new Summary instance.
        """
        return cls(
            id=UUID(data["id"]) if isinstance(data.get("id"), str) else data.get("id", uuid4()),
            summary=data["summary"],
            sentiment=data["sentiment"],
            sentiment_score=float(data["sentiment_score"]),
            keywords=data.get("keywords", []),
            pros=data.get("pros", []),
            cons=data.get("cons", []),
            ai_model=data.get("ai_model"),
            created_at=(
                datetime.fromisoformat(data["created_at"])
                if isinstance(data.get("created_at"), str)
                else data.get("created_at", datetime.now())
            ),
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert the Summary instance to a dictionary.

        Returns:
            Dictionary with all summary fields, UUIDs and datetimes as strings.
        """
        return {
            "id": str(self.id),
            "summary": self.summary,
            "sentiment": self.sentiment,
            "sentiment_score": self.sentiment_score,
            "keywords": self.keywords,
            "pros": self.pros,
            "cons": self.cons,
            "ai_model": self.ai_model,
            "created_at": self.created_at.isoformat(),
        }
