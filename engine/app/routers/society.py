import json
from datetime import datetime
from typing import AsyncGenerator

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from ..agents.orchestrator import orchestrate
from ..db.client import get_db

router = APIRouter(prefix="/society", tags=["society"])


def _serialize(d: dict) -> dict:
    d["id"] = str(d.pop("_id"))
    if isinstance(d.get("created_at"), datetime):
        d["created_at"] = d["created_at"].isoformat()
    return d


async def _event_stream(
    disruption_id: str, shipment_id: str
) -> AsyncGenerator[str, None]:
    try:
        async for event in orchestrate(disruption_id, shipment_id):
            yield f"data: {json.dumps(event)}\n\n"
    except Exception as exc:
        yield f"data: {json.dumps({'phase': 'error', 'message': str(exc)})}\n\n"
    yield "data: [DONE]\n\n"


@router.get("/stream", summary="SSE stream of agent-society debate")
async def stream_society(
    disruption_id: str = Query(...),
    shipment_id: str = Query(...),
) -> StreamingResponse:
    if not disruption_id or not shipment_id:
        raise HTTPException(status_code=400, detail="disruption_id and shipment_id required")
    return StreamingResponse(
        _event_stream(disruption_id, shipment_id),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/determinations", summary="List stored determinations")
async def list_determinations(
    disruption_id: str | None = Query(None),
    shipment_id: str | None = Query(None),
) -> list[dict]:
    db = get_db()
    filt: dict = {}
    if disruption_id:
        filt["disruption_id"] = disruption_id
    if shipment_id:
        filt["shipment_id"] = shipment_id
    docs = await db.determinations.find(filt).sort("created_at", -1).to_list(None)
    return [_serialize(d) for d in docs]
