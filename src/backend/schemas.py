# Contract schemas

from pydantic import BaseModel, ConfigDict, Field

from backend.models import AudienceType, PostStatus


class EventDetailSchema(BaseModel):
    # Event fields
    is_event: bool = False
    event_date: str | None = None
    event_location: str | None = None

    # Serialization config
    model_config = ConfigDict(from_attributes=True)


class PostCreateRequest(BaseModel):
    # Input validation
    title: str = Field(..., min_length=3, max_length=120)
    content: str = Field(..., min_length=5, max_length=5000)
    author_id: str = Field(..., min_length=1, max_length=50)
    author_name: str = Field(..., min_length=1, max_length=60)
    audience: AudienceType = AudienceType.CAMPUS_ONLY
    community_id: str | None = Field(default=None, max_length=50)
    tags: list[str] = Field(default_factory=list)
    request_ai_summary: bool = False
    event_detail: EventDetailSchema | None = None


class PostResponse(BaseModel):
    # Output schema
    id: str
    title: str
    content: str
    author_id: str
    author_name: str
    audience: AudienceType
    community_id: str | None = None
    status: PostStatus
    tags: list[str]
    ai_summary: str | None = None
    event_detail: EventDetailSchema
    created_at: str

    # Serialization config
    model_config = ConfigDict(from_attributes=True)


class PostListResponse(BaseModel):
    # Collection schema
    items: list[PostResponse]
    total: int


class AISummaryRequest(BaseModel):
    # AI input
    text: str = Field(..., min_length=10, max_length=5000)


class AISummaryResponse(BaseModel):
    # AI output with circuit breaker indicator
    summary: str
    detected_event: bool
    suggested_date: str | None = None
    suggested_location: str | None = None
    suggested_tags: list[str]
    is_fallback: bool = False


class ErrorResponse(BaseModel):
    # Standard error format
    error_code: str
    message: str
    details: dict | None = None
