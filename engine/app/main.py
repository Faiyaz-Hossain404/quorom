"""Quorum engine — FastAPI app.

Day 1 surface: liveness + the Qwen cascade smoke test. The society, ingestion,
exposure mapping, SSE stream and eval harness land on Days 2–4.
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import qwen
from .config import settings

app = FastAPI(title="Quorum Engine", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=list({settings.web_origin, "http://localhost:3000"}),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root() -> dict:
    return {"name": "Quorum Engine", "version": "0.1.0", "status": "ok"}


@app.get("/health")
async def health() -> dict:
    return {
        "status": "ok",
        "qwen_key_configured": bool(settings.dashscope_api_key),
        "mongodb_configured": bool(settings.mongodb_uri),
    }


@app.get("/llm/test")
async def llm_test(
    tier: str = Query("flash", pattern="^(flash|max)$"),
    prompt: str = "Reply with exactly: Quorum online.",
) -> dict:
    """Smoke-test one cascade tier end-to-end."""
    if not settings.dashscope_api_key:
        raise HTTPException(
            status_code=503,
            detail="DASHSCOPE_API_KEY not configured — see docs/DEPLOY.md.",
        )
    try:
        return await qwen.complete(
            tier, [{"role": "user", "content": prompt}], max_tokens=64
        )
    except Exception as exc:  # surface the real cause to the caller
        raise HTTPException(
            status_code=502, detail=f"Qwen call failed: {type(exc).__name__}: {exc}"
        )
