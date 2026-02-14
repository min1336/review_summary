import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock, patch

from app.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def mock_supabase():
    """Mock Supabase client for unit tests."""
    mock = MagicMock()
    # Setup common mock returns
    mock.table.return_value = mock
    mock.select.return_value = mock
    mock.insert.return_value = mock
    mock.delete.return_value = mock
    mock.eq.return_value = mock
    mock.execute.return_value = MagicMock(data=[], count=0)
    return mock


@pytest.fixture
def sample_review_data():
    """Sample review data for testing."""
    return {
        "title": "Great Product Review",
        "content": "This product exceeded my expectations in every way.",
        "category": "product",
        "rating": 5,
        "source": "https://example.com/review"
    }


@pytest.fixture
def sample_summary_data():
    """Sample summary data for testing."""
    return {
        "summary": "Overall positive review highlighting product quality.",
        "sentiment": "positive",
        "sentiment_score": 0.85,
        "keywords": ["quality", "excellent", "recommended"],
        "pros": ["Great build quality", "Good value"],
        "cons": ["Slightly expensive"],
        "ai_model": "gpt-4"
    }
