from pymongo import ASCENDING, GEOSPHERE

from .client import get_db


async def create_all_indexes() -> None:
    db = get_db()

    # Geospatial — 2dsphere required for $geoNear / $geoWithin queries
    await db.ports.create_index([("location", GEOSPHERE)], background=True)
    await db.disruptions.create_index([("location", GEOSPHERE)], background=True)
    await db.shipments.create_index([("current_position", GEOSPHERE)], background=True)

    # Query support
    await db.disruptions.create_index([("status", ASCENDING)], background=True)
    await db.disruptions.create_index([("type", ASCENDING)], background=True)
    await db.shipments.create_index([("status", ASCENDING)], background=True)
    await db.shipments.create_index(
        [("origin", ASCENDING), ("destination", ASCENDING)], background=True
    )
    await db.determinations.create_index(
        [("disruption_id", ASCENDING)], background=True
    )
    await db.determinations.create_index(
        [("shipment_id", ASCENDING)], background=True
    )
    await db.determinations.create_index(
        [("created_at", ASCENDING)], background=True
    )
