from dataclasses import dataclass


@dataclass
class Activity:
    timestamp: str
    type: str
    actor: str
    description: str
    details: dict