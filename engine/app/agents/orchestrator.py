"""Coordinates the Skeptic → Analyst → Judge cascade and streams events."""

from datetime import datetime, timezone
from typing import AsyncGenerator

from bson import ObjectId
from bson.errors import InvalidId

from ..db.client import get_db
from .analyst import run_analyst
from .judge import run_judge
from .schemas import DebateContext
from .skeptic import run_skeptic

CONFIDENCE_THRESHOLD = 0.75


def _prep_disruption(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    if isinstance(doc.get("created_at"), datetime):
        doc["created_at"] = doc["created_at"].isoformat()
    return doc


def _prep_shipment(doc: dict) -> dict:
    doc["id"] = str(doc.pop("_id"))
    for field in ("predicted_eta", "actual_arrival", "sla_deadline", "created_at"):
        if isinstance(doc.get(field), datetime):
            doc[field] = doc[field].isoformat()
    return doc


async def orchestrate(
    disruption_id: str, shipment_id: str
) -> AsyncGenerator[dict, None]:
    db = get_db()

    try:
        d_oid = ObjectId(disruption_id)
        s_oid = ObjectId(shipment_id)
    except InvalidId as exc:
        yield {"phase": "error", "message": f"Invalid ID: {exc}"}
        return

    d_doc = await db.disruptions.find_one({"_id": d_oid})
    s_doc = await db.shipments.find_one({"_id": s_oid})

    if not d_doc or not s_doc:
        yield {"phase": "error", "message": "Disruption or shipment not found"}
        return

    ctx = DebateContext(
        disruption_id=disruption_id,
        shipment_id=shipment_id,
        disruption=_prep_disruption(d_doc),
        shipment=_prep_shipment(s_doc),
    )

    # ── Skeptic ──────────────────────────────────────────────────────
    yield {"phase": "skeptic", "status": "running"}
    skeptic_text = await run_skeptic(ctx, "flash")
    yield {"phase": "skeptic", "status": "done", "text": skeptic_text}

    # ── Analyst ──────────────────────────────────────────────────────
    yield {"phase": "analyst", "status": "running"}
    analyst_text = await run_analyst(ctx, "flash")
    yield {"phase": "analyst", "status": "done", "text": analyst_text}

    # ── Judge (flash first) ──────────────────────────────────────────
    yield {"phase": "judge", "status": "running", "tier": "flash"}
    judge_out = await run_judge(skeptic_text, analyst_text, ctx, "flash")
    tier_used = "flash"

    if judge_out.confidence < CONFIDENCE_THRESHOLD:
        yield {
            "phase": "escalating",
            "reason": "low_confidence",
            "confidence": round(judge_out.confidence, 3),
            "threshold": CONFIDENCE_THRESHOLD,
        }
        yield {"phase": "judge", "status": "running", "tier": "max"}
        judge_out = await run_judge(skeptic_text, analyst_text, ctx, "max")
        tier_used = "max"

    yield {
        "phase": "judge",
        "status": "done",
        "tier": tier_used,
        "is_material": judge_out.is_material,
        "confidence": round(judge_out.confidence, 3),
        "reasoning": judge_out.reasoning,
    }

    # ── Persist ──────────────────────────────────────────────────────
    doc = {
        "disruption_id": disruption_id,
        "shipment_id": shipment_id,
        "is_material": judge_out.is_material,
        "confidence": round(judge_out.confidence, 3),
        "tier_used": tier_used,
        "skeptic_argument": skeptic_text,
        "analyst_argument": analyst_text,
        "judge_reasoning": judge_out.reasoning,
        "created_at": datetime.now(timezone.utc),
    }
    result = await db.determinations.insert_one(doc)

    yield {
        "phase": "complete",
        "determination_id": str(result.inserted_id),
        "is_material": judge_out.is_material,
        "confidence": round(judge_out.confidence, 3),
        "tier_used": tier_used,
        "skeptic_argument": skeptic_text,
        "analyst_argument": analyst_text,
        "judge_reasoning": judge_out.reasoning,
    }
