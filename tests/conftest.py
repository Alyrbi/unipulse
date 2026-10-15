# Test fixtures
import pytest
from fastapi.testclient import TestClient

from backend.main import app
from backend.repository import PostRepository, post_repository


@pytest.fixture
def client() -> TestClient:
    # Test client
    return TestClient(app)


@pytest.fixture(autouse=True)
def reset_repository() -> None:
    # Fresh repository
    fresh_repo = PostRepository()
    post_repository._posts = fresh_repo._posts.copy()
