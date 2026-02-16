import asyncio
import logging
import os
import tempfile
from pathlib import Path
from typing import Optional

import yt_dlp
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi

logger = logging.getLogger(__name__)

_yt_transcript_api = YouTubeTranscriptApi()


async def get_transcript(video: dict) -> tuple[list[dict], str]:
    """
    Get transcript for a video. Tries YouTube captions first,
    falls back to Whisper if unavailable.
    Returns (segments, source) where segments = [{start, text}, ...].
    """
    video_id = video["video_id"]

    segments = await _fetch_youtube_captions(video_id)
    if segments:
        return segments, "youtube_captions"

    logger.info(f"No YouTube captions for {video_id}, falling back to Whisper")
    segments = await _transcribe_with_whisper(video["url"])
    return segments, "whisper"


async def _fetch_youtube_captions(video_id: str) -> Optional[list[dict]]:
    """Fetch YouTube captions with timestamps using youtube-transcript-api."""
    try:
        fetched = await asyncio.to_thread(
            _fetch_captions_sync, video_id
        )
        return fetched
    except Exception as e:
        logger.warning(f"Could not fetch YouTube captions for {video_id}: {e}")
        return None


def _fetch_captions_sync(video_id: str) -> list[dict]:
    transcript_list = _yt_transcript_api.list(video_id)

    try:
        transcript = transcript_list.find_manually_created_transcript(["en"])
    except Exception:
        try:
            transcript = transcript_list.find_generated_transcript(["en"])
        except Exception:
            available = list(transcript_list)
            if available:
                transcript = available[0]
                if transcript.language_code != "en":
                    transcript = transcript.translate("en")
            else:
                raise ValueError("No transcripts available")

    fetched = transcript.fetch()
    segments = []
    for entry in fetched:
        segments.append({
            "start": round(entry.start, 1),
            "text": entry.text.strip(),
        })
    return segments


async def _transcribe_with_whisper(url: str) -> list[dict]:
    """Download audio and transcribe with OpenAI Whisper API."""
    audio_path = None
    try:
        audio_path = await asyncio.to_thread(_download_audio, url)
        segments = await _whisper_transcribe(audio_path)
        return segments
    finally:
        if audio_path and os.path.exists(audio_path):
            os.remove(audio_path)
            logger.info(f"Cleaned up audio file: {audio_path}")


def _download_audio(url: str) -> str:
    """Download audio from YouTube video using yt-dlp."""
    tmp_dir = tempfile.mkdtemp(prefix="yt_audio_")
    output_path = os.path.join(tmp_dir, "audio.%(ext)s")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_path,
        "postprocessors": [{
            "key": "FFmpegExtractAudio",
            "preferredcodec": "mp3",
            "preferredquality": "128",
        }],
        "quiet": True,
        "no_warnings": True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

    mp3_path = os.path.join(tmp_dir, "audio.mp3")
    if not os.path.exists(mp3_path):
        for f in os.listdir(tmp_dir):
            if f.endswith((".mp3", ".m4a", ".wav", ".ogg", ".webm")):
                mp3_path = os.path.join(tmp_dir, f)
                break

    if not os.path.exists(mp3_path):
        raise FileNotFoundError(f"Audio file not found in {tmp_dir}")

    return mp3_path


async def _whisper_transcribe(audio_path: str) -> list[dict]:
    """Transcribe audio using OpenAI Whisper API with timestamps."""
    client = OpenAI()
    file_size = os.path.getsize(audio_path)
    max_size = 25 * 1024 * 1024  # 25MB

    if file_size <= max_size:
        return await _whisper_single_file(client, audio_path)
    else:
        return await _whisper_chunked(client, audio_path)


async def _whisper_single_file(client: OpenAI, audio_path: str) -> list[dict]:
    """Transcribe a single audio file with Whisper."""
    def _transcribe():
        with open(audio_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                response_format="verbose_json",
                timestamp_granularities=["segment"],
            )
        segments = []
        for seg in response.segments:
            segments.append({
                "start": round(seg["start"], 1),
                "text": seg["text"].strip(),
            })
        return segments

    return await asyncio.to_thread(_transcribe)


async def _whisper_chunked(client: OpenAI, audio_path: str) -> list[dict]:
    """Split audio into chunks and transcribe each with Whisper."""
    from pydub import AudioSegment

    def _split_and_transcribe():
        audio = AudioSegment.from_file(audio_path)
        chunk_duration_ms = 10 * 60 * 1000  # 10 minutes per chunk
        chunks = []
        for i in range(0, len(audio), chunk_duration_ms):
            chunks.append(audio[i:i + chunk_duration_ms])

        all_segments = []
        offset_seconds = 0.0

        for i, chunk in enumerate(chunks):
            chunk_path = audio_path + f".chunk{i}.mp3"
            chunk.export(chunk_path, format="mp3")
            try:
                with open(chunk_path, "rb") as f:
                    response = client.audio.transcriptions.create(
                        model="whisper-1",
                        file=f,
                        response_format="verbose_json",
                        timestamp_granularities=["segment"],
                    )
                for seg in response.segments:
                    all_segments.append({
                        "start": round(seg["start"] + offset_seconds, 1),
                        "text": seg["text"].strip(),
                    })
            finally:
                if os.path.exists(chunk_path):
                    os.remove(chunk_path)

            offset_seconds += chunk.duration_seconds

        return all_segments

    return await asyncio.to_thread(_split_and_transcribe)
