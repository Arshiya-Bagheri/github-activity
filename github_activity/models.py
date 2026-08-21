"""Data models used by the GitHub Activity application."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any


@dataclass
class Activity:
    """Represent a normalized GitHub activity event.

    This model provides a consistent structure for GitHub events after
    they have been processed by EventHandler. Instead of working with
    the different nested structures returned by the GitHub API, the
    rest of the application can work with a common Activity object.

    Attributes:
        timestamp: Date and time when the event occurred.
        type: GitHub event type, such as "PushEvent" or "IssuesEvent".
        actor: GitHub username that performed the activity.
        description: Human-readable description of the activity.
        details: Additional structured information specific to the event.
    """

    timestamp: datetime
    type: str
    actor: str
    description: str
    details: dict[str, Any]