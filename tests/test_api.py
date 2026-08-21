from unittest.mock import MagicMock, patch

import pytest
import requests

from github_activity.api import GitHubAPI


def make_response(
    status_code=200,
    json_data=None,
    headers=None,
):
    response = MagicMock()

    response.status_code = status_code
    response.headers = headers or {}

    response.raise_for_status.return_value = None
    response.json.return_value = (
        json_data if json_data is not None else []
    )

    return response


# ---------------------------------------------------------
# Initialization
# ---------------------------------------------------------


def test_api_creates_session():
    api = GitHubAPI()

    assert isinstance(
        api.session,
        requests.Session,
    )


# ---------------------------------------------------------
# _get_page
# ---------------------------------------------------------


def test_get_page_success():
    api = GitHubAPI()

    response = make_response(
        json_data=[
            {"type": "PushEvent"},
        ]
    )

    api.session.get = MagicMock(
        return_value=response
    )

    result = api._get_page(
        "testuser",
        {
            "page": 1,
            "per_page": 100,
        },
    )

    assert result == [
        {"type": "PushEvent"},
    ]

    api.session.get.assert_called_once_with(
        "https://api.github.com/users/testuser/events",
        params={
            "page": 1,
            "per_page": 100,
        },
        timeout=10,
    )


def test_get_page_calls_raise_for_status():
    api = GitHubAPI()

    response = make_response(
        json_data=[]
    )

    api.session.get = MagicMock(
        return_value=response
    )

    api._get_page("testuser", {})

    response.raise_for_status.assert_called_once()


# ---------------------------------------------------------
# Pagination
# ---------------------------------------------------------


def test_get_user_events_single_page():
    api = GitHubAPI()

    page = [
        {"id": "1"},
        {"id": "2"},
    ]

    api._get_page = MagicMock(
        return_value=page
    )

    result = api.get_user_events(
        "testuser"
    )

    assert result == page
    api._get_page.assert_called_once()


def test_get_user_events_stops_on_empty_page():
    api = GitHubAPI()

    api._get_page = MagicMock(
        side_effect=[
            [{"id": "1"}],
            [],
        ]
    )

    result = api.get_user_events(
        "testuser"
    )

    assert result == [{"id": "1"}]
    assert api._get_page.call_count == 1


def test_get_user_events_fetches_multiple_pages():
    api = GitHubAPI()

    first_page = [
        {"id": str(i)}
        for i in range(100)
    ]

    second_page = [
        {"id": str(i)}
        for i in range(100, 150)
    ]

    api._get_page = MagicMock(
        side_effect=[
            first_page,
            second_page,
        ]
    )

    result = api.get_user_events(
        "testuser"
    )

    assert len(result) == 150
    assert api._get_page.call_count == 2


def test_get_user_events_passes_correct_page_numbers():
    api = GitHubAPI()

    first_page = [
        {"id": str(i)}
        for i in range(100)
    ]

    second_page = [
        {"id": str(i)}
        for i in range(100, 101)
    ]

    api._get_page = MagicMock(
        side_effect=[
            first_page,
            second_page,
        ]
    )

    api.get_user_events("testuser")

    assert api._get_page.call_args_list[0].args[1] == {
        "page": 1,
        "per_page": 100,
    }

    assert api._get_page.call_args_list[1].args[1] == {
        "page": 2,
        "per_page": 100,
    }


# ---------------------------------------------------------
# Limit
# ---------------------------------------------------------


def test_get_user_events_limit():
    api = GitHubAPI()

    events = [
        {"id": str(i)}
        for i in range(100)
    ]

    api._get_page = MagicMock(
        return_value=events
    )

    result = api.get_user_events(
        "testuser",
        limit=10,
    )

    assert len(result) == 10
    assert result == events[:10]


def test_limit_stops_pagination_when_enough_events():
    api = GitHubAPI()

    first_page = [
        {"id": str(i)}
        for i in range(100)
    ]

    api._get_page = MagicMock(
        return_value=first_page
    )

    result = api.get_user_events(
        "testuser",
        limit=10,
    )

    assert len(result) == 10
    assert api._get_page.call_count == 1


# ---------------------------------------------------------
# Event filter
# ---------------------------------------------------------


def test_get_user_events_event_filter():
    api = GitHubAPI()

    events = [
        {"id": "1", "type": "PushEvent"},
        {"id": "2", "type": "IssuesEvent"},
        {"id": "3", "type": "PushEvent"},
    ]

    api._get_page = MagicMock(
        return_value=events
    )

    result = api.get_user_events(
        "testuser",
        event_filter=lambda event: (
            event["type"] == "PushEvent"
        ),
    )

    assert result == [
        {"id": "1", "type": "PushEvent"},
        {"id": "3", "type": "PushEvent"},
    ]


def test_event_filter_allows_pagination_until_limit():
    api = GitHubAPI()

    first_page = [
        {
            "id": str(i),
            "type": "IssuesEvent",
        }
        for i in range(100)
    ]

    first_page[99]["type"] = "PushEvent"

    second_page = [
        {
            "id": str(i),
            "type": "PushEvent",
        }
        for i in range(100, 110)
    ]

    api._get_page = MagicMock(
        side_effect=[
            first_page,
            second_page,
        ]
    )

    result = api.get_user_events(
        "testuser",
        limit=5,
        event_filter=lambda event: (
            event["type"] == "PushEvent"
        ),
    )

    assert len(result) == 5
    assert api._get_page.call_count == 2


# ---------------------------------------------------------
# fetch_all
# ---------------------------------------------------------


def test_fetch_all_ignores_limit_for_pagination():
    api = GitHubAPI()

    first_page = [
        {"id": str(i)}
        for i in range(100)
    ]

    second_page = [
        {"id": str(i)}
        for i in range(100, 120)
    ]

    api._get_page = MagicMock(
        side_effect=[
            first_page,
            second_page,
        ]
    )

    result = api.get_user_events(
        "testuser",
        limit=5,
        fetch_all=True,
    )

    assert len(result) == 120
    assert api._get_page.call_count == 2


# ---------------------------------------------------------
# HTTP errors / retries
# ---------------------------------------------------------


def test_get_page_http_error_is_raised():
    api = GitHubAPI()

    response = make_response(
        status_code=500
    )

    error = requests.HTTPError("Server error")
    error.response = response

    response.raise_for_status.side_effect = error

    api.session.get = MagicMock(
        return_value=response
    )

    with pytest.raises(requests.HTTPError):
        api._get_page("testuser", {})


def test_get_page_retries_rate_limit():
    api = GitHubAPI()

    rate_response = make_response(
        status_code=429,
        headers={
            "Retry-After": "10",
        },
    )

    success_response = make_response(
        status_code=200,
        json_data=[
            {"id": "1"},
        ],
    )

    api.session.get = MagicMock(
        side_effect=[
            rate_response,
            success_response,
        ]
    )

    with patch(
        "github_activity.api.time.sleep"
    ) as mock_sleep, patch(
        "github_activity.api.random.uniform",
        return_value=7,
    ):

        result = api._get_page(
            "testuser",
            {},
        )

    assert result == [{"id": "1"}]
    assert api.session.get.call_count == 2

    mock_sleep.assert_called_once_with(17)


def test_get_page_retries_network_error():
    api = GitHubAPI()

    success_response = make_response(
        json_data=[
            {"id": "1"},
        ]
    )

    api.session.get = MagicMock(
        side_effect=[
            requests.ConnectionError("Network down"),
            success_response,
        ]
    )

    with patch(
        "github_activity.api.time.sleep"
    ) as mock_sleep:

        result = api._get_page(
            "testuser",
            {},
        )

    assert result == [{"id": "1"}]
    assert api.session.get.call_count == 2
    mock_sleep.assert_called_once_with(5)


def test_get_page_network_error_after_retries():
    api = GitHubAPI()

    api.session.get = MagicMock(
        side_effect=requests.ConnectionError(
            "Network down"
        )
    )

    with patch(
        "github_activity.api.time.sleep"
    ) as mock_sleep:

        with pytest.raises(
            requests.ConnectionError
        ):
            api._get_page(
                "testuser",
                {},
            )

    assert api.session.get.call_count == 3
    assert mock_sleep.call_count == 2


def test_get_page_rate_limit_after_all_retries():
    api = GitHubAPI()

    response = make_response(
        status_code=429,
        headers={
            "Retry-After": "1",
        },
    )

    error = requests.HTTPError(
        "Too many requests"
    )

    response.raise_for_status.side_effect = error

    api.session.get = MagicMock(
        return_value=response
    )

    with patch(
        "github_activity.api.time.sleep"
    ) as mock_sleep, patch(
        "github_activity.api.random.uniform",
        return_value=5,
    ):

        with pytest.raises(requests.HTTPError):
            api._get_page(
                "testuser",
                {},
            )

    assert api.session.get.call_count == 3
    assert mock_sleep.call_count == 2