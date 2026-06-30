from fastapi import APIRouter

from ..db.client import get_db

router = APIRouter(prefix="/ports", tags=["ports"])


@router.get("", summary="All ports as GeoJSON FeatureCollection")
async def list_ports() -> dict:
    db = get_db()
    docs = await db.ports.find(
        {},
        {"_id": 1, "name": 1, "country": 1, "location": 1, "annual_teu": 1, "timezone": 1},
    ).to_list(None)
    return {
        "type": "FeatureCollection",
        "features": [
            {
                "type": "Feature",
                "geometry": p["location"],
                "properties": {
                    "id": p["_id"],
                    "name": p["name"],
                    "country": p["country"],
                    "timezone": p["timezone"],
                    "annual_teu": p["annual_teu"],
                },
            }
            for p in docs
        ],
    }
