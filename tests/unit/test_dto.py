"""Unit tests for DTO validation."""

from datetime import datetime
from uuid import uuid4

import pytest
from pydantic import ValidationError

from app.dto.analytics import AnalyticsResponse, CategoryStats, SentimentStats
from app.dto.review import ReviewCreate, ReviewListResponse, ReviewResponse
from app.dto.summary import SummaryCreate
from app.dto.user import UserCreate


class TestReviewCreate:
    """Tests for ReviewCreate DTO validation."""

    def test_valid_review_create(self) -> None:
        """ReviewCreate accepts valid data with all fields."""
        review = ReviewCreate(
            title="Great Product",
            content="This product exceeded my expectations.",
            category="product",
            rating=5,
            source="https://example.com/review/1",
        )
        assert review.title == "Great Product"
        assert review.content == "This product exceeded my expectations."
        assert review.category == "product"
        assert review.rating == 5
        assert review.source == "https://example.com/review/1"

    def test_valid_review_create_minimal(self) -> None:
        """ReviewCreate accepts valid data with only required fields."""
        review = ReviewCreate(
            title="Good Book",
            content="A must-read for everyone.",
            category="book",
        )
        assert review.title == "Good Book"
        assert review.category == "book"
        assert review.rating is None
        assert review.source is None

    def test_invalid_category(self) -> None:
        """ReviewCreate rejects invalid category values."""
        with pytest.raises(ValidationError) as exc_info:
            ReviewCreate(
                title="Test",
                content="Test content",
                category="invalid_category",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("category",) for e in errors)

    def test_title_too_long(self) -> None:
        """ReviewCreate rejects titles exceeding 200 characters."""
        with pytest.raises(ValidationError) as exc_info:
            ReviewCreate(
                title="A" * 201,
                content="Test content",
                category="product",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("title",) for e in errors)

    def test_rating_out_of_range_low(self) -> None:
        """ReviewCreate rejects ratings below 1."""
        with pytest.raises(ValidationError) as exc_info:
            ReviewCreate(
                title="Test",
                content="Test content",
                category="product",
                rating=0,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("rating",) for e in errors)

    def test_rating_out_of_range_high(self) -> None:
        """ReviewCreate rejects ratings above 5."""
        with pytest.raises(ValidationError) as exc_info:
            ReviewCreate(
                title="Test",
                content="Test content",
                category="product",
                rating=6,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("rating",) for e in errors)


class TestSummaryCreate:
    """Tests for SummaryCreate DTO validation."""

    def test_valid_summary_create(self) -> None:
        """SummaryCreate accepts valid data with all fields."""
        summary = SummaryCreate(
            summary="This is a well-crafted product with minor flaws.",
            sentiment="positive",
            sentiment_score=0.85,
            keywords=["quality", "durable", "affordable"],
            pros=["Good build quality", "Affordable price"],
            cons=["Limited color options"],
            ai_model="gpt-4",
        )
        assert summary.summary == "This is a well-crafted product with minor flaws."
        assert summary.sentiment == "positive"
        assert summary.sentiment_score == 0.85
        assert summary.keywords == ["quality", "durable", "affordable"]
        assert summary.pros == ["Good build quality", "Affordable price"]
        assert summary.cons == ["Limited color options"]
        assert summary.ai_model == "gpt-4"

    def test_valid_summary_create_minimal(self) -> None:
        """SummaryCreate accepts valid data with only required fields."""
        summary = SummaryCreate(
            summary="Neutral review overall.",
            sentiment="neutral",
            sentiment_score=0.0,
        )
        assert summary.keywords == []
        assert summary.pros == []
        assert summary.cons == []
        assert summary.ai_model is None

    def test_sentiment_score_too_low(self) -> None:
        """SummaryCreate rejects sentiment_score below -1.0."""
        with pytest.raises(ValidationError) as exc_info:
            SummaryCreate(
                summary="Bad product.",
                sentiment="negative",
                sentiment_score=-1.5,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("sentiment_score",) for e in errors)

    def test_sentiment_score_too_high(self) -> None:
        """SummaryCreate rejects sentiment_score above 1.0."""
        with pytest.raises(ValidationError) as exc_info:
            SummaryCreate(
                summary="Great product.",
                sentiment="positive",
                sentiment_score=1.5,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("sentiment_score",) for e in errors)

    def test_invalid_sentiment_value(self) -> None:
        """SummaryCreate rejects invalid sentiment literals."""
        with pytest.raises(ValidationError) as exc_info:
            SummaryCreate(
                summary="Some review.",
                sentiment="very_positive",
                sentiment_score=0.5,
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("sentiment",) for e in errors)


class TestUserCreate:
    """Tests for UserCreate DTO validation."""

    def test_valid_user_create(self) -> None:
        """UserCreate accepts valid email and password."""
        user = UserCreate(
            email="user@example.com",
            password="securepassword123",
        )
        assert user.email == "user@example.com"
        assert user.password == "securepassword123"

    def test_short_password(self) -> None:
        """UserCreate rejects passwords shorter than 8 characters."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="user@example.com",
                password="short",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("password",) for e in errors)

    def test_invalid_email(self) -> None:
        """UserCreate rejects invalid email addresses."""
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(
                email="not-an-email",
                password="securepassword123",
            )
        errors = exc_info.value.errors()
        assert any(e["loc"] == ("email",) for e in errors)


class TestReviewListResponse:
    """Tests for ReviewListResponse DTO."""

    def test_valid_review_list_response(self) -> None:
        """ReviewListResponse accepts a valid paginated response."""
        now = datetime.now()
        review_id = uuid4()

        review_data = ReviewResponse(
            id=review_id,
            title="Test Review",
            content="Test content here.",
            category="movie",
            rating=4,
            source=None,
            author_id=None,
            summary_id=None,
            created_at=now,
            updated_at=now,
        )

        response = ReviewListResponse(
            items=[review_data],
            total=1,
            page=1,
            per_page=10,
        )
        assert len(response.items) == 1
        assert response.total == 1
        assert response.page == 1
        assert response.per_page == 10
        assert response.items[0].id == review_id
        assert response.items[0].title == "Test Review"

    def test_empty_review_list_response(self) -> None:
        """ReviewListResponse accepts an empty items list."""
        response = ReviewListResponse(
            items=[],
            total=0,
            page=1,
            per_page=10,
        )
        assert len(response.items) == 0
        assert response.total == 0


class TestAnalyticsDTOs:
    """Tests for analytics DTOs."""

    def test_valid_analytics_response(self) -> None:
        """AnalyticsResponse accepts valid analytics data."""
        response = AnalyticsResponse(
            sentiment_stats=SentimentStats(
                positive=10,
                negative=3,
                neutral=5,
                mixed=2,
                total=20,
            ),
            category_stats=[
                CategoryStats(category="product", count=8, avg_rating=4.2),
                CategoryStats(category="book", count=12, avg_rating=3.8),
            ],
            total_reviews=20,
            avg_rating=4.0,
        )
        assert response.sentiment_stats.positive == 10
        assert response.sentiment_stats.total == 20
        assert len(response.category_stats) == 2
        assert response.total_reviews == 20
        assert response.avg_rating == 4.0

    def test_analytics_response_no_rating(self) -> None:
        """AnalyticsResponse accepts null avg_rating."""
        response = AnalyticsResponse(
            sentiment_stats=SentimentStats(
                positive=0, negative=0, neutral=0, mixed=0, total=0
            ),
            category_stats=[],
            total_reviews=0,
            avg_rating=None,
        )
        assert response.avg_rating is None
        assert response.total_reviews == 0
