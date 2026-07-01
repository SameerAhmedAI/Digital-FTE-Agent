"""Command-line interface for the social content agent."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from src.agent import SocialContentAgent, SocialContentAgentError


HISTORY_PATH = Path(__file__).parent / "outputs" / "history.json"


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate a platform-ready social media post.")
    parser.add_argument("--text", help="Source text to turn into a social media post.")
    return parser.parse_args()


def append_history(result: dict[str, Any], history_path: Path = HISTORY_PATH) -> None:
    """Append a successful agent run to the JSON history file."""
    history_path.parent.mkdir(parents=True, exist_ok=True)

    if history_path.exists():
        with history_path.open("r", encoding="utf-8") as file:
            history = json.load(file)
    else:
        history = []

    history.append(
        {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "result": result,
        }
    )

    with history_path.open("w", encoding="utf-8") as file:
        json.dump(history, file, indent=2)
        file.write("\n")


def print_result(result: dict[str, Any]) -> None:
    """Print the generated social content result."""
    analysis = result["analysis"]
    print(f"Platform: {analysis['platform']}")
    print(f"Tone: {analysis['tone']}")
    print("Post:")
    print(result["post"])


def main() -> int:
    """Run the CLI application."""
    args = parse_args()
    text = args.text if args.text is not None else input("Enter text: ")

    try:
        result = SocialContentAgent().run(text)
    except (ValueError, SocialContentAgentError) as exc:
        print(f"Error: {exc}")
        return 1

    print_result(result)
    append_history(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
