"""Quorum engine — FastAPI app."""
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from . import qwen
from .config import settings
from .db.client import close_client
from .db.indexes import create_all_indexes
from .routers import disruptions, ports, shipments


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all_indexes()
    yield
    await close_client()


app = FastAPI(title="Quorum Engine", version="0.1.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=list({settings.web_origin, "http://localhost:3000"}),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ports.router)
app.include_router(disruptions.router)
app.include_router(shipments.router)


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
    except Exception as exc:
        raise HTTPException(
            status_code=502, detail=f"Qwen call failed: {type(exc).__name__}: {exc}"
        )
