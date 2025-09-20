"""
test_cli.py

Unit tests for the GitHubActivity CLI.

Tests include:
- Time formatting
- Event filtering
- All show_* commands (all, push, issues, pullrequest, issuecomment, watch, fork)
- API fetching (mocked)
- CLI run loop behavior

Run tests with: pytest
"""

import pytest
from unittest.mock import patch, MagicMock
from github_activity.cli import GitHubActivity
from requests.exceptions import HTTPError

# -------------------------------
# Helper Function Tests
# -------------------------------

def test_format_time():
    """
    Test that format_time converts GitHub UTC timestamps correctly.
    """
    cli = GitHubActivity()
    utc_str = "2025-09-20T10:00:00Z"
    formatted = cli.format_time(utc_str)
    assert formatted == "2025-09-20 10:00:00"


def test_filter_events():
    """
    Test filtering events by type.
    """
    cli = GitHubActivity()
    events = [
        {"type": "PushEvent"},
        {"type": "IssuesEvent"},
        {"type": "PushEvent"}
    ]
    filtered = cli.filter_events(events, "PushEvent")
    assert len(filtered) == 2
    assert all(e["type"] == "PushEvent" for e in filtered)


# -------------------------------
# Fetching Tests (Mocked)
# -------------------------------

@patch("github_activity.cli.requests.get")
def test_fetch_activity_success(mock_get):
    """
    Test fetch_activity returns JSON data on successful request.
    """
    cli = GitHubActivity()

    # Mock successful response
    mock_response = MagicMock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = [{"type": "PushEvent"}]
    mock_get.return_value = mock_response

    data = cli.fetch_activity("fakeuser")
    assert isinstance(data, list)
    assert data[0]["type"] == "PushEvent"


@patch("github_activity.cli.requests.get")
def test_fetch_activity_http_error(mock_get):
    """
    Test fetch_activity handles HTTP errors properly.
    """
    cli = GitHubActivity()

    # Mock HTTPError (404)
    mock_response = MagicMock()
    mock_response.raise_for_status.side_effect = HTTPError("404 Client Error")
    mock_response.status_code = 404
    mock_get.return_value = mock_response

    data = cli.fetch_activity("nonexistentuser")
    assert data is None


# -------------------------------
# Show Method Tests
# -------------------------------

@patch.object(GitHubActivity, "fetch_activity")
def test_show_all(fetch_mock):
    """
    Test show_all prints activity for all event types.
    """
    cli = GitHubActivity()
    fetch_mock.return_value = [
        {"type": "PushEvent", "repo": {"name": "repo1"}, "payload": {"commits": [{}]}, "created_at": "2025-09-20T10:00:00Z"},
        {"type": "IssuesEvent", "repo": {"name": "repo2"}, "payload": {"action": "opened", "issue": {"number": 1, "title": "Bug"}}, "created_at": "2025-09-20T10:01:00Z"},
        {"type": "PullRequestEvent", "repo": {"name": "repo3"}, "payload": {"action": "closed", "pull_request": {"number": 5, "title": "Feature"}}, "created_at": "2025-09-20T10:02:00Z"},
        {"type": "IssueCommentEvent", "repo": {"name": "repo4"}, "payload": {"comment": {"body": "Nice!"}, "issue": {"number": 2}}, "created_at": "2025-09-20T10:03:00Z"},
        {"type": "WatchEvent", "repo": {"name": "repo5"}, "payload": {}, "created_at": "2025-09-20T10:04:00Z"},
        {"type": "ForkEvent", "repo": {"name": "repo6"}, "payload": {"forkee": {"full_name": "user/repo6"}}, "created_at": "2025-09-20T10:05:00Z"}
    ]

    with patch("builtins.print") as mock_print:
        cli.show_all("user", fetch_mock.return_value)
        assert mock_print.call_count >= 6  # At least one print per event


@patch.object(GitHubActivity, "fetch_activity")
def test_user_commands(fetch_mock):
    """
    Test each individual user command prints expected output.
    """
    cli = GitHubActivity()

    # Mock a generic event for each type
    events = {
        "push": [{"type": "PushEvent", "repo": {"name": "repo"}, "payload": {"commits": [{}]}, "created_at": "2025-09-20T10:00:00Z"}],
        "issues": [{"type": "IssuesEvent", "repo": {"name": "repo"}, "payload": {"action": "opened", "issue": {"number": 1, "title": "Bug"}}, "created_at": "2025-09-20T10:01:00Z"}],
        "pullrequest": [{"type": "PullRequestEvent", "repo": {"name": "repo"}, "payload": {"action": "closed", "pull_request": {"number": 2, "title": "Feature"}}, "created_at": "2025-09-20T10:02:00Z"}],
        "issuecomment": [{"type": "IssueCommentEvent", "repo": {"name": "repo"}, "payload": {"comment": {"body": "Nice!"}, "issue": {"number": 3}}, "created_at": "2025-09-20T10:03:00Z"}],
        "watch": [{"type": "WatchEvent", "repo": {"name": "repo"}, "payload": {}, "created_at": "2025-09-20T10:04:00Z"}],
        "fork": [{"type": "ForkEvent", "repo": {"name": "repo"}, "payload": {"forkee": {"full_name": "user/repo"}}, "created_at": "2025-09-20T10:05:00Z"}],
    }

    for cmd, event_list in events.items():
        fetch_mock.return_value = event_list
        with patch("builtins.print") as mock_print:
            cli.user_commands[cmd]("user", event_list)
            mock_print.assert_called()  # Ensure print is called


# -------------------------------
# Run Loop Tests (Mocked Input)
# -------------------------------

@patch("builtins.input", side_effect=["help", "exit"])
def test_run_help_exit(mock_input):
    """
    Test the run loop with 'help' command followed by 'exit'.
    """
    cli = GitHubActivity()
    with patch("builtins.print") as mock_print:
        cli.run()
        # Check that the help text is printed
        help_calls = [call for call in mock_print.call_args_list if "Available commands" in str(call)]
        assert help_calls


@patch("builtins.input", side_effect=["nonexistentuser", "exit"])
@patch.object(GitHubActivity, "fetch_activity", return_value=None)
def test_run_nonexistent_user(mock_fetch, mock_input):
    """
    Test the run loop with a nonexistent GitHub username.
    """
    cli = GitHubActivity()
    with patch("builtins.print") as mock_print:
        cli.run()
        mock_fetch.assert_called_with("nonexistentuser")


@patch("builtins.input", side_effect=KeyboardInterrupt)
def test_run_keyboard_interrupt(mock_input):
    """
    Test that the CLI handles KeyboardInterrupt gracefully.
    """
    cli = GitHubActivity()
    with patch("builtins.print") as mock_print:
        cli.run()
        # Check that exit message is printed
        exit_calls = [call for call in mock_print.call_args_list if "Exiting" in str(call)]
        assert exit_calls
