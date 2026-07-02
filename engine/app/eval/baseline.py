"""Single-agent baseline: one qwen-flash call, no debate."""
from ..agents.judge import _parse_json
from ..agents.prompts import format_context
from ..agents.schemas import DebateContext, JudgeOutput
from ..qwen import complete

_SYSTEM = """\
You are a supply-chain risk analyst. Given a disruption and a shipment, determine
whether the disruption materially affects that shipment's delivery.
"Material" means the disruption is likely to cause an SLA breach or significant delay.
Respond ONLY with valid JSON — no markdown, no explanation:
{"is_material": <bool>, "confidence": <float 0.0–1.0>, "reasoning": "<one concise sentence>"}"""


async def run_baseline(ctx: DebateContext) -> JudgeOutput:
    result = await complete(
        "flash",
        [
            {"role": "system", "content": _SYSTEM},
            {"role": "user", "content": format_context(ctx)},
        ],
        max_tokens=128,
    )
    parsed = _parse_json(result["text"].strip())
    return JudgeOutput(
        is_material=bool(parsed["is_material"]),
        confidence=float(parsed["confidence"]),
        reasoning=str(parsed["reasoning"]),
    )
