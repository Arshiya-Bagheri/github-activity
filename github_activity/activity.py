import requests

from datetime import datetime

from github_activity.api import GitHubAPI
from github_activity.handler import EventHandler


EVENT_TYPES = {
    "push": "PushEvent",
    "create": "CreateEvent",
    "issuecomment": "IssueCommentEvent",
    "pullrequestreview": "PullRequestReviewEvent",
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


class InvalidEventTypeError(GitHubActivityError):
    """Raised when an unsupported event type is requested."""


class InvalidDateError(GitHubActivityError):
    """Raised when an invalid date is provided."""


class UserNotFoundError(GitHubActivityError):
    """Raised when a GitHub user does not exist."""


class RateLimitError(GitHubActivityError):
    """Raised when the GitHub API rate limit is exceeded."""


class GitHubActivity:
    def __init__(self):
        self.api = GitHubAPI()
        self.handler = EventHandler()

    def get_activity(
        self,
        username,
        event_type=None,
        repo=None,
        limit=None,
        since=None,
        until=None,
        sort="newest",
    ):
        if event_type:
            event_type = event_type.lower()

            if event_type not in EVENT_TYPES:
                raise InvalidEventTypeError(
                    f"Unknown event type '{event_type}'. "
                    f"Available types: {', '.join(EVENT_TYPES)}"
                )

            event_type = EVENT_TYPES[event_type]

        since_date = self.parse_date(since)
        until_date = self.parse_date(until)

        if since_date and until_date and since_date > until_date:
            raise InvalidDateError(
                "The --since date cannot be later than the --until date."
            )

        if sort not in ("newest", "oldest"):
            raise GitHubActivityError(
                "Sort must be either 'newest' or 'oldest'."
            )

        event_filter = lambda event: self.event_matches_filters(
            event,
            event_type=event_type,
            repo=repo,
            since=since_date,
            until=until_date,
        )

        fetch_all = sort == "oldest"

        try:
            events = self.api.get_user_events(
                username,
                limit=limit,
                event_filter=event_filter,
                fetch_all=fetch_all,
            )

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

        events = self.sort_events(
            events,
            order=sort,
        )

        # Apply the final limit AFTER sorting.
        if limit is not None:
            events = events[:limit]

        return [
            self.handler.handle(event)
            for event in events
        ]

    @staticmethod
    def parse_date(date_string):
        """
        Convert a YYYY-MM-DD string into a date.

        Returns None when no date was provided.
        """
        if date_string is None:
            return None

        try:
            return datetime.strptime(
                date_string,
                "%Y-%m-%d",
            ).date()

        except ValueError as error:
            raise InvalidDateError(
                f"Invalid date '{date_string}'. "
                f"Use the format YYYY-MM-DD."
            ) from error

    @staticmethod
    def event_matches_filters(
        event,
        event_type=None,
        repo=None,
        since=None,
        until=None,
    ):
        """
        Return True when a raw GitHub event matches all
        requested filters.
        """

        if event_type:
            if event.get("type") != event_type:
                return False

        if repo:
            repo = repo.lower()

            event_repo = (
                event.get("repo", {})
                .get("name", "")
                .lower()
            )

            if (
                event_repo != repo
                and not event_repo.endswith(f"/{repo}")
            ):
                return False

        # Date filters
        if since or until:
            created_at = event.get("created_at")

            if not created_at:
                return False

            event_datetime = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            )

            event_date = event_datetime.date()

            if since and event_date < since:
                return False

            if until and event_date > until:
                return False

        return True

    @staticmethod
    def filter_events(
        events,
        event_type=None,
        repo=None,
        since=None,
        until=None,
    ):
        """
        Filter an existing list of events.

        Kept as a separate public method for reuse and compatibility.
        """
        return [
            event
            for event in events
            if GitHubActivity.event_matches_filters(
                event,
                event_type=event_type,
                repo=repo,
                since=since,
                until=until,
            )
        ]

    @staticmethod
    def sort_events(events, order="newest"):
        """
        Sort events by their creation timestamp.

        newest:
            Most recent events first.

        oldest:
            Oldest events first.
        """
        return sorted(
            events,
            key=lambda event: event.get("created_at", ""),
            reverse=(order == "newest"),
        )