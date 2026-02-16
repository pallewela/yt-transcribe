# YT Transcribe

A web application that transcribes YouTube videos and generates AI-powered summaries with clickable timestamp links. Submit video URLs, let the app process them in the background, and come back later to read the summaries.

## Features

- **Batch video submission** — paste one or more YouTube URLs at once
- **Async processing** — videos are transcribed and summarized in the background
- **Smart transcription** — uses YouTube captions when available (free & fast), falls back to OpenAI Whisper
- **AI summaries with timestamps** — each key point links to the exact moment in the video
- **Clickable timestamps** — click any timestamp in the summary or transcript to jump to that point on YouTube
- **Status tracking** — see which videos are queued, processing, completed, or failed

## Tech Stack

- **Backend**: Python, FastAPI, SQLite (WAL mode), asyncio
- **Frontend**: React, Vite, React Router, Axios
- **AI/ML**: OpenAI Whisper API (transcription fallback), OpenAI GPT-4o-mini (summarization)
- **YouTube**: youtube-transcript-api (captions), yt-dlp (audio download & metadata)

## Setup

### Prerequisites

- Python 3.11+
- Node.js 18+
- An OpenAI API key

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create .env from example
cp .env.example .env
# Edit .env and add your OPENAI_API_KEY
```

### Frontend

```bash
cd frontend
npm install
```

## Running

### Development (two terminals)

**Terminal 1 — Backend:**
```bash
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — Frontend:**
```bash
cd frontend
npm run dev
```

Open http://localhost:5173 in your browser.

### Production

Build the frontend and serve from the backend:

```bash
cd frontend
npm run build
cp -r dist/* ../backend/static/

cd ../backend
source venv/bin/activate
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

Open http://localhost:8000 in your browser.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | (required) | Your OpenAI API key |
| `DATABASE_PATH` | `data/yt_transcribe.db` | Path to SQLite database |
| `MAX_RETRY_ATTEMPTS` | `3` | Max retries for failed jobs |
| `RETRY_DELAY_SECONDS` | `30` | Delay between retries |
| `WORKER_POLL_INTERVAL` | `5` | Seconds between job queue polls |

## How It Works

1. **Submit** YouTube URLs via the web interface
2. **Queue** — videos are validated and queued for processing
3. **Transcribe** — the worker first checks for YouTube captions (with timestamps); if none exist, it downloads audio and uses OpenAI Whisper
4. **Summarize** — the timestamped transcript is sent to GPT-4o-mini, which produces an overview and timestamp-anchored key points
5. **Review** — browse completed summaries; click any timestamp to jump to that moment on YouTube
