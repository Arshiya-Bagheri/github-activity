import requests
from datetime import datetime


BASE_URL = "https://api.github.com"


class GitHubAPI():
    def __init__(self):
        self.session = requests.Session()

    def get_user_events(self, username):
        url = f"{BASE_URL}/users/{username}/events"
        response = self.session.get(url, timeout=10)
        response.raise_for_status()
        return response.json()


