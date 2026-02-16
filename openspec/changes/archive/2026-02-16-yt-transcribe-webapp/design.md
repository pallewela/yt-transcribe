## Context

This is a greenfield web application for transcribing and summarizing YouTube videos. Users submit video URLs through a web interface, and the system processes them asynchronously — downloading audio, transcribing it, and generating summaries. Users return later to review completed summaries. There is no existing codebase; all components are new.

## Goals / Non-Goals

**Goals:**
- Simple, responsive web UI for submitting YouTube links and reviewing summaries
- Fully asynchronous processing — users never wait for transcription or summarization to complete
- Reliable job pipeline that handles failures gracefully with retry logic
- Persistent storage of video metadata, transcripts, summaries, and job status
- Clear visibility into processing status for each submitted video

**Non-Goals:**
- User authentication or multi-tenancy (single-user app for now)
- Real-time streaming of transcription progress
- Video playback within the application
- Support for non-YouTube video sources
- Editing or annotating transcripts/summaries
- Mobile-native application (responsive web is sufficient)

## Decisions

### 1. Tech Stack: Python + FastAPI + SQLite + React

**Choice:** Python backend with FastAPI, SQLite for storage, React frontend with Vite.

**Rationale:** Python has the strongest ecosystem for the core requirements — yt-dlp for YouTube audio extraction, OpenAI Whisper for transcription, and OpenAI/LLM client libraries for summarization. FastAPI provides async support and automatic API documentation. SQLite keeps infrastructure simple (no separate database server) while being sufficient for single-user workloads. React with Vite gives a modern, fast frontend development experience.

**Alternatives considered:**
- Node.js/TypeScript full-stack: Weaker ecosystem for audio processing and ML tooling
- Django: Heavier than needed for an API-first app
- PostgreSQL: Overkill for single-user; SQLite is simpler to deploy

### 2. Transcription Strategy: YouTube captions first, Whisper as fallback

**Choice:** Attempt to fetch YouTube's existing transcript/captions first. Only download audio and use Whisper if no captions are available.

**Rationale:** Many YouTube videos already have auto-generated or manually uploaded captions. Using these is instant, free, and avoids downloading large audio files. This dramatically reduces processing time and API cost for the majority of videos. yt-dlp can extract subtitles/captions alongside metadata. The youtube-transcript-api Python library is another lightweight option for fetching captions directly. Whisper remains available as a high-quality fallback for videos without captions.

**Alternatives considered:**
- Always use Whisper: Consistent quality but unnecessary cost and latency when captions exist
- Only use YouTube captions: Cheaper but some videos lack captions entirely

### 3. Audio Extraction (fallback): yt-dlp

**Choice:** Use yt-dlp to download audio when YouTube captions are not available.

**Rationale:** yt-dlp is the most actively maintained YouTube downloader, supports audio-only extraction, subtitle extraction, and handles various YouTube URL formats. It serves double duty — checking for captions and downloading audio when needed.

**Alternatives considered:**
- pytube: Less actively maintained, more frequent breakage with YouTube changes
- YouTube Data API: Only provides metadata, not audio content

### 4. Transcription (fallback): OpenAI Whisper API

**Choice:** Use OpenAI's Whisper API for speech-to-text when YouTube captions are unavailable.

**Rationale:** Cloud API avoids the need to run a local Whisper model (which requires significant GPU resources). Provides high-quality transcription across languages. Pay-per-use pricing is cost-effective since it's only used as a fallback.

**Alternatives considered:**
- Local Whisper model: Requires GPU, complex deployment, but free after setup
- Google Speech-to-Text: Similar quality but more complex API setup
- AssemblyAI: Good alternative but adds another vendor dependency

### 5. Timestamped Transcripts and Clickable Summary Links

**Choice:** Store transcripts as timestamped segments (start time + text). Require the LLM to anchor each summary key point to a timestamp. Render summary key points as clickable links that open the YouTube video at the corresponding time.

**Rationale:** Both transcript sources naturally support timestamps — YouTube captions come with per-segment timing, and Whisper API returns segment-level timestamps when using `response_format="verbose_json"`. By preserving this timing data through to summarization, each key point in the summary can reference a specific moment in the video. The frontend renders these as clickable links using YouTube's `?t=` URL parameter, letting users jump directly to relevant parts of the video. This transforms the summary from a passive read into an interactive navigation tool.

**Storage format:** Transcript segments are stored as JSON (array of `{start: seconds, text: "..."}` objects) alongside a plain-text version for display. The summary is stored as JSON with each key point carrying a `timestamp` field.

**Alternatives considered:**
- Plain text transcripts only: Simpler but loses the ability to link back to video positions
- Word-level timestamps: More precise but excessive granularity; segment-level (every few seconds) is sufficient for navigation

### 6. Summarization: OpenAI GPT API

**Choice:** Use OpenAI's GPT API (gpt-4o-mini or similar) for transcript summarization.

**Rationale:** Same vendor as Whisper simplifies API key management. GPT models produce high-quality summaries and can handle long transcripts via chunking. gpt-4o-mini offers a good balance of quality and cost.

**Alternatives considered:**
- Local LLM (Ollama): Free but requires significant hardware and produces lower-quality summaries
- Anthropic Claude: Excellent quality but adds another API key/vendor
- Simple extractive summarization: Lower quality, no semantic understanding

### 7. Background Processing: Python asyncio with a simple task runner

**Choice:** Use a lightweight in-process task runner built on Python's asyncio and SQLite-backed job queue.

**Rationale:** For a single-user application, a full-blown task queue like Celery or BullMQ is overkill. A simple approach using asyncio background tasks with job state persisted in SQLite keeps the architecture simple — one process, one database, no Redis dependency. Jobs are picked up from SQLite and processed sequentially or with limited concurrency.

**Alternatives considered:**
- Celery + Redis: Production-grade but adds Redis as a dependency and operational complexity
- ARQ (async Redis queue): Still requires Redis
- Huey: Lighter than Celery but still adds a dependency

### 8. Project Structure: Monorepo with separate frontend/backend

**Choice:** Single repository with `backend/` and `frontend/` directories.

**Rationale:** Simplifies development and deployment for a single-developer project. Backend serves the API, frontend is a static SPA built by Vite and can be served by the backend or a simple static file server.

## Risks / Trade-offs

- **[yt-dlp breakage]** YouTube frequently changes its internals, which can break yt-dlp. → *Mitigation:* Keep yt-dlp updated. The library has an active community that patches quickly. Pin to latest working version.

- **[API cost]** Whisper + GPT API calls cost money per video. → *Mitigation:* Use YouTube captions when available (free) to avoid Whisper costs entirely for most videos. Use gpt-4o-mini for summarization (cheaper).

- **[Long video processing time]** A 2-hour video may take several minutes to download and transcribe. → *Mitigation:* Async processing with clear status indicators. Users are explicitly not waiting.

- **[SQLite concurrency]** SQLite has limited write concurrency. → *Mitigation:* Acceptable for single-user app. Use WAL mode for better concurrent read/write performance.

- **[Large audio files]** Downloaded audio files consume disk space. → *Mitigation:* Delete audio files after transcription is complete. Store only transcripts and summaries.

- **[OpenAI API dependency]** Single vendor for both transcription and summarization. → *Mitigation:* Abstract the transcription and summarization behind interfaces so providers can be swapped later.
