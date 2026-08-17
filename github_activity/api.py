import requests
import os
from datetime import datetime


class GitHubActivity:
    """
    GitHubActivity CLI

    Fetches and displays recent GitHub user activity in the terminal.
    Supports commands like push, issues, pull requests, comments, stars, and forks.
    """

    def __init__(self):
        # Commands that don't need a username argument
        self.global_commands = {
            "help": self.show_help,
            "start": self.show_start,
        }

        # Commands that act on a specific username's activity
        self.user_commands = {
            "all": self.show_all,
            "push": self.show_push,
            "issues": self.show_issues,
            "pullrequest": self.show_pullrequest,
            "issuecomment": self.show_issuecomment,
            "watch": self.show_watch,
            "fork": self.show_fork
        }

    # ---------- Helpers ----------
    def format_time(self, utc_str):
        """
        Convert GitHub UTC timestamp to local readable format.

        Args:
            utc_str (str): UTC timestamp from GitHub API (e.g., "2025-09-20T10:00:00Z")

        Returns:
            str: Formatted local datetime string (YYYY-MM-DD HH:MM:SS)
        """
        dt = datetime.fromisoformat(utc_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")

    def filter_events(self, activities, etype):
        """
        Filter GitHub activities by event type.

        Args:
            activities (list): List of GitHub events (dict)
            etype (str): Event type to filter (e.g., "PushEvent")

        Returns:
            list: Filtered list of events
        """
        return [activity for activity in activities if activity["type"] == etype]

    def show_filtered_events(self, username, activities, event_type, formatter, no_msg):
        """
        Generic method to display filtered events.

        Args:
            username (str): GitHub username
            activities (list): List of events
            event_type (str): Event type to filter
            formatter (function): Function to format each event for printing
            no_msg (str): Message to print if no events are found
        """
        events = self.filter_events(activities, event_type)
        if not events:
            print(no_msg.format(username=username))
            return
        for event in events:
            print(formatter(event))

    # ---------- UI ----------
    def show_start(self):
        """Display the welcome message and quickstart instructions."""
        print("\n👋 Welcome to Github-Activity CLI!")
        print("Github-Activity is a simple command line interface (CLI) to fetch the recent activity of a GitHub user.")
        print("\n👉 Quickstart examples:")
        print("   <username>")
        print("Type 'help' to see available commands, 'exit' to quit.\n")
    
    def show_help(self):
        """Display available commands and their descriptions."""
        print("""
        Available commands:
        <username>              Show all recent activity
        <username> push         Show push events
        <username> issues       Show issues activity
        <username> pullrequest  Show pull request activity
        <username> issuecomment Show issue comments
        <username> watch        Show stars
        <username> fork         Show forks
        """)

    # ---------- Fetch ----------
    def fetch_activity(self, username):
        """
        Fetch the latest events for a GitHub user from GitHub API.

        Args:
            username (str): GitHub username

        Returns:
            list or None: List of events if successful, None if error occurs
        """
        url = f"https://api.github.com/users/{username}/events?page=1&per_page=100"
        headers = {}
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers["Authorization"] = f"token {token}"

        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                print(f"❌ User {username} not found on GitHub.")
            elif response.status_code == 403 and response.headers.get("X-RateLimit-Remaining") == "0":
                print("⚠️  Rate limit exceeded. Try again later or use a GitHub token.")
            else:
                print(f"❌ HTTP error: {e}")
            return None
        except requests.exceptions.RequestException as e:
            print(f"❌ Network error: {e}")
            return None

        return response.json()

    # ---------- Show Methods ----------
    def show_all(self, username, activities):
        """Display all types of events for a user."""
        for activity in activities:
            etype = activity["type"]
            repo = activity["repo"]["name"]
            created = self.format_time(activity["created_at"])

            if etype == "PushEvent":
                print(f"🟢 Pushed {len(activity['payload']['commits'])} commits to {repo} at {created}")
            elif etype == "IssuesEvent":
                issue = activity["payload"]["issue"]
                print(f"🟠 {activity['payload']['action'].title()} issue #{issue['number']} "
                      f"in {repo}: \"{issue['title']}\" at {created}")
            elif etype == "PullRequestEvent":
                pr = activity["payload"]["pull_request"]
                print(f"🔵 {activity['payload']['action'].title()} pull request #{pr['number']} "
                      f"in {repo}: \"{pr['title']}\" at {created}")
            elif etype == "IssueCommentEvent":
                comment = activity["payload"]["comment"]
                print(f"💬 Commented in {repo}: \"{comment['body'][:40]}...\" at {created}")
            elif etype == "WatchEvent":
                print(f"⭐ Starred {repo} at {created}")
            elif etype == "ForkEvent":
                print(f"🍴 Forked {repo} to {activity['payload']['forkee']['full_name']} at {created}")

    def show_push(self, username, activities):
        """Display push events for a user."""
        self.show_filtered_events(
            username, activities, "PushEvent",
            lambda e: f"Pushed {len(e['payload']['commits'])} commits "
                      f"to {e['repo']['name']} at {self.format_time(e['created_at'])}",
            "⚠️ No push activity found for {username}!"
        )

    def show_issues(self, username, activities):
        """Display issues events for a user."""
        self.show_filtered_events(
            username, activities, "IssuesEvent",
            lambda e: f"{e['payload']['action'].title()} issue #{e['payload']['issue']['number']} "
                      f"in {e['repo']['name']}: \"{e['payload']['issue']['title']}\" "
                      f"at {self.format_time(e['created_at'])}",
            "⚠️  No issues activity found for {username}!"
        )

    def show_pullrequest(self, username, activities):
        """Display pull request events for a user."""
        self.show_filtered_events(
            username, activities, "PullRequestEvent",
            lambda e: f"{e['payload']['action'].title()} pull request #{e['payload']['pull_request']['number']} "
                      f"in {e['repo']['name']}: \"{e['payload']['pull_request']['title']}\" "
                      f"at {self.format_time(e['created_at'])}",
            "⚠️  No pull request activity found for {username}!"
        )

    def show_issuecomment(self, username, activities):
        """Display issue comment events for a user."""
        self.show_filtered_events(
            username, activities, "IssueCommentEvent",
            lambda e: f"Commented on issue #{e['payload']['issue']['number']} in {e['repo']['name']}: "
                      f"\"{e['payload']['comment']['body'][:50]}...\" "
                      f"at {self.format_time(e['created_at'])}",
            "⚠️  No issue comment activity found for {username}!"
        )

    def show_watch(self, username, activities):
        """Display star/watch events for a user."""
        self.show_filtered_events(
            username, activities, "WatchEvent",
            lambda e: f"Starred {e['repo']['name']} at {self.format_time(e['created_at'])}",
            "⚠️  No watch/star activity found for {username}!"
        )

    def show_fork(self, username, activities):
        """Display fork events for a user."""
        self.show_filtered_events(
            username, activities, "ForkEvent",
            lambda e: f"Forked {e['repo']['name']} to {e['payload']['forkee']['full_name']} "
                      f"at {self.format_time(e['created_at'])}",
            "⚠️  No fork activity found for {username}!"
        )

    # ---------- Runner ----------
    def run(self):
        """Run the interactive CLI loop."""
        self.show_start()

        while True:
            try:
                user_input = input("github-activity> ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nExiting Github Activity CLI. Bye! 👋")
                break

            if not user_input:
                continue
            if user_input.lower() in ("exit", "quit"):
                print("Goodbye! 👋")
                break

            parts = user_input.split()
            # Single command (either global or username)
            if len(parts) == 1:
                cmd = parts[0].lower()
                if cmd in self.global_commands:
                    self.global_commands[cmd]()
                else:
                    # Treat as GitHub username and show all activity
                    username = parts[0]
                    activities = self.fetch_activity(username)
                    if activities:
                        self.show_all(username, activities)
            # Username + specific command
            elif len(parts) > 1:
                username, cmd = parts[0], parts[1].lower()
                activities = self.fetch_activity(username)
                if not activities:
                    continue
                if cmd in self.user_commands:
                    self.user_commands[cmd](username, activities)
                else:
                    print(f"⚠️ Unknown command: {cmd}. Type 'help' to see commands.")


if __name__ == "__main__":
    # Run CLI directly if script is executed
    cli = GitHubActivity()
    cli.run()
