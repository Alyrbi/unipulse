# AI service
import re
from datetime import UTC, datetime

from backend.config import settings
from backend.schemas import AISummaryResponse


class AISummarizerService:
    def summarize(self, text: str) -> AISummaryResponse:
        # Clean text
        clean = " ".join(text.split())
        sentences = [s.strip() for s in re.split(r"[.!?]", clean) if s.strip()]

        # Generate summary (extractive heuristic)
        if len(sentences) <= 2:
            summary = clean
        else:
            summary = ". ".join(sentences[:2]) + "."

        # Circuit breaker check: simulated timeout if latency > 3.0s (3000ms)
        if settings.mock_llm_latency_ms > 3000:
            return AISummaryResponse(
                summary=f"[Fallback Extractive] {summary}",
                detected_event=False,
                suggested_date=None,
                suggested_location=None,
                suggested_tags=["fallback", "offline"],
                is_fallback=True,
            )

        # Detect events using word-boundary regex to prevent false positives
        # (e.g. 'team', 'name')
        lower = clean.lower()
        event_patterns = [
            r"\b(room|auditorium|building|hall|lab|center)\b",
            r"\b\d{1,2}:\d{2}\s*(?:am|pm)?\b",
            r"\b(am|pm)\b",
            r"\b(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\s+\d{1,2}\b",
            r"\b\d{4}-\d{2}-\d{2}\b",
            r"\b(hackathon|workshop|seminar|conference|lecture|meetup)\b",
        ]
        is_event = any(re.search(pat, lower) for pat in event_patterns)

        # Extract dynamic date from text (ISO format or parsed date, null if absent)
        suggested_date: str | None = None
        iso_match = re.search(r"\b(\d{4}-\d{2}-\d{2})\b", text)
        if iso_match:
            suggested_date = f"{iso_match.group(1)}T10:00:00Z"
        elif re.search(r"\b(oct|nov|dec)[a-z]*\s+(\d{1,2})\b", lower):
            month_match = re.search(r"\b(oct|nov|dec)[a-z]*\s+(\d{1,2})\b", lower)
            month_num = {"oct": "10", "nov": "11", "dec": "12"}.get(
                month_match.group(1)[:3], "10"
            )
            day = int(month_match.group(2))
            suggested_date = f"2026-{month_num}-{day:02d}T14:00:00Z"
        elif is_event and re.search(r"\b\d{1,2}:\d{2}\b", text):
            suggested_date = datetime.now(UTC).strftime("%Y-%m-%dT%H:00:00Z")

        # Extract location using word boundaries
        location: str | None = None
        for loc in ["auditorium", "hall", "lab", "campus center", "room"]:
            loc_match = re.search(rf"\b{loc}\b", lower)
            if loc_match:
                location = f"Campus {loc.title()}"
                break

        # Suggest tags
        tags: list[str] = ["campus"]
        if is_event:
            tags.append("event")
        if re.search(r"\b(hackathon|code|ai|technology|ml)\b", lower):
            tags.append("technology")
        if re.search(r"\bworkshop\b", lower):
            tags.append("workshop")

        # Return response schema
        return AISummaryResponse(
            summary=summary,
            detected_event=is_event,
            suggested_date=suggested_date,
            suggested_location=location,
            suggested_tags=tags,
            is_fallback=False,
        )


# Service instance
ai_service = AISummarizerService()
