"""Command-line interface for the GitHub Activity application."""

import argparse

import github_activity.exports
from github_activity.activity import (
    GitHubActivity,
    GitHubActivityError,
    UserNotFoundError,
    RateLimitError,
)




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

    parser.add_argument(
        "--format", "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)"
    )

    args = parser.parse_args()

    activity = GitHubActivity()

    try:
        events = activity.get_activity(
            args.username,
            event_type=args.event,
            repo=args.repo,
            limit=args.limit
        )

    except UserNotFoundError:
        print(f"Error: GitHub user '{args.username}' was not found.")
        return

    except RateLimitError:
        print("Error: GitHub API rate limit exceeded or access denied.")
        return

    except GitHubActivityError as error:
        print(f"Error: {error}")
        return

    
    if args.format == "json":
        output = github_activity.exports.format_as_json(events)
        print(output)

    else: 
        for event in events:
            print(github_activity.exports.format_as_text(event))



if __name__ == "__main__":
    main()