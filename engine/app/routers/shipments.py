from datetime import datetime

from fastapi import APIRouter, Query

from ..db.client import get_db

router = APIRouter(prefix="/shipments", tags=["shipments"])

_DATE_FIELDS = ("predicted_eta", "actual_arrival", "sla_deadline", "created_at")


def _serialize(s: dict) -> dict:
    s["id"] = str(s.pop("_id"))
    for field in _DATE_FIELDS:
        if isinstance(s.get(field), datetime):
            s[field] = s[field].isoformat()
    return s


@router.get("", summary="List shipments, optionally filtered by status")
async def list_shipments(
    status: str | None = Query(None, pattern="^(in_transit|delayed|arrived)$"),
) -> list[dict]:
    db = get_db()
    filt: dict = {"status": status} if status else {}
    docs = await db.shipments.find(filt).to_list(None)
    return [_serialize(s) for s in docs]
