# Post routes

from fastapi import APIRouter, Depends, Header, HTTPException, status

from backend.models import AudienceType
from backend.schemas import (
    AISummaryRequest,
    AISummaryResponse,
    PostCreateRequest,
    PostListResponse,
    PostResponse,
)
from backend.services.ai_service import ai_service
from backend.services.post_service import post_service

# Router setup
router = APIRouter(prefix="/api/posts", tags=["posts"])


def get_current_user_role(
    authorization: str | None = Header(default=None),
    x_mock_role: str | None = Header(default=None),
) -> str:
    """Mock identity provider dependency for PoC.

    Extracts user role from X-Mock-Role or Bearer token claims.
    """
    # Check explicitly for invalid token header to simulate token expiration
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1].lower()
            if token == "invalid":
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail={
                        "error_code": "UNAUTHORIZED",
                        "message": "Invalid or expired session token",
                    },
                )
            if "faculty" in token:
                return "faculty"
            if "moderator" in token:
                return "moderator"
            if "exec" in token:
                return "club_exec"
            return "student"

    if x_mock_role:
        return x_mock_role.strip().lower()

    # Default to unprivileged student role
    return "student"


@router.get("", response_model=PostListResponse)
def get_posts(
    community_id: str | None = None,
    audience: AudienceType | None = None,
    user_role: str = Depends(get_current_user_role),
) -> PostListResponse:
    # Fetch posts with server-side query scoping
    items = post_service.list_posts(
        community_id=community_id, audience=audience, user_role=user_role
    )
    return PostListResponse(
        items=[PostResponse.model_validate(p) for p in items],
        total=len(items),
    )


@router.post("", response_model=PostResponse, status_code=status.HTTP_201_CREATED)
def create_new_post(payload: PostCreateRequest) -> PostResponse:
    # Save post
    created = post_service.create_post(payload)
    return PostResponse.model_validate(created)


@router.get("/{post_id}", response_model=PostResponse)
def get_single_post(
    post_id: str,
    user_role: str = Depends(get_current_user_role),
) -> PostResponse:
    # Retrieve single post
    post = post_service.get_post(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found",
        )

    # Server-side Audience Scoping enforcement:
    # Return 403 Forbidden if a student attempts to access a faculty_only post
    if post.audience == AudienceType.FACULTY_ONLY and user_role != "faculty":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error_code": "FORBIDDEN_AUDIENCE",
                "message": (
                    "Access denied: Faculty Only announcement requires faculty role"
                ),
            },
        )

    return PostResponse.model_validate(post)


@router.post("/ai/preview", response_model=AISummaryResponse)
def preview_ai_summary(payload: AISummaryRequest) -> AISummaryResponse:
    # Preview AI summary with circuit breaker fallback
    return ai_service.summarize(payload.text)
