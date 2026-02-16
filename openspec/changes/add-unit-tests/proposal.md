## Why

The application has no automated tests. All backend modules — URL validation, database CRUD, API endpoints, transcription pipeline, and summarization — are untested. Adding unit tests provides a safety net against regressions, validates existing behavior, and enables confident future changes.

## What Changes

- **New test suite** for the Python backend using pytest with pytest-asyncio
- **Unit tests for `youtube.py`**: URL validation, video ID extraction across all URL formats, edge cases
- **Unit tests for `database.py`**: CRUD operations, duplicate handling, status filtering, JSON serialization/deserialization
- **Unit tests for `routes.py`**: API endpoint behavior using FastAPI's TestClient, including validation, batch submission, error responses
- **Unit tests for `summarizer.py`**: Transcript formatting, segment chunking logic, summary structure validation
- **Unit tests for `transcriber.py`**: Caption fetching fallback logic, transcript normalization, audio cleanup
- **Unit tests for `pipeline.py`**: End-to-end pipeline orchestration with mocked dependencies
- **Unit tests for `worker.py`**: Job queue polling, retry logic, status transitions
- **Test infrastructure**: pytest configuration, fixtures for test database, mocking helpers for external APIs (OpenAI, yt-dlp, youtube-transcript-api)

## Capabilities

### New Capabilities

- `backend-testing`: Test infrastructure, fixtures, and unit tests covering all backend modules with external API mocking

### Modified Capabilities

_None — adding tests does not change any existing application requirements._

## Impact

- **New files**: `backend/tests/` directory with test modules and `conftest.py`
- **New dependencies**: pytest, pytest-asyncio, httpx (for FastAPI TestClient)
- **Configuration**: `backend/pytest.ini` or `pyproject.toml` section for pytest settings
- **No changes to application code** — tests are additive only
