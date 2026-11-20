from typing import Any

from personal_assistant.gmail.messages import parse_message_summary


def make_raw() -> dict[str, Any]:
    return {
        "id": "msg-1",
        "threadId": "thread-1",
        "snippet": "Hi Test, Welcome. We&#39;ll send you some tips",
        "payload": {
            "headers": [
                {"name": "Date", "value": "Tue, 17 Nov 2026 11:27:22 -0800"},
                {"name": "Subject", "value": "Finish setting up your account"},
                {"name": "From", "value": "Google <no-reply@google.com>"},
            ]
        },
    }


def test_parses_headers() -> None:
    summary = parse_message_summary(make_raw())

    assert summary.subject == "Finish setting up your account"
    assert summary.sender == "Google <no-reply@google.com>"
    assert summary.date == "Tue, 17 Nov 2026 11:27:22 -0800"


def test_snippet_is_unescaped() -> None:
    summary = parse_message_summary(make_raw())

    assert "We'll" in summary.snippet
    assert "&#39;" not in summary.snippet


def test_missing_subject_gives_empty_string() -> None:
    raw = make_raw()
    new_headers = []
    for h in raw["payload"]["headers"]:
        if h["name"] != "Subject":
            new_headers.append(h)

    raw["payload"]["headers"] = new_headers

    summary = parse_message_summary(raw)
    assert summary.subject == ""


def test_missing_payload_does_not_crash() -> None:
    raw = make_raw()
    raw.pop("payload")
    summary = parse_message_summary(raw)
    assert summary.subject == ""
    assert summary.sender == ""
    assert summary.date == ""


def test_missing_snippet_gives_empty_string() -> None:
    raw = make_raw()
    raw.pop("snippet")

    summary = parse_message_summary(raw)
    assert summary.snippet == ""


def test_header_names_are_case_insensitive() -> None:
    raw = make_raw()
    raw["payload"]["headers"] = [{"name": "SUBJECT", "value": "Shouting"}]

    assert parse_message_summary(raw).subject == "Shouting"
