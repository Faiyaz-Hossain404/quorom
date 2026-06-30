#!/usr/bin/env python3
"""Seed MongoDB Atlas with ports, disruptions, and shipments.

Run from the quorum/ root:
    python -m engine.scripts.seed
or:
    python engine/scripts/seed.py

Idempotent — ports are upserted by LOCODE; disruptions and shipments are
cleared and re-inserted on every run so demo state is always predictable.
"""
import asyncio
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Load .env from the quorum root (parent of engine/)
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

try:
    from motor.motor_asyncio import AsyncIOMotorClient
    from pymongo import ASCENDING, GEOSPHERE
except ImportError:
    sys.exit("Run: pip install motor pymongo dnspython")

MONGODB_URI = os.getenv("MONGODB_URI", "")
MONGODB_DB = os.getenv("MONGODB_DB", "quorum")

if not MONGODB_URI:
    sys.exit("FAIL: MONGODB_URI not set in .env")


def now_utc() -> datetime:
    return datetime.now(timezone.utc)


def pt(days: int = 0, hours: int = 0) -> datetime:
    """now + timedelta"""
    return now_utc() + timedelta(days=days, hours=hours)


def mt(days: int = 0, hours: int = 0) -> datetime:
    """now - timedelta (past)"""
    return now_utc() - timedelta(days=days, hours=hours)


# ── Ports (20 major commercial ports) ──────────────────────────────────────────
# Coordinates are [longitude, latitude] — GeoJSON order.

PORTS = [
    {
        "_id": "SGSIN",
        "name": "Port of Singapore",
        "country": "SG",
        "location": {"type": "Point", "coordinates": [103.8198, 1.3521]},
        "timezone": "Asia/Singapore",
        "annual_teu": 3740,
    },
    {
        "_id": "MYPKG",
        "name": "Port Klang",
        "country": "MY",
        "location": {"type": "Point", "coordinates": [101.3942, 3.0110]},
        "timezone": "Asia/Kuala_Lumpur",
        "annual_teu": 1400,
    },
    {
        "_id": "MYTPP",
        "name": "Tanjung Pelepas",
        "country": "MY",
        "location": {"type": "Point", "coordinates": [103.5531, 1.3628]},
        "timezone": "Asia/Kuala_Lumpur",
        "annual_teu": 1100,
    },
    {
        "_id": "LKCMB",
        "name": "Port of Colombo",
        "country": "LK",
        "location": {"type": "Point", "coordinates": [79.8578, 6.9319]},
        "timezone": "Asia/Colombo",
        "annual_teu": 740,
    },
    {
        "_id": "AEJEA",
        "name": "Jebel Ali (Dubai)",
        "country": "AE",
        "location": {"type": "Point", "coordinates": [55.0272, 24.9857]},
        "timezone": "Asia/Dubai",
        "annual_teu": 1480,
    },
    {
        "_id": "EGPSD",
        "name": "Port Said (Suez Canal)",
        "country": "EG",
        "location": {"type": "Point", "coordinates": [32.3019, 31.2653]},
        "timezone": "Africa/Cairo",
        "annual_teu": 480,
    },
    {
        "_id": "NLRTM",
        "name": "Port of Rotterdam",
        "country": "NL",
        "location": {"type": "Point", "coordinates": [4.4777, 51.9244]},
        "timezone": "Europe/Amsterdam",
        "annual_teu": 1490,
    },
    {
        "_id": "BEANR",
        "name": "Port of Antwerp",
        "country": "BE",
        "location": {"type": "Point", "coordinates": [4.3997, 51.2194]},
        "timezone": "Europe/Brussels",
        "annual_teu": 1200,
    },
    {
        "_id": "DEHAM",
        "name": "Port of Hamburg",
        "country": "DE",
        "location": {"type": "Point", "coordinates": [9.9937, 53.5461]},
        "timezone": "Europe/Berlin",
        "annual_teu": 870,
    },
    {
        "_id": "GBFXT",
        "name": "Port of Felixstowe",
        "country": "GB",
        "location": {"type": "Point", "coordinates": [1.3510, 51.9540]},
        "timezone": "Europe/London",
        "annual_teu": 380,
    },
    {
        "_id": "CNSHA",
        "name": "Port of Shanghai",
        "country": "CN",
        "location": {"type": "Point", "coordinates": [121.4737, 31.2304]},
        "timezone": "Asia/Shanghai",
        "annual_teu": 4730,
    },
    {
        "_id": "CNTAO",
        "name": "Port of Qingdao",
        "country": "CN",
        "location": {"type": "Point", "coordinates": [120.3826, 36.0671]},
        "timezone": "Asia/Shanghai",
        "annual_teu": 2560,
    },
    {
        "_id": "CNTSN",
        "name": "Port of Tianjin (Xingang)",
        "country": "CN",
        "location": {"type": "Point", "coordinates": [117.7201, 39.0842]},
        "timezone": "Asia/Shanghai",
        "annual_teu": 2180,
    },
    {
        "_id": "KRPUS",
        "name": "Port of Busan",
        "country": "KR",
        "location": {"type": "Point", "coordinates": [129.0403, 35.1028]},
        "timezone": "Asia/Seoul",
        "annual_teu": 2290,
    },
    {
        "_id": "HKHKG",
        "name": "Port of Hong Kong",
        "country": "HK",
        "location": {"type": "Point", "coordinates": [114.1095, 22.3964]},
        "timezone": "Asia/Hong_Kong",
        "annual_teu": 1800,
    },
    {
        "_id": "TWKHH",
        "name": "Port of Kaohsiung",
        "country": "TW",
        "location": {"type": "Point", "coordinates": [120.2696, 22.6143]},
        "timezone": "Asia/Taipei",
        "annual_teu": 1040,
    },
    {
        "_id": "THLCH",
        "name": "Laem Chabang",
        "country": "TH",
        "location": {"type": "Point", "coordinates": [100.8798, 13.0845]},
        "timezone": "Asia/Bangkok",
        "annual_teu": 820,
    },
    {
        "_id": "USLAX",
        "name": "Los Angeles / Long Beach",
        "country": "US",
        "location": {"type": "Point", "coordinates": [-118.2614, 33.7294]},
        "timezone": "America/Los_Angeles",
        "annual_teu": 1980,
    },
    {
        "_id": "USNYC",
        "name": "Port of New York / Newark",
        "country": "US",
        "location": {"type": "Point", "coordinates": [-74.0445, 40.6892]},
        "timezone": "America/New_York",
        "annual_teu": 930,
    },
    {
        "_id": "USSAV",
        "name": "Port of Savannah",
        "country": "US",
        "location": {"type": "Point", "coordinates": [-81.0912, 32.0809]},
        "timezone": "America/New_York",
        "annual_teu": 580,
    },
]


def make_disruptions() -> list[dict]:
    return [
        {
            "type": "port_closure",
            "title": "Red Sea lane suspension — vessels rerouting via Cape of Good Hope",
            "description": (
                "Ongoing security incidents near the Bab el-Mandeb Strait have forced "
                "major carriers to suspend Suez Canal transits. All Asia–Europe services "
                "are rerouting via the Cape of Good Hope, adding 10–14 days to voyages."
            ),
            "location": {"type": "Point", "coordinates": [43.2, 12.6]},
            "affected_ports": ["AEJEA", "EGPSD", "NLRTM", "BEANR", "DEHAM", "GBFXT"],
            "severity": 5,
            "radius_km": 800.0,
            "status": "open",
            "created_at": mt(days=4),
        },
        {
            "type": "storm",
            "title": "Typhoon Kira — South China Sea disruption",
            "description": (
                "Typhoon Kira is tracking NNW across the South China Sea with sustained "
                "winds of 130 kt. Port operations suspended at Hong Kong; vessel arrivals "
                "at Shanghai and Busan delayed 2–4 days."
            ),
            "location": {"type": "Point", "coordinates": [115.5, 18.2]},
            "affected_ports": ["HKHKG", "CNSHA", "CNTAO", "KRPUS", "TWKHH"],
            "severity": 4,
            "radius_km": 650.0,
            "status": "open",
            "created_at": mt(days=1),
        },
        {
            "type": "strike",
            "title": "Felixstowe dock workers strike — terminal operations suspended",
            "description": (
                "Unite union members at Felixstowe have begun an indefinite strike after "
                "pay talks broke down. All container terminal operations are suspended. "
                "Vessels are being diverted to Rotterdam, Antwerp, and Hamburg."
            ),
            "location": {"type": "Point", "coordinates": [1.3510, 51.9540]},
            "affected_ports": ["GBFXT"],
            "severity": 3,
            "radius_km": 30.0,
            "status": "open",
            "created_at": mt(hours=18),
        },
        {
            "type": "vessel_delay",
            "title": "Port of Los Angeles chassis shortage — dwell times elevated",
            "description": (
                "Chassis pool depletion at LA/Long Beach has caused average vessel dwell "
                "to rise to 6.2 days. Carriers reporting 3–5 day delays on discharge. "
                "No terminal closure; operations continue at reduced throughput."
            ),
            "location": {"type": "Point", "coordinates": [-118.2614, 33.7294]},
            "affected_ports": ["USLAX"],
            "severity": 2,
            "radius_km": 50.0,
            "status": "open",
            "created_at": mt(days=2),
        },
    ]


def make_shipments() -> list[dict]:
    # ── Active (in_transit) ──────────────────────────────────────────────────
    active = [
        {
            # MATERIAL — Suez reroute adds 12 days, SLA deadline is 15 days out
            "vessel_name": "MV Pacific Jade",
            "imo_number": "9876543",
            "origin": "CNSHA",
            "destination": "NLRTM",
            "cargo_type": "electronics",
            "cargo_description": "Consumer electronics — 1,840 TEU smartphones / displays",
            "current_position": {"type": "Point", "coordinates": [103.8, 1.3]},
            "predicted_eta": pt(days=10),   # original Suez ETA (now 22 days via Cape)
            "actual_arrival": None,
            "sla_deadline": pt(days=15),
            "status": "in_transit",
            "created_at": mt(days=18),
        },
        {
            # IMMATERIAL — Typhoon is in South China Sea; this ship is already
            # mid-Pacific on the trans-Pacific arc, route unaffected
            "vessel_name": "MV Coral Star",
            "imo_number": "9234567",
            "origin": "KRPUS",
            "destination": "USLAX",
            "cargo_type": "automotive",
            "cargo_description": "Automotive parts — 620 TEU engine components",
            "current_position": {"type": "Point", "coordinates": [175.0, 35.0]},
            "predicted_eta": pt(days=8),
            "actual_arrival": None,
            "sla_deadline": pt(days=12),
            "status": "in_transit",
            "created_at": mt(days=6),
        },
        {
            # MATERIAL — Red Sea suspension + Felixstowe strike (double disruption)
            "vessel_name": "MV Straits Express",
            "imo_number": "9345678",
            "origin": "SGSIN",
            "destination": "GBFXT",
            "cargo_type": "general",
            "cargo_description": "General merchandise — 980 TEU mixed consumer goods",
            "current_position": {"type": "Point", "coordinates": [45.0, 12.5]},
            "predicted_eta": pt(days=15),
            "actual_arrival": None,
            "sla_deadline": pt(days=14),   # SLA already breached by reroute + strike
            "status": "in_transit",
            "created_at": mt(days=12),
        },
    ]

    # ── Historical (arrived) — ground truth for eval harness ─────────────────
    historical = [
        {
            # MATERIAL — LA chassis shortage added 4 days, breached SLA by 2 days
            "vessel_name": "MV Dragon Pearl",
            "imo_number": "9456789",
            "origin": "CNTAO",
            "destination": "USLAX",
            "cargo_type": "general",
            "cargo_description": "Industrial machinery — 740 TEU heavy equipment",
            "current_position": {"type": "Point", "coordinates": [-118.2614, 33.7294]},
            "predicted_eta": mt(days=3),
            "actual_arrival": mt(days=1),   # arrived 2 days late
            "sla_deadline": mt(days=2),     # SLA was breached (arrived 1 day after SLA)
            "status": "arrived",
            "created_at": mt(days=21),
        },
        {
            # IMMATERIAL — Hamburg → New York, no active disruption on route, on time
            "vessel_name": "MV Nordic Bridge",
            "imo_number": "9567890",
            "origin": "DEHAM",
            "destination": "USNYC",
            "cargo_type": "chemicals",
            "cargo_description": "Specialty chemicals — 420 TEU industrial compounds",
            "current_position": {"type": "Point", "coordinates": [-74.0445, 40.6892]},
            "predicted_eta": mt(days=5),
            "actual_arrival": mt(days=5),   # arrived exactly on time
            "sla_deadline": mt(days=3),
            "status": "arrived",
            "created_at": mt(days=19),
        },
        {
            # IMMATERIAL — Short Colombo → Klang hop; Typhoon Kira was 2000km away
            "vessel_name": "MV Eastern Dawn",
            "imo_number": "9678901",
            "origin": "LKCMB",
            "destination": "MYPKG",
            "cargo_type": "perishables",
            "cargo_description": "Perishables — 180 TEU spices / agricultural produce",
            "current_position": {"type": "Point", "coordinates": [101.3942, 3.0110]},
            "predicted_eta": mt(days=2),
            "actual_arrival": mt(days=2),   # on time
            "sla_deadline": mt(days=1),
            "status": "arrived",
            "created_at": mt(days=8),
        },
    ]

    return active + historical


async def seed() -> None:
    client = AsyncIOMotorClient(MONGODB_URI, serverSelectionTimeoutMS=8000, appname="quorum-seed")
    db = client[MONGODB_DB]

    # ── Indexes ────────────────────────────────────────────────────────────────
    print("Creating indexes...")
    await db.ports.create_index([("location", GEOSPHERE)], background=True)
    await db.disruptions.create_index([("location", GEOSPHERE)], background=True)
    await db.disruptions.create_index([("status", ASCENDING)], background=True)
    await db.shipments.create_index([("current_position", GEOSPHERE)], background=True)
    await db.shipments.create_index([("status", ASCENDING)], background=True)
    await db.determinations.create_index([("disruption_id", ASCENDING)], background=True)
    await db.determinations.create_index([("shipment_id", ASCENDING)], background=True)
    print("  OK indexes ready")

    # ── Ports (upsert by LOCODE) ───────────────────────────────────────────────
    print(f"Upserting {len(PORTS)} ports...")
    for port in PORTS:
        await db.ports.update_one(
            {"_id": port["_id"]},
            {"$set": port},
            upsert=True,
        )
    print(f"  OK {len(PORTS)} ports")

    # ── Disruptions (clear + re-insert for predictable demo state) ────────────
    disruptions = make_disruptions()
    print(f"Seeding {len(disruptions)} disruptions...")
    await db.disruptions.delete_many({})
    result = await db.disruptions.insert_many(disruptions)
    print(f"  OK {len(result.inserted_ids)} disruptions")

    # ── Shipments (clear + re-insert) ─────────────────────────────────────────
    shipments = make_shipments()
    print(f"Seeding {len(shipments)} shipments...")
    await db.shipments.delete_many({})
    result = await db.shipments.insert_many(shipments)
    print(f"  OK {len(result.inserted_ids)} shipments ({sum(1 for s in shipments if s['status'] == 'in_transit')} active, {sum(1 for s in shipments if s['status'] == 'arrived')} historical)")

    client.close()
    print("\nSeed complete. quorum database ready.")


if __name__ == "__main__":
    asyncio.run(seed())
