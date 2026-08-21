"""Command-line interface for the GitHub Activity application."""

import argparse

import github_activity.exports
from github_activity.activity import (
    GitHubActivity,
    GitHubActivityError,
    UserNotFoundError,
    RateLimitError,
    InvalidEventTypeError,
)


def main():
    """Run the GitHub Activity command-line application.

    Parses command-line arguments, retrieves the user's GitHub
    activity, handles application-specific errors, and displays
    the results in the requested format.
    """
    parser = argparse.ArgumentParser(
        description="Display recent GitHub activity for a user."
    )

    # Required GitHub username.
    parser.add_argument(
        "username",
        help="GitHub username",
    )

    # Optional filters controlling how many and which events are shown.
    parser.add_argument(
        "--limit",
        type=int,
        choices=range(1, 301),
        metavar="N",
        help="Number of events to display (1-300)",
    )

    parser.add_argument(
        "--event",
        help="Filter activity by event type",
    )

    parser.add_argument(
        "--repo",
        help="Filter activity by repository name",
    )

    parser.add_argument(
        "--since",
        help="Show events after this date/time",
    )

    parser.add_argument(
        "--until",
        help="Show events before this date/time",
    )

    # Output format. Text is used by default for human-readable output.
    parser.add_argument(
        "--format",
        "-f",
        choices=["text", "json"],
        default="text",
        help="Output format (default: text)",
    )

    args = parser.parse_args()

    activity = GitHubActivity()

    try:
        # Retrieve activity using the requested filters.
        events = activity.get_activity(
            args.username,
            event_type=args.event,
            repo=args.repo,
            limit=args.limit,
            since=args.since,
            until=args.until,
        )

    # command-line error messages.
    except UserNotFoundError:
        print(
            f"Error: GitHub user '{args.username}' was not found."
        )
        return

    except RateLimitError:
        print(
            "Error: GitHub API rate limit exceeded "
            "or access denied."
        )
        return

    except InvalidEventTypeError as error:
        print(f"Error: {error}")
        return

    except GitHubActivityError as error:
        print(f"Error: {error}")
        return

    # Format and display the retrieved events.
    if args.format == "json":
        output = github_activity.exports.format_as_json(events)
        print(output)

    else:
        github_activity.exports.print_rich_activity(
            events,
            args.username,
        )


if __name__ == "__main__":
    main()