## Context

The YT Transcribe backend has 7 Python modules (`youtube.py`, `database.py`, `routes.py`, `transcriber.py`, `summarizer.py`, `pipeline.py`, `worker.py`) with zero test coverage. The modules depend on external services (OpenAI API, yt-dlp, youtube-transcript-api) and an async SQLite database. Tests need to run fast and offline, which requires mocking all external dependencies.

## Goals / Non-Goals

**Goals:**
- Unit test coverage for all backend modules
- Tests run fast (no network calls, no real API usage)
- Tests use an in-memory SQLite database, isolated per test
- External services are mocked consistently with realistic return values
- Tests are easy to run with a single `pytest` command

**Non-Goals:**
- Integration or end-to-end tests
- Frontend (React) tests
- Performance or load testing
- 100% line coverage — focus on meaningful behavior coverage

## Decisions

### 1. Test Framework: pytest + pytest-asyncio

**Choice:** pytest with pytest-asyncio for async test support, httpx for FastAPI TestClient.

**Rationale:** pytest is the de facto Python test framework. pytest-asyncio handles async/await test functions natively. httpx's `ASGITransport` integrates cleanly with FastAPI for testing endpoints without starting a server.

**Alternatives considered:**
- unittest: More verbose, weaker fixture support, no native async
- anyio: More general than needed; pytest-asyncio is simpler for our pure-asyncio codebase

### 2. Database Isolation: In-memory SQLite per test

**Choice:** Each test gets a fresh in-memory SQLite database via a fixture that patches `DATABASE_PATH` and calls `init_db()`.

**Rationale:** In-memory SQLite is fast, fully isolated, and requires no cleanup. Patching the module-level `DATABASE_PATH` variable ensures all database helpers use the test database.

**Alternatives considered:**
- Temporary file database: Slower, requires cleanup
- Shared test database with rollback: More complex, risk of test coupling

### 3. Mocking Strategy: unittest.mock.patch for external services

**Choice:** Use `unittest.mock.patch` and `AsyncMock` to mock:
- `yt_dlp.YoutubeDL` for metadata fetching and audio download
- `youtube_transcript_api.YouTubeTranscriptApi` for caption fetching
- `openai.OpenAI` client for Whisper and GPT API calls

**Rationale:** Standard library mocking avoids extra dependencies. Patching at the module import level ensures no real network calls leak through. Each test module sets up its own mocks for clarity.

**Alternatives considered:**
- responses/respx: HTTP-level mocking is too low-level for SDK clients
- Factory fixtures: Over-engineering for this scope

### 4. Test Structure: One test file per module

**Choice:** Mirror the `app/` structure in `tests/`:
- `tests/test_youtube.py`
- `tests/test_database.py`
- `tests/test_routes.py`
- `tests/test_transcriber.py`
- `tests/test_summarizer.py`
- `tests/test_pipeline.py`
- `tests/test_worker.py`
- `tests/conftest.py` for shared fixtures

**Rationale:** One-to-one mapping makes it obvious which tests cover which module. `conftest.py` holds the database fixture and common mock factories.

## Risks / Trade-offs

- **[Mock fidelity]** Mocks may drift from real API behavior over time. → *Mitigation:* Use realistic return structures based on actual API responses. Document mock shapes.

- **[Async test complexity]** pytest-asyncio requires careful fixture scoping. → *Mitigation:* Use function-scoped async fixtures for database isolation. Keep fixtures simple.

- **[Brittle patch paths]** Patching imports can break if module structure changes. → *Mitigation:* Patch where the symbol is used (e.g., `app.transcriber.YouTubeTranscriptApi`), not where it's defined.
