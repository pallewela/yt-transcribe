import json
import logging
from datetime import datetime, timezone

from app.database import update_video
from app.transcriber import get_transcript
from app.summarizer import generate_summary

logger = logging.getLogger(__name__)


async def process_video(video: dict):
    """Full processing pipeline: transcribe → summarize → mark complete."""
    video_id = video["id"]
    url = video["url"]

    logger.info(f"Processing video {video_id}: {url}")

    transcript_segments, transcript_source = await get_transcript(video)

    transcript_text = " ".join(seg["text"] for seg in transcript_segments)

    await update_video(
        video_id,
        transcript_source=transcript_source,
        transcript_segments=json.dumps(transcript_segments),
        transcript_text=transcript_text,
    )

    logger.info(f"Video {video_id}: transcript obtained via {transcript_source} ({len(transcript_segments)} segments)")

    summary_data = await generate_summary(transcript_segments, transcript_text)

    now = datetime.now(timezone.utc).isoformat()
    await update_video(
        video_id,
        summary_json=json.dumps(summary_data),
        status="completed",
        completed_at=now,
    )

    logger.info(f"Video {video_id}: processing complete")
