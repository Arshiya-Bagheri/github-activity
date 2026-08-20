import requests

from github_activity.api import GitHubAPI
from github_activity.handler import EventHandler


EVENT_TYPES = {
    "push": "PushEvent",
    "create": "CreateEvent",
    "issuecomment": "IssueCommentEvent",
    "pullrequestevent": "PullRequestReviewEvent",
    "pullrequestreviewcomment": "PullRequestReviewCommentEvent",
    "delete": "DeleteEvent",
    "pullrequest": "PullRequestEvent",
    "issues": "IssuesEvent",
    "watch": "WatchEvent",
    "public": "PublicEvent",
    "release": "ReleaseEvent",
    "fork": "ForkEvent",
}


class GitHubActivityError(Exception):
    """Base exception for GitHub Activity errors."""


class UserNotFoundError(GitHubActivityError):
    """Raised when a GitHub user does not exist."""


class RateLimitError(GitHubActivityError):
    """Raised when the GitHub API rate limit is exceeded."""


class GitHubActivity:
    def __init__(self):
        self.api = GitHubAPI()
        self.handler = EventHandler()

    def get_activity(self, username, event_type=None, repo=None, limit=None):
        try:
            events = self.api.get_user_events(username)

        except requests.HTTPError as error:
            status_code = error.response.status_code

            if status_code == 404:
                raise UserNotFoundError(username) from error

            if status_code == 403:
                raise RateLimitError() from error

            raise GitHubActivityError(
                f"GitHub API returned status {status_code}."
            ) from error

        except requests.RequestException as error:
            raise GitHubActivityError(
                f"Could not connect to GitHub: {error}"
            ) from error

        if event_type:
            event_type = EVENT_TYPES.get(event_type, event_type)

        events = self.filter_events(events, event_type=event_type, repo=repo)

        if limit is not None:
            events = events[:limit]

        return [
            self.handler.handle(event)
            for event in events
        ]

    @staticmethod
    def filter_events(events, event_type=None, repo=None):
        if event_type:
            events = [
                event
                for event in events
                if event["type"] == event_type
            ]

        if repo:
            events = [
                event
                for event in events
                if event["repo"]["name"].endswith(
                    f"/{repo}"
                )
            ]

        return events