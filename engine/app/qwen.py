"""Qwen client over the Model Studio OpenAI-compatible endpoint.

Two tiers back the confidence-gated cascade:
  - "flash" (qwen-flash): fast/cheap first-pass triage
  - "max"   (qwen-max):   deep escalation for low-confidence / high-stakes calls
"""

import time
from typing import Any

from openai import AsyncOpenAI

from .config import settings

_client: AsyncOpenAI | None = None


def get_client() -> AsyncOpenAI:
    if not settings.dashscope_api_key:
        raise RuntimeError(
            "DASHSCOPE_API_KEY is not set — add it to .env or the environment."
        )
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.dashscope_base_url,
        )
    return _client


def _model_for(tier: str) -> str:
    return settings.qwen_model_max if tier == "max" else settings.qwen_model_flash


async def complete(tier: str, messages: list[dict[str, Any]], **kwargs: Any) -> dict[str, Any]:
    """Run a chat completion and return text + usage + latency."""
    model = _model_for(tier)
    client = get_client()
    started = time.perf_counter()
    resp = await client.chat.completions.create(model=model, messages=messages, **kwargs)
    latency_ms = round((time.perf_counter() - started) * 1000)
    usage = resp.usage
    return {
        "tier": tier,
        "model": model,
        "text": resp.choices[0].message.content,
        "latency_ms": latency_ms,
        "usage": {
            "prompt_tokens": getattr(usage, "prompt_tokens", None),
            "completion_tokens": getattr(usage, "completion_tokens", None),
            "total_tokens": getattr(usage, "total_tokens", None),
        },
    }
