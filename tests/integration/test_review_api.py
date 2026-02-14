"""Integration tests for the Review Summary Platform API."""

from __future__ import annotations

import uuid

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


class TestHealthAndPages:
    """Tests for basic health checks and page rendering."""

    def test_root_page_returns_200(self) -> None:
        """The landing page should return HTTP 200."""
        response = client.get("/")
        assert response.status_code == 200
        assert "ReviewSummary" in response.text

    def test_reviews_page_returns_200(self) -> None:
        """The reviews list page should return HTTP 200."""
        response = client.get("/reviews")
        assert response.status_code == 200

    def test_reviews_new_page_returns_200(self) -> None:
        """The create-review page should return HTTP 200."""
        response = client.get("/reviews/new")
        assert response.status_code == 200

    def test_analytics_page_returns_200(self) -> None:
        """The analytics dashboard page should return HTTP 200."""
        response = client.get("/analytics")
        assert response.status_code == 200


class TestReviewsAPI:
    """Tests for the /api/v1/reviews endpoints."""

    def test_list_reviews_returns_200(self) -> None:
        """GET /api/v1/reviews should return 200 with a list structure."""
        response = client.get("/api/v1/reviews")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "per_page" in data
        assert isinstance(data["items"], list)

    def test_list_reviews_with_pagination(self) -> None:
        """GET /api/v1/reviews should accept pagination query params."""
        response = client.get("/api/v1/reviews?page=1&per_page=5")
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 5

    def test_list_reviews_with_category_filter(self) -> None:
        """GET /api/v1/reviews should accept a category filter."""
        response = client.get("/api/v1/reviews?category=product")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data["items"], list)

    def test_create_review_unauthenticated(self) -> None:
        """POST /api/v1/reviews without auth should return 401."""
        payload = {
            "title": "Test Review",
            "content": "This is a test review content.",
            "category": "product",
            "rating": 4,
        }
        response = client.post("/api/v1/reviews", json=payload)
        assert response.status_code == 401

    def test_create_review_missing_auth_header(self) -> None:
        """POST /api/v1/reviews with no Authorization header should return 401."""
        payload = {
            "title": "Test Review",
            "content": "Test content",
            "category": "book",
        }
        response = client.post("/api/v1/reviews", json=payload)
        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_create_review_invalid_token(self) -> None:
        """POST /api/v1/reviews with an invalid token should return 401."""
        payload = {
            "title": "Test Review",
            "content": "Test content",
            "category": "book",
        }
        response = client.post(
            "/api/v1/reviews",
            json=payload,
            headers={"Authorization": "Bearer invalid-token-value"},
        )
        assert response.status_code == 401

    def test_get_nonexistent_review(self) -> None:
        """GET /api/v1/reviews/<nonexistent-uuid> should return 404."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/reviews/{fake_id}")
        assert response.status_code == 404

    def test_get_review_invalid_uuid(self) -> None:
        """GET /api/v1/reviews/not-a-uuid should return 422."""
        response = client.get("/api/v1/reviews/not-a-uuid")
        assert response.status_code == 422

    def test_delete_review_unauthenticated(self) -> None:
        """DELETE /api/v1/reviews/<id> without auth should return 401."""
        fake_id = str(uuid.uuid4())
        response = client.delete(f"/api/v1/reviews/{fake_id}")
        assert response.status_code == 401

    def test_summarize_review_unauthenticated(self) -> None:
        """POST /api/v1/reviews/<id>/summarize without auth should return 401."""
        fake_id = str(uuid.uuid4())
        response = client.post(f"/api/v1/reviews/{fake_id}/summarize")
        assert response.status_code == 401


class TestSummariesAPI:
    """Tests for the /api/v1/summaries endpoints."""

    def test_get_nonexistent_summary(self) -> None:
        """GET /api/v1/summaries/<nonexistent-uuid> should return 404."""
        fake_id = str(uuid.uuid4())
        response = client.get(f"/api/v1/summaries/{fake_id}")
        assert response.status_code == 404

    def test_list_summaries_returns_200(self) -> None:
        """GET /api/v1/summaries should return 200 with a list."""
        response = client.get("/api/v1/summaries")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)


class TestAuthAPI:
    """Tests for the /api/v1/auth endpoints."""

    def test_login_missing_fields(self) -> None:
        """POST /api/v1/auth/login with missing fields should return 422."""
        response = client.post("/api/v1/auth/login", json={})
        assert response.status_code == 422

    def test_signup_missing_fields(self) -> None:
        """POST /api/v1/auth/signup with missing fields should return 422."""
        response = client.post("/api/v1/auth/signup", json={})
        assert response.status_code == 422

    def test_signup_short_password(self) -> None:
        """POST /api/v1/auth/signup with a short password should return 422."""
        response = client.post(
            "/api/v1/auth/signup",
            json={"email": "test@example.com", "password": "short"},
        )
        assert response.status_code == 422

    def test_get_me_unauthenticated(self) -> None:
        """GET /api/v1/auth/me without auth should return 401."""
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401

    def test_logout_unauthenticated(self) -> None:
        """POST /api/v1/auth/logout without auth should return 401."""
        response = client.post("/api/v1/auth/logout")
        assert response.status_code == 401


class TestAnalyticsAPI:
    """Tests for the /api/v1/analytics endpoints."""

    def test_analytics_overview_returns_200(self) -> None:
        """GET /api/v1/analytics/overview should return 200."""
        response = client.get("/api/v1/analytics/overview")
        assert response.status_code == 200
        data = response.json()
        assert "sentiment_stats" in data
        assert "category_stats" in data
        assert "total_reviews" in data
