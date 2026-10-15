# Boundary tests
from fastapi.testclient import TestClient


def test_bva_title_minimum_valid(client: TestClient) -> None:
    # Boundary valid
    payload = {
        "title": "ABC",
        "content": "Valid content length here.",
        "author_id": "u-1",
        "author_name": "Tester",
        "audience": "campus_only",
    }
    res = client.post("/api/posts", json=payload)
    assert res.status_code == 201


def test_bva_title_minimum_invalid(client: TestClient) -> None:
    # Boundary invalid
    payload = {
        "title": "AB",
        "content": "Valid content length here.",
        "author_id": "u-1",
        "author_name": "Tester",
        "audience": "campus_only",
    }
    res = client.post("/api/posts", json=payload)
    assert res.status_code == 422


def test_bva_title_maximum_valid(client: TestClient) -> None:
    # Boundary max
    payload = {
        "title": "T" * 120,
        "content": "Valid content length here.",
        "author_id": "u-1",
        "author_name": "Tester",
        "audience": "campus_only",
    }
    res = client.post("/api/posts", json=payload)
    assert res.status_code == 201


def test_bva_title_maximum_invalid(client: TestClient) -> None:
    # Boundary overflow
    payload = {
        "title": "T" * 121,
        "content": "Valid content length here.",
        "author_id": "u-1",
        "author_name": "Tester",
        "audience": "campus_only",
    }
    res = client.post("/api/posts", json=payload)
    assert res.status_code == 422


def test_equivalence_invalid_audience(client: TestClient) -> None:
    # Invalid partition
    payload = {
        "title": "Valid Title",
        "content": "Valid content length here.",
        "author_id": "u-1",
        "author_name": "Tester",
        "audience": "invalid_audience_level",
    }
    res = client.post("/api/posts", json=payload)
    assert res.status_code == 422
