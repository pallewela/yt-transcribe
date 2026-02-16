import json
from unittest.mock import patch, AsyncMock

import pytest

from app.pipeline import process_video


SAMPLE_VIDEO = {
    "id": 1,
    "url": "https://www.youtube.com/watch?v=test12345ab",
    "video_id": "test12345ab",
    "status": "processing",
    "attempt_count": 0,
}

SAMPLE_SEGMENTS = [
    {"start": 0.0, "text": "Hello"},
    {"start": 5.0, "text": "World"},
]

SAMPLE_SUMMARY = {
    "overview": "Test overview.",
    "key_points": [{"timestamp": 0, "text": "Hello point"}],
}


class TestProcessVideo:
    @patch("app.pipeline.update_video", new_callable=AsyncMock)
    @patch("app.pipeline.generate_summary", new_callable=AsyncMock)
    @patch("app.pipeline.get_transcript", new_callable=AsyncMock)
    async def test_successful_pipeline(self, mock_transcript, mock_summary, mock_update):
        mock_transcript.return_value = (SAMPLE_SEGMENTS, "youtube_captions")
        mock_summary.return_value = SAMPLE_SUMMARY

        await process_video(SAMPLE_VIDEO)

        assert mock_transcript.call_count == 1
        assert mock_summary.call_count == 1
        assert mock_update.call_count == 2

    @patch("app.pipeline.update_video", new_callable=AsyncMock)
    @patch("app.pipeline.generate_summary", new_callable=AsyncMock)
    @patch("app.pipeline.get_transcript", new_callable=AsyncMock)
    async def test_stores_transcript_data(self, mock_transcript, mock_summary, mock_update):
        mock_transcript.return_value = (SAMPLE_SEGMENTS, "whisper")
        mock_summary.return_value = SAMPLE_SUMMARY

        await process_video(SAMPLE_VIDEO)

        first_update_kwargs = mock_update.call_args_list[0]
        args, kwargs = first_update_kwargs
        assert args[0] == 1  # video_id
        assert kwargs["transcript_source"] == "whisper"
        assert json.loads(kwargs["transcript_segments"]) == SAMPLE_SEGMENTS
        assert "Hello World" == kwargs["transcript_text"]

    @patch("app.pipeline.update_video", new_callable=AsyncMock)
    @patch("app.pipeline.generate_summary", new_callable=AsyncMock)
    @patch("app.pipeline.get_transcript", new_callable=AsyncMock)
    async def test_stores_summary_and_marks_completed(self, mock_transcript, mock_summary, mock_update):
        mock_transcript.return_value = (SAMPLE_SEGMENTS, "youtube_captions")
        mock_summary.return_value = SAMPLE_SUMMARY

        await process_video(SAMPLE_VIDEO)

        second_update_kwargs = mock_update.call_args_list[1]
        args, kwargs = second_update_kwargs
        assert args[0] == 1
        assert kwargs["status"] == "completed"
        assert json.loads(kwargs["summary_json"]) == SAMPLE_SUMMARY
        assert "completed_at" in kwargs
