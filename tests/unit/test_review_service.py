"""Unit tests for ReviewService with mocked repository."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Dict
from unittest.mock import MagicMock
from uuid import UUID, uuid4

import pytest

from app.core.exceptions import AuthorizationException, NotFoundException
from app.dto.review import ReviewCreate, ReviewListResponse, ReviewResponse
from app.repositories.review_repo import ReviewRepository
from app.services.review_service import ReviewService


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_review_dict(
    review_id: UUID,
    author_id: UUID,
    **overrides: Any,
) -> Dict[str, Any]:
    """Build a review record dictionary matching the Supabase row shape."""
    now = datetime.utcnow().isoformat()
    base: Dict[str, Any] = {
        "id": str(review_id),
        "title": "Great Product",
        "content": "This product is amazing and works perfectly.",
        "category": "product",
        "rating": 5,
        "source": "https://example.com",
        "author_id": str(author_id),
        "summary_id": None,
        "created_at": now,
        "updated_at": now,
    }
    base.update(overrides)
    return base


@pytest.fixture
def mock_repo() -> MagicMock:
    """Return a mocked ReviewRepository."""
    return MagicMock(spec=ReviewRepository)


@pytest.fixture
def service(mock_repo: MagicMock) -> ReviewService:
    """Return a ReviewService wired to the mocked repo."""
    return ReviewService(repo=mock_repo)


@pytest.fixture
def review_id() -> UUID:
    return uuid4()


@pytest.fixture
def author_id() -> UUID:
    return uuid4()


# ---------------------------------------------------------------------------
# create_review
# ---------------------------------------------------------------------------

class TestCreateReview:
    """Tests for ReviewService.create_review."""

    def test_create_review_returns_response(
        self,
        service: ReviewService,
        mock_repo: MagicMock,
        author_id: UUID,
    ) -> None:
        """create_review should persist the data and return a ReviewResponse."""
        review_id = uuid4()
        mock_repo.create.return_value = _make_review_dict(review_id, author_id)

        dto = ReviewCreate(
            title="Great Product",
            content="This product is amazing and works perfectly.",
            category="product",
            rating=5,
            source="https://example.com",
        )

        result = service.create_review(dto, author_id=author_id)

        assert isinstance(result, ReviewResponse)
        assert result.id == review_id
        assert result.title == "Great Product"
        assert result.author_id == author_id
        mock_repo.create.assert_called_once()

    def test_create_review_without_author(
        self,
        service: ReviewService,
        mock_repo: MagicMock,
    ) -> None:
        """create_review should work without an author_id."""
        review_id = uuid4()
        record = _make_review_dict(review_id, uuid4(), author_id=None)
        mock_repo.create.return_value = record

        dto = ReviewCreate(
            title="Anonymous Review",
            content="Some review content.",
            category="other",
        )

        result = service.create_review(dto)

        assert isinstance(result, ReviewResponse)
        assert result.author_id is None


# ---------------------------------------------------------------------------
# get_review
# ---------------------------------------------------------------------------

class TestGetReview:
    """Tests for ReviewService.get_review."""

    def test_get_review_found(
        self,
        service: ReviewService,
        mock_repo: MagicMock,
        review_id: UUID,
        author_id: UUID,
    ) -> None:
        """get_review should return a ReviewResponse when the record exists."""
        mock_repo.get_by_id.return_value = _make_review_dict(review_id, author_id)

        result = service.get_review(review_id)

        assert isinstance(result, ReviewResponse)
        assert result.id == review_id
        mock_repo.get_by_id.assert_called_once_with(review_id)

    def test_get_review_not_found(
        self,
        service: ReviewService,
        mock_repo: MagicMock,
        review_id: UUID,
    ) -> None:
        """get_review should raise NotFoundException when the record is missing."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException) as exc_info:
            service.get_review(review_id)

        assert "Review" in str(exc_info.value)
        assert str(review_id) in str(exc_info.value)


# ---------------------------------------------------------------------------
# list_reviews
# ---------------------------------------------------------------------------

class TestListReviews:
    """Tests for ReviewService.list_reviews."""

    def test_list_reviews_no_filter(
        self,
        service: ReviewService,
        mock_repo: MagicMock,
        author_id: UUID,
    ) -> None:
        """list_reviews without category should call get_all."""
        records = [_make_review_dict(uuid4(), author_id) for _ in range(3)]
        mock_repo.get_all.return_value = (records, 3)

        result = service.list_reviews(page=1, per_page=20)

        assert isinstance(result, ReviewListResponse)
        assert len(result.items) == 3
        assert result.total == 3
        assert result.page == 1
        assert result.per_page == 20
        mock_repo.get_all.assert_called_once_with(page=1, per_page=20)

    def test_list_reviews_with_category(
        self,
        service: ReviewService,
        mock_repo: MagicMock,
        author_id: UUID,
    ) -> None:
        """list_reviews with category should call get_by_category."""
        records = [_make_review_dict(uuid4(), author_id, category="book")]
        mock_repo.get_by_category.return_value = (records, 1)

        result = service.list_reviews(page=1, per_page=10, category="book")

        assert result.total == 1
        mock_repo.get_by_category.assert_called_once_with(
            "book", page=1, per_page=10
        )

    def test_list_reviews_empty(
        self,
        service: ReviewService,
        mock_repo: MagicMock,
    ) -> None:
        """list_reviews should return an empty list when no records exist."""
        mock_repo.get_all.return_value = ([], 0)

        result = service.list_reviews()

        assert result.items == []
        assert result.total == 0


# ---------------------------------------------------------------------------
# delete_review
# ---------------------------------------------------------------------------

class TestDeleteReview:
    """Tests for ReviewService.delete_review."""

    def test_delete_review_by_author(
        self,
        service: ReviewService,
        mock_repo: MagicMock,
        review_id: UUID,
        author_id: UUID,
    ) -> None:
        """delete_review should succeed when the requester is the author."""
        mock_repo.get_by_id.return_value = _make_review_dict(review_id, author_id)
        mock_repo.delete.return_value = True

        result = service.delete_review(review_id, user_id=author_id)

        assert result is True
        mock_repo.delete.assert_called_once_with(review_id)

    def test_delete_review_not_author(
        self,
        service: ReviewService,
        mock_repo: MagicMock,
        review_id: UUID,
        author_id: UUID,
    ) -> None:
        """delete_review should raise AuthorizationException for non-authors."""
        mock_repo.get_by_id.return_value = _make_review_dict(review_id, author_id)
        other_user = uuid4()

        with pytest.raises(AuthorizationException):
            service.delete_review(review_id, user_id=other_user)

        mock_repo.delete.assert_not_called()

    def test_delete_review_not_found(
        self,
        service: ReviewService,
        mock_repo: MagicMock,
        review_id: UUID,
        author_id: UUID,
    ) -> None:
        """delete_review should raise NotFoundException for missing reviews."""
        mock_repo.get_by_id.return_value = None

        with pytest.raises(NotFoundException):
            service.delete_review(review_id, user_id=author_id)
