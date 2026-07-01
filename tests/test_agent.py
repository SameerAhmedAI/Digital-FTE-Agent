"""Tests for the social content agent."""

import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import AgentAPIError, SocialContentAgent


def make_response(content: str) -> SimpleNamespace:
    """Create a minimal mocked Gemini response."""
    return SimpleNamespace(text=content)


def test_successful_run_mocks_gemini_calls() -> None:
    agent = SocialContentAgent(api_key="test-key")
    agent.client = Mock()
    agent.client.models.generate_content.side_effect = [
        make_response('```json\n{"platform": "LinkedIn", "tone": "professional"}\n```'),
        make_response("Launch announcement post."),
    ]

    result = agent.run("We launched a new AI workflow tool.")

    assert result == {
        "input": "We launched a new AI workflow tool.",
        "analysis": {"platform": "LinkedIn", "tone": "professional"},
        "post": "Launch announcement post.",
    }
    assert agent.client.models.generate_content.call_count == 2
    first_call = agent.client.models.generate_content.call_args_list[0]
    assert first_call.kwargs["model"] == "gemini-2.5-flash"
    assert first_call.kwargs["config"]["response_mime_type"] == "application/json"
    assert first_call.kwargs["config"]["response_schema"]["required"] == ["platform", "tone"]


def test_api_failure_is_wrapped() -> None:
    agent = SocialContentAgent(api_key="test-key")
    agent.client = Mock()
    agent.client.models.generate_content.side_effect = RuntimeError("SDK failure")

    with pytest.raises(AgentAPIError, match="Gemini API request failed"):
        agent.analyze("Draft a post about our product update.")


def test_invalid_input_rejected_before_api_call() -> None:
    agent = SocialContentAgent(api_key="test-key")
    agent.client = Mock()

    with pytest.raises(ValueError, match="Input text cannot be empty"):
        agent.run("   ")

    agent.client.models.generate_content.assert_not_called()


@pytest.mark.parametrize("invalid_input", [None, 123, []])
def test_non_string_input_rejected(invalid_input: object) -> None:
    agent = SocialContentAgent(api_key="test-key")

    with pytest.raises(ValueError, match="Input must be a string"):
        agent.take_input(invalid_input)  # type: ignore[arg-type]
