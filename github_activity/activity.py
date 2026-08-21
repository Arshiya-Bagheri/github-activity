"""Core logic for retrieving, filtering, sorting, and processing GitHub activity."""

from datetime import date, datetime

import requests

from github_activity.api import GitHubAPI
from github_activity.handler import EventHandler


# Maps user-friendly event names accepted by the CLI to GitHub's official event type names.
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
    """Base exception for errors raised by the GitHub Activity application."""


class InvalidEventTypeError(GitHubActivityError):
    """Raised when an unsupported event type is requested."""


class InvalidDateError(GitHubActivityError):
    """Raised when an invalid date is provided."""


class UserNotFoundError(GitHubActivityError):
    """Raised when the requested GitHub user does not exist."""


class RateLimitError(GitHubActivityError):
    """Raised when the GitHub API rate limit is exceeded or access is denied."""


class GitHubActivity:
    """Provide high-level operations for retrieving and processing GitHub activity."""

    def __init__(self) -> None:
        """Initialize the GitHub API client and event handler."""
        self.api = GitHubAPI()
        self.handler = EventHandler()

    def get_activity(
        self,
        username: str,
        event_type: str | None = None,
        repo: str | None = None,
        limit: int | None = None,
        since: str | None = None,
        until: str | None = None,
        sort: str = "newest",
    ) -> list:
        """Retrieve and process activity for a GitHub user.

        Args:
            username: GitHub username whose activity should be retrieved.
            event_type: Optional event type filter, such as ``push``.
            repo: Optional repository name filter.
            limit: Maximum number of events to return.
            since: Optional start date in ``YYYY-MM-DD`` format.
            until: Optional end date in ``YYYY-MM-DD`` format.
            sort: Sort order, either ``newest`` or ``oldest``.

        Returns:
            A list of processed GitHub activity events.

        Raises:
            InvalidEventTypeError: If ``event_type`` is not supported.
            InvalidDateError: If a date is invalid or the date range is
                reversed.
            UserNotFoundError: If the GitHub user does not exist.
            RateLimitError: If the GitHub API rate limit is exceeded.
            GitHubActivityError: If another API or application error occurs.
        """
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

        # When sorting oldest-first, all matching pages may need to be
        # fetched before the complete result can be sorted.
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

        events = self.sort_events(events, order=sort)

        # The limit is applied after sorting so that it always returns
        # the requested number of events from the correct end of the list.
        if limit is not None:
            events = events[:limit]

        return [
            self.handler.handle(event)
            for event in events
        ]

    @staticmethod
    def parse_date(date_string: str | None) -> date | None:
        """Convert a ``YYYY-MM-DD`` string into a date object.

        Args:
            date_string: Date string to parse, or ``None``.

        Returns:
            A ``date`` object, or ``None`` if no date was provided.

        Raises:
            InvalidDateError: If the date does not use the expected format.
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
        event: dict,
        event_type: str | None = None,
        repo: str | None = None,
        since: date | None = None,
        until: date | None = None,
    ) -> bool:
        """Check whether a GitHub event matches all supplied filters.

        Args:
            event: Raw GitHub event data.
            event_type: Optional GitHub event type to match.
            repo: Optional repository name to match.
            since: Optional earliest allowed event date.
            until: Optional latest allowed event date.

        Returns:
            ``True`` if the event satisfies every supplied filter;
            otherwise ``False``.
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

            # Support both "owner/repository" and just "repository".
            if (
                event_repo != repo
                and not event_repo.endswith(f"/{repo}")
            ):
                return False

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
        events: list[dict],
        event_type: str | None = None,
        repo: str | None = None,
        since: date | None = None,
        until: date | None = None,
    ) -> list[dict]:
        """Filter an existing list of raw GitHub events.

        This method is kept separate as a public utility for reuse and
        compatibility with existing callers.

        Args:
            events: Raw GitHub events to filter.
            event_type: Optional GitHub event type to match.
            repo: Optional repository name to match.
            since: Optional earliest allowed event date.
            until: Optional latest allowed event date.

        Returns:
            A list containing only events that match all supplied filters.
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
    def sort_events(
        events: list[dict],
        order: str = "newest",
    ) -> list[dict]:
        """Sort events by their creation timestamp.

        Args:
            events: Raw GitHub events to sort.
            order: Sort order. ``newest`` places recent events first;
                ``oldest`` places older events first.

        Returns:
            A new list containing the events in the requested order.
        """
        return sorted(
            events,
            key=lambda event: event.get("created_at", ""),
            reverse=(order == "newest"),
        )