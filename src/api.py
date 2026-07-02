"""FastAPI backend for the social content agent."""

from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from .agent import (
    AgentAuthenticationError,
    AgentConfigurationError,
    AgentRateLimitError,
    AgentTimeoutError,
    SocialContentAgent,
    SocialContentAgentError,
)


app = FastAPI(title="Digital FTE Agent API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    """Request body for post generation."""

    text: str


class GenerateResponse(BaseModel):
    """Response body for generated social content."""

    platform: str
    tone: str
    post: str


@app.post("/generate", response_model=GenerateResponse)
def generate_post(request: GenerateRequest) -> GenerateResponse:
    """Generate a platform-aware social post from input text."""
    try:
        result = SocialContentAgent().run(request.text)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail={"error": str(exc)}) from exc
    except AgentConfigurationError as exc:
        raise HTTPException(status_code=500, detail={"error": str(exc)}) from exc
    except AgentAuthenticationError as exc:
        raise HTTPException(status_code=401, detail={"error": str(exc)}) from exc
    except AgentRateLimitError as exc:
        raise HTTPException(status_code=429, detail={"error": str(exc)}) from exc
    except AgentTimeoutError as exc:
        raise HTTPException(status_code=504, detail={"error": str(exc)}) from exc
    except SocialContentAgentError as exc:
        raise HTTPException(status_code=502, detail={"error": str(exc)}) from exc

    analysis = result["analysis"]
    return GenerateResponse(
        platform=analysis["platform"],
        tone=analysis["tone"],
        post=result["post"],
    )
