from dataclasses import dataclass
from typing import Any


@dataclass
class Activity:
    timestamp: str
    type: str
    actor: str
    description: str
    details: dict[str, Any]