from datetime import datetime

import pytest

from github_activity.handler import EventHandler
from github_activity.models import Activity


@pytest.fixture
def handler():
    return EventHandler()


def test_handler_returns_activity(handler, push_event):
    activity = handler.handle(push_event)

    assert isinstance(activity, Activity)
    assert activity.type == "PushEvent"
    assert activity.actor == "testuser"
    assert isinstance(activity.timestamp, datetime)


# ---------------------------------------------------------
# Push
# ---------------------------------------------------------


def test_handle_push_event(handler, push_event):
    description, details = handler.handle_PushEvent(push_event)

    assert description == "Pushed 2 commits to testuser/test-repo on main"

    assert details == {
        "repository": "testuser/test-repo",
        "branch": "main",
        "commits": 2,
    }


def test_handle_push_event_without_branch(handler):
    event = {
        "type": "PushEvent",
        "repo": {"name": "user/repo"},
        "payload": {
            "commits": [],
        },
    }

    description, details = handler.handle_PushEvent(event)

    assert "unknown branch" in description
    assert details["commits"] == 0


# ---------------------------------------------------------
# Create
# ---------------------------------------------------------


def test_handle_create_event(handler):
    event = {
        "type": "CreateEvent",
        "repo": {"name": "user/repo"},
        "payload": {
            "ref_type": "branch",
            "ref": "feature/login",
        },
    }

    description, details = handler.handle_CreateEvent(event)

    assert description == (
        "Created branch feature/login in user/repo"
    )

    assert details["repository"] == "user/repo"
    assert details["ref_type"] == "branch"
    assert details["ref"] == "feature/login"


def test_handle_create_event_without_ref(handler):
    event = {
        "type": "CreateEvent",
        "repo": {"name": "user/repo"},
        "payload": {
            "ref_type": "repository",
        },
    }

    description, details = handler.handle_CreateEvent(event)

    assert description == "Created a repository in user/repo"
    assert details["ref"] is None


# ---------------------------------------------------------
# Issue comment
# ---------------------------------------------------------


def test_handle_issue_comment_event(handler, comment_event):
    description, details = handler.handle_IssueCommentEvent(
        comment_event
    )

    assert description == (
        "Commented on issue #5 in testuser/test-repo: Looks good!"
    )

    assert details == {
        "repository": "testuser/test-repo",
        "issue_number": 5,
        "comment": "Looks good!",
    }


def test_handle_issue_comment_without_body(handler):
    event = {
        "type": "IssueCommentEvent",
        "repo": {"name": "user/repo"},
        "payload": {
            "comment": {},
            "issue": {"number": 10},
        },
    }

    description, details = handler.handle_IssueCommentEvent(event)

    assert description == "Commented on issue #10 in user/repo"
    assert details["comment"] is None


# ---------------------------------------------------------
# Pull request review
# ---------------------------------------------------------


def test_handle_pull_request_review(handler):
    event = {
        "type": "PullRequestReviewEvent",
        "repo": {"name": "user/repo"},
        "payload": {
            "review": {
                "state": "approved",
            },
            "pull_request": {
                "number": 25,
            },
        },
    }

    description, details = handler.handle_PullRequestReviewEvent(
        event
    )

    assert description == (
        "Reviewed pull request #25 in user/repo: approved"
    )

    assert details["pull_request_number"] == 25
    assert details["review_state"] == "approved"


# ---------------------------------------------------------
# Pull request review comment
# ---------------------------------------------------------


def test_handle_pull_request_review_comment(handler):
    event = {
        "type": "PullRequestReviewCommentEvent",
        "repo": {"name": "user/repo"},
        "payload": {
            "comment": {
                "body": "Please change this.",
            },
            "pull_request": {
                "number": 30,
            },
        },
    }

    description, details = (
        handler.handle_PullRequestReviewCommentEvent(event)
    )

    assert description == (
        "Commented on pull request "
        "#30 in user/repo: Please change this."
    )

    assert details["pull_request_number"] == 30
    assert details["comment"] == "Please change this."


# ---------------------------------------------------------
# Delete
# ---------------------------------------------------------


def test_handle_delete_event(handler):
    event = {
        "type": "DeleteEvent",
        "repo": {"name": "user/repo"},
        "payload": {
            "ref_type": "branch",
            "ref": "old-feature",
        },
    }

    description, details = handler.handle_DeleteEvent(event)

    assert description == (
        "Deleted branch old-feature from user/repo"
    )

    assert details["ref_type"] == "branch"
    assert details["ref"] == "old-feature"


# ---------------------------------------------------------
# Pull request
# ---------------------------------------------------------


def test_handle_pull_request_event(handler, pull_request_event):
    description, details = handler.handle_PullRequestEvent(
        pull_request_event
    )

    assert description == (
        "Pull request #10 closed "
        "in testuser/test-repo: Add new feature"
    )

    assert details["action"] == "closed"
    assert details["pull_request_number"] == 10
    assert details["title"] == "Add new feature"


def test_handle_pull_request_without_title(handler):
    event = {
        "type": "PullRequestEvent",
        "repo": {"name": "user/repo"},
        "payload": {
            "action": "opened",
            "number": 3,
            "pull_request": {},
        },
    }

    description, details = handler.handle_PullRequestEvent(event)

    assert description == "Pull request #3 opened in user/repo"
    assert details["title"] is None


# ---------------------------------------------------------
# Issues
# ---------------------------------------------------------


def test_handle_issues_event(handler, issue_event):
    description, details = handler.handle_IssuesEvent(
        issue_event
    )

    assert description == (
        "Issue #42 opened "
        "in testuser/test-repo: Bug report"
    )

    assert details["action"] == "opened"
    assert details["issue_number"] == 42
    assert details["title"] == "Bug report"


def test_handle_issue_without_title(handler):
    event = {
        "type": "IssuesEvent",
        "repo": {"name": "user/repo"},
        "payload": {
            "action": "closed",
            "issue": {
                "number": 10,
            },
        },
    }

    description, details = handler.handle_IssuesEvent(event)

    assert description == "Issue #10 closed in user/repo"
    assert details["title"] is None


# ---------------------------------------------------------
# Watch
# ---------------------------------------------------------


def test_handle_watch_event(handler, watch_event):
    description, details = handler.handle_WatchEvent(
        watch_event
    )

    assert description == "Starred testuser/test-repo"
    assert details["action"] == "started"


def test_handle_watch_non_started(handler):
    event = {
        "type": "WatchEvent",
        "repo": {"name": "user/repo"},
        "payload": {
            "action": "stopped",
        },
    }

    description, details = handler.handle_WatchEvent(event)

    assert description == (
        "Watch action 'stopped' on user/repo"
    )


# ---------------------------------------------------------
# Public
# ---------------------------------------------------------


def test_handle_public_event(handler):
    event = {
        "type": "PublicEvent",
        "repo": {
            "name": "user/repo",
        },
    }

    description, details = handler.handle_PublicEvent(event)

    assert description == "Made user/repo public"
    assert details["repository"] == "user/repo"


# ---------------------------------------------------------
# Release
# ---------------------------------------------------------


def test_handle_release_event(handler):
    event = {
        "type": "ReleaseEvent",
        "repo": {"name": "user/repo"},
        "payload": {
            "action": "published",
            "release": {
                "tag_name": "v1.0.0",
            },
        },
    }

    description, details = handler.handle_ReleaseEvent(event)

    assert description == (
        "Release v1.0.0 published in user/repo"
    )

    assert details["action"] == "published"
    assert details["tag"] == "v1.0.0"


def test_handle_release_without_tag(handler):
    event = {
        "type": "ReleaseEvent",
        "repo": {"name": "user/repo"},
        "payload": {
            "action": "deleted",
            "release": {},
        },
    }

    description, details = handler.handle_ReleaseEvent(event)

    assert description == "Release deleted in user/repo"
    assert details["tag"] is None


# ---------------------------------------------------------
# Fork
# ---------------------------------------------------------


def test_handle_fork_event(handler, fork_event):
    description, details = handler.handle_ForkEvent(
        fork_event
    )

    assert description == (
        "Forked original-owner/original-repo "
        "to testuser/forked-repo"
    )

    assert details == {
        "original_repository": "original-owner/original-repo",
        "forked_repository": "testuser/forked-repo",
    }


# ---------------------------------------------------------
# Unknown event
# ---------------------------------------------------------


def test_handle_unknown_event(handler):
    event = {
        "type": "SomethingNewEvent",
    }

    description, details = handler.handle_unknown(event)

    assert description == (
        "Unsupported event: SomethingNewEvent"
    )

    assert details == {
        "event_type": "SomethingNewEvent",
    }


def test_handle_unknown_event_through_handle(handler):
    event = {
        "type": "SomethingNewEvent",
        "actor": {
            "login": "testuser",
        },
    }

    activity = handler.handle(event)

    assert activity.type == "SomethingNewEvent"
    assert activity.description == (
        "Unsupported event: SomethingNewEvent"
    )


# ---------------------------------------------------------
# Missing timestamp / actor
# ---------------------------------------------------------


def test_handle_missing_timestamp(handler):
    event = {
        "type": "PushEvent",
        "actor": {
            "login": "testuser",
        },
        "repo": {
            "name": "user/repo",
        },
        "payload": {
            "commits": [],
        },
    }

    activity = handler.handle(event)

    assert isinstance(activity.timestamp, datetime)


def test_handle_missing_actor(handler):
    event = {
        "type": "PushEvent",
        "repo": {
            "name": "user/repo",
        },
        "payload": {
            "commits": [],
        },
    }

    activity = handler.handle(event)

    assert activity.actor == "unknown"