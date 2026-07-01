# digital-fte-agent

Built with the raw Gemini API rather than LangChain/CrewAI to keep the agent's decision logic transparent and avoid unnecessary abstraction.

A minimal Python agent that analyzes social content intent, chooses a platform and tone, then generates a ready-to-post draft with `gemini-2.5-flash`.

## Getting Started

1. Clone the repo:

   ```bash
   git clone https://github.com/SameerAhmedAI/Digital-FTE-Agent.git
   cd Digital-FTE-Agent
   ```

2. Create and activate a virtual environment:

   Windows:

   ```bat
   python -m venv venv
   venv\Scripts\activate
   ```

   Mac/Linux:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your own `GEMINI_API_KEY`. A free key can be obtained at [aistudio.google.com](https://aistudio.google.com/).

   Windows:

   ```bat
   copy .env.example .env
   ```

   Mac/Linux:

   ```bash
   cp .env.example .env
   ```

5. Run via CLI:

   ```bash
   python main.py --text "Your topic here"
   ```

6. Run via UI:

   ```bash
   streamlit run app.py
   ```

   Streamlit opens automatically in your browser at `localhost:8501`.

## What "agent" means here

In this project, an agent is a small workflow with explicit decision steps: analyze → generate. It is not just one direct API call. The agent first validates the input, asks Gemini to classify the best platform and tone, then uses that decision to generate a platform-appropriate post.

## Sample Output

```text
Platform: LinkedIn
Tone: professional
Post:
We just launched an AI assistant built for small teams that want to turn meeting notes into useful social content faster.

Instead of starting from a blank page, teams can capture the key ideas from a meeting and transform them into clear, publish-ready posts.

If your team is trying to stay visible without adding more manual content work, this is exactly the kind of workflow we built it for.
```

Each successful CLI run is appended to `outputs/history.json` with a UTC timestamp.

## Project Structure

```text
digital-fte-agent/
├── app.py
├── main.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── .streamlit/
│   └── config.toml
├── outputs/
│   └── history.json
├── src/
│   ├── agent.py
│   └── config.py
└── tests/
    └── test_agent.py
```
