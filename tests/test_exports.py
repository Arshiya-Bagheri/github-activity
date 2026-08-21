"""Tests for GitHub Activity output formatting and terminal presentation."""

import json
from datetime import datetime, timezone

from rich.console import Console

from github_activity import exports
from github_activity.models import Activity


def make_activity(
    type="PushEvent",
    actor="testuser",
    description="Pushed 2 commits",
    details=None,
):
    """Create a sample Activity object for use in tests."""
    return Activity(
        timestamp=datetime(
            2026,
            8,
            15,
            12,
            30,
            0,
            tzinfo=timezone.utc,
        ),
        type=type,
        actor=actor,
        description=description,
        details=details or {},
    )


# ---------------------------------------------------------
# format_as_text
# ---------------------------------------------------------


def test_format_as_text():
    """Format an Activity object as human-readable text."""
    activity = make_activity()

    result = exports.format_as_text(activity)

    assert result == (
        "[2026-08-15 12:30:00] "
        "Pushed 2 commits "
        "by testuser"
    )


def test_format_as_text_uses_activity_data():
    """Include the actor and description from the Activity object."""
    activity = make_activity(
        actor="alice",
        description="Opened an issue",
    )

    result = exports.format_as_text(activity)

    assert "alice" in result
    assert "Opened an issue" in result


# ---------------------------------------------------------
# JSON
# ---------------------------------------------------------


def test_format_as_json_empty():
    """Return an empty JSON list when no activities are provided."""
    result = exports.format_as_json([])

    assert json.loads(result) == []


def test_format_as_json():
    """Serialize an Activity object with all expected fields."""
    activity = make_activity(
        details={
            "repository": "testuser/test-repo",
            "commits": 2,
        }
    )

    result = exports.format_as_json([activity])

    data = json.loads(result)

    assert len(data) == 1

    assert data[0]["timestamp"] == (
        "2026-08-15T12:30:00+00:00"
    )

    assert data[0]["type"] == "PushEvent"
    assert data[0]["actor"] == "testuser"
    assert data[0]["description"] == "Pushed 2 commits"

    assert data[0]["details"] == {
        "repository": "testuser/test-repo",
        "commits": 2,
    }


def test_format_as_json_multiple_events():
    """Serialize multiple Activity objects into a JSON list."""
    activities = [
        make_activity(
            type="PushEvent",
            description="Push",
        ),
        make_activity(
            type="IssuesEvent",
            description="Issue",
        ),
    ]

    result = exports.format_as_json(activities)

    data = json.loads(result)

    assert len(data) == 2
    assert data[0]["type"] == "PushEvent"
    assert data[1]["type"] == "IssuesEvent"


# ---------------------------------------------------------
# Rich output
# ---------------------------------------------------------


def test_print_rich_activity_empty(monkeypatch):
    """Display a message when the user has no activity."""
    console = Console(record=True)

    monkeypatch.setattr(
        exports,
        "console",
        console,
    )

    exports.print_rich_activity(
        [],
        "testuser",
    )

    output = console.export_text()

    assert "No activity found" in output
    assert "testuser" in output


def test_print_rich_activity_header(monkeypatch):
    """Display the username and event count in the output header."""
    console = Console(record=True)

    monkeypatch.setattr(
        exports,
        "console",
        console,
    )

    activities = [
        make_activity(),
    ]

    exports.print_rich_activity(
        activities,
        "testuser",
    )

    output = console.export_text()

    assert "GitHub Activity" in output
    assert "User:" in output
    assert "testuser" in output
    assert "Events:" in output
    assert "1" in output


def test_print_rich_activity_contains_event(monkeypatch):
    """Display an event's style label, description, and actor."""
    console = Console(record=True)

    monkeypatch.setattr(
        exports,
        "console",
        console,
    )

    activity = make_activity(
        description="Pushed 2 commits to repo",
    )

    exports.print_rich_activity(
        [activity],
        "testuser",
    )

    output = console.export_text()

    assert "PUSH" in output
    assert "Pushed 2 commits to" in output
    assert "repo" in output
    assert "testuser" in output


def test_print_rich_activity_footer(monkeypatch):
    """Display the number of events in the output footer."""
    console = Console(record=True)

    monkeypatch.setattr(
        exports,
        "console",
        console,
    )

    activities = [
        make_activity(),
        make_activity(
            type="IssuesEvent",
            description="Opened issue",
        ),
    ]

    exports.print_rich_activity(
        activities,
        "testuser",
    )

    output = console.export_text()

    assert "2 event(s) displayed" in output


def test_print_rich_activity_all_event_styles(monkeypatch):
    """Display the correct label for every supported event style."""
    console = Console(record=True)

    monkeypatch.setattr(
        exports,
        "console",
        console,
    )

    event_types = [
        "PushEvent",
        "CreateEvent",
        "IssueCommentEvent",
        "PullRequestReviewEvent",
        "PullRequestReviewCommentEvent",
        "DeleteEvent",
        "PullRequestEvent",
        "IssuesEvent",
        "WatchEvent",
        "PublicEvent",
        "ReleaseEvent",
        "ForkEvent",
    ]

    activities = [
        make_activity(
            type=event_type,
            description=f"Test {event_type}",
        )
        for event_type in event_types
    ]

    exports.print_rich_activity(
        activities,
        "testuser",
    )

    output = console.export_text()

    for event_type in event_types:
        label = exports.EVENT_STYLES[event_type][0]
        assert label in output


def test_unknown_event_style(monkeypatch):
    """Use the fallback style when an unknown event type is provided."""
    console = Console(record=True)

    monkeypatch.setattr(
        exports,
        "console",
        console,
    )

    activity = make_activity(
        type="UnknownEvent",
        description="Something happened",
    )

    exports.print_rich_activity(
        [activity],
        "testuser",
    )

    output = console.export_text()

    assert "UNKNOWN" in output
    assert "Something happened" in output