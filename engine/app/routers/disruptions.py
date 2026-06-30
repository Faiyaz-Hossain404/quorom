from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from ..db.client import get_db
from ..db.models import GeoPoint

router = APIRouter(prefix="/disruptions", tags=["disruptions"])


class DisruptionCreate(BaseModel):
    type: Literal["port_closure", "vessel_delay", "storm", "strike", "tariff"]
    title: str
    description: str
    location: GeoPoint
    affected_ports: list[str]
    severity: int = Field(..., ge=1, le=5)
    radius_km: float = Field(..., gt=0)
    status: Literal["open", "resolved"] = "open"


def _serialize(d: dict) -> dict:
    d["id"] = str(d.pop("_id"))
    if isinstance(d.get("created_at"), datetime):
        d["created_at"] = d["created_at"].isoformat()
    return d


@router.get("", summary="List disruptions, optionally filtered by status")
async def list_disruptions(
    status: str | None = Query(None, pattern="^(open|resolved)$"),
) -> list[dict]:
    db = get_db()
    filt: dict = {"status": status} if status else {}
    docs = await db.disruptions.find(filt).to_list(None)
    return [_serialize(d) for d in docs]


@router.post("", status_code=201, summary="Ingest a new disruption signal")
async def create_disruption(payload: DisruptionCreate) -> dict:
    db = get_db()
    doc = payload.model_dump()
    doc["created_at"] = datetime.now(timezone.utc)
    result = await db.disruptions.insert_one(doc)
    doc["id"] = str(result.inserted_id)
    doc.pop("_id", None)
    doc["created_at"] = doc["created_at"].isoformat()
    return doc
