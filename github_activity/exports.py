import json


def format_as_text(event):
    """Format an Activity object as human-readable text."""
    return (
        f"[{event.timestamp}] "
        f"{event.description} "
        f"by {event.actor}"
    )


def format_as_json(events):
    """Format Activity objects as JSON."""
    data = [
        {
            "timestamp": event.timestamp,
            "type": event.type,
            "actor": event.actor,
            "description": event.description,
            "details": event.details,
        }
        for event in events
    ]

    return json.dumps(data, indent=2)