"""AI service for generating review summaries via OpenAI or Gemini."""

from __future__ import annotations

import json
import logging
from typing import Any, Dict, List

import httpx

from app.core.config import get_settings
from app.core.exceptions import AIServiceException
from app.dto.summary import SummaryCreate

logger = logging.getLogger(__name__)

# Shared system prompt used for both providers.
_SYSTEM_PROMPT = (
    "You are a professional review analyst. Analyze the given review and "
    "produce a structured JSON response with exactly these keys:\n"
    '  "summary": a concise 1-3 sentence summary of the review,\n'
    '  "sentiment": one of "positive", "negative", "neutral", or "mixed",\n'
    '  "sentiment_score": a float from -1.0 (most negative) to 1.0 (most positive),\n'
    '  "keywords": a list of up to 10 relevant keywords,\n'
    '  "pros": a list of identified advantages or positive points,\n'
    '  "cons": a list of identified disadvantages or negative points.\n'
    "Respond ONLY with valid JSON. Do not include markdown fences."
)

_USER_PROMPT_TEMPLATE = (
    "Analyze this review:\n"
    "Title: {title}\n"
    "Content: {content}\n\n"
    "Provide: 1) Brief summary 2) Sentiment (positive/negative/neutral/mixed) "
    "3) Sentiment score (-1.0 to 1.0) 4) Keywords 5) Pros 6) Cons\n\n"
    "Respond in JSON format."
)

_REQUEST_TIMEOUT = 30.0


class AIService:
    """Generates AI summaries using OpenAI or Gemini APIs."""

    def __init__(self) -> None:
        self.settings = get_settings()

    async def generate_summary(
        self,
        content: str,
        title: str = "",
    ) -> SummaryCreate:
        """Generate an AI summary for review content.

        Tries OpenAI first if an API key is configured, then falls back
        to Gemini.

        Args:
            content: The review body text.
            title: Optional review title for additional context.

        Returns:
            A ``SummaryCreate`` DTO ready to be persisted.

        Raises:
            AIServiceException: If no API key is configured or the
                                upstream API call fails.
        """
        if self.settings.openai_api_key:
            return await self._generate_with_openai(content, title)
        if self.settings.gemini_api_key:
            return await self._generate_with_gemini(content, title)
        raise AIServiceException("No AI API key configured")

    # ------------------------------------------------------------------
    # OpenAI
    # ------------------------------------------------------------------

    async def _generate_with_openai(
        self,
        content: str,
        title: str,
    ) -> SummaryCreate:
        """Call the OpenAI Chat Completions API.

        Args:
            content: Review body text.
            title: Review title.

        Returns:
            Parsed ``SummaryCreate`` from the model response.
        """
        user_prompt = _USER_PROMPT_TEMPLATE.format(title=title, content=content)

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.settings.openai_api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": "gpt-4o-mini",
                        "messages": [
                            {"role": "system", "content": _SYSTEM_PROMPT},
                            {"role": "user", "content": user_prompt},
                        ],
                        "response_format": {"type": "json_object"},
                        "temperature": 0.3,
                    },
                    timeout=_REQUEST_TIMEOUT,
                )
                response.raise_for_status()

            data = response.json()
            raw_text = data["choices"][0]["message"]["content"]
            parsed = self._parse_ai_response(raw_text)
            parsed["ai_model"] = "gpt-4o-mini"
            return SummaryCreate(**parsed)

        except httpx.HTTPStatusError as exc:
            logger.error("OpenAI API HTTP error: %s", exc)
            raise AIServiceException(
                f"OpenAI API error: {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            logger.error("OpenAI API request error: %s", exc)
            raise AIServiceException(
                "Failed to connect to OpenAI API"
            ) from exc
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            logger.error("Failed to parse OpenAI response: %s", exc)
            raise AIServiceException(
                "Failed to parse AI response"
            ) from exc

    # ------------------------------------------------------------------
    # Gemini
    # ------------------------------------------------------------------

    async def _generate_with_gemini(
        self,
        content: str,
        title: str,
    ) -> SummaryCreate:
        """Call the Google Gemini ``generateContent`` API.

        Args:
            content: Review body text.
            title: Review title.

        Returns:
            Parsed ``SummaryCreate`` from the model response.
        """
        user_prompt = _USER_PROMPT_TEMPLATE.format(title=title, content=content)
        full_prompt = f"{_SYSTEM_PROMPT}\n\n{user_prompt}"

        url = (
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-2.0-flash:generateContent"
            f"?key={self.settings.gemini_api_key}"
        )

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [
                            {"parts": [{"text": full_prompt}]},
                        ],
                        "generationConfig": {
                            "temperature": 0.3,
                            "responseMimeType": "application/json",
                        },
                    },
                    timeout=_REQUEST_TIMEOUT,
                )
                response.raise_for_status()

            data = response.json()
            raw_text = data["candidates"][0]["content"]["parts"][0]["text"]
            parsed = self._parse_ai_response(raw_text)
            parsed["ai_model"] = "gemini-2.0-flash"
            return SummaryCreate(**parsed)

        except httpx.HTTPStatusError as exc:
            logger.error("Gemini API HTTP error: %s", exc)
            raise AIServiceException(
                f"Gemini API error: {exc.response.status_code}"
            ) from exc
        except httpx.RequestError as exc:
            logger.error("Gemini API request error: %s", exc)
            raise AIServiceException(
                "Failed to connect to Gemini API"
            ) from exc
        except (KeyError, IndexError, json.JSONDecodeError) as exc:
            logger.error("Failed to parse Gemini response: %s", exc)
            raise AIServiceException(
                "Failed to parse AI response"
            ) from exc

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _parse_ai_response(raw_text: str) -> Dict[str, Any]:
        """Parse the raw JSON text returned by an AI model.

        Normalises keys and applies sensible defaults so that the result
        can be fed directly into ``SummaryCreate``.

        Args:
            raw_text: Raw JSON string from the AI model.

        Returns:
            A dictionary suitable for constructing a ``SummaryCreate``.

        Raises:
            json.JSONDecodeError: If ``raw_text`` is not valid JSON.
        """
        parsed: Dict[str, Any] = json.loads(raw_text)

        # Ensure required fields have sensible defaults.
        summary = parsed.get("summary", "")
        sentiment = parsed.get("sentiment", "neutral")
        sentiment_score = parsed.get("sentiment_score", 0.0)
        keywords: List[str] = parsed.get("keywords", [])
        pros: List[str] = parsed.get("pros", [])
        cons: List[str] = parsed.get("cons", [])

        # Clamp sentiment_score to valid range.
        sentiment_score = max(-1.0, min(1.0, float(sentiment_score)))

        # Normalise sentiment value.
        valid_sentiments = {"positive", "negative", "neutral", "mixed"}
        if sentiment not in valid_sentiments:
            sentiment = "neutral"

        return {
            "summary": summary,
            "sentiment": sentiment,
            "sentiment_score": sentiment_score,
            "keywords": keywords,
            "pros": pros,
            "cons": cons,
        }
