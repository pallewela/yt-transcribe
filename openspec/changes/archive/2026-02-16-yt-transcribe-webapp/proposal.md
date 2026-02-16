## Why

Watching YouTube videos to extract key information is time-consuming. There's a need for a tool that can accept YouTube video links, automatically transcribe the audio, and generate concise summaries — all without requiring the user to wait for processing to complete. Users should be able to submit a batch of videos and return later to read through the summaries at their convenience.

## What Changes

- **New web application** for submitting YouTube video links and reviewing generated summaries
- **Batch video submission**: Users can paste one or more YouTube URLs at once without waiting for results
- **Asynchronous transcription pipeline**: Videos are queued and transcribed in the background using speech-to-text
- **AI-powered summarization**: Transcripts are automatically summarized into digestible overviews
- **Summary review dashboard**: A dedicated view where users can browse, read, and manage completed summaries
- **Job status tracking**: Users can see which videos are still processing, completed, or failed

## Capabilities

### New Capabilities

- `video-submission`: Accepting YouTube video URLs (single or batch), validating them, and queuing them for processing
- `transcription-pipeline`: Downloading audio from YouTube videos and converting speech to text via a transcription service
- `summarization`: Generating concise summaries from transcripts using an LLM
- `job-queue`: Background job processing system that handles transcription and summarization asynchronously, with status tracking
- `summary-dashboard`: Web UI for browsing, reading, and managing completed video summaries

### Modified Capabilities

_None — this is a greenfield application._

## Impact

- **New full-stack web application**: Frontend (UI for submission and review) + Backend (API, job processing)
- **External API dependencies**: YouTube data extraction (e.g., yt-dlp), speech-to-text service (e.g., OpenAI Whisper), LLM for summarization (e.g., OpenAI GPT)
- **Persistent storage**: Database needed for storing video metadata, transcripts, summaries, and job status
- **Background processing**: Requires a task queue or job runner for async work (e.g., BullMQ, Celery, or similar)
- **Infrastructure**: Hosting for the web app, database, and background workers
