# Contract tests
from fastapi.testclient import TestClient


def test_health_endpoint(client: TestClient) -> None:
    # Health check
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_get_posts_contract(client: TestClient) -> None:
    # List contract
    response = client.get("/api/posts")
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert "total" in data
    assert isinstance(data["items"], list)
    assert data["total"] >= 2


def test_create_post_contract(client: TestClient) -> None:
    # Create contract
    payload = {
        "title": "Machine Learning Study Jam",
        "content": (
            "Meeting in CS Lab 2 at 4 PM to review "
            "transformer models and attention mechanisms."
        ),
        "author_id": "u-student-99",
        "author_name": "Bob Chen",
        "audience": "campus_only",
        "community_id": "ai-study",
        "tags": ["ml", "study"],
        "request_ai_summary": True,
    }
    response = client.post("/api/posts", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["title"] == payload["title"]
    assert created["author_name"] == payload["author_name"]
    assert created["audience"] == "campus_only"
    assert created["ai_summary"] is not None
    assert "id" in created
    assert "created_at" in created


def test_get_single_post_found(client: TestClient) -> None:
    # Retrieve single
    response = client.get("/api/posts/p-101")
    assert response.status_code == 200
    post = response.json()
    assert post["id"] == "p-101"
    assert post["title"] == "Welcome to Semester 1 2026 Orientation"


def test_get_single_post_not_found(client: TestClient) -> None:
    # Missing post
    response = client.get("/api/posts/non-existent-id-999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Post not found"


def test_audience_filtering(client: TestClient) -> None:
    # Filter test
    response_public = client.get("/api/posts?audience=public")
    assert response_public.status_code == 200
    items = response_public.json()["items"]
    assert all(item["audience"] == "public" for item in items)


def test_create_post_with_null_community_id(client: TestClient) -> None:
    # Contract validation: community_id: null is accepted
    payload = {
        "title": "General Campus Notice",
        "content": "This notice applies campus-wide without a specific sub-community.",
        "author_id": "u-admin-01",
        "author_name": "Campus Admin",
        "audience": "campus_only",
        "community_id": None,
    }
    response = client.post("/api/posts", json=payload)
    assert response.status_code == 201
    created = response.json()
    assert created["community_id"] is None


def test_faculty_only_post_returns_403_for_student(client: TestClient) -> None:
    # Scoping check: student role cannot access faculty_only post p-103
    response = client.get("/api/posts/p-103", headers={"X-Mock-Role": "student"})
    assert response.status_code == 403
    data = response.json()
    assert data["detail"]["error_code"] == "FORBIDDEN_AUDIENCE"


def test_faculty_only_post_returns_200_for_faculty(client: TestClient) -> None:
    # Scoping check: faculty role can access faculty_only post p-103
    response = client.get("/api/posts/p-103", headers={"X-Mock-Role": "faculty"})
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "p-103"
    assert data["audience"] == "faculty_only"


def test_faculty_only_post_bearer_token(client: TestClient) -> None:
    # Scoping check: Bearer token containing faculty role
    response = client.get(
        "/api/posts/p-103",
        headers={"Authorization": "Bearer mock-faculty-session-token"},
    )
    assert response.status_code == 200


def test_invalid_bearer_token_returns_401(client: TestClient) -> None:
    # Auth check: invalid token simulation
    response = client.get(
        "/api/posts/p-103",
        headers={"Authorization": "Bearer invalid"},
    )
    assert response.status_code == 401
    data = response.json()
    assert data["detail"]["error_code"] == "UNAUTHORIZED"


def test_faculty_posts_excluded_from_student_feed(client: TestClient) -> None:
    # Scoping check: student feed does not include faculty_only posts
    response = client.get("/api/posts", headers={"X-Mock-Role": "student"})
    assert response.status_code == 200
    items = response.json()["items"]
    assert all(item["audience"] != "faculty_only" for item in items)

