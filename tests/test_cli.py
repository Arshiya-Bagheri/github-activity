"""Tests for the GitHub Activity command-line interface."""

import sys
from unittest.mock import MagicMock

import pytest

import main
from github_activity.activity import (
    GitHubActivityError,
    InvalidEventTypeError,
    RateLimitError,
    UserNotFoundError,
)


def run_cli(monkeypatch, *args):
    """Run the CLI with the given command-line arguments."""
    monkeypatch.setattr(
        sys,
        "argv",
        ["main.py", *args],
    )

    main.main()


# ---------------------------------------------------------
# Basic argument parsing
# ---------------------------------------------------------


def test_cli_calls_activity(monkeypatch):
    """Pass the username and default options to GitHubActivity."""
    activity = MagicMock()

    activity.get_activity.return_value = []

    monkeypatch.setattr(
        main,
        "GitHubActivity",
        lambda: activity,
    )

    run_cli(
        monkeypatch,
        "testuser",
    )

    activity.get_activity.assert_called_once_with(
        "testuser",
        event_type=None,
        repo=None,
        limit=None,
        since=None,
        until=None,
    )


# ---------------------------------------------------------
# Options
# ---------------------------------------------------------


def test_cli_passes_limit(monkeypatch):
    """Pass the --limit option to GitHubActivity."""
    activity = MagicMock()
    activity.get_activity.return_value = []

    monkeypatch.setattr(
        main,
        "GitHubActivity",
        lambda: activity,
    )

    run_cli(
        monkeypatch,
        "testuser",
        "--limit",
        "25",
    )

    kwargs = activity.get_activity.call_args.kwargs

    assert kwargs["limit"] == 25


def test_cli_passes_event(monkeypatch):
    """Pass the --event option to GitHubActivity."""
    activity = MagicMock()
    activity.get_activity.return_value = []

    monkeypatch.setattr(
        main,
        "GitHubActivity",
        lambda: activity,
    )

    run_cli(
        monkeypatch,
        "testuser",
        "--event",
        "push",
    )

    kwargs = activity.get_activity.call_args.kwargs

    assert kwargs["event_type"] == "push"


def test_cli_passes_repo(monkeypatch):
    """Pass the --repo option to GitHubActivity."""
    activity = MagicMock()
    activity.get_activity.return_value = []

    monkeypatch.setattr(
        main,
        "GitHubActivity",
        lambda: activity,
    )

    run_cli(
        monkeypatch,
        "testuser",
        "--repo",
        "test-repo",
    )

    kwargs = activity.get_activity.call_args.kwargs

    assert kwargs["repo"] == "test-repo"


def test_cli_passes_since(monkeypatch):
    """Pass the --since option to GitHubActivity."""
    activity = MagicMock()
    activity.get_activity.return_value = []

    monkeypatch.setattr(
        main,
        "GitHubActivity",
        lambda: activity,
    )

    run_cli(
        monkeypatch,
        "testuser",
        "--since",
        "2026-08-01",
    )

    kwargs = activity.get_activity.call_args.kwargs

    assert kwargs["since"] == "2026-08-01"


def test_cli_passes_until(monkeypatch):
    """Pass the --until option to GitHubActivity."""
    activity = MagicMock()
    activity.get_activity.return_value = []

    monkeypatch.setattr(
        main,
        "GitHubActivity",
        lambda: activity,
    )

    run_cli(
        monkeypatch,
        "testuser",
        "--until",
        "2026-08-20",
    )

    kwargs = activity.get_activity.call_args.kwargs

    assert kwargs["until"] == "2026-08-20"


def test_cli_passes_all_filters(monkeypatch):
    """Pass all supported filtering options to GitHubActivity."""
    activity = MagicMock()
    activity.get_activity.return_value = []

    monkeypatch.setattr(
        main,
        "GitHubActivity",
        lambda: activity,
    )

    run_cli(
        monkeypatch,
        "testuser",
        "--limit",
        "50",
        "--event",
        "push",
        "--repo",
        "test-repo",
        "--since",
        "2026-08-01",
        "--until",
        "2026-08-20",
    )

    activity.get_activity.assert_called_once_with(
        "testuser",
        event_type="push",
        repo="test-repo",
        limit=50,
        since="2026-08-01",
        until="2026-08-20",
    )


# ---------------------------------------------------------
# Text / JSON output
# ---------------------------------------------------------


def test_cli_uses_rich_output_by_default(monkeypatch):
    """Use Rich output when no output format is specified."""
    activity = MagicMock()

    events = [
        MagicMock(),
    ]

    activity.get_activity.return_value = events

    monkeypatch.setattr(
        main,
        "GitHubActivity",
        lambda: activity,
    )

    rich_mock = MagicMock()

    monkeypatch.setattr(
        main.github_activity.exports,
        "print_rich_activity",
        rich_mock,
    )

    run_cli(
        monkeypatch,
        "testuser",
    )

    rich_mock.assert_called_once_with(
        events,
        "testuser",
    )


def test_cli_uses_json_output(monkeypatch):
    """Use JSON formatting when --format json is specified."""
    activity = MagicMock()

    events = [
        MagicMock(),
    ]

    activity.get_activity.return_value = events

    monkeypatch.setattr(
        main,
        "GitHubActivity",
        lambda: activity,
    )

    json_mock = MagicMock(
        return_value='[{"type": "PushEvent"}]'
    )

    monkeypatch.setattr(
        main.github_activity.exports,
        "format_as_json",
        json_mock,
    )

    run_cli(
        monkeypatch,
        "testuser",
        "--format",
        "json",
    )

    json_mock.assert_called_once_with(events)


# ---------------------------------------------------------
# Error handling
# ---------------------------------------------------------


def test_cli_user_not_found(monkeypatch, capsys):
    """Print an error when the requested GitHub user does not exist."""
    activity = MagicMock()

    activity.get_activity.side_effect = (
        UserNotFoundError("testuser")
    )

    monkeypatch.setattr(
        main,
        "GitHubActivity",
        lambda: activity,
    )

    run_cli(
        monkeypatch,
        "testuser",
    )

    output = capsys.readouterr().out

    assert (
        "GitHub user 'testuser' was not found"
        in output
    )


def test_cli_rate_limit(monkeypatch, capsys):
    """Print an error when the GitHub API rate limit is exceeded."""
    activity = MagicMock()

    activity.get_activity.side_effect = (
        RateLimitError()
    )

    monkeypatch.setattr(
        main,
        "GitHubActivity",
        lambda: activity,
    )

    run_cli(
        monkeypatch,
        "testuser",
    )

    output = capsys.readouterr().out

    assert "rate limit exceeded" in output


def test_cli_invalid_event(monkeypatch, capsys):
    """Print an error when an unsupported event type is requested."""
    activity = MagicMock()

    activity.get_activity.side_effect = (
        InvalidEventTypeError(
            "Unknown event type 'banana'."
        )
    )

    monkeypatch.setattr(
        main,
        "GitHubActivity",
        lambda: activity,
    )

    run_cli(
        monkeypatch,
        "testuser",
    )

    output = capsys.readouterr().out

    assert "Unknown event type" in output


def test_cli_generic_error(monkeypatch, capsys):
    """Print the error message for an unexpected application error."""
    activity = MagicMock()

    activity.get_activity.side_effect = (
        GitHubActivityError(
            "Something went wrong."
        )
    )

    monkeypatch.setattr(
        main,
        "GitHubActivity",
        lambda: activity,
    )

    run_cli(
        monkeypatch,
        "testuser",
    )

    output = capsys.readouterr().out

    assert "Something went wrong." in output


# ---------------------------------------------------------
# argparse validation
# ---------------------------------------------------------


def test_cli_limit_cannot_be_zero(monkeypatch):
    """Reject a --limit value below the allowed range."""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "testuser",
            "--limit",
            "0",
        ],
    )

    with pytest.raises(SystemExit):
        main.main()


def test_cli_limit_cannot_exceed_300(monkeypatch):
    """Reject a --limit value above the allowed range."""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "testuser",
            "--limit",
            "301",
        ],
    )

    with pytest.raises(SystemExit):
        main.main()


def test_cli_invalid_format(monkeypatch):
    """Reject an output format that is not supported."""
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "main.py",
            "testuser",
            "--format",
            "xml",
        ],
    )

    with pytest.raises(SystemExit):
        main.main()