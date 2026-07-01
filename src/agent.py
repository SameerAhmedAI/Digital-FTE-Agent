"""Social content agent built on the raw Gemini API."""

from __future__ import annotations

import json
import re
from typing import Any

from google import genai

try:
    from .config import GEMINI_API_KEY
except ImportError:  # pragma: no cover - supports running this file outside a package.
    from config import GEMINI_API_KEY


class SocialContentAgentError(Exception):
    """Base exception for SocialContentAgent failures."""


class AgentConfigurationError(SocialContentAgentError):
    """Raised when required agent configuration is missing or invalid."""


class AgentRateLimitError(SocialContentAgentError):
    """Raised when the Gemini API rate limit is reached."""


class AgentTimeoutError(SocialContentAgentError):
    """Raised when a Gemini API request times out."""


class AgentAuthenticationError(SocialContentAgentError):
    """Raised when the Gemini API key is invalid or unauthorized."""


class AgentAPIError(SocialContentAgentError):
    """Raised when the Gemini API request fails for another reason."""


class SocialContentAgent:
    """Create platform-specific social posts from a source idea or draft."""

    VALID_PLATFORMS = {"LinkedIn", "Twitter", "Instagram"}
    VALID_TONES = {"professional", "casual", "promotional"}

    def __init__(self, api_key: str | None = GEMINI_API_KEY, model: str = "gemini-2.5-flash") -> None:
        """Initialize the agent with a Gemini API key and model name.

        Args:
            api_key: Gemini API key. Defaults to the key loaded from the environment.
            model: Gemini model used for analysis and generation.

        Raises:
            AgentConfigurationError: If no API key is provided.
        """
        if not isinstance(api_key, str) or not api_key.strip():
            raise AgentConfigurationError("GEMINI_API_KEY is required to use SocialContentAgent.")

        self.model = model
        self.client = genai.Client(api_key=api_key)

    def take_input(self, text: str) -> str:
        """Validate and normalize input text.

        Args:
            text: Source idea, draft, or instruction to turn into a social post.

        Returns:
            The stripped input text.

        Raises:
            ValueError: If text is not a string or is empty after stripping.
        """
        if not isinstance(text, str):
            raise ValueError("Input must be a string.")

        normalized_text = text.strip()
        if not normalized_text:
            raise ValueError("Input text cannot be empty.")

        return normalized_text

    def analyze(self, text: str) -> dict[str, str]:
        """Classify the best social platform and tone for the input text.

        Args:
            text: Validated source text to analyze.

        Returns:
            A dictionary with platform and tone keys.

        Raises:
            ValueError: If the model returns an unsupported platform or tone.
            SocialContentAgentError: If the Gemini API request fails.
        """
        prompt = (
            "Classify the best social platform and tone for this content. "
            "Return only JSON with keys platform and tone. "
            "platform must be one of LinkedIn, Twitter, Instagram. "
            "tone must be one of professional, casual, promotional.\n\n"
            f"Content:\n{text}"
        )
        content = self._generate_content(
            system_instruction="You are a concise social media strategy assistant.",
            prompt=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "object",
                    "properties": {
                        "platform": {
                            "type": "string",
                            "enum": ["LinkedIn", "Twitter", "Instagram"],
                        },
                        "tone": {
                            "type": "string",
                            "enum": ["professional", "casual", "promotional"],
                        },
                    },
                    "required": ["platform", "tone"],
                },
            },
        )
        normalized_content = self._strip_markdown_code_fence(content)

        try:
            result = json.loads(normalized_content)
        except json.JSONDecodeError as exc:
            print(f"Raw Gemini analysis response: {content}")
            raise AgentAPIError("Gemini returned an invalid analysis response.") from exc

        platform = result.get("platform")
        tone = result.get("tone")
        if platform not in self.VALID_PLATFORMS:
            raise ValueError(f"Unsupported platform returned by analysis: {platform!r}.")
        if tone not in self.VALID_TONES:
            raise ValueError(f"Unsupported tone returned by analysis: {tone!r}.")

        return {"platform": platform, "tone": tone}

    def generate(self, text: str, platform: str, tone: str) -> str:
        """Generate a platform-appropriate social post.

        Args:
            text: Validated source text to transform into a post.
            platform: Target platform: LinkedIn, Twitter, or Instagram.
            tone: Target tone: professional, casual, or promotional.

        Returns:
            The generated social post.

        Raises:
            ValueError: If platform or tone is unsupported.
            SocialContentAgentError: If the Gemini API request fails.
        """
        if platform not in self.VALID_PLATFORMS:
            raise ValueError(f"Unsupported platform: {platform!r}.")
        if tone not in self.VALID_TONES:
            raise ValueError(f"Unsupported tone: {tone!r}.")

        prompt = (
            f"Write a {tone} social media post for {platform}. "
            "Make it appropriate for the platform and ready to publish. "
            "Return only the post text.\n\n"
            f"Source content:\n{text}"
        )
        return self._generate_content(
            system_instruction="You write clear, platform-aware social media content.",
            prompt=prompt,
        )

    def run(self, text: str) -> dict[str, str | dict[str, str]]:
        """Validate, analyze, and generate a social post from input text.

        Args:
            text: Source idea, draft, or instruction to turn into a social post.

        Returns:
            A structured result containing input, analysis, and generated post.

        Raises:
            ValueError: If input, platform, or tone validation fails.
            SocialContentAgentError: If configuration or Gemini API calls fail.
        """
        validated_text = self.take_input(text)
        analysis = self.analyze(validated_text)
        post = self.generate(validated_text, analysis["platform"], analysis["tone"])

        return {
            "input": validated_text,
            "analysis": analysis,
            "post": post,
        }

    def _generate_content(
        self,
        system_instruction: str,
        prompt: str,
        config: dict[str, Any] | None = None,
    ) -> str:
        """Call Gemini and normalize known API failures."""
        request_config: dict[str, Any] = {"system_instruction": system_instruction}
        if config is not None:
            request_config.update(config)

        try:
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=request_config,
            )
        except Exception as exc:
            self._raise_agent_error(exc)

        content = self._extract_response_text(response)
        if not content:
            raise AgentAPIError("Gemini returned an empty response.")

        return content.strip()

    def _extract_response_text(self, response: Any) -> str:
        """Extract text from a Gemini SDK response object."""
        content = getattr(response, "text", None)
        if isinstance(content, str):
            return content
        return ""

    def _strip_markdown_code_fence(self, text: str) -> str:
        """Remove optional markdown code fences around JSON text."""
        stripped = text.strip()
        fenced_match = re.fullmatch(
            r"```(?:json)?\s*(.*?)\s*```",
            stripped,
            flags=re.DOTALL | re.IGNORECASE,
        )
        if fenced_match:
            return fenced_match.group(1).strip()
        return stripped

    def _raise_agent_error(self, exc: Exception) -> None:
        """Convert Gemini SDK exceptions into project-level exceptions."""
        status_code = getattr(exc, "status_code", None) or getattr(exc, "code", None)
        message = str(exc).lower()

        if isinstance(exc, TimeoutError) or "timeout" in message:
            raise AgentTimeoutError("Gemini API request timed out. Try again later.") from exc
        if status_code in {401, 403} or "api key" in message or "unauthorized" in message:
            raise AgentAuthenticationError("Gemini API key is invalid or unauthorized.") from exc
        if status_code == 429 or "rate limit" in message or "quota" in message:
            raise AgentRateLimitError("Gemini API rate limit reached. Try again later.") from exc

        raise AgentAPIError("Gemini API request failed.") from exc
