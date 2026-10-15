# Post service

from backend.models import AudienceType, EventDetail, Post, PostStatus
from backend.repository import PostRepository, post_repository
from backend.schemas import PostCreateRequest
from backend.services.ai_service import AISummarizerService, ai_service


class PostService:
    def __init__(
        self,
        repo: PostRepository = post_repository,
        ai: AISummarizerService = ai_service,
    ) -> None:
        # Assign dependencies
        self._repo = repo
        self._ai = ai

    def list_posts(
        self,
        community_id: str | None = None,
        audience: AudienceType | None = None,
        user_role: str = "student",
    ) -> list[Post]:
        # Query repository with role-based scoping
        return self._repo.get_all(
            community_id=community_id, audience=audience, user_role=user_role
        )

    def get_post(self, post_id: str) -> Post | None:
        # Find post
        return self._repo.get_by_id(post_id)

    def create_post(self, payload: PostCreateRequest) -> Post:
        # Build event
        evt = EventDetail()
        if payload.event_detail:
            evt.is_event = payload.event_detail.is_event
            evt.event_date = payload.event_detail.event_date
            evt.event_location = payload.event_detail.event_location

        # Handle AI
        ai_summary: str | None = None
        tags = list(payload.tags)
        if payload.request_ai_summary:
            ai_res = self._ai.summarize(payload.content)
            ai_summary = ai_res.summary
            for t in ai_res.suggested_tags:
                if t not in tags:
                    tags.append(t)
            if not evt.is_event and ai_res.detected_event:
                evt.is_event = True
                evt.event_date = ai_res.suggested_date
                evt.event_location = ai_res.suggested_location

        # Instantiate entity
        new_post = Post(
            title=payload.title,
            content=payload.content,
            author_id=payload.author_id,
            author_name=payload.author_name,
            audience=payload.audience,
            community_id=payload.community_id,
            status=PostStatus.PUBLISHED,
            tags=tags,
            ai_summary=ai_summary,
            event_detail=evt,
        )

        # Save entity
        return self._repo.create(new_post)


# Singleton instance
post_service = PostService()
