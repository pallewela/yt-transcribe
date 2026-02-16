import os
import tempfile
from unittest.mock import patch, MagicMock, AsyncMock

import pytest

from app.transcriber import get_transcript, _fetch_youtube_captions, _transcribe_with_whisper


SAMPLE_VIDEO = {
    "id": 1,
    "url": "https://www.youtube.com/watch?v=test12345ab",
    "video_id": "test12345ab",
}


def _make_mock_snippet(start, text):
    """Create a mock transcript snippet with .start and .text attributes."""
    snippet = MagicMock()
    snippet.start = start
    snippet.text = text
    return snippet


MOCK_FETCHED_ENTRIES = [
    _make_mock_snippet(0.0, " Hello everyone. "),
    _make_mock_snippet(5.5, " Welcome to this video. "),
]


def _make_mock_transcript_list(has_captions=True):
    """Create a mock transcript list object."""
    mock_list = MagicMock()
    if has_captions:
        mock_transcript = MagicMock()
        mock_transcript.fetch.return_value = MOCK_FETCHED_ENTRIES
        mock_list.find_manually_created_transcript.return_value = mock_transcript
    else:
        mock_list.find_manually_created_transcript.side_effect = Exception("No manual")
        mock_list.find_generated_transcript.side_effect = Exception("No generated")
        mock_list.__iter__ = MagicMock(return_value=iter([]))
    return mock_list


class TestGetTranscript:
    @patch("app.transcriber._fetch_youtube_captions")
    async def test_returns_youtube_captions_when_available(self, mock_fetch):
        mock_fetch.return_value = [
            {"start": 0.0, "text": "Hello"},
            {"start": 5.5, "text": "World"},
        ]
        segments, source = await get_transcript(SAMPLE_VIDEO)
        assert source == "youtube_captions"
        assert len(segments) == 2
        assert segments[0]["text"] == "Hello"

    @patch("app.transcriber._transcribe_with_whisper")
    @patch("app.transcriber._fetch_youtube_captions")
    async def test_falls_back_to_whisper_when_no_captions(self, mock_captions, mock_whisper):
        mock_captions.return_value = None
        mock_whisper.return_value = [{"start": 0.0, "text": "Whisper text"}]

        segments, source = await get_transcript(SAMPLE_VIDEO)
        assert source == "whisper"
        assert segments[0]["text"] == "Whisper text"
        mock_whisper.assert_called_once_with(SAMPLE_VIDEO["url"])

    @patch("app.transcriber._transcribe_with_whisper")
    @patch("app.transcriber._fetch_youtube_captions")
    async def test_caption_exception_falls_back_to_whisper(self, mock_captions, mock_whisper):
        mock_captions.return_value = None
        mock_whisper.return_value = [{"start": 0.0, "text": "Fallback"}]

        segments, source = await get_transcript(SAMPLE_VIDEO)
        assert source == "whisper"


class TestFetchYoutubeCaptions:
    @patch("app.transcriber._yt_transcript_api")
    async def test_returns_timestamped_segments(self, mock_api):
        mock_api.list.return_value = _make_mock_transcript_list(has_captions=True)
        segments = await _fetch_youtube_captions("test12345ab")
        assert segments is not None
        assert len(segments) == 2
        assert segments[0]["start"] == 0.0
        assert segments[0]["text"] == "Hello everyone."
        assert segments[1]["start"] == 5.5

    @patch("app.transcriber._yt_transcript_api")
    async def test_returns_none_on_failure(self, mock_api):
        mock_api.list.side_effect = Exception("Network error")
        segments = await _fetch_youtube_captions("test12345ab")
        assert segments is None


class TestAudioCleanup:
    @patch("app.transcriber._whisper_transcribe")
    @patch("app.transcriber._download_audio")
    async def test_cleanup_after_success(self, mock_download, mock_whisper):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.write(b"fake audio")
        tmp.close()

        mock_download.return_value = tmp.name
        mock_whisper.return_value = [{"start": 0.0, "text": "Hello"}]

        await _transcribe_with_whisper("https://youtu.be/test12345ab")
        assert not os.path.exists(tmp.name)

    @patch("app.transcriber._whisper_transcribe")
    @patch("app.transcriber._download_audio")
    async def test_cleanup_after_failure(self, mock_download, mock_whisper):
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        tmp.write(b"fake audio")
        tmp.close()

        mock_download.return_value = tmp.name
        mock_whisper.side_effect = Exception("Whisper failed")

        with pytest.raises(Exception, match="Whisper failed"):
            await _transcribe_with_whisper("https://youtu.be/test12345ab")
        assert not os.path.exists(tmp.name)
