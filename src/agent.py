"""Social content agent built on the raw OpenAI SDK."""

from __future__ import annotations

import json
from typing import Any

from openai import APIConnectionError, APIError, APITimeoutError, AuthenticationError, OpenAI
from openai import RateLimitError as OpenAIRateLimitError

try:
    from .config import OPENAI_API_KEY
except ImportError:  # pragma: no cover - supports running this file outside a package.
    from config import OPENAI_API_KEY


class SocialContentAgentError(Exception):
    """Base exception for SocialContentAgent failures."""


class AgentConfigurationError(SocialContentAgentError):
    """Raised when required agent configuration is missing or invalid."""


class AgentRateLimitError(SocialContentAgentError):
    """Raised when the OpenAI API rate limit is reached."""


class AgentTimeoutError(SocialContentAgentError):
    """Raised when an OpenAI API request times out."""


class AgentAuthenticationError(SocialContentAgentError):
    """Raised when the OpenAI API key is invalid or unauthorized."""


class AgentAPIError(SocialContentAgentError):
    """Raised when the OpenAI API request fails for another reason."""


class SocialContentAgent:
    """Create platform-specific social posts from a source idea or draft."""

    VALID_PLATFORMS = {"LinkedIn", "Twitter", "Instagram"}
    VALID_TONES = {"professional", "casual", "promotional"}

    def __init__(self, api_key: str | None = OPENAI_API_KEY, model: str = "gpt-4o-mini") -> None:
        """Initialize the agent with an OpenAI API key and model name.

        Args:
            api_key: OpenAI API key. Defaults to the key loaded from the environment.
            model: OpenAI model used for analysis and generation.

        Raises:
            AgentConfigurationError: If no API key is provided.
        """
        if not isinstance(api_key, str) or not api_key.strip():
            raise AgentConfigurationError("OPENAI_API_KEY is required to use SocialContentAgent.")

        self.model = model
        self.client = OpenAI(api_key=api_key)

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
            SocialContentAgentError: If the OpenAI API request fails.
        """
        prompt = (
            "Classify the best social platform and tone for this content. "
            "Return only JSON with keys platform and tone. "
            "platform must be one of LinkedIn, Twitter, Instagram. "
            "tone must be one of professional, casual, promotional.\n\n"
            f"Content:\n{text}"
        )
        content = self._chat_completion(
            system_message="You are a concise social media strategy assistant.",
            user_message=prompt,
            response_format={"type": "json_object"},
        )

        try:
            result = json.loads(content)
        except json.JSONDecodeError as exc:
            raise AgentAPIError("OpenAI returned an invalid analysis response.") from exc

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
            SocialContentAgentError: If the OpenAI API request fails.
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
        return self._chat_completion(
            system_message="You write clear, platform-aware social media content.",
            user_message=prompt,
        )

    def run(self, text: str) -> dict[str, str | dict[str, str]]:
        """Validate, analyze, and generate a social post from input text.

        Args:
            text: Source idea, draft, or instruction to turn into a social post.

        Returns:
            A structured result containing input, analysis, and generated post.

        Raises:
            ValueError: If input, platform, or tone validation fails.
            SocialContentAgentError: If configuration or OpenAI API calls fail.
        """
        validated_text = self.take_input(text)
        analysis = self.analyze(validated_text)
        post = self.generate(validated_text, analysis["platform"], analysis["tone"])

        return {
            "input": validated_text,
            "analysis": analysis,
            "post": post,
        }

    def _chat_completion(
        self,
        system_message: str,
        user_message: str,
        response_format: dict[str, str] | None = None,
    ) -> str:
        """Call OpenAI chat completions and normalize known API failures."""
        request: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message},
            ],
        }
        if response_format is not None:
            request["response_format"] = response_format

        try:
            response = self.client.chat.completions.create(**request)
        except AuthenticationError as exc:
            raise AgentAuthenticationError("OpenAI API key is invalid or unauthorized.") from exc
        except OpenAIRateLimitError as exc:
            raise AgentRateLimitError("OpenAI API rate limit reached. Try again later.") from exc
        except APITimeoutError as exc:
            raise AgentTimeoutError("OpenAI API request timed out. Try again later.") from exc
        except APIConnectionError as exc:
            raise AgentAPIError("Could not connect to the OpenAI API.") from exc
        except APIError as exc:
            raise AgentAPIError("OpenAI API request failed.") from exc

        content = response.choices[0].message.content
        if not content:
            raise AgentAPIError("OpenAI returned an empty response.")

        return content.strip()
