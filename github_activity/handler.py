class EventHandler:
    def handle(self, event):
        event_type = event["type"]

        handler = getattr(self, f"handle_{event_type}", self.handle_unknown)
        return handler(event)

    def handle_PushEvent(self, event):
        repo = event["repo"]["name"]
        branch = event["payload"]["ref"]

        return f"Pushed to {repo} on {branch}"

    def handle_CreateEvent(self, event):
        repo = event["repo"]["name"]
        ref = event["payload"]["ref"]

        return f"Created {event['payload']['ref_type']} {ref} in {repo}"

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

    def handle_unknown(self, event):
        return f"Unsupported event: {event['type']}"