class GitHubActivity:
    def __init__(self, api, handler):
        self.api = api
        self.handler = handler

    def get_activity(self, username, event_type=None, repo=None, limit=None):
        events = self.api.get_user_events(username)

        events = self.filter_events(
            events,
            event_type=event_type,
            repo=repo
        )

        if limit is not None:
            events = events[:limit]

        return [
            self.handler.handle(event)
            for event in events
        ]

    @staticmethod
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