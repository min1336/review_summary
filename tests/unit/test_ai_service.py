"""Unit tests for AIService with mocked httpx and settings."""

from __future__ import annotations

import json
from typing import Any, Dict
from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from app.core.exceptions import AIServiceException
from app.dto.summary import SummaryCreate
from app.services.ai_service import AIService


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ai_response_payload() -> Dict[str, Any]:
    """Return a well-formed AI JSON payload."""
    return {
        "summary": "An excellent product with minor flaws.",
        "sentiment": "positive",
        "sentiment_score": 0.85,
        "keywords": ["quality", "value", "design"],
        "pros": ["Great build quality", "Good price"],
        "cons": ["Slightly heavy"],
    }


def _openai_chat_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Wrap *payload* in an OpenAI Chat Completions response structure."""
    return {
        "choices": [
            {
                "message": {
                    "content": json.dumps(payload),
                },
            },
        ],
    }


def _gemini_generate_response(payload: Dict[str, Any]) -> Dict[str, Any]:
    """Wrap *payload* in a Gemini generateContent response structure."""
    return {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": json.dumps(payload)},
                    ],
                },
            },
        ],
    }


def _mock_httpx_response(
    status_code: int = 200,
    json_data: Any = None,
) -> MagicMock:
    """Create a mock ``httpx.Response``."""
    resp = MagicMock(spec=httpx.Response)
    resp.status_code = status_code
    resp.json.return_value = json_data or {}
    if status_code >= 400:
        resp.raise_for_status.side_effect = httpx.HTTPStatusError(
            message="error",
            request=MagicMock(spec=httpx.Request),
            response=resp,
        )
    else:
        resp.raise_for_status.return_value = None
    return resp


# ---------------------------------------------------------------------------
# Tests - OpenAI
# ---------------------------------------------------------------------------

class TestGenerateSummaryOpenAI:
    """Tests for AIService._generate_with_openai (via generate_summary)."""

    @pytest.mark.asyncio
    async def test_generate_summary_openai_success(self) -> None:
        """generate_summary should return a SummaryCreate on success."""
        payload = _ai_response_payload()
        mock_response = _mock_httpx_response(
            json_data=_openai_chat_response(payload),
        )

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.ai_service.get_settings") as mock_settings, \
             patch("app.services.ai_service.httpx.AsyncClient", return_value=mock_client):
            settings = MagicMock()
            settings.openai_api_key = "sk-test-key"
            settings.gemini_api_key = ""
            mock_settings.return_value = settings

            service = AIService()
            result = await service.generate_summary(
                content="This product is amazing!",
                title="Great Product",
            )

        assert isinstance(result, SummaryCreate)
        assert result.summary == "An excellent product with minor flaws."
        assert result.sentiment == "positive"
        assert result.sentiment_score == 0.85
        assert result.ai_model == "gpt-4o-mini"
        assert "quality" in result.keywords

    @pytest.mark.asyncio
    async def test_generate_summary_openai_api_error(self) -> None:
        """generate_summary should raise AIServiceException on HTTP errors."""
        mock_response = _mock_httpx_response(status_code=500)

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.ai_service.get_settings") as mock_settings, \
             patch("app.services.ai_service.httpx.AsyncClient", return_value=mock_client):
            settings = MagicMock()
            settings.openai_api_key = "sk-test-key"
            settings.gemini_api_key = ""
            mock_settings.return_value = settings

            service = AIService()

            with pytest.raises(AIServiceException) as exc_info:
                await service.generate_summary(
                    content="Some review",
                    title="Title",
                )

            assert "OpenAI API error" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Tests - Gemini
# ---------------------------------------------------------------------------

class TestGenerateSummaryGemini:
    """Tests for AIService._generate_with_gemini (via generate_summary)."""

    @pytest.mark.asyncio
    async def test_generate_summary_gemini_success(self) -> None:
        """generate_summary should fall back to Gemini when no OpenAI key."""
        payload = _ai_response_payload()
        mock_response = _mock_httpx_response(
            json_data=_gemini_generate_response(payload),
        )

        mock_client = AsyncMock(spec=httpx.AsyncClient)
        mock_client.post.return_value = mock_response
        mock_client.__aenter__ = AsyncMock(return_value=mock_client)
        mock_client.__aexit__ = AsyncMock(return_value=False)

        with patch("app.services.ai_service.get_settings") as mock_settings, \
             patch("app.services.ai_service.httpx.AsyncClient", return_value=mock_client):
            settings = MagicMock()
            settings.openai_api_key = ""
            settings.gemini_api_key = "gemini-test-key"
            mock_settings.return_value = settings

            service = AIService()
            result = await service.generate_summary(
                content="A wonderful restaurant experience.",
                title="Best Restaurant",
            )

        assert isinstance(result, SummaryCreate)
        assert result.sentiment == "positive"
        assert result.ai_model == "gemini-2.0-flash"


# ---------------------------------------------------------------------------
# Tests - No API key
# ---------------------------------------------------------------------------

class TestGenerateSummaryNoKey:
    """Tests for AIService when no API key is configured."""

    @pytest.mark.asyncio
    async def test_generate_summary_no_api_key(self) -> None:
        """generate_summary should raise AIServiceException with no keys."""
        with patch("app.services.ai_service.get_settings") as mock_settings:
            settings = MagicMock()
            settings.openai_api_key = ""
            settings.gemini_api_key = ""
            mock_settings.return_value = settings

            service = AIService()

            with pytest.raises(AIServiceException) as exc_info:
                await service.generate_summary(
                    content="Some content",
                    title="Title",
                )

            assert "No AI API key configured" in str(exc_info.value)


# ---------------------------------------------------------------------------
# Tests - JSON parsing
# ---------------------------------------------------------------------------

class TestParseAIResponse:
    """Tests for AIService._parse_ai_response."""

    def test_parse_valid_json(self) -> None:
        """_parse_ai_response should correctly parse well-formed JSON."""
        payload = _ai_response_payload()
        result = AIService._parse_ai_response(json.dumps(payload))

        assert result["summary"] == payload["summary"]
        assert result["sentiment"] == "positive"
        assert result["sentiment_score"] == 0.85
        assert result["keywords"] == payload["keywords"]

    def test_parse_clamps_score(self) -> None:
        """_parse_ai_response should clamp sentiment_score to [-1.0, 1.0]."""
        payload = _ai_response_payload()
        payload["sentiment_score"] = 5.0
        result = AIService._parse_ai_response(json.dumps(payload))
        assert result["sentiment_score"] == 1.0

        payload["sentiment_score"] = -3.0
        result = AIService._parse_ai_response(json.dumps(payload))
        assert result["sentiment_score"] == -1.0

    def test_parse_normalises_invalid_sentiment(self) -> None:
        """_parse_ai_response should default to 'neutral' for unknown sentiments."""
        payload = _ai_response_payload()
        payload["sentiment"] = "happy"
        result = AIService._parse_ai_response(json.dumps(payload))
        assert result["sentiment"] == "neutral"

    def test_parse_invalid_json_raises(self) -> None:
        """_parse_ai_response should raise on invalid JSON."""
        with pytest.raises(json.JSONDecodeError):
            AIService._parse_ai_response("not valid json {{{")

    def test_parse_missing_fields_uses_defaults(self) -> None:
        """_parse_ai_response should fill in defaults for missing keys."""
        result = AIService._parse_ai_response("{}")
        assert result["summary"] == ""
        assert result["sentiment"] == "neutral"
        assert result["sentiment_score"] == 0.0
        assert result["keywords"] == []
        assert result["pros"] == []
        assert result["cons"] == []
