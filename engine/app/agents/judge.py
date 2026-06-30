import json
import re

from ..qwen import complete
from .prompts import JUDGE_SYSTEM, format_context
from .schemas import DebateContext, JudgeOutput


def _parse_json(raw: str) -> dict:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass
    cleaned = re.sub(r"```(?:json)?\s*", "", raw).strip().rstrip("`").strip()
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        pass
    m = re.search(r"\{[^{}]+\}", raw, re.DOTALL)
    if m:
        return json.loads(m.group())
    raise ValueError(f"Could not parse judge JSON from: {raw[:300]}")


async def run_judge(
    skeptic_argument: str,
    analyst_argument: str,
    ctx: DebateContext,
    tier: str = "flash",
) -> JudgeOutput:
    user_msg = (
        f"{format_context(ctx)}\n\n"
        f"SKEPTIC: {skeptic_argument}\n\n"
        f"ANALYST: {analyst_argument}"
    )
    result = await complete(
        tier,
        [
            {"role": "system", "content": JUDGE_SYSTEM},
            {"role": "user", "content": user_msg},
        ],
        max_tokens=128,
    )
    parsed = _parse_json(result["text"].strip())
    return JudgeOutput(
        is_material=bool(parsed["is_material"]),
        confidence=float(parsed["confidence"]),
        reasoning=str(parsed["reasoning"]),
    )
