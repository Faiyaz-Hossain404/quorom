"""Evaluation harness: society vs single-agent baseline on historical shipments."""
from datetime import datetime, timezone
from typing import Any

from bson import ObjectId

from ..agents.orchestrator import _prep_disruption, _prep_shipment, orchestrate
from ..agents.schemas import DebateContext
from ..db.client import get_db
from .baseline import run_baseline
from .ground_truth import compute_ground_truth


async def run_eval() -> dict[str, Any]:
    db = get_db()

    arrived = await db.shipments.find(
        {"status": "arrived", "actual_arrival": {"$ne": None}}
    ).to_list(length=None)

    all_disruptions = await db.disruptions.find({}).to_list(length=None)

    cases: list[dict[str, Any]] = []

    for ship in arrived:
        ground_truth = compute_ground_truth(ship)
        ship_id = str(ship["_id"])

        relevant = [
            d for d in all_disruptions
            if ship["origin"] in d.get("affected_ports", [])
            or ship["destination"] in d.get("affected_ports", [])
        ]

        for dis in relevant:
            dis_id = str(dis["_id"])

            # Build DebateContext for the baseline (copies — _prep_* mutate in place)
            dis_copy = _prep_disruption(dict(dis))
            ship_copy = _prep_shipment(dict(ship))
            ctx = DebateContext(
                disruption_id=dis_id,
                shipment_id=ship_id,
                disruption=dis_copy,
                shipment=ship_copy,
            )

            case: dict[str, Any] = {
                "shipment_id": ship_id,
                "disruption_id": dis_id,
                "vessel_name": ship["vessel_name"],
                "disruption_title": dis.get("title", ""),
                "ground_truth_material": ground_truth,
                "baseline_is_material": None,
                "baseline_confidence": None,
                "baseline_correct": None,
                "society_is_material": None,
                "society_confidence": None,
                "society_tier_used": None,
                "society_correct": None,
                "determination_id": None,
                "error": None,
            }

            # ── Baseline (single-agent, no debate) ──────────────────────────
            try:
                b = await run_baseline(ctx)
                case["baseline_is_material"] = b.is_material
                case["baseline_confidence"] = round(b.confidence, 3)
                case["baseline_correct"] = (b.is_material == ground_truth)
            except Exception as exc:
                case["error"] = f"baseline: {exc}"

            # ── Society (full Skeptic → Analyst → Judge cascade) ─────────────
            try:
                async for event in orchestrate(dis_id, ship_id):
                    if event.get("phase") == "complete":
                        case["determination_id"] = event.get("determination_id")
                        case["society_is_material"] = event["is_material"]
                        case["society_confidence"] = event["confidence"]
                        case["society_tier_used"] = event["tier_used"]
                        case["society_correct"] = (event["is_material"] == ground_truth)
            except Exception as exc:
                existing = case.get("error") or ""
                case["error"] = (existing + f" society: {exc}").strip()

            # ── Stamp determination with ground-truth fields ─────────────────
            if case["determination_id"]:
                try:
                    await db.determinations.update_one(
                        {"_id": ObjectId(case["determination_id"])},
                        {
                            "$set": {
                                "ground_truth_material": ground_truth,
                                "eval_correct": case["society_correct"],
                            }
                        },
                    )
                except Exception:
                    pass

            cases.append(case)

    valid = [
        c for c in cases
        if c["society_correct"] is not None and c["baseline_correct"] is not None
    ]
    total = len(valid)
    soc_n = sum(1 for c in valid if c["society_correct"])
    base_n = sum(1 for c in valid if c["baseline_correct"])
    soc_acc = round(soc_n / total, 3) if total else 0.0
    base_acc = round(base_n / total, 3) if total else 0.0

    summary = {
        "total_cases": total,
        "society_correct": soc_n,
        "baseline_correct": base_n,
        "society_accuracy": soc_acc,
        "baseline_accuracy": base_acc,
        "society_beats_baseline": soc_acc >= base_acc,
    }

    run_doc = {
        "created_at": datetime.now(timezone.utc),
        "summary": summary,
        "cases": cases,
    }
    result = await db.eval_runs.insert_one(run_doc)

    return {
        "run_id": str(result.inserted_id),
        "created_at": run_doc["created_at"].isoformat(),
        "summary": summary,
        "cases": cases,
    }
