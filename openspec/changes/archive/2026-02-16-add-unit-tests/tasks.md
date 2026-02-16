## 1. Test Infrastructure Setup

- [x] 1.1 Add test dependencies to `backend/requirements.txt` (pytest, pytest-asyncio, httpx)
- [x] 1.2 Create `backend/pytest.ini` with asyncio mode and test discovery configuration
- [x] 1.3 Create `backend/tests/__init__.py`
- [x] 1.4 Create `backend/tests/conftest.py` with in-memory SQLite database fixture, mock factories for OpenAI/yt-dlp/youtube-transcript-api

## 2. YouTube Module Tests

- [x] 2.1 Create `backend/tests/test_youtube.py` with tests for `validate_youtube_url` (standard, short, embed, shorts URLs accepted; non-YouTube rejected)
- [x] 2.2 Add tests for `extract_video_id` across all URL formats and `None` for invalid URLs
- [x] 2.3 Add tests for `fetch_video_metadata` with mocked yt-dlp (success and error cases)

## 3. Database Tests

- [x] 3.1 Create `backend/tests/test_database.py` with tests for `create_video` and `get_video_by_id`
- [x] 3.2 Add tests for duplicate `video_id` handling
- [x] 3.3 Add tests for `get_video_by_video_id` (found and not found)
- [x] 3.4 Add tests for `get_all_videos` (all and with status filter)
- [x] 3.5 Add tests for `update_video` field updates
- [x] 3.6 Add tests for `delete_video` (existing and non-existent)
- [x] 3.7 Add tests for `get_next_queued_video` (picks oldest queued, returns None when empty)
- [x] 3.8 Add tests for `_row_to_dict` JSON deserialization of `transcript_segments` and `summary_json`

## 4. API Route Tests

- [x] 4.1 Create `backend/tests/test_routes.py` with FastAPI TestClient setup using httpx ASGITransport
- [x] 4.2 Add tests for `POST /api/videos` (valid URL, invalid URL 400, duplicate returns existing)
- [x] 4.3 Add tests for `POST /api/videos/batch` (mixed valid/invalid URLs)
- [x] 4.4 Add tests for `GET /api/videos` (list all, with status filter)
- [x] 4.5 Add tests for `GET /api/videos/{id}` (found, 404 not found)
- [x] 4.6 Add tests for `DELETE /api/videos/{id}` (success, 404 not found)

## 5. Transcription Pipeline Tests

- [x] 5.1 Create `backend/tests/test_transcriber.py` with mocked youtube-transcript-api and OpenAI Whisper
- [x] 5.2 Add test for YouTube captions available path (returns segments with source "youtube_captions")
- [x] 5.3 Add test for captions unavailable fallback to Whisper (returns segments with source "whisper")
- [x] 5.4 Add test for caption fetch exception fallback to Whisper
- [x] 5.5 Add tests for audio file cleanup after success and after failure

## 6. Summarizer Tests

- [x] 6.1 Create `backend/tests/test_summarizer.py` with mocked OpenAI GPT client
- [x] 6.2 Add test for `_format_timestamped_transcript` output format
- [x] 6.3 Add test for `_split_segments_into_chunks` splitting logic
- [x] 6.4 Add test for single-pass `generate_summary` (short transcript)
- [x] 6.5 Add test for chunked `generate_summary` (long transcript triggers multi-pass)

## 7. Pipeline and Worker Tests

- [x] 7.1 Create `backend/tests/test_pipeline.py` with mocked transcriber and summarizer
- [x] 7.2 Add test for successful `process_video` (transcript stored, summary stored, status completed)
- [x] 7.3 Create `backend/tests/test_worker.py` with mocked pipeline and database
- [x] 7.4 Add test for worker picking up queued job and processing it
- [x] 7.5 Add test for worker retry on failure (re-queues with incremented attempt count)
- [x] 7.6 Add test for worker permanent failure after max retries

## 8. Verification

- [x] 8.1 Run full test suite with `pytest -v` and verify all tests pass
