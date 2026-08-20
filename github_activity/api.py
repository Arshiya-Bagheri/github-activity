import random
import time

import requests


BASE_URL = "https://api.github.com"


class GitHubAPI:
    def __init__(self):
        self.session = requests.Session()

    def get_user_events(self, username):
        url = f"{BASE_URL}/users/{username}/events"
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=10)

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