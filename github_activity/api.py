"""Client for interacting with the GitHub REST API."""

import random
import time

import requests


BASE_URL = "https://api.github.com"


class GitHubAPI:
    """Handle HTTP requests to the GitHub REST API."""

    def __init__(self) -> None:
        """Initialize a reusable HTTP session."""
        self.session = requests.Session()

    def get_user_events(
        self,
        username: str,
        limit: int | None = None,
        event_filter=None,
        fetch_all: bool = False,
    ) -> list[dict]:
        """Fetch public events for a GitHub user.

        GitHub returns user events in pages of up to 100 events. When
        an event filter is provided, additional pages are fetched until
        enough matching events have been collected.

        If ``fetch_all`` is ``True``, all available pages are fetched
        regardless of ``limit``. This is required when the caller needs
        to sort the complete result set, such as when sorting oldest-first.

        Args:
            username: GitHub username whose events should be fetched.
            limit: Maximum number of matching events to return when
                ``fetch_all`` is ``False``.
            event_filter: Optional callable that receives a raw event
                and returns ``True`` if the event should be included.
            fetch_all: Whether to fetch all available pages instead of
                stopping once ``limit`` matching events have been found.

        Returns:
            A list of raw GitHub event dictionaries.

        Raises:
            requests.HTTPError: If GitHub returns an HTTP error.
            requests.RequestException: If the request fails after all
                retry attempts.
        """
        events = []
        page = 1
        per_page = 100

        while True:
            params = {
                "page": page,
                "per_page": per_page,
            }

            page_events = self._get_page(username, params)

            # An empty page means there are no more events to fetch.
            if not page_events:
                break

            if event_filter:
                matching_events = [
                    event
                    for event in page_events
                    if event_filter(event)
                ]
            else:
                matching_events = page_events

            events.extend(matching_events)

            # When we have enough matching events, there is no need
            # to request additional pages unless all pages are required.
            if (
                limit is not None
                and not fetch_all
                and len(events) >= limit
            ):
                break

            # A page containing fewer than 100 events indicates the
            # final page of the available results.
            if len(page_events) < per_page:
                break

            page += 1

        # Limit the result here as well as in the loop because the
        # final page may contain more matching events than requested.
        if limit is not None and not fetch_all:
            return events[:limit]

        return events

    def _get_page(
        self,
        username: str,
        params: dict,
    ) -> list[dict]:
        """Fetch one page of GitHub user events with retry handling.

        Requests that fail because of rate limiting or temporary network
        errors are retried up to three times.

        Args:
            username: GitHub username whose events should be fetched.
            params: Query parameters for the GitHub API request.

        Returns:
            The decoded JSON response containing GitHub events.

        Raises:
            requests.HTTPError: If GitHub returns an HTTP error that
                cannot be recovered from.
            requests.RequestException: If a network request fails after
                all retry attempts.
        """
        url = f"{BASE_URL}/users/{username}/events"
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.session.get(
                    url,
                    params=params,
                    timeout=10,
                )

                # GitHub may respond with 403 or 429 when the API rate
                # limit has been reached. Retry when attempts remain.
                if response.status_code in (403, 429):
                    retry_after = int(
                        response.headers.get("Retry-After", 60)
                    )

                    if attempt < max_retries - 1:
                        print(
                            f"Rate limit reached. "
                            f"Retrying after {retry_after} seconds..."
                        )

                        # Add a small random delay to avoid retrying at
                        # exactly the same time as other requests.
                        time.sleep(
                            retry_after + random.uniform(5, 15)
                        )

                        continue

                response.raise_for_status()

                return response.json()

            except requests.HTTPError:
                # HTTP errors are handled by the caller, which converts
                # them into application-specific exceptions.
                raise

            except requests.RequestException as error:
                if attempt < max_retries - 1:
                    print(f"Network error: {error}")
                    time.sleep(5)
                    continue

                raise

        # This should only be reached if the retry loop exits without
        # returning or raising an exception.
        raise requests.HTTPError(
            "GitHub API request failed after all retry attempts."
        )