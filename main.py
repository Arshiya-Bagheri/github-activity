"""Command-line interface for the weather application."""

import argparse
import requests

from github_activity.api import GitHubAPI
from github_activity.handler import EventHandler


def filter_events(events, event_type=None, repo=None):
    if event_type:
        events = [
            event for event in events
            if event["type"] == event_type
        ]

    if repo:
        events = [
            event for event in events
            if event["repo"]["name"].endswith(f"/{repo}")
        ]

    return events


def main():
    parser = argparse.ArgumentParser(
        description="Display recent GitHub activity for a user."
    )

    parser.add_argument(
        "username",
        help="GitHub username"
    )

    parser.add_argument(
        "--limit",
        type=int,
        help="Number of events to display"
    )

    parser.add_argument(
        "--event",
        help="Filter activity by event type"
    )

    parser.add_argument(
        "--repo",
        help="Filter activity by repository name"
    )

    args = parser.parse_args()

    api = GitHubAPI()

    api = GitHubAPI()

    try:
        events = api.get_user_events(args.username)

    except requests.HTTPError as error:
        if error.response.status_code == 404:
            print(f"Error: GitHub user '{args.username}' was not found.")
        elif error.response.status_code == 403:
            print("Error: GitHub API rate limit exceeded or access denied.")
        else:
            print(
                f"Error: GitHub API returned "
                f"status {error.response.status_code}."
            )

        return

    except requests.RequestException as error:
        print(f"Error: Could not connect to GitHub: {error}")
        return
    
    events = filter_events(
        events,
        event_type=args.event,
        repo=args.repo
    )

    handler = EventHandler()

    for event in events[:args.limit]:
        print(handler.handle(event))


if __name__ == "__main__":
    main()

