"""Tests for the GitHubActivity service and its filtering logic."""

from datetime import date
from unittest.mock import MagicMock

import pytest

from github_activity.activity import (
    EVENT_TYPES,
    GitHubActivity,
    GitHubActivityError,
    InvalidDateError,
    InvalidEventTypeError,
    RateLimitError,
    UserNotFoundError,
)


def test_event_types_contains_expected_events():
    """Verify that commonly used event names map to GitHub event types."""
    assert EVENT_TYPES["push"] == "PushEvent"
    assert EVENT_TYPES["issues"] == "IssuesEvent"
    assert EVENT_TYPES["pullrequest"] == "PullRequestEvent"
    assert EVENT_TYPES["watch"] == "WatchEvent"
    assert EVENT_TYPES["fork"] == "ForkEvent"


# ---------------------------------------------------------------------------
# parse_date
# ---------------------------------------------------------------------------


def test_parse_date():
    """Convert a valid YYYY-MM-DD string into a date object."""
    result = GitHubActivity.parse_date("2026-08-21")

    assert result == date(2026, 8, 21)


def test_parse_date_none():
    """Return None when no date value is provided."""
    assert GitHubActivity.parse_date(None) is None


def test_parse_date_invalid():
    """Raise InvalidDateError when the date format is invalid."""
    with pytest.raises(InvalidDateError, match="Invalid date"):
        GitHubActivity.parse_date("21-08-2026")


def test_parse_date_invalid_day():
    """Raise InvalidDateError when the date contains an invalid day."""
    with pytest.raises(InvalidDateError):
        GitHubActivity.parse_date("2026-02-30")


# ---------------------------------------------------------------------------
# event_matches_filters
# ---------------------------------------------------------------------------


def test_event_matches_without_filters(push_event):
    """Match an event when no filters are provided."""
    assert GitHubActivity.event_matches_filters(push_event)


def test_event_matches_event_type(push_event):
    """Match an event when its type matches the requested type."""
    assert GitHubActivity.event_matches_filters(
        push_event,
        event_type="PushEvent",
    )


def test_event_does_not_match_event_type(push_event):
    """Reject an event when its type does not match the requested type."""
    assert not GitHubActivity.event_matches_filters(
        push_event,
        event_type="IssuesEvent",
    )


def test_event_matches_repository_full_name(push_event):
    """Match an event using the repository's full owner/name."""
    assert GitHubActivity.event_matches_filters(
        push_event,
        repo="testuser/test-repo",
    )


def test_event_matches_repository_short_name(push_event):
    """Match an event using only the repository name."""
    assert GitHubActivity.event_matches_filters(
        push_event,
        repo="test-repo",
    )


def test_repository_filter_is_case_insensitive(push_event):
    """Repository filtering should ignore differences in letter case."""
    assert GitHubActivity.event_matches_filters(
        push_event,
        repo="TEST-REPO",
    )


def test_event_does_not_match_repository(push_event):
    """Reject an event when its repository does not match the filter."""
    assert not GitHubActivity.event_matches_filters(
        push_event,
        repo="other-repo",
    )


def test_event_matches_since_date(push_event):
    """Match an event occurring on or after the since date."""
    since = date(2026, 8, 15)

    assert GitHubActivity.event_matches_filters(
        push_event,
        since=since,
    )


def test_event_fails_since_date(push_event):
    """Reject an event occurring before the since date."""
    since = date(2026, 8, 16)

    assert not GitHubActivity.event_matches_filters(
        push_event,
        since=since,
    )


def test_event_matches_until_date(push_event):
    """Match an event occurring on or before the until date."""
    until = date(2026, 8, 15)

    assert GitHubActivity.event_matches_filters(
        push_event,
        until=until,
    )


def test_event_fails_until_date(push_event):
    """Reject an event occurring after the until date."""
    until = date(2026, 8, 14)

    assert not GitHubActivity.event_matches_filters(
        push_event,
        until=until,
    )


def test_event_matches_date_range(push_event):
    """Match an event occurring within the requested date range."""
    assert GitHubActivity.event_matches_filters(
        push_event,
        since=date(2026, 8, 14),
        until=date(2026, 8, 16),
    )


def test_event_without_timestamp_fails_date_filter():
    """Reject an event without a timestamp when date filtering is used."""
    event = {
        "type": "PushEvent",
        "repo": {
            "name": "user/repo",
        },
    }

    assert not GitHubActivity.event_matches_filters(
        event,
        since=date(2026, 8, 1),
    )


# ---------------------------------------------------------------------------
# filter_events
# ---------------------------------------------------------------------------


def test_filter_events_by_type(all_events):
    """Filter a collection of events by event type."""
    filtered = GitHubActivity.filter_events(
        all_events,
        event_type="PushEvent",
    )

    assert len(filtered) == 1
    assert filtered[0]["type"] == "PushEvent"


def test_filter_events_by_repository(all_events):
    """Filter a collection of events by repository name."""
    filtered = GitHubActivity.filter_events(
        all_events,
        repo="test-repo",
    )

    assert len(filtered) == 5


def test_filter_events_by_date(all_events):
    """Filter a collection of events by a date range."""
    filtered = GitHubActivity.filter_events(
        all_events,
        since=date(2026, 8, 13),
        until=date(2026, 8, 15),
    )

    assert len(filtered) == 3


def test_filter_events_combines_filters(all_events):
    """Apply event type, repository, and date filters together."""
    filtered = GitHubActivity.filter_events(
        all_events,
        event_type="PushEvent",
        repo="test-repo",
        since=date(2026, 8, 15),
        until=date(2026, 8, 15),
    )

    assert len(filtered) == 1


# ---------------------------------------------------------------------------
# sort_events
# ---------------------------------------------------------------------------


def test_sort_events_newest(all_events):
    """Sort events from newest to oldest."""
    sorted_events = GitHubActivity.sort_events(
        all_events,
        order="newest",
    )

    dates = [
        event["created_at"]
        for event in sorted_events
    ]

    assert dates == sorted(dates, reverse=True)


def test_sort_events_oldest(all_events):
    """Sort events from oldest to newest."""
    sorted_events = GitHubActivity.sort_events(
        all_events,
        order="oldest",
    )

    dates = [
        event["created_at"]
        for event in sorted_events
    ]

    assert dates == sorted(dates)


# ---------------------------------------------------------------------------
# get_activity
# ---------------------------------------------------------------------------


def test_get_activity_returns_activities(push_event):
    """Convert raw GitHub events into Activity objects."""
    activity = GitHubActivity()

    activity.api.get_user_events = lambda *args, **kwargs: [
        push_event
    ]

    events = activity.get_activity("testuser")

    assert len(events) == 1
    assert events[0].type == "PushEvent"
    assert events[0].actor == "testuser"


def test_get_activity_filters_event_type(all_events):
    """Pass the correct event-type filter to the API layer."""
    activity = GitHubActivity()

    mock_get_user_events = MagicMock(
        return_value=[
            event
            for event in all_events
            if event["type"] == "PushEvent"
        ]
    )

    activity.api.get_user_events = mock_get_user_events

    result = activity.get_activity(
        "testuser",
        event_type="push",
    )

    assert len(result) == 1
    assert result[0].type == "PushEvent"

    _, kwargs = mock_get_user_events.call_args

    event_filter = kwargs["event_filter"]

    assert event_filter(
        {"type": "PushEvent"}
    ) is True

    assert event_filter(
        {"type": "IssuesEvent"}
    ) is False


def test_get_activity_accepts_case_insensitive_event_type(
    push_event,
):
    """Accept event type filters regardless of letter case."""
    activity = GitHubActivity()

    activity.api.get_user_events = lambda *args, **kwargs: [
        push_event
    ]

    result = activity.get_activity(
        "testuser",
        event_type="PUSH",
    )

    assert len(result) == 1


def test_get_activity_invalid_event_type():
    """Raise InvalidEventTypeError for an unsupported event type."""
    activity = GitHubActivity()

    with pytest.raises(
        InvalidEventTypeError,
        match="Unknown event type",
    ):
        activity.get_activity(
            "testuser",
            event_type="banana",
        )


def test_get_activity_invalid_date():
    """Raise InvalidDateError when an invalid date is provided."""
    activity = GitHubActivity()

    with pytest.raises(InvalidDateError):
        activity.get_activity(
            "testuser",
            since="not-a-date",
        )


def test_get_activity_since_after_until():
    """Reject a date range where since occurs after until."""
    activity = GitHubActivity()

    with pytest.raises(
        InvalidDateError,
        match="cannot be later",
    ):
        activity.get_activity(
            "testuser",
            since="2026-08-20",
            until="2026-08-10",
        )


def test_get_activity_invalid_sort():
    """Raise an error when an unsupported sort order is requested."""
    activity = GitHubActivity()

    with pytest.raises(
        GitHubActivityError,
        match="Sort must be either",
    ):
        activity.get_activity(
            "testuser",
            sort="random",
        )


# ---------------------------------------------------------------------------
# get_activity sorting + limit
# ---------------------------------------------------------------------------


def test_get_activity_newest_first(all_events):
    """Return activities ordered from newest to oldest."""
    activity = GitHubActivity()

    activity.api.get_user_events = lambda *args, **kwargs: all_events

    result = activity.get_activity(
        "testuser",
        sort="newest",
    )

    timestamps = [
        item.timestamp
        for item in result
    ]

    assert timestamps == sorted(
        timestamps,
        reverse=True,
    )


def test_get_activity_oldest_first(all_events):
    """Return activities ordered from oldest to newest."""
    activity = GitHubActivity()

    activity.api.get_user_events = lambda *args, **kwargs: all_events

    result = activity.get_activity(
        "testuser",
        sort="oldest",
    )

    timestamps = [
        item.timestamp
        for item in result
    ]

    assert timestamps == sorted(timestamps)


def test_get_activity_applies_limit_after_sorting(all_events):
    """Apply the event limit after sorting the complete result."""
    activity = GitHubActivity()

    activity.api.get_user_events = lambda *args, **kwargs: all_events

    result = activity.get_activity(
        "testuser",
        limit=2,
        sort="newest",
    )

    assert len(result) == 2
    assert result[0].type == "PushEvent"
    assert result[1].type == "IssuesEvent"


def test_get_activity_passes_oldest_as_fetch_all(all_events):
    """Request all available API pages when sorting oldest-first."""
    activity = GitHubActivity()

    captured = {}

    def fake_get_user_events(*args, **kwargs):
        captured.update(kwargs)
        return all_events

    activity.api.get_user_events = fake_get_user_events

    activity.get_activity(
        "testuser",
        sort="oldest",
    )

    assert captured["fetch_all"] is True


def test_get_activity_newest_does_not_fetch_all(all_events):
    """Avoid fetching every API page when sorting newest-first."""
    activity = GitHubActivity()

    captured = {}

    def fake_get_user_events(*args, **kwargs):
        captured.update(kwargs)
        return all_events

    activity.api.get_user_events = fake_get_user_events

    activity.get_activity(
        "testuser",
        sort="newest",
    )

    assert captured["fetch_all"] is False


# ---------------------------------------------------------------------------
# API error translation
# ---------------------------------------------------------------------------


def make_http_error(status_code):
    """Create a requests HTTPError containing the given status code."""
    from requests import Response
    from requests.exceptions import HTTPError

    response = Response()
    response.status_code = status_code

    error = HTTPError(
        f"HTTP {status_code}"
    )
    error.response = response

    return error


def test_get_activity_user_not_found():
    """Translate a GitHub 404 response into UserNotFoundError."""
    activity = GitHubActivity()

    def raise_error(*args, **kwargs):
        raise make_http_error(404)

    activity.api.get_user_events = raise_error

    with pytest.raises(UserNotFoundError):
        activity.get_activity("unknown-user")


def test_get_activity_rate_limit():
    """Translate a GitHub 403 response into RateLimitError."""
    activity = GitHubActivity()

    def raise_error(*args, **kwargs):
        raise make_http_error(403)

    activity.api.get_user_events = raise_error

    with pytest.raises(RateLimitError):
        activity.get_activity("testuser")


def test_get_activity_other_http_error():
    """Translate unexpected HTTP errors into GitHubActivityError."""
    activity = GitHubActivity()

    def raise_error(*args, **kwargs):
        raise make_http_error(500)

    activity.api.get_user_events = raise_error

    with pytest.raises(
        GitHubActivityError,
        match="status 500",
    ):
        activity.get_activity("testuser")


def test_get_activity_request_exception():
    """Translate network errors into GitHubActivityError."""
    import requests

    activity = GitHubActivity()

    def raise_error(*args, **kwargs):
        raise requests.RequestException("Connection failed")

    activity.api.get_user_events = raise_error

    with pytest.raises(
        GitHubActivityError,
        match="Could not connect to GitHub",
    ):
        activity.get_activity("testuser")