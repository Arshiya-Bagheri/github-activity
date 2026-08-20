from datetime import datetime

from github_activity.models import Activity


class EventHandler:
    def handle(self, event):
        event_type = event["type"]

        handler = getattr(
            self,
            f"handle_{event_type}",
            self.handle_unknown,
        )

        description, details = handler(event)

        timestamp = datetime.fromisoformat(
            event["created_at"].replace("Z", "+00:00")
        ).astimezone()

        return Activity(
            timestamp=timestamp,
            type=event_type,
            actor=event["actor"]["login"],
            description=description,
            details=details,
        )

    def handle_PushEvent(self, event):
        repo = event["repo"]["name"]
        branch = event["payload"]["ref"].removeprefix("refs/heads/")
        commits = event["payload"].get("commits", [])

        description = (
            f"Pushed {len(commits)} commits "
            f"to {repo} on {branch}"
        )

        details = {
            "repository": repo,
            "branch": branch,
            "commits": len(commits),
        }

        return description, details

    def handle_CreateEvent(self, event):
        repo = event["repo"]["name"]
        payload = event["payload"]

        ref_type = payload["ref_type"]
        ref = payload["ref"]

        description = (
            f"Created {ref_type} {ref} in {repo}"
        )

        details = {
            "repository": repo,
            "ref_type": ref_type,
            "ref": ref,
        }

        return description, details

    def handle_IssueCommentEvent(self, event):
        repo = event["repo"]["name"]
        payload = event["payload"]

        comment = payload["comment"]["body"]
        issue_number = payload["issue"]["number"]

        description = (
            f"Commented on issue #{issue_number} "
            f"in {repo}: {comment}"
        )

        details = {
            "repository": repo,
            "issue_number": issue_number,
            "comment": comment,
        }

        return description, details

    def handle_PullRequestReviewEvent(self, event):
        repo = event["repo"]["name"]
        payload = event["payload"]

        state = payload["review"]["state"]
        pull_request_number = payload["pull_request"]["number"]

        description = (
            f"Reviewed pull request #{pull_request_number} "
            f"in {repo}: {state}"
        )

        details = {
            "repository": repo,
            "pull_request_number": pull_request_number,
            "review_state": state,
        }

        return description, details

    def handle_PullRequestReviewCommentEvent(self, event):
        repo = event["repo"]["name"]
        payload = event["payload"]

        comment = payload["comment"]["body"]
        pull_request_number = payload["pull_request"]["number"]

        description = (
            f"Commented on pull request "
            f"#{pull_request_number} in {repo}: {comment}"
        )

        details = {
            "repository": repo,
            "pull_request_number": pull_request_number,
            "comment": comment,
        }

        return description, details

    def handle_DeleteEvent(self, event):
        repo = event["repo"]["name"]
        payload = event["payload"]

        ref_type = payload["ref_type"]
        ref = payload["ref"]

        description = (
            f"Deleted {ref_type} {ref} from {repo}"
        )

        details = {
            "repository": repo,
            "ref_type": ref_type,
            "ref": ref,
        }

        return description, details

    def handle_PullRequestEvent(self, event):
        repo = event["repo"]["name"]
        payload = event["payload"]

        action = payload["action"]
        number = payload["number"]
        title = payload["pull_request"]["title"]

        description = (
            f"Pull request #{number} {action} "
            f"in {repo}: {title}"
        )

        details = {
            "repository": repo,
            "action": action,
            "pull_request_number": number,
            "title": title,
        }

        return description, details

    def handle_IssuesEvent(self, event):
        repo = event["repo"]["name"]
        payload = event["payload"]

        action = payload["action"]
        number = payload["issue"]["number"]
        title = payload["issue"]["title"]

        description = (
            f"Issue #{number} {action} "
            f"in {repo}: {title}"
        )

        details = {
            "repository": repo,
            "action": action,
            "issue_number": number,
            "title": title,
        }

        return description, details

    def handle_WatchEvent(self, event):
        repo = event["repo"]["name"]
        action = event["payload"].get("action", "started")

        description = f"Starred {repo}"

        details = {
            "repository": repo,
            "action": action,
        }

        return description, details

    def handle_PublicEvent(self, event):
        repo = event["repo"]["name"]

        description = f"Made {repo} public"

        details = {
            "repository": repo,
        }

        return description, details

    def handle_ReleaseEvent(self, event):
        repo = event["repo"]["name"]
        payload = event["payload"]

        action = payload["action"]
        tag = payload["release"]["tag_name"]

        description = (
            f"Release {tag} {action} in {repo}"
        )

        details = {
            "repository": repo,
            "action": action,
            "tag": tag,
        }

        return description, details

    def handle_ForkEvent(self, event):
        original_repo = event["repo"]["name"]
        forked_repo = event["payload"]["forkee"]["full_name"]

        description = (
            f"Forked {original_repo} to {forked_repo}"
        )

        details = {
            "original_repository": original_repo,
            "forked_repository": forked_repo,
        }

        return description, details

    def handle_unknown(self, event):
        event_type = event["type"]

        description = f"Unsupported event: {event_type}"

        details = {
            "event_type": event_type,
        }

        return description, details