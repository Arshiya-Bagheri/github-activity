from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Activity:
    timestamp: datetime
    type: str
    actor: str
    description: str
    details: dict[str, Any]