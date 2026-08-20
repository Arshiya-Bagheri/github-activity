import random
import time

import requests


BASE_URL = "https://api.github.com"


class GitHubAPI:
    def __init__(self):
        self.session = requests.Session()

    def get_user_events(self, username, limit=None):
        """
        Fetch recent public events for a GitHub user.

        If a limit is provided, additional API pages are fetched
        until the requested number of events is collected or
        GitHub returns an empty page.
        """
        events = []
        page = 1
        per_page = 100

        while True:
            if limit is not None and len(events) >= limit:
                break

            params = {
                "page": page,
                "per_page": per_page,
            }

            page_events = self._get_page(username, params)

            if not page_events:
                break

            events.extend(page_events)

            if len(page_events) < per_page:
                break

            page += 1

        if limit is not None:
            return events[:limit]

        return events

    def _get_page(self, username, params):
        """
        Fetch one page of GitHub user events with retry handling.
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

                if response.status_code in (403, 429):
                    retry_after = int(
                        response.headers.get("Retry-After", 60)
                    )

                    if attempt < max_retries - 1:
                        print(
                            f"Rate limit reached. "
                            f"Retrying after {retry_after} seconds..."
                        )

                        time.sleep(
                            retry_after + random.uniform(5, 15)
                        )

                        continue

                response.raise_for_status()

                return response.json()

            except requests.HTTPError:
                raise

            except requests.RequestException as error:
                if attempt < max_retries - 1:
                    print(f"Network error: {error}")
                    time.sleep(5)
                    continue

                raise

        raise requests.HTTPError(
            "GitHub API request failed after all retry attempts."
        )