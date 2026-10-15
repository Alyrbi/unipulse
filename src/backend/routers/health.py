# Health routes
from fastapi import APIRouter

from backend.config import settings

# Router setup
router = APIRouter(tags=["health"])


@router.get("/health")
def health_check() -> dict[str, str]:
    # Return status
    return {
        "status": "healthy",
        "app": settings.app_name,
        "environment": settings.app_env,
    }
