import json
from unittest.mock import patch, MagicMock

import pytest

from app.summarizer import (
    _format_timestamped_transcript,
    _split_segments_into_chunks,
    generate_summary,
)


SAMPLE_SEGMENTS = [
    {"start": 0.0, "text": "Hello and welcome."},
    {"start": 65.3, "text": "Now let's discuss the main topic."},
    {"start": 130.0, "text": "In conclusion, testing is important."},
]

MOCK_SUMMARY_RESPONSE = json.dumps({
    "overview": "This video covers testing.",
    "key_points": [
        {"timestamp": 0, "text": "Introduction."},
        {"timestamp": 65, "text": "Main discussion."},
        {"timestamp": 130, "text": "Conclusion."},
    ],
})


class TestFormatTimestampedTranscript:
    def test_formats_segments_correctly(self):
        result = _format_timestamped_transcript(SAMPLE_SEGMENTS)
        lines = result.strip().split("\n")
        assert len(lines) == 3
        assert lines[0] == "[00:00] (0.0s) Hello and welcome."
        assert lines[1] == "[01:05] (65.3s) Now let's discuss the main topic."
        assert lines[2] == "[02:10] (130.0s) In conclusion, testing is important."

    def test_empty_segments(self):
        result = _format_timestamped_transcript([])
        assert result == ""


class TestSplitSegmentsIntoChunks:
    def test_single_chunk_when_small(self):
        chunks = _split_segments_into_chunks(SAMPLE_SEGMENTS, max_chars=10000)
        assert len(chunks) == 1
        assert len(chunks[0]) == 3

    def test_multiple_chunks_when_large(self):
        segments = [{"start": i * 5.0, "text": f"Segment number {i} with some text."} for i in range(100)]
        chunks = _split_segments_into_chunks(segments, max_chars=500)
        assert len(chunks) > 1
        total = sum(len(c) for c in chunks)
        assert total == 100

    def test_no_empty_chunks(self):
        segments = [{"start": 0.0, "text": "A"}]
        chunks = _split_segments_into_chunks(segments, max_chars=100)
        assert len(chunks) == 1
        assert len(chunks[0]) == 1


def _make_mock_openai_client(response_content):
    """Create a mock OpenAI client that returns the given content."""
    mock_client = MagicMock()
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = response_content
    mock_client.chat.completions.create.return_value = mock_response
    return mock_client


class TestGenerateSummary:
    @patch("app.summarizer.OpenAI")
    async def test_single_pass_summary(self, mock_openai_class):
        mock_client = _make_mock_openai_client(MOCK_SUMMARY_RESPONSE)
        mock_openai_class.return_value = mock_client

        transcript_text = " ".join(seg["text"] for seg in SAMPLE_SEGMENTS)
        result = await generate_summary(SAMPLE_SEGMENTS, transcript_text)

        assert "overview" in result
        assert "key_points" in result
        assert len(result["key_points"]) == 3
        mock_client.chat.completions.create.assert_called_once()

    @patch("app.summarizer.OpenAI")
    async def test_chunked_summary(self, mock_openai_class):
        mock_client = _make_mock_openai_client(MOCK_SUMMARY_RESPONSE)
        mock_openai_class.return_value = mock_client

        # Need >100,000 chars in transcript_text to trigger chunked path
        long_segments = [{"start": i * 5.0, "text": "x" * 1000} for i in range(150)]
        long_text = " ".join(seg["text"] for seg in long_segments)
        assert len(long_text) > 100_000

        result = await generate_summary(long_segments, long_text)

        assert "overview" in result
        assert "key_points" in result
        assert mock_client.chat.completions.create.call_count > 1
