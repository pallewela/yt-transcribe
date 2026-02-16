## 1. Project Setup

- [x] 1.1 Initialize monorepo with `backend/` and `frontend/` directories
- [x] 1.2 Set up Python backend with FastAPI, create `requirements.txt` with dependencies (fastapi, uvicorn, yt-dlp, openai, youtube-transcript-api, aiosqlite, pydub)
- [x] 1.3 Set up React frontend with Vite and install dependencies (react-router, axios or fetch wrapper)
- [x] 1.4 Create `.env.example` with required environment variables (OPENAI_API_KEY)
- [x] 1.5 Set up SQLite database initialization script with WAL mode enabled

## 2. Database Schema

- [x] 2.1 Create `videos` table schema (id, url, video_id, title, duration, status, transcript_source, transcript_segments JSON, transcript_text, summary_json, error_message, attempt_count, created_at, completed_at)
- [x] 2.2 Implement database connection helper with async SQLite support
- [x] 2.3 Implement CRUD operations for video records (create, get_by_id, get_all, update_status, delete)

## 3. Video Submission API

- [x] 3.1 Implement YouTube URL validation (standard watch URLs, short youtu.be URLs, reject non-YouTube)
- [x] 3.2 Implement video ID extraction from various YouTube URL formats
- [x] 3.3 Implement video metadata fetching (title, duration) using yt-dlp
- [x] 3.4 Create `POST /api/videos` endpoint for single URL submission with validation, duplicate detection, and metadata fetch
- [x] 3.5 Create `POST /api/videos/batch` endpoint for batch URL submission with partial success handling
- [x] 3.6 Create `GET /api/videos` endpoint to list all videos with optional status filter
- [x] 3.7 Create `GET /api/videos/{id}` endpoint to get a single video with transcript and summary
- [x] 3.8 Create `DELETE /api/videos/{id}` endpoint to delete a video and its data

## 4. Transcription Pipeline

- [x] 4.1 Implement YouTube captions fetcher using youtube-transcript-api, preserving per-segment timestamps (preferred transcript source)
- [x] 4.2 Implement audio download fallback using yt-dlp (when no captions available)
- [x] 4.3 Implement audio chunking for files exceeding Whisper's 25MB limit
- [x] 4.4 Implement Whisper API transcription with verbose JSON response format to obtain segment-level timestamps
- [x] 4.5 Normalize both transcript sources into a common timestamped format: JSON array of `{start: seconds, text: "..."}` segments
- [x] 4.6 Derive and store plain-text transcript (concatenated segments) alongside the timestamped JSON
- [x] 4.7 Implement transcript source recording ("youtube_captions" or "whisper")
- [x] 4.8 Implement temporary audio file cleanup (on success and failure)

## 5. Summarization

- [x] 5.1 Implement LLM summarization function using OpenAI GPT API (gpt-4o-mini)
- [x] 5.2 Implement prompt template that includes timestamped transcript and instructs the LLM to anchor each key point to a timestamp
- [x] 5.3 Parse LLM response into structured JSON: `{overview: "...", key_points: [{timestamp: seconds, text: "..."}]}`
- [x] 5.4 Implement transcript chunking and multi-pass summarization for long transcripts, preserving original video timestamps
- [x] 5.5 Update video status to "completed" with completion timestamp after successful summarization

## 6. Job Queue and Background Worker

- [x] 6.1 Implement job queue polling loop using asyncio (pick oldest "queued" job, process it)
- [x] 6.2 Implement full processing pipeline orchestration: captions check → (audio download → Whisper) → summarize → mark complete
- [x] 6.3 Implement status transitions (queued → processing → completed/failed) with error message capture
- [x] 6.4 Implement retry logic with configurable max attempts and delay between retries
- [x] 6.5 Start background worker as an asyncio task on FastAPI application startup

## 7. Frontend - Layout and Submission

- [x] 7.1 Create app layout with header/navigation and main content area
- [x] 7.2 Create video submission component with multi-line textarea for pasting URLs (one per line)
- [x] 7.3 Implement client-side YouTube URL validation with feedback
- [x] 7.4 Wire submission form to `POST /api/videos/batch` endpoint

## 8. Frontend - Dashboard and Summary View

- [x] 8.1 Create video list component showing all videos with title, status badge, and submission date
- [x] 8.2 Implement status filter controls (All, Queued, Processing, Completed, Failed)
- [x] 8.3 Create empty state component prompting user to submit their first video
- [x] 8.4 Create summary detail view showing video title, overview, key points with clickable timestamp links, full timestamped transcript, and transcript source
- [x] 8.5 Implement clickable timestamp links that open YouTube video at the corresponding time (`?t=` parameter) in a new tab
- [x] 8.6 Display transcript segments with visible clickable timestamps
- [x] 8.7 Implement delete video functionality with confirmation
- [x] 8.8 Implement auto-refresh polling (periodic fetch of video list to reflect status updates)

## 9. Integration and Polish

- [x] 9.1 Configure FastAPI to serve the built React frontend as static files
- [x] 9.2 Add CORS configuration for development (frontend dev server → backend API)
- [x] 9.3 Add error handling and user-friendly error messages throughout the API
- [x] 9.4 Add loading states and error states in the frontend UI
- [x] 9.5 Write a README with setup instructions, environment variables, and how to run the app
