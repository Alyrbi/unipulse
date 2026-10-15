# Data models
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import StrEnum
from uuid import uuid4


class AudienceType(StrEnum):
    # Audience levels
    PUBLIC = "public"
    CAMPUS_ONLY = "campus_only"
    CLUB_MEMBERS = "club_members"
    FACULTY_ONLY = "faculty_only"


class PostStatus(StrEnum):
    # Unified post statuses across report, ERD, and code
    DRAFT = "draft"
    PUBLISHED = "published"
    QUARANTINED = "quarantined"
    ARCHIVED = "archived"


@dataclass
class EventDetail:
    # Event metadata
    is_event: bool = False
    event_date: str | None = None
    event_location: str | None = None


@dataclass
class Post:
    # Post entity
    title: str
    content: str
    author_id: str
    author_name: str
    audience: AudienceType = AudienceType.CAMPUS_ONLY
    community_id: str | None = None
    id: str = field(default_factory=lambda: str(uuid4()))
    status: PostStatus = PostStatus.PUBLISHED
    tags: list[str] = field(default_factory=list)
    ai_summary: str | None = None
    event_detail: EventDetail = field(default_factory=EventDetail)
    created_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
