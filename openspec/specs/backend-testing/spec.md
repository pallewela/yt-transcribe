### Requirement: YouTube URL validation tests
The test suite SHALL verify that `youtube.py` correctly validates and extracts video IDs from all supported YouTube URL formats.

#### Scenario: Standard watch URL accepted
- **WHEN** `validate_youtube_url` is called with `https://www.youtube.com/watch?v=dQw4w9WgXcQ`
- **THEN** it returns `True`

#### Scenario: Short URL accepted
- **WHEN** `validate_youtube_url` is called with `https://youtu.be/dQw4w9WgXcQ`
- **THEN** it returns `True`

#### Scenario: Embed URL accepted
- **WHEN** `validate_youtube_url` is called with `https://www.youtube.com/embed/dQw4w9WgXcQ`
- **THEN** it returns `True`

#### Scenario: Shorts URL accepted
- **WHEN** `validate_youtube_url` is called with `https://www.youtube.com/shorts/dQw4w9WgXcQ`
- **THEN** it returns `True`

#### Scenario: Non-YouTube URL rejected
- **WHEN** `validate_youtube_url` is called with `https://vimeo.com/123456`
- **THEN** it returns `False`

#### Scenario: Video ID extraction
- **WHEN** `extract_video_id` is called with any supported YouTube URL format
- **THEN** it returns the 11-character video ID

#### Scenario: Video ID extraction returns None for invalid URL
- **WHEN** `extract_video_id` is called with a non-YouTube URL
- **THEN** it returns `None`

### Requirement: Video metadata fetch tests
The test suite SHALL verify that `fetch_video_metadata` returns title and duration when successful, and an error when the video is unavailable.

#### Scenario: Successful metadata fetch
- **WHEN** `fetch_video_metadata` is called and yt-dlp returns valid info
- **THEN** it returns a dict with `title` and `duration` keys

#### Scenario: Metadata fetch failure
- **WHEN** `fetch_video_metadata` is called and yt-dlp raises an exception
- **THEN** it returns a dict with `title: None`, `duration: None`, and an `error` key

### Requirement: Database CRUD tests
The test suite SHALL verify all database operations against an isolated in-memory SQLite database.

#### Scenario: Create and retrieve video
- **WHEN** `create_video` is called with valid parameters
- **THEN** `get_video_by_id` returns the created record with status "queued"

#### Scenario: Duplicate video ID rejected
- **WHEN** `create_video` is called twice with the same `video_id`
- **THEN** the second call raises an integrity error

#### Scenario: Get video by YouTube video ID
- **WHEN** `get_video_by_video_id` is called with an existing YouTube ID
- **THEN** it returns the matching video record

#### Scenario: Get video by YouTube video ID not found
- **WHEN** `get_video_by_video_id` is called with a non-existent YouTube ID
- **THEN** it returns `None`

#### Scenario: List all videos
- **WHEN** multiple videos are created and `get_all_videos` is called
- **THEN** it returns all videos ordered by creation date descending

#### Scenario: Filter videos by status
- **WHEN** `get_all_videos` is called with a status filter
- **THEN** it returns only videos matching that status

#### Scenario: Update video fields
- **WHEN** `update_video` is called with new field values
- **THEN** the record reflects the updated values

#### Scenario: Delete video
- **WHEN** `delete_video` is called with a valid ID
- **THEN** the video is removed and the function returns `True`

#### Scenario: Delete non-existent video
- **WHEN** `delete_video` is called with a non-existent ID
- **THEN** the function returns `False`

#### Scenario: Get next queued video
- **WHEN** multiple videos exist with different statuses and `get_next_queued_video` is called
- **THEN** it returns the oldest video with status "queued"

#### Scenario: JSON deserialization of stored fields
- **WHEN** a video has `transcript_segments` and `summary_json` stored as JSON strings
- **THEN** `_row_to_dict` deserializes them into Python lists and dicts

### Requirement: API endpoint tests
The test suite SHALL verify all REST API endpoints return correct status codes and response bodies.

#### Scenario: Submit valid video URL
- **WHEN** `POST /api/videos` is called with a valid YouTube URL
- **THEN** the response has status 200 and returns a video object with status "queued"

#### Scenario: Submit invalid URL returns 400
- **WHEN** `POST /api/videos` is called with an invalid URL
- **THEN** the response has status 400

#### Scenario: Submit duplicate URL returns existing record
- **WHEN** `POST /api/videos` is called with a URL already submitted
- **THEN** the response returns the existing video record

#### Scenario: Batch submit with mixed URLs
- **WHEN** `POST /api/videos/batch` is called with valid and invalid URLs
- **THEN** the response contains success results for valid URLs and error results for invalid ones

#### Scenario: List videos
- **WHEN** `GET /api/videos` is called
- **THEN** the response returns a list of all video records

#### Scenario: List videos with status filter
- **WHEN** `GET /api/videos?status=completed` is called
- **THEN** only completed videos are returned

#### Scenario: Get single video
- **WHEN** `GET /api/videos/{id}` is called with a valid ID
- **THEN** the response returns the full video record

#### Scenario: Get non-existent video returns 404
- **WHEN** `GET /api/videos/{id}` is called with a non-existent ID
- **THEN** the response has status 404

#### Scenario: Delete video
- **WHEN** `DELETE /api/videos/{id}` is called with a valid ID
- **THEN** the response has status 200 and the video is removed

#### Scenario: Delete non-existent video returns 404
- **WHEN** `DELETE /api/videos/{id}` is called with a non-existent ID
- **THEN** the response has status 404

### Requirement: Transcription pipeline tests
The test suite SHALL verify the transcription fallback logic and transcript normalization with mocked external services.

#### Scenario: YouTube captions available
- **WHEN** `get_transcript` is called and YouTube captions are available
- **THEN** it returns timestamped segments with source "youtube_captions" and does not attempt audio download

#### Scenario: Captions unavailable falls back to Whisper
- **WHEN** `get_transcript` is called and YouTube captions are unavailable
- **THEN** it downloads audio via yt-dlp, transcribes via Whisper, and returns segments with source "whisper"

#### Scenario: Caption fetch failure falls back to Whisper
- **WHEN** `get_transcript` is called and the caption API raises an exception
- **THEN** it falls back to the Whisper path instead of failing

#### Scenario: Audio cleanup after successful transcription
- **WHEN** Whisper transcription completes successfully
- **THEN** the temporary audio file is deleted

#### Scenario: Audio cleanup after failed transcription
- **WHEN** Whisper transcription fails
- **THEN** the temporary audio file is still deleted

### Requirement: Summarizer tests
The test suite SHALL verify transcript formatting, segment chunking, and summary generation with mocked OpenAI calls.

#### Scenario: Transcript formatting
- **WHEN** `_format_timestamped_transcript` is called with segments
- **THEN** each segment is formatted as `[MM:SS] (Xs) text`

#### Scenario: Segment chunking
- **WHEN** `_split_segments_into_chunks` is called with segments exceeding max_chars
- **THEN** it splits into multiple chunks without losing any segments

#### Scenario: Single-pass summarization
- **WHEN** `generate_summary` is called with a short transcript
- **THEN** it makes one OpenAI API call and returns a dict with `overview` and `key_points`

#### Scenario: Chunked summarization
- **WHEN** `generate_summary` is called with a transcript exceeding the character limit
- **THEN** it summarizes chunks individually and combines them into a final summary

### Requirement: Pipeline orchestration tests
The test suite SHALL verify the full processing pipeline with mocked transcription and summarization.

#### Scenario: Successful pipeline execution
- **WHEN** `process_video` is called with a video record
- **THEN** it obtains a transcript, generates a summary, and updates the database with status "completed"

#### Scenario: Transcript stored during pipeline
- **WHEN** `process_video` completes the transcription step
- **THEN** the video record is updated with `transcript_segments`, `transcript_text`, and `transcript_source`

### Requirement: Worker tests
The test suite SHALL verify the background worker's job processing, retry logic, and status transitions.

#### Scenario: Worker picks up queued job
- **WHEN** the worker loop runs and a queued job exists
- **THEN** it changes the job status to "processing" and calls `process_video`

#### Scenario: Worker retries on failure
- **WHEN** `process_video` raises an exception and the attempt count is below max retries
- **THEN** the worker re-queues the job with an incremented attempt count

#### Scenario: Worker marks permanent failure
- **WHEN** `process_video` raises an exception and the attempt count has reached max retries
- **THEN** the worker marks the job as permanently "failed"

#### Scenario: Worker idles when queue is empty
- **WHEN** the worker loop runs and no queued jobs exist
- **THEN** it sleeps for the configured poll interval before checking again

### Requirement: Test infrastructure
The test suite SHALL provide shared fixtures and configuration for consistent test execution.

#### Scenario: Isolated test database
- **WHEN** any test runs
- **THEN** it uses a fresh in-memory SQLite database that is torn down after the test

#### Scenario: Tests run without network access
- **WHEN** the full test suite is executed
- **THEN** no real HTTP requests are made to YouTube, OpenAI, or any external service

#### Scenario: Single command execution
- **WHEN** `pytest` is run from the `backend/` directory
- **THEN** all tests are discovered and executed
