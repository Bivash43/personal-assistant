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

        A plain keyword like `invoice` searches subjects and bodies. Use `subject:` only
        when the user asks about subjects specifically. If a search finds nothing, try a
        broader query before saying there are no matching emails.

        Write `query` in Gmail search syntax, or pass `""` to match all emails.
        Examples: `from:alice@example.com`, `subject:invoice`, `is:unread`,
        `has:attachment`, or combine them: `from:google.com has:attachment`.
        For relative date windows, use `days_back` instead of `newer_than:` in `query`.

        `days_back` limits results to emails from the last N days (1 to 365): use 1 for
        "today", 7 for "this week", 30 for "this month", or omit for no date limit.
        For older or exact date ranges, use `after:YYYY/MM/DD` / `before:YYYY/MM/DD` in `query`.
        Only set `days_back` when the user mentions a time period. Do not add a date
        limit on your own.

        Returns one line per email with its id, date, sender, subject and a short
        preview. It does not return full email bodies. `max_results` is how many
        emails to return (default 10, at most 25).
        """
        results = search_emails(service, query, max_results, days_back)
        if not results:
            return f"No emails matched the query {query!r} (days_back={days_back})."
        return format_summaries(results)

    return [search_gmail]
