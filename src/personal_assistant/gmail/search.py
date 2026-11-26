from typing import Any

from personal_assistant.gmail.messages import EmailSummary, parse_message_summary

MAX_RESULTS_CAP = 25
MAX_DAYS_CAP = 365


def search_emails(
    service: Any, query: str, max_results: int = 10, days_back: int | None = None
) -> list[EmailSummary]:
    limit = max(1, min(max_results, MAX_RESULTS_CAP))

    q = query
    if days_back is not None:
        days = max(1, min(days_back, MAX_DAYS_CAP))
        q = f"{query} newer_than:{days}d".strip()

    resp = service.users().messages().list(userId="me", q=q, maxResults=limit).execute()

    summaries: list[EmailSummary] = []

    for item in resp.get("messages", []):
        raw = (
            service.users()
            .messages()
            .get(
                userId="me",
                id=item["id"],
                format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            )
            .execute()
        )

        summary = parse_message_summary(raw)

        summaries.append(summary)

    return summaries
