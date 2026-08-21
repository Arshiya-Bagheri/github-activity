from datetime import datetime, timezone

from github_activity.models import Activity


def test_activity_creation():
    timestamp = datetime(
        2026,
        8,
        15,
        12,
        30,
        tzinfo=timezone.utc,
    )

    activity = Activity(
        timestamp=timestamp,
        type="PushEvent",
        actor="testuser",
        description="Pushed 2 commits",
        details={
            "repository": "testuser/test-repo",
            "commits": 2,
        },
    )

    assert activity.timestamp == timestamp
    assert activity.type == "PushEvent"
    assert activity.actor == "testuser"
    assert activity.description == "Pushed 2 commits"
    assert activity.details["commits"] == 2


def test_activity_is_dataclass():
    timestamp = datetime.now(timezone.utc)

    activity = Activity(
        timestamp=timestamp,
        type="PushEvent",
        actor="user",
        description="Test",
        details={},
    )

    assert activity.__dataclass_fields__ is not None