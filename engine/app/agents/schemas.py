from dataclasses import dataclass


@dataclass
class DebateContext:
    disruption_id: str
    shipment_id: str
    disruption: dict
    shipment: dict


@dataclass
class JudgeOutput:
    is_material: bool
    confidence: float
    reasoning: str
