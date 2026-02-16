from unittest.mock import patch, AsyncMock

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
def anyio_backend():
    return "asyncio"


@pytest.fixture
async def client(test_db):
    """Provide an async test client with mocked worker startup."""
    with patch("app.main.start_worker", new_callable=AsyncMock) as mock_start, \
         patch("app.main.stop_worker", new_callable=AsyncMock):
        mock_start.return_value = AsyncMock()
        transport = ASGITransport(app=app, raise_app_exceptions=False)
        async with AsyncClient(transport=transport, base_url="http://test") as ac:
            yield ac


class TestSubmitVideo:
    @patch("app.routes.fetch_video_metadata", return_value={"title": "Test", "duration": 60})
    async def test_submit_valid_url(self, mock_meta, client):
        resp = await client.post("/api/videos", json={"url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["video_id"] == "dQw4w9WgXcQ"
        assert data["status"] == "queued"
        assert data["title"] == "Test"

    async def test_submit_invalid_url_returns_400(self, client):
        resp = await client.post("/api/videos", json={"url": "https://vimeo.com/12345"})
        assert resp.status_code == 400

    @patch("app.routes.fetch_video_metadata", return_value={"title": "Test", "duration": 60})
    async def test_submit_duplicate_returns_existing(self, mock_meta, client):
        await client.post("/api/videos", json={"url": "https://youtu.be/dQw4w9WgXcQ"})
        resp = await client.post("/api/videos", json={"url": "https://youtu.be/dQw4w9WgXcQ"})
        assert resp.status_code == 200
        assert resp.json()["video_id"] == "dQw4w9WgXcQ"

    @patch("app.routes.fetch_video_metadata", return_value={"error": "Video is private"})
    async def test_submit_meta_error_creates_failed_video(self, mock_meta, client):
        resp = await client.post("/api/videos", json={"url": "https://www.youtube.com/watch?v=private1234"})
        assert resp.status_code == 200
        data = resp.json()
        assert data["status"] == "failed"
        assert "Video unavailable" in data["error_message"]


class TestBatchSubmit:
    @patch("app.routes.fetch_video_metadata", return_value={"title": "Test", "duration": 60})
    async def test_batch_mixed_urls(self, mock_meta, client):
        resp = await client.post("/api/videos/batch", json={
            "urls": [
                "https://youtu.be/abc12345678",
                "https://invalid-url.com",
                "https://youtu.be/def12345678",
            ]
        })
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert len(results) == 3
        assert results[0]["success"] is True
        assert results[1]["success"] is False
        assert results[1]["error"] == "Invalid YouTube URL"
        assert results[2]["success"] is True

    @patch("app.routes.fetch_video_metadata", return_value={"title": "Test", "duration": 60})
    async def test_batch_skips_empty_urls(self, mock_meta, client):
        resp = await client.post("/api/videos/batch", json={
            "urls": ["  ", "", "https://youtu.be/single12345"],
        })
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert len(results) == 1
        assert results[0]["success"] is True
        assert results[0]["video"]["video_id"] == "single12345"

    @patch("app.routes.fetch_video_metadata", return_value={"title": "Existing", "duration": 60})
    async def test_batch_returns_existing_video(self, mock_meta, client):
        await client.post("/api/videos", json={"url": "https://youtu.be/exist1234567"})
        resp = await client.post("/api/videos/batch", json={
            "urls": ["https://youtu.be/exist1234567"],
        })
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert len(results) == 1
        assert results[0]["success"] is True
        # YouTube IDs are 11 chars; extract_video_id returns first 11
        assert results[0]["video"]["video_id"] == "exist123456"
        assert mock_meta.call_count == 1

    @patch("app.routes.fetch_video_metadata", return_value={"error": "Unavailable"})
    async def test_batch_meta_error_creates_failed_video(self, mock_meta, client):
        resp = await client.post("/api/videos/batch", json={
            "urls": ["https://youtu.be/unavail12345"],
        })
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert len(results) == 1
        assert results[0]["success"] is True
        assert results[0]["video"]["status"] == "failed"
        assert "Unavailable" in results[0]["video"]["error_message"]

    @patch("app.routes.fetch_video_metadata", side_effect=Exception("Network error"))
    async def test_batch_exception_appends_error_result(self, mock_meta, client):
        resp = await client.post("/api/videos/batch", json={
            "urls": ["https://youtu.be/boom12345678"],
        })
        assert resp.status_code == 200
        results = resp.json()["results"]
        assert len(results) == 1
        assert results[0]["success"] is False
        assert results[0]["error"] == "Network error"


class TestListVideos:
    @patch("app.routes.fetch_video_metadata", return_value={"title": "V1", "duration": 60})
    async def test_list_all(self, mock_meta, client):
        await client.post("/api/videos", json={"url": "https://youtu.be/list1234567"})
        resp = await client.get("/api/videos")
        assert resp.status_code == 200
        assert len(resp.json()) >= 1

    @patch("app.routes.fetch_video_metadata", return_value={"title": "V1", "duration": 60})
    async def test_filter_by_status(self, mock_meta, client):
        await client.post("/api/videos", json={"url": "https://youtu.be/filt1234567"})
        resp = await client.get("/api/videos", params={"status": "completed"})
        assert resp.status_code == 200
        assert len(resp.json()) == 0


class TestGetVideo:
    @patch("app.routes.fetch_video_metadata", return_value={"title": "Test", "duration": 60})
    async def test_get_existing(self, mock_meta, client):
        create_resp = await client.post("/api/videos", json={"url": "https://youtu.be/get_1234567"})
        vid_id = create_resp.json()["id"]
        resp = await client.get(f"/api/videos/{vid_id}")
        assert resp.status_code == 200
        assert resp.json()["video_id"] == "get_1234567"

    async def test_get_nonexistent_returns_404(self, client):
        resp = await client.get("/api/videos/9999")
        assert resp.status_code == 404


class TestDeleteVideo:
    @patch("app.routes.fetch_video_metadata", return_value={"title": "Test", "duration": 60})
    async def test_delete_existing(self, mock_meta, client):
        create_resp = await client.post("/api/videos", json={"url": "https://youtu.be/del_12345678"})
        vid_id = create_resp.json()["id"]
        resp = await client.delete(f"/api/videos/{vid_id}")
        assert resp.status_code == 200

    async def test_delete_nonexistent_returns_404(self, client):
        resp = await client.delete("/api/videos/9999")
        assert resp.status_code == 404


class TestMainExceptionHandler:
    async def test_unhandled_exception_returns_500(self, client):
        with patch("app.routes.get_all_videos", side_effect=RuntimeError("Unexpected failure")):
            resp = await client.get("/api/videos")
        assert resp.status_code == 500
        assert "detail" in resp.json()
        assert "internal" in resp.json()["detail"].lower()
