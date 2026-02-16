import asyncio
import json
import logging

from openai import OpenAI

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a video summarization assistant. You receive a transcript of a YouTube video with timestamps.

Your task is to produce a structured JSON summary with:
1. An "overview" field: 2-3 sentences summarizing the video's main topic and purpose.
2. A "key_points" array: Each key point has:
   - "timestamp": The start time in seconds (integer) of the most relevant moment for this point. Use the timestamps from the transcript.
   - "text": A concise description of the key point (1-2 sentences).

Return ONLY valid JSON, no markdown formatting, no code fences. Example format:
{
  "overview": "This video discusses...",
  "key_points": [
    {"timestamp": 0, "text": "Introduction to the topic..."},
    {"timestamp": 125, "text": "The speaker explains..."},
    {"timestamp": 340, "text": "Key insight about..."}
  ]
}

Aim for 5-10 key points that capture the most important ideas, decisions, or insights from the video. Each key point should reference the timestamp where that topic is discussed."""


def _format_timestamped_transcript(segments: list[dict]) -> str:
    """Format transcript segments with timestamps for the LLM prompt."""
    lines = []
    for seg in segments:
        start = seg["start"]
        minutes = int(start // 60)
        seconds = int(start % 60)
        lines.append(f"[{minutes:02d}:{seconds:02d}] ({start}s) {seg['text']}")
    return "\n".join(lines)


async def generate_summary(transcript_segments: list[dict], transcript_text: str) -> dict:
    """Generate a timestamp-anchored summary from transcript segments."""
    client = OpenAI()

    total_chars = len(transcript_text)
    max_chars = 100_000  # roughly fits in context with prompt overhead

    if total_chars <= max_chars:
        return await _summarize_single(client, transcript_segments)
    else:
        return await _summarize_chunked(client, transcript_segments, max_chars)


async def _summarize_single(client: OpenAI, segments: list[dict]) -> dict:
    """Summarize transcript in a single LLM call."""
    formatted = _format_timestamped_transcript(segments)

    def _call():
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"Here is the timestamped transcript:\n\n{formatted}"},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)

    return await asyncio.to_thread(_call)


async def _summarize_chunked(client: OpenAI, segments: list[dict],
                              max_chars: int) -> dict:
    """Summarize long transcripts by chunking and combining."""
    chunks = _split_segments_into_chunks(segments, max_chars)
    logger.info(f"Splitting transcript into {len(chunks)} chunks for summarization")

    chunk_summaries = []
    for i, chunk in enumerate(chunks):
        logger.info(f"Summarizing chunk {i + 1}/{len(chunks)}")
        summary = await _summarize_single(client, chunk)
        chunk_summaries.append(summary)

    return await _combine_summaries(client, chunk_summaries)


def _split_segments_into_chunks(segments: list[dict], max_chars: int) -> list[list[dict]]:
    """Split segments into chunks that fit within character limits."""
    chunks = []
    current_chunk = []
    current_size = 0

    for seg in segments:
        seg_size = len(seg["text"]) + 20  # account for timestamp formatting
        if current_size + seg_size > max_chars and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_size = 0
        current_chunk.append(seg)
        current_size += seg_size

    if current_chunk:
        chunks.append(current_chunk)

    return chunks


async def _combine_summaries(client: OpenAI, chunk_summaries: list[dict]) -> dict:
    """Combine multiple chunk summaries into a final summary."""
    chunks_text = []
    for i, summary in enumerate(chunk_summaries):
        chunks_text.append(f"--- Chunk {i + 1} ---")
        chunks_text.append(f"Overview: {summary.get('overview', '')}")
        for kp in summary.get("key_points", []):
            chunks_text.append(f"  [{kp['timestamp']}s] {kp['text']}")

    combined_input = "\n".join(chunks_text)

    combine_prompt = """You are given summaries of different parts of the same video.
Combine them into a single cohesive summary with the same JSON format:
- "overview": 2-3 sentences covering the entire video
- "key_points": 5-10 most important points across all chunks, preserving their original timestamps (in seconds)

Return ONLY valid JSON, no markdown, no code fences."""

    def _call():
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": combine_prompt},
                {"role": "user", "content": combined_input},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        content = response.choices[0].message.content
        return json.loads(content)

    return await asyncio.to_thread(_call)
