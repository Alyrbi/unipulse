# Unit tests
from backend.models import AudienceType, Post, PostStatus
from backend.services.ai_service import AISummarizerService


def test_post_instantiation() -> None:
    # Model test
    post = Post(
        title="Test Title",
        content="Test content for verification.",
        author_id="user-1",
        author_name="Alice",
        audience=AudienceType.PUBLIC,
    )
    assert post.title == "Test Title"
    assert post.status == PostStatus.PUBLISHED
    assert post.id is not None


def test_ai_summarizer_basic() -> None:
    # Service test
    ai = AISummarizerService()
    text = (
        "Students are invited to the robotics lab. "
        "Bring your laptops and sensors. See you there."
    )
    res = ai.summarize(text)
    assert res.summary is not None
    assert len(res.summary) > 0
    assert "robotics lab" in res.summary.lower()


def test_ai_event_detection() -> None:
    # Detection test
    ai = AISummarizerService()
    text = "Join us in the Grand Auditorium at 10 AM for the orientation session."
    res = ai.summarize(text)
    assert res.detected_event is True
    assert res.suggested_location == "Campus Auditorium"


def test_ai_regex_no_false_positive_on_common_words() -> None:
    # Ensure words like 'team' or 'name' do not falsely trigger event detection
    ai = AISummarizerService()
    text = "Our team will announce the project name shortly."
    res = ai.summarize(text)
    assert res.detected_event is False
    assert res.suggested_date is None


def test_ai_circuit_breaker_fallback(monkeypatch: object) -> None:
    # Verify circuit breaker trips when latency exceeds 3000ms
    from backend.config import settings

    monkeypatch.setattr(settings, "mock_llm_latency_ms", 3500)
    ai = AISummarizerService()
    res = ai.summarize("This is a long test text for verifying the circuit breaker.")
    assert res.is_fallback is True
    assert "[Fallback Extractive]" in res.summary
    assert "fallback" in res.suggested_tags

