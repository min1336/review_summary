"""Business logic for review management."""

from __future__ import annotations

from typing import Optional
from uuid import UUID

from app.core.exceptions import AuthorizationException, NotFoundException
from app.dto.review import (
    ReviewCreate,
    ReviewListResponse,
    ReviewResponse,
)
from app.repositories.review_repo import ReviewRepository


class ReviewService:
    """Application service encapsulating review business rules."""

    def __init__(self, repo: ReviewRepository) -> None:
        self.repo = repo

    def create_review(
        self,
        data: ReviewCreate,
        author_id: Optional[UUID] = None,
    ) -> ReviewResponse:
        """Create a new review.

        Args:
            data: Validated review creation payload.
            author_id: Optional UUID of the authenticated author.

        Returns:
            The newly created review as a response DTO.
        """
        review_data = data.model_dump()
        if author_id:
            review_data["author_id"] = str(author_id)
        result = self.repo.create(review_data)
        return ReviewResponse(**result)

    def get_review(self, review_id: UUID) -> ReviewResponse:
        """Get a single review by ID.

        Args:
            review_id: UUID of the review to retrieve.

        Returns:
            The matching review as a response DTO.

        Raises:
            NotFoundException: If no review with the given ID exists.
        """
        result = self.repo.get_by_id(review_id)
        if result is None:
            raise NotFoundException("Review", str(review_id))
        return ReviewResponse(**result)

    def list_reviews(
        self,
        page: int = 1,
        per_page: int = 20,
        category: Optional[str] = None,
    ) -> ReviewListResponse:
        """List reviews with pagination and optional category filter.

        Args:
            page: 1-based page number.
            per_page: Number of items per page.
            category: Optional category to filter by.

        Returns:
            Paginated list of reviews.
        """
        if category:
            items, total = self.repo.get_by_category(
                category, page=page, per_page=per_page
            )
        else:
            items, total = self.repo.get_all(page=page, per_page=per_page)

        reviews = [ReviewResponse(**item) for item in items]
        return ReviewListResponse(
            items=reviews,
            total=total,
            page=page,
            per_page=per_page,
        )

    def update_review(
        self,
        review_id: UUID,
        data: dict,
        user_id: UUID,
    ) -> ReviewResponse:
        """Update an existing review. Only the author may update.

        Args:
            review_id: UUID of the review to update.
            data: Dictionary of fields to update.
            user_id: UUID of the requesting user.

        Returns:
            The updated review as a response DTO.

        Raises:
            NotFoundException: If the review does not exist.
            AuthorizationException: If the user is not the author.
        """
        existing = self.repo.get_by_id(review_id)
        if existing is None:
            raise NotFoundException("Review", str(review_id))

        if existing.get("author_id") != str(user_id):
            raise AuthorizationException(
                "You do not have permission to update this review"
            )

        result = self.repo.update(review_id, data)
        if result is None:
            raise NotFoundException("Review", str(review_id))
        return ReviewResponse(**result)

    def delete_review(self, review_id: UUID, user_id: UUID) -> bool:
        """Delete a review. Only the author may delete.

        Args:
            review_id: UUID of the review to delete.
            user_id: UUID of the requesting user.

        Returns:
            ``True`` if the review was successfully deleted.

        Raises:
            NotFoundException: If the review does not exist.
            AuthorizationException: If the user is not the author.
        """
        existing = self.repo.get_by_id(review_id)
        if existing is None:
            raise NotFoundException("Review", str(review_id))

        if existing.get("author_id") != str(user_id):
            raise AuthorizationException(
                "You do not have permission to delete this review"
            )

        return self.repo.delete(review_id)

    def search_reviews(
        self,
        query: str,
        page: int = 1,
        per_page: int = 20,
    ) -> ReviewListResponse:
        """Search reviews by title or content.

        Args:
            query: Search string (case-insensitive partial match).
            page: 1-based page number.
            per_page: Number of items per page.

        Returns:
            Paginated list of matching reviews.
        """
        items, total = self.repo.search(query, page=page, per_page=per_page)
        reviews = [ReviewResponse(**item) for item in items]
        return ReviewListResponse(
            items=reviews,
            total=total,
            page=page,
            per_page=per_page,
        )
