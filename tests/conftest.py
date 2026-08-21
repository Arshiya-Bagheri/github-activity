import pytest


@pytest.fixture
def push_event():
    return {
        "type": "PushEvent",
        "actor": {
            "login": "testuser",
        },
        "repo": {
            "name": "testuser/test-repo",
        },
        "created_at": "2026-08-15T12:30:00Z",
        "payload": {
            "ref": "refs/heads/main",
            "commits": [
                {"sha": "abc123"},
                {"sha": "def456"},
            ],
        },
    }


@pytest.fixture
def issue_event():
    return {
        "type": "IssuesEvent",
        "actor": {
            "login": "testuser",
        },
        "repo": {
            "name": "testuser/test-repo",
        },
        "created_at": "2026-08-14T10:00:00Z",
        "payload": {
            "action": "opened",
            "issue": {
                "number": 42,
                "title": "Bug report",
            },
        },
    }


@pytest.fixture
def pull_request_event():
    return {
        "type": "PullRequestEvent",
        "actor": {
            "login": "testuser",
        },
        "repo": {
            "name": "testuser/test-repo",
        },
        "created_at": "2026-08-13T09:00:00Z",
        "payload": {
            "action": "closed",
            "number": 10,
            "pull_request": {
                "number": 10,
                "title": "Add new feature",
            },
        },
    }


@pytest.fixture
def comment_event():
    return {
        "type": "IssueCommentEvent",
        "actor": {
            "login": "testuser",
        },
        "repo": {
            "name": "testuser/test-repo",
        },
        "created_at": "2026-08-12T08:00:00Z",
        "payload": {
            "comment": {
                "body": "Looks good!",
            },
            "issue": {
                "number": 5,
            },
        },
    }


@pytest.fixture
def watch_event():
    return {
        "type": "WatchEvent",
        "actor": {
            "login": "testuser",
        },
        "repo": {
            "name": "testuser/test-repo",
        },
        "created_at": "2026-08-11T07:00:00Z",
        "payload": {
            "action": "started",
        },
    }


@pytest.fixture
def fork_event():
    return {
        "type": "ForkEvent",
        "actor": {
            "login": "testuser",
        },
        "repo": {
            "name": "original-owner/original-repo",
        },
        "created_at": "2026-08-10T06:00:00Z",
        "payload": {
            "forkee": {
                "full_name": "testuser/forked-repo",
            },
        },
    }


@pytest.fixture
def all_events(
    push_event,
    issue_event,
    pull_request_event,
    comment_event,
    watch_event,
    fork_event,
):
    return [
        push_event,
        issue_event,
        pull_request_event,
        comment_event,
        watch_event,
        fork_event,
    ]