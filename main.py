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

    parser.add_argument(
        "--limit",
        type=int,
        help="Number of events to display"
    )
    
    args = parser.parse_args()

    api = GitHubAPI()

    events = api.get_user_events(args.username)

    handler = EventHandler()

    for event in events[:args.limit]:
        print(handler.handle(event))


if __name__ == "__main__":
    main()

