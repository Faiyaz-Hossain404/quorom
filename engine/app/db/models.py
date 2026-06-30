"""Pydantic models for MongoDB collections.

GeoJSON coordinates are always [longitude, latitude] per the GeoJSON spec
(opposite of the intuitive lat/lon order).
"""
from __future__ import annotations

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class GeoPoint(BaseModel):
    type: Literal["Point"] = "Point"
    coordinates: list[float]  # [longitude, latitude]


# ── ports ──────────────────────────────────────────────────────────────────────

class Port(BaseModel):
    """Reference data for a major commercial port."""

    model_config = ConfigDict(populate_by_name=True)

    id: str = Field(alias="_id")  # UN/LOCODE e.g. "SGSIN"
    name: str
    country: str  # ISO 3166-1 alpha-2
    location: GeoPoint
    timezone: str  # IANA tz e.g. "Asia/Singapore"
    annual_teu: int  # rough TEU capacity (millions × 100 for int)


# ── disruptions ────────────────────────────────────────────────────────────────

DisruptionType = Literal["port_closure", "vessel_delay", "storm", "strike", "tariff"]
DisruptionStatus = Literal["open", "resolved"]


class Disruption(BaseModel):
    type: DisruptionType
    title: str
    description: str
    location: GeoPoint  # epicentre
    affected_ports: list[str]  # LOCODEs
    severity: int  # 1 (minor) – 5 (catastrophic)
    radius_km: float
    status: DisruptionStatus = "open"
    created_at: datetime


# ── shipments ──────────────────────────────────────────────────────────────────

CargoType = Literal["electronics", "automotive", "chemicals", "perishables", "general"]
ShipmentStatus = Literal["in_transit", "delayed", "arrived"]


class Shipment(BaseModel):
    vessel_name: str
    imo_number: str
    origin: str  # LOCODE
    destination: str  # LOCODE
    cargo_type: CargoType
    cargo_description: str
    current_position: GeoPoint
    predicted_eta: datetime
    actual_arrival: datetime | None = None
    sla_deadline: datetime
    status: ShipmentStatus = "in_transit"
    created_at: datetime


# ── determinations ─────────────────────────────────────────────────────────────
# Written by the Judge agent (Day 3). Defined here so the schema is stable.

class Determination(BaseModel):
    disruption_id: str  # ObjectId as str
    shipment_id: str  # ObjectId as str
    is_material: bool
    confidence: float  # 0.0 – 1.0
    tier_used: Literal["flash", "max"]
    skeptic_argument: str
    analyst_argument: str
    judge_reasoning: str
    created_at: datetime
    # eval fields — set by the eval harness (Day 4)
    ground_truth_material: bool | None = None
    eval_correct: bool | None = None
