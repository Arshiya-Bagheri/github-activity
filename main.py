"""Command-line interface for the weather application."""

import argparse

from github_activity.api import GitHubAPI
from github_activity.handler import EventHandler


def main():

    parser = argparse.ArgumentParser(
        prog="Github-Activity API",
        description="Get the recent GitHub activity of a user."
    )

    parser.add_argument(
        "username",
        help="GitHub username to fetch activity for"
    )

    args = parser.parse_args()

    api = GitHubAPI()

    events = api.get_user_events(args.username)

    handler = EventHandler()

    for event in events:
        result = handler.handle(event)
        print(result)


if __name__ == "__main__":
    main()

