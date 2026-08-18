"""Command-line interface for the weather application."""

import argparse
import requests

from github_activity.api import GitHubAPI
from github_activity.handler import EventHandler
from github_activity.activity import GitHubActivity


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
    handler = EventHandler()
    activity = GitHubActivity(api, handler)

    try:
        events = activity.get_activity(
        args.username,
        event_type=args.event,
        repo=args.repo,
        limit=args.limit
    )

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
    
    for event in events:
        print(event)

if __name__ == "__main__":
    main()

