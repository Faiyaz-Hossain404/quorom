from ..qwen import complete
from .prompts import ANALYST_SYSTEM, format_context
from .schemas import DebateContext


async def run_analyst(ctx: DebateContext, tier: str = "flash") -> str:
    result = await complete(
        tier,
        [
            {"role": "system", "content": ANALYST_SYSTEM},
            {"role": "user", "content": format_context(ctx)},
        ],
        max_tokens=200,
    )
    return result["text"].strip()
