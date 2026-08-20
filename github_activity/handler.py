from datetime import datetime

from github_activity.models import Activity


class EventHandler:
    def handle(self, event):
        """Convert a raw GitHub event into an Activity object."""
        event_type = event.get("type", "UnknownEvent")

        handler = getattr(
            self,
            f"handle_{event_type}",
            self.handle_unknown,
        )

        description, details = handler(event)

        created_at = event.get("created_at")

        if created_at:
            timestamp = datetime.fromisoformat(
                created_at.replace("Z", "+00:00")
            ).astimezone()
        else:
            timestamp = datetime.now().astimezone()

        actor = event.get("actor", {}).get("login", "unknown")

        return Activity(
            timestamp=timestamp,
            type=event_type,
            actor=actor,
            description=description,
            details=details,
        )

    def handle_PushEvent(self, event):
        repo = event.get("repo", {}).get("name", "unknown repository")
        payload = event.get("payload", {})

        ref = payload.get("ref", "")
        branch = ref.removeprefix("refs/heads/") or "unknown branch"

        commits = payload.get("commits", [])

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
        repo = event.get("repo", {}).get("name", "unknown repository")
        payload = event.get("payload", {})

        ref_type = payload.get("ref_type", "unknown")
        ref = payload.get("ref")

        if ref:
            description = (
                f"Created {ref_type} {ref} in {repo}"
            )
        else:
            description = (
                f"Created a {ref_type} in {repo}"
            )

        details = {
            "repository": repo,
            "ref_type": ref_type,
            "ref": ref,
        }

        return description, details

    def handle_IssueCommentEvent(self, event):
        repo = event.get("repo", {}).get("name", "unknown repository")
        payload = event.get("payload", {})

        comment = payload.get("comment", {})
        issue = payload.get("issue", {})

        comment_body = comment.get("body")
        issue_number = issue.get("number")

        if comment_body:
            description = (
                f"Commented on issue #{issue_number} "
                f"in {repo}: {comment_body}"
            )
        else:
            description = (
                f"Commented on issue #{issue_number} "
                f"in {repo}"
            )

        details = {
            "repository": repo,
            "issue_number": issue_number,
            "comment": comment_body,
        }

        return description, details

    def handle_PullRequestReviewEvent(self, event):
        repo = event.get("repo", {}).get("name", "unknown repository")
        payload = event.get("payload", {})

        review = payload.get("review", {})
        pull_request = payload.get("pull_request", {})

        state = review.get("state", "unknown")
        pull_request_number = pull_request.get("number")

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
        repo = event.get("repo", {}).get("name", "unknown repository")
        payload = event.get("payload", {})

        comment = payload.get("comment", {})
        pull_request = payload.get("pull_request", {})

        comment_body = comment.get("body")
        pull_request_number = pull_request.get("number")

        if comment_body:
            description = (
                f"Commented on pull request "
                f"#{pull_request_number} in {repo}: {comment_body}"
            )
        else:
            description = (
                f"Commented on pull request "
                f"#{pull_request_number} in {repo}"
            )

        details = {
            "repository": repo,
            "pull_request_number": pull_request_number,
            "comment": comment_body,
        }

        return description, details

    def handle_DeleteEvent(self, event):
        repo = event.get("repo", {}).get("name", "unknown repository")
        payload = event.get("payload", {})

        ref_type = payload.get("ref_type", "unknown")
        ref = payload.get("ref", "unknown")

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
        repo = event.get("repo", {}).get("name", "unknown repository")
        payload = event.get("payload", {})

        action = payload.get("action", "updated")
        number = payload.get("number")

        pull_request = payload.get("pull_request", {})
        title = pull_request.get("title")

        if title:
            description = (
                f"Pull request #{number} {action} "
                f"in {repo}: {title}"
            )
        else:
            description = (
                f"Pull request #{number} {action} "
                f"in {repo}"
            )

        details = {
            "repository": repo,
            "action": action,
            "pull_request_number": number,
            "title": title,
        }

        return description, details

    def handle_IssuesEvent(self, event):
        repo = event.get("repo", {}).get("name", "unknown repository")
        payload = event.get("payload", {})

        action = payload.get("action", "updated")

        issue = payload.get("issue", {})
        number = issue.get("number")
        title = issue.get("title")

        if title:
            description = (
                f"Issue #{number} {action} "
                f"in {repo}: {title}"
            )
        else:
            description = (
                f"Issue #{number} {action} "
                f"in {repo}"
            )

        details = {
            "repository": repo,
            "action": action,
            "issue_number": number,
            "title": title,
        }

        return description, details

    def handle_WatchEvent(self, event):
        repo = event.get("repo", {}).get("name", "unknown repository")
        payload = event.get("payload", {})

        action = payload.get("action", "started")

        if action == "started":
            description = f"Starred {repo}"
        else:
            description = f"Watch action '{action}' on {repo}"

        details = {
            "repository": repo,
            "action": action,
        }

        return description, details

    def handle_PublicEvent(self, event):
        repo = event.get("repo", {}).get("name", "unknown repository")

        description = f"Made {repo} public"

        details = {
            "repository": repo,
        }

        return description, details

    def handle_ReleaseEvent(self, event):
        repo = event.get("repo", {}).get("name", "unknown repository")
        payload = event.get("payload", {})

        action = payload.get("action", "updated")

        release = payload.get("release", {})
        tag = release.get("tag_name")

        if tag:
            description = (
                f"Release {tag} {action} in {repo}"
            )
        else:
            description = (
                f"Release {action} in {repo}"
            )

        details = {
            "repository": repo,
            "action": action,
            "tag": tag,
        }

        return description, details

    def handle_ForkEvent(self, event):
        original_repo = event.get("repo", {}).get(
            "name",
            "unknown repository",
        )

        payload = event.get("payload", {})
        forkee = payload.get("forkee", {})

        forked_repo = forkee.get(
            "full_name",
            "unknown repository",
        )

        description = (
            f"Forked {original_repo} to {forked_repo}"
        )

        details = {
            "original_repository": original_repo,
            "forked_repository": forked_repo,
        }

        return description, details

    def handle_unknown(self, event):
        event_type = event.get("type", "UnknownEvent")

        description = f"Unsupported event: {event_type}"

        details = {
            "event_type": event_type,
        }

        return description, details