class EventHandler:
    def handle(self, event):
        event_type = event["type"]

        handler = getattr(self, f"handle_{event_type}", self.handle_unknown)
        return handler(event)

    def handle_PushEvent(self, event):
        repo = event["repo"]["name"]
        branch = event["payload"]["ref"].removeprefix("refs/heads/")
        commits = event["payload"].get("commits", [])

        return f"Pushed {len(commits)} commits to {repo} on {branch}"

    def handle_CreateEvent(self, event):
        repo = event["repo"]["name"]
        payload = event["payload"]

        ref_type = payload["ref_type"]
        ref = payload["ref"]

        return f"Created {ref_type} {ref} in {repo}"

    def handle_IssueCommentEvent(self, event):
        repo = event["repo"]["name"]
        comment = event["payload"]["comment"]["body"]

        return f"Commented on an issue in {repo}: {comment}"

    def handle_PullRequestReviewEvent(self, event):
        repo = event["repo"]["name"]
        state = event["payload"]["review"]["state"]

        return f"Reviewed a pull request in {repo}: {state}"

    def handle_PullRequestReviewCommentEvent(self, event):
        repo = event["repo"]["name"]
        comment = event["payload"]["comment"]["body"]

        return f"Commented on a pull request in {repo}: {comment}"

    def handle_DeleteEvent(self, event):
        repo = event["repo"]["name"]
        ref = event["payload"]["ref"]

        return f"Deleted {event['payload']['ref_type']} {ref}"

    def handle_PullRequestEvent(self, event):
        payload = event["payload"]

        action = payload["action"]
        number = payload["number"]
        repo = event["repo"]["name"]

        return f"Pull request #{number} {action} in {repo}"

    def handle_IssuesEvent(self, event):
        payload = event["payload"]

        action = payload["action"]
        number = payload["issue"]["number"]
        title = payload["issue"]["title"]
        repo = event["repo"]["name"]

        return f"Issue #{number} {action} in {repo}: {title}"

    def handle_WatchEvent(self, event):
        repo = event["repo"]["name"]

        return f"Starred {repo}"

    def handle_PublicEvent(self, event):
        repo = event["repo"]["name"]

        return f"Made {repo} public"

    def handle_ReleaseEvent(self, event):
        repo = event["repo"]["name"]
        action = event["payload"]["action"]
        tag = event["payload"]["release"]["tag_name"]

        return f"Release {tag} {action} in {repo}"

    def handle_ForkEvent(self, event):
        original_repo = event["repo"]["name"]
        forked_repo = event["payload"]["forkee"]["full_name"]

        return f"Forked {original_repo} to {forked_repo}"

    def handle_unknown(self, event):
        return f"Unsupported event: {event['type']}"