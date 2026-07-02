"""Ground-truth derivation from shipment outcome data."""
from datetime import datetime


def compute_ground_truth(shipment: dict) -> bool:
    """Return True (material) if the shipment breached its SLA.

    Rule: actual_arrival > sla_deadline  →  SLA was missed  →  disruption was material.
    Both fields are datetime objects from MongoDB; returns False if either is absent.
    """
    actual = shipment.get("actual_arrival")
    sla = shipment.get("sla_deadline")
    if not isinstance(actual, datetime) or not isinstance(sla, datetime):
        return False
    return actual > sla
