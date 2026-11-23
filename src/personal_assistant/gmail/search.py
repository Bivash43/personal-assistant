from typing import Any

from personal_assistant.gmail.messages import EmailSummary, parse_message_summary

MAX_RESULTS_CAP = 25


def search_emails(service: Any, query: str, max_results: int = 10) -> list[EmailSummary]:
    limit = max(1, min(max_results, MAX_RESULTS_CAP))

    resp = service.users().messages().list(userId="me", q=query, maxResults=limit).execute()

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
