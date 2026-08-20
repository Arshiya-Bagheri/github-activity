import requests
import time
import random
from github_activity.activity import GitHubActivityError
from github_activity.activity import RateLimitError

BASE_URL = "https://api.github.com"


class GitHubAPI():
    def __init__(self):
        self.session = requests.Session()

    def get_user_events(self, username):
        url = f"{BASE_URL}/users/{username}/events"
        max_retries = 3

        for attempt in range(max_retries):
            try:
                response = self.session.get(url, timeout=10)
                
                if response.status_code == 403:
                    retry_after = int(response.headers.get('Retry-After', 60))
                    print(f"Rate limit reached. Waiting {retry_after} seconds...")
                    time.sleep(retry_after + random.uniform(5, 15))
                    continue
                
                response.raise_for_status()
                
                return response.json()
            
            except requests.exceptions.HTTPError as error:
                status_code = error.response.status_code

                if status_code == 404:
                    from github_activity.activity import UserNotFoundError
                    raise UserNotFoundError(username) from error

                if status_code == 429:
                    retry_after = int(error.response.headers.get('Retry-After', 60))
                    print(f"API rate limit exceeded. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after + random.uniform(5, 15))
                    continue

                if status_code == 403 and 'rate_limit' in str(error):
                    retry_after = int(error.response.headers.get('Retry-After', 60))
                    print(f"Rate limit hit. Retrying after {retry_after} seconds...")
                    time.sleep(retry_after + random.uniform(5, 15))
                    continue

                raise GitHubActivityError(
                    f"GitHub API returned status {status_code}."
                ) from error

            except requests.exceptions.RequestException as error:
                print(f"Network error: {error}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                continue
            
            except Exception as error:
                print(f"❌ Unexpected error: {error}")
                if attempt < max_retries - 1:
                    time.sleep(5)
                continue

        # If we reach here after all retries, raise an exception
        raise RateLimitError(f"Rate limit exceeded after {max_retries} attempts.")
