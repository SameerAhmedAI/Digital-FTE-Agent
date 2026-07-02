# digital-fte-agent

A Python social-content agent that takes an input topic or announcement, analyzes it, decides the best platform and tone, then generates a platform-ready post using Gemini.

The agent uses the raw Gemini API rather than LangChain/CrewAI to keep the decision logic transparent and avoid unnecessary abstraction. The task listed raw API as an accepted approach.

## Architecture

```text
Python agent (src/agent.py)
  -> FastAPI backend (src/api.py, POST /generate)
  -> Next.js frontend (frontend/)
```

- `src/agent.py` owns the agent workflow: validate input -> analyze platform/tone -> generate post.
- `src/api.py` exposes the workflow over HTTP at `POST /generate`.
- `frontend/` calls the backend from a Next.js UI running at `http://localhost:3000`.

## Backend Setup

1. Clone the repo and enter the project:

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
   python -m venv venv
   source venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and add your `GEMINI_API_KEY`. A free key can be obtained at [aistudio.google.com](https://aistudio.google.com/).

   Windows:

   ```bat
   copy .env.example .env
   ```

   Mac/Linux:

   ```bash
   cp .env.example .env
   ```

5. Start the backend:

   ```bash
   uvicorn src.api:app --reload
   ```

## Frontend Setup

Open a separate terminal:

```bash
cd frontend
npm install
npm run dev -- --webpack
```

Turbopack is not supported on all platforms. You can also run:

```bash
npx next dev --webpack
```

Open [http://localhost:3000](http://localhost:3000).

## CLI Alternative

```bash
python main.py --text "Your topic here"
```

## Running Tests

```bash
python -m pytest tests/ -v
```

## Project Structure

```text
digital-fte-agent/
├── frontend/
│   ├── app/
│   │   ├── globals.css
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── eslint.config.mjs
│   ├── next-env.d.ts
│   ├── next.config.ts
│   ├── package.json
│   ├── postcss.config.mjs
│   ├── README.md
│   └── tsconfig.json
├── main.py
├── requirements.txt
├── README.md
├── .env.example
├── .gitignore
├── outputs/
│   └── history.json
├── src/
│   ├── agent.py
│   ├── api.py
│   └── config.py
└── tests/
    └── test_agent.py
```
