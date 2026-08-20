import json


def format_as_text(event):
    """Format event as plain text."""
    return f"[{event.timestamp}] {event.type}: {event.description} by {event.actor}"

def format_as_json(events):
    """Format events as JSON."""
    return json.dumps(events, indent=2)
