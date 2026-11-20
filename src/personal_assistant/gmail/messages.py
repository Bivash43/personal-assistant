import html
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class EmailSummary:
    id: str
    thread_id: str
    subject: str
    sender: str
    date: str
    snippet: str


def _header(raw: dict[str, Any], name: str) -> str:
    headers = raw.get("payload", {}).get("headers", [])
    if headers != []:
        for h in headers:
            if str(h.get("name", "")).lower() == name.lower():
                return str(h.get("value", ""))
    return ""


def parse_message_summary(raw: dict[str, Any]) -> EmailSummary:
    return EmailSummary(
        id=raw["id"],
        thread_id=raw["threadId"],
        subject=_header(raw, "Subject"),
        sender=_header(raw, "From"),
        date=_header(raw, "Date"),
        snippet=html.unescape(raw.get("snippet", "")),
    )
