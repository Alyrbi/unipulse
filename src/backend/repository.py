# Repository pattern
from backend.models import AudienceType, EventDetail, Post, PostStatus


class PostRepository:
    def __init__(self) -> None:
        # Storage dictionary
        self._posts: dict[str, Post] = {}
        # Seed samples
        self._seed_data()

    def _seed_data(self) -> None:
        # Seed posts
        p1 = Post(
            id="p-101",
            title="Welcome to Semester 1 2026 Orientation",
            content=(
                "Campus orientation starts at 10 AM in the Grand Auditorium. "
                "Meet your department advisors and student society leaders."
            ),
            author_id="u-admin-1",
            author_name="Campus Affairs Office",
            audience=AudienceType.CAMPUS_ONLY,
            community_id="announcements",
            tags=["orientation", "campus", "welcome"],
            ai_summary=(
                "Orientation begins at 10 AM in Grand Auditorium with advisor meetups."
            ),
            event_detail=EventDetail(
                is_event=True,
                event_date="2026-10-20T10:00:00Z",
                event_location="Grand Auditorium",
            ),
        )
        p2 = Post(
            id="p-102",
            title="Robotics Club Hackathon Registration Open",
            content=(
                "Join us for a 24-hour robotics challenge. "
                "Build intelligent agents and autonomous hardware. "
                "Refreshments provided."
            ),
            author_id="u-student-42",
            author_name="Robotics Society",
            audience=AudienceType.PUBLIC,
            community_id="robotics",
            tags=["hackathon", "robotics", "ai"],
            ai_summary="24-hour robotics and AI challenge with hardware prototyping.",
            event_detail=EventDetail(
                is_event=True,
                event_date="2026-11-05T09:00:00Z",
                event_location="Engineering Building Lab 3",
            ),
        )
        p3 = Post(
            id="p-103",
            title="Faculty Senate Curriculum & Grading Policy",
            content=(
                "Confidential faculty guidelines on grading distribution and "
                "assessment criteria for the upcoming semester."
            ),
            author_id="u-faculty-1",
            author_name="Faculty Academic Senate",
            audience=AudienceType.FACULTY_ONLY,
            community_id="faculty-senate",
            tags=["faculty", "policy", "grading"],
            ai_summary="Faculty curriculum guidelines and grading assessment policies.",
            event_detail=EventDetail(is_event=False),
        )
        self._posts[p1.id] = p1
        self._posts[p2.id] = p2
        self._posts[p3.id] = p3

    def get_all(
        self,
        community_id: str | None = None,
        audience: AudienceType | None = None,
        user_role: str = "student",
    ) -> list[Post]:
        # Filter posts with audience scoping
        results = list(self._posts.values())
        if community_id:
            results = [p for p in results if p.community_id == community_id]
        if audience:
            results = [p for p in results if p.audience == audience]
        # Query-level scoping: exclude FACULTY_ONLY unless user has faculty role
        if user_role != "faculty":
            results = [p for p in results if p.audience != AudienceType.FACULTY_ONLY]
        return sorted(results, key=lambda x: x.created_at, reverse=True)

    def get_by_id(self, post_id: str) -> Post | None:
        # Lookup post
        return self._posts.get(post_id)

    def create(self, post: Post) -> Post:
        # Insert post
        self._posts[post.id] = post
        return post

    def delete(self, post_id: str) -> bool:
        # Remove post
        if post_id in self._posts:
            del self._posts[post_id]
            return True
        return False

    def update_status(self, post_id: str, status: PostStatus) -> Post | None:
        # Update status
        post = self._posts.get(post_id)
        if post:
            post.status = status
            return post
        return None


# Singleton instance
post_repository = PostRepository()
