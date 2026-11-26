from typing import Any
from unittest.mock import MagicMock

from personal_assistant.gmail.search import MAX_RESULTS_CAP, search_emails


def make_service(
    list_response: dict[str, Any], raw_message: dict[str, Any]
) -> tuple[MagicMock, MagicMock]:
    service = MagicMock()
    messages = service.users.return_value.messages.return_value
    messages.list.return_value.execute.return_value = list_response
    messages.get.return_value.execute.return_value = raw_message
    return service, messages


def make_raw() -> dict[str, Any]:
    return {
        "id": "msg-1",
        "threadId": "thread-1",
        "snippet": "Hello there",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Finish setting up your account"},
                {"name": "From", "value": "Google <no-reply@google.com>"},
                {"name": "Date", "value": "Tue, 17 Nov 2026 11:27:22 -0800"},
            ]
        },
    }


def test_return_one_summary_per_message() -> None:
    service, messages = make_service(
        {"messages": [{"id": "msg-1", "threadId": "thread-1"}]}, make_raw()
    )

    results = search_emails(service, "from:google.com")

    assert len(results) == 1
    assert results[0].subject == "Finish setting up your account"
    assert messages.list.call_args.kwargs["q"] == "from:google.com"


def test_no_results_returns_empty_list() -> None:
    service, messages = make_service({}, make_raw())

    results = search_emails(service, "from:google.com")

    assert len(results) == 0
    messages.get.assert_not_called()


def test_max_results_is_capped() -> None:
    service, messages = make_service(
        {"messages": [{"id": "msg-1", "threadId": "thread-1"}]}, make_raw()
    )

    search_emails(service, "from:google.com", 1000)

    assert messages.list.call_args.kwargs["maxResults"] == MAX_RESULTS_CAP


def test_max_results_has_a_floor_of_one() -> None:
    service, messages = make_service({}, make_raw())

    search_emails(service, "x", max_results=0)

    assert messages.list.call_args.kwargs["maxResults"] == 1


def test_days_back_adds_newer_than() -> None:
    service, messages = make_service({}, make_raw())

    search_emails(service, "from:google.com", days_back=7)

    assert messages.list.call_args.kwargs["q"] == "from:google.com newer_than:7d"
