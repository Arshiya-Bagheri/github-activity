"""Command-line interface for the weather application."""

from github_activity.api import GitHubAPI
from github_activity.handler import EventHandler


def main():
    username = "xai"

    api = GitHubAPI()
    events = api.get_user_events(username)
    handler = EventHandler()

    for event in events:
        result = handler.handle(event)
        print(result)


if __name__ == "__main__":
    main()


if __name__ == "__main__":
    main()