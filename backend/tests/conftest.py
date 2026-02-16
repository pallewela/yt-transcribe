import os
import pytest
import pytest_asyncio

os.environ["DATABASE_PATH"] = ":memory:"
os.environ["OPENAI_API_KEY"] = "sk-test-fake-key"
os.environ["WORKER_POLL_INTERVAL"] = "0"
os.environ["MAX_RETRY_ATTEMPTS"] = "3"
os.environ["RETRY_DELAY_SECONDS"] = "0"


@pytest_asyncio.fixture
async def test_db(monkeypatch, tmp_path):
    """Provide a fresh SQLite database for each test using a temp file."""
    import app.database as db_module

    db_path = str(tmp_path / "test.db")
    monkeypatch.setattr(db_module, "DATABASE_PATH", db_path)

    await db_module.init_db()

    yield

    # Cleanup happens automatically via tmp_path


def make_mock_transcript_segments():
    """Create sample timestamped transcript segments."""
    return [
        {"start": 0.0, "text": "Hello and welcome to this video."},
        {"start": 5.2, "text": "Today we will discuss testing."},
        {"start": 12.8, "text": "Let's get started."},
    ]


def make_mock_summary():
    """Create a sample summary JSON structure."""
    return {
        "overview": "This video discusses testing best practices.",
        "key_points": [
            {"timestamp": 0, "text": "Introduction to the topic."},
            {"timestamp": 5, "text": "Discussion of testing approaches."},
            {"timestamp": 12, "text": "Getting started with implementation."},
        ],
    }
