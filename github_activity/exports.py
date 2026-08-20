import json

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text


console = Console()


EVENT_STYLES = {
    "PushEvent": ("PUSH", "green", "🚀"),
    "CreateEvent": ("CREATE", "cyan", "✨"),
    "IssueCommentEvent": ("COMMENT", "yellow", "💬"),
    "PullRequestReviewEvent": ("REVIEW", "magenta", "👀"),
    "PullRequestReviewCommentEvent": ("REVIEW", "magenta", "💬"),
    "DeleteEvent": ("DELETE", "red", "🗑"),
    "PullRequestEvent": ("PULL REQUEST", "blue", "🔀"),
    "IssuesEvent": ("ISSUE", "yellow", "🐛"),
    "WatchEvent": ("STAR", "bright_yellow", "⭐"),
    "PublicEvent": ("PUBLIC", "green", "🌐"),
    "ReleaseEvent": ("RELEASE", "bright_magenta", "📦"),
    "ForkEvent": ("FORK", "cyan", "🍴"),
}


def format_as_text(event):
    """Format an Activity object as plain human-readable text."""

    timestamp = event.timestamp.strftime("%Y-%m-%d %H:%M:%S")

    return (
        f"[{timestamp}] "
        f"{event.description} "
        f"by {event.actor}"
    )


def format_as_json(events):
    """Format Activity objects as JSON."""

    data = [
        {
            "timestamp": event.timestamp.isoformat(),
            "type": event.type,
            "actor": event.actor,
            "description": event.description,
            "details": event.details,
        }
        for event in events
    ]

    return json.dumps(data, indent=2)


def print_rich_activity(events, username):
    """
    Display GitHub activity using Rich.

    This function is responsible only for terminal presentation.
    It does not modify Activity objects or application logic.
    """

    if not events:
        console.print(
            Panel(
                f"[yellow]No activity found for [bold]{username}[/bold].[/yellow]",
                title="GitHub Activity",
                border_style="yellow",
            )
        )
        return

    # ---------------------------------------------------------
    # Header
    # ---------------------------------------------------------

    header = Text()
    header.append("GitHub Activity\n", style="bold cyan")
    header.append(f"User: ", style="bold")
    header.append(username, style="bold white")
    header.append("    ")
    header.append("Events: ", style="bold")
    header.append(str(len(events)), style="bold green")

    console.print(
        Panel(
            header,
            border_style="cyan",
            padding=(0, 2),
        )
    )

    # ---------------------------------------------------------
    # Activity table
    # ---------------------------------------------------------

    table = Table(
        show_header=True,
        show_lines=True,
        header_style="bold white",
        border_style="bright_black",
        expand=True,
        padding=(0, 1),
    )

    table.add_column(
        "Time",
        style="dim",
        no_wrap=True,
        width=18,
    )

    table.add_column(
        "Event",
        no_wrap=True,
        width=20,
    )

    table.add_column(
        "Activity",
        ratio=1,
    )

    table.add_column(
        "Actor",
        style="bright_black",
        no_wrap=True,
    )

    for event in events:
        label, color, icon = EVENT_STYLES.get(
            event.type,
            ("UNKNOWN", "white", "❓"),
        )

        timestamp = event.timestamp.strftime(
            "%b %d %H:%M:%S"
        )

        event_text = Text()
        event_text.append(f"{icon} ", style=color)
        event_text.append(label, style=f"bold {color}")

        description = Text(
            event.description,
            overflow="ellipsis",
        )

        table.add_row(
            timestamp,
            event_text,
            description,
            event.actor,
        )

    console.print(table)

    # ---------------------------------------------------------
    # Footer
    # ---------------------------------------------------------

    console.print(
        f"\n[bold green]✓[/bold green] "
        f"[dim]{len(events)} event(s) displayed.[/dim]"
    )