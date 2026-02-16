from unittest.mock import patch, MagicMock

from app.youtube import validate_youtube_url, extract_video_id, fetch_video_metadata


class TestValidateYoutubeUrl:
    def test_standard_watch_url(self):
        assert validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ") is True

    def test_short_url(self):
        assert validate_youtube_url("https://youtu.be/dQw4w9WgXcQ") is True

    def test_embed_url(self):
        assert validate_youtube_url("https://www.youtube.com/embed/dQw4w9WgXcQ") is True

    def test_shorts_url(self):
        assert validate_youtube_url("https://www.youtube.com/shorts/dQw4w9WgXcQ") is True

    def test_watch_url_with_extra_params(self):
        assert validate_youtube_url("https://www.youtube.com/watch?v=dQw4w9WgXcQ&t=120") is True

    def test_url_without_https(self):
        assert validate_youtube_url("www.youtube.com/watch?v=dQw4w9WgXcQ") is True

    def test_non_youtube_url_rejected(self):
        assert validate_youtube_url("https://vimeo.com/123456") is False

    def test_empty_string_rejected(self):
        assert validate_youtube_url("") is False

    def test_random_text_rejected(self):
        assert validate_youtube_url("not a url at all") is False

    def test_youtube_domain_without_video(self):
        assert validate_youtube_url("https://www.youtube.com/") is False


class TestExtractVideoId:
    def test_standard_watch_url(self):
        assert extract_video_id("https://www.youtube.com/watch?v=dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_short_url(self):
        assert extract_video_id("https://youtu.be/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_embed_url(self):
        assert extract_video_id("https://www.youtube.com/embed/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_shorts_url(self):
        assert extract_video_id("https://www.youtube.com/shorts/dQw4w9WgXcQ") == "dQw4w9WgXcQ"

    def test_returns_none_for_invalid_url(self):
        assert extract_video_id("https://vimeo.com/123456") is None

    def test_returns_none_for_empty_string(self):
        assert extract_video_id("") is None

    def test_strips_whitespace(self):
        assert extract_video_id("  https://youtu.be/dQw4w9WgXcQ  ") == "dQw4w9WgXcQ"


class TestFetchVideoMetadata:
    @patch("app.youtube.yt_dlp.YoutubeDL")
    def test_successful_metadata_fetch(self, mock_ydl_class):
        mock_ydl = MagicMock()
        mock_ydl.extract_info.return_value = {
            "title": "Test Video",
            "duration": 300,
        }
        mock_ydl_class.return_value.__enter__ = MagicMock(return_value=mock_ydl)
        mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)

        result = fetch_video_metadata("https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        assert result["title"] == "Test Video"
        assert result["duration"] == 300
        assert "error" not in result

    @patch("app.youtube.yt_dlp.YoutubeDL")
    def test_metadata_fetch_failure(self, mock_ydl_class):
        mock_ydl_class.return_value.__enter__ = MagicMock(
            side_effect=Exception("Video unavailable")
        )
        mock_ydl_class.return_value.__exit__ = MagicMock(return_value=False)

        result = fetch_video_metadata("https://www.youtube.com/watch?v=invalid123")
        assert result["title"] is None
        assert result["duration"] is None
        assert "error" in result
