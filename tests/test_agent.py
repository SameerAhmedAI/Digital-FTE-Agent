import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from openai import APIError

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.agent import AgentAPIError, SocialContentAgent


def make_response(content: str) -> SimpleNamespace:
    return SimpleNamespace(
        choices=[SimpleNamespace(message=SimpleNamespace(content=content))]
    )


def test_successful_run_mocks_openai_calls() -> None:
    agent = SocialContentAgent(api_key="test-key")
    agent.client = Mock()
    agent.client.chat.completions.create.side_effect = [
        make_response('{"platform": "LinkedIn", "tone": "professional"}'),
        make_response("Launch announcement post."),
    ]

    result = agent.run("We launched a new AI workflow tool.")

    assert result == {
        "input": "We launched a new AI workflow tool.",
        "analysis": {"platform": "LinkedIn", "tone": "professional"},
        "post": "Launch announcement post.",
    }
    assert agent.client.chat.completions.create.call_count == 2


def test_api_failure_is_wrapped() -> None:
    agent = SocialContentAgent(api_key="test-key")
    agent.client = Mock()
    sdk_error = APIError("SDK failure", request=Mock(), body=None)
    agent.client.chat.completions.create.side_effect = sdk_error

    with pytest.raises(AgentAPIError, match="OpenAI API request failed"):
        agent.analyze("Draft a post about our product update.")


def test_invalid_input_rejected_before_api_call() -> None:
    agent = SocialContentAgent(api_key="test-key")
    agent.client = Mock()

    with pytest.raises(ValueError, match="Input text cannot be empty"):
        agent.run("   ")

    agent.client.chat.completions.create.assert_not_called()


@pytest.mark.parametrize("invalid_input", [None, 123, []])
def test_non_string_input_rejected(invalid_input: object) -> None:
    agent = SocialContentAgent(api_key="test-key")

    with pytest.raises(ValueError, match="Input must be a string"):
        agent.take_input(invalid_input)  # type: ignore[arg-type]
