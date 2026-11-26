from typing import Any

from langchain_core.tools import BaseTool, tool

from personal_assistant.gmail.messages import EmailSummary
from personal_assistant.gmail.search import search_emails

SUBJECT_CHARS = 200
PREVIEW_CHARS = 150


def _one_line(text: str, limit: int) -> str:
    """Collapse all whitespace (including newlines) and cut to `limit` characters."""
    collapsed = " ".join(text.split())
    if len(collapsed) > limit:
        return collapsed[: limit - 1] + "…"
    return collapsed


def format_summaries(summaries: list[EmailSummary]) -> str:
    if not summaries:
        return "No emails found."

    lines = []
    for s in summaries:
        lines.append(
            f"[{s.id}] {s.date} | From: {_one_line(s.sender, SUBJECT_CHARS)} "
            f"| Subject: {_one_line(s.subject, SUBJECT_CHARS)} "
            f"| Preview: {_one_line(s.snippet, PREVIEW_CHARS)}"
        )
    return "\n".join(lines)


def make_gmail_tools(service: Any) -> list[BaseTool]:
    @tool
    def search_gmail(query: str, max_results: int = 10, days_back: int | None = None) -> str:
        """Search the user's Gmail mailbox (read-only) and list matching emails.

        Write `query` in Gmail search syntax. Examples: `from:alice@example.com`,
        `subject:invoice`, `newer_than:7d`, `is:unread`, `has:attachment`, or combine
        them: `from:google.com newer_than:30d`.

        Returns one line per email with its id, date, sender, subject and a short
        preview. It does not return full email bodies. `max_results` is how many
        emails to return (default 10, at most 25).

        `days_back` limits results to emails from the last N days. Use 1 for "today",
        7 for "this week", 30 for "this month". Leave it out for no date limit.
        """
        return format_summaries(search_emails(service, query, max_results, days_back))

    return [search_gmail]
