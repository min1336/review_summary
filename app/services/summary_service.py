"""Business logic for summary management."""

from __future__ import annotations

from typing import Any
from uuid import UUID

from app.core.exceptions import NotFoundException
from app.dto.summary import SummaryCreate, SummaryResponse
from app.repositories.review_repo import ReviewRepository
from app.repositories.summary_repo import SummaryRepository


class SummaryService:
    """Application service encapsulating summary business rules."""

    def __init__(
        self,
        summary_repo: SummaryRepository,
        review_repo: ReviewRepository,
    ) -> None:
        self.summary_repo = summary_repo
        self.review_repo = review_repo

    def create_summary(self, data: SummaryCreate) -> SummaryResponse:
        """Persist a new AI-generated summary.

        Args:
            data: Validated summary creation payload.

        Returns:
            The newly created summary as a response DTO.
        """
        summary_data: dict[str, Any] = data.model_dump()
        result = self.summary_repo.create(summary_data)
        return SummaryResponse(**result)

    def get_summary(self, summary_id: UUID) -> SummaryResponse:
        """Retrieve a single summary by ID.

        Args:
            summary_id: UUID of the summary to retrieve.

        Returns:
            The matching summary as a response DTO.

        Raises:
            NotFoundException: If no summary with the given ID exists.
        """
        result = self.summary_repo.get_by_id(summary_id)
        if result is None:
            raise NotFoundException("Summary", str(summary_id))
        return SummaryResponse(**result)

    def link_summary_to_review(
        self,
        review_id: UUID,
        summary_id: UUID,
    ) -> None:
        """Associate an existing summary with a review.

        Updates the review's ``summary_id`` foreign key to point to the
        given summary.

        Args:
            review_id: UUID of the review to update.
            summary_id: UUID of the summary to link.

        Raises:
            NotFoundException: If either the review or the summary does
                               not exist.
        """
        review = self.review_repo.get_by_id(review_id)
        if review is None:
            raise NotFoundException("Review", str(review_id))

        summary = self.summary_repo.get_by_id(summary_id)
        if summary is None:
            raise NotFoundException("Summary", str(summary_id))

        self.review_repo.update(review_id, {"summary_id": str(summary_id)})
