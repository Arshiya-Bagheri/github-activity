import requests
import time
import random


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

                if response.status_code == 403:
                    retry_after = int(
                        response.headers.get("Retry-After", 60)
                    )

                    print(
                        f"Rate limit reached. "
                        f"Waiting {retry_after} seconds..."
                    )

                    time.sleep(
                        retry_after + random.uniform(5, 15)
                    )
                    continue

                response.raise_for_status()

                return response.json()

            except requests.HTTPError as error:
                status_code = error.response.status_code

                if status_code == 429:
                    retry_after = int(
                        error.response.headers.get("Retry-After", 60)
                    )

                    print(
                        f"API rate limit exceeded. "
                        f"Retrying after {retry_after} seconds..."
                    )

                    time.sleep(
                        retry_after + random.uniform(5, 15)
                    )
                    continue

                raise

            except requests.RequestException as error:
                print(f"Network error: {error}")

                if attempt < max_retries - 1:
                    time.sleep(5)
                    continue

                raise