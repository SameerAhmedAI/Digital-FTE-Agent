# digital-fte-agent

Built with the raw OpenAI API rather than LangChain/CrewAI to keep the agent's decision logic transparent and avoid unnecessary abstraction — the task listed raw API as an accepted approach.

A minimal Python agent that analyzes social content intent, chooses a platform and tone, then generates a ready-to-post draft.

## What "agent" means here

In this project, an agent is a small workflow with explicit decision steps: analyze → generate. It is not just one direct API call. The agent first validates the input, asks OpenAI to classify the best platform and tone, then uses that decision to generate a platform-appropriate post.

## Setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy `.env.example` to `.env`.
4. Add your OpenAI API key:

   ```env
   OPENAI_API_KEY=
   ```

## Usage

Run with a text flag:

```bash
python main.py --text "We just launched an AI assistant that helps small teams repurpose meeting notes into social posts."
```

Or run interactively:

```bash
python main.py
```

Sample output:

```text
Platform: LinkedIn
Tone: professional
Post:
We just launched an AI assistant built for small teams that want to turn meeting notes into useful social content faster.

Instead of starting from a blank page, teams can capture the key ideas from a meeting and transform them into clear, publish-ready posts.

If your team is trying to stay visible without adding more manual content work, this is exactly the kind of workflow we built it for.
```

Each successful run is appended to `outputs/history.json` with a UTC timestamp.

## Project Structure

```text
digital-fte-agent/
├── main.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── outputs/
│   └── history.json
├── src/
│   ├── agent.py
│   └── config.py
└── tests/
    └── test_agent.py
```
