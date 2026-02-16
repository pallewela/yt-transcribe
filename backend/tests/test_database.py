import json

import aiosqlite
import pytest

from app.database import (
    create_video,
    delete_video,
    get_all_videos,
    get_next_queued_video,
    get_video_by_id,
    get_video_by_video_id,
    update_video,
    _row_to_dict,
)


class TestCreateAndGetVideo:
    async def test_create_video_returns_record(self, test_db):
        video = await create_video(
            url="https://www.youtube.com/watch?v=abc12345678",
            video_id="abc12345678",
            title="Test Video",
            duration=120,
        )
        assert video["id"] is not None
        assert video["url"] == "https://www.youtube.com/watch?v=abc12345678"
        assert video["video_id"] == "abc12345678"
        assert video["title"] == "Test Video"
        assert video["duration"] == 120
        assert video["status"] == "queued"

    async def test_get_video_by_id(self, test_db):
        video = await create_video(
            url="https://youtu.be/xyz98765432",
            video_id="xyz98765432",
        )
        fetched = await get_video_by_id(video["id"])
        assert fetched is not None
        assert fetched["video_id"] == "xyz98765432"

    async def test_get_video_by_id_not_found(self, test_db):
        result = await get_video_by_id(9999)
        assert result is None


class TestDuplicateHandling:
    async def test_duplicate_video_id_raises(self, test_db):
        await create_video(url="https://youtu.be/dup123456ab", video_id="dup123456ab")
        with pytest.raises(aiosqlite.IntegrityError):
            await create_video(url="https://youtu.be/dup123456ab", video_id="dup123456ab")


class TestGetVideoByVideoId:
    async def test_found(self, test_db):
        await create_video(url="https://youtu.be/findme12345", video_id="findme12345", title="Find Me")
        result = await get_video_by_video_id("findme12345")
        assert result is not None
        assert result["title"] == "Find Me"

    async def test_not_found(self, test_db):
        result = await get_video_by_video_id("nonexistent00")
        assert result is None


class TestGetAllVideos:
    async def test_returns_all_ordered_by_date_desc(self, test_db):
        await create_video(url="https://youtu.be/vid1_1234ab", video_id="vid1_1234ab", title="First")
        await create_video(url="https://youtu.be/vid2_1234ab", video_id="vid2_1234ab", title="Second")
        videos = await get_all_videos()
        assert len(videos) == 2
        assert videos[0]["title"] == "Second"
        assert videos[1]["title"] == "First"

    async def test_filter_by_status(self, test_db):
        v1 = await create_video(url="https://youtu.be/sta1_1234ab", video_id="sta1_1234ab")
        await create_video(url="https://youtu.be/sta2_1234ab", video_id="sta2_1234ab")
        await update_video(v1["id"], status="completed")

        queued = await get_all_videos(status="queued")
        assert len(queued) == 1
        completed = await get_all_videos(status="completed")
        assert len(completed) == 1


class TestUpdateVideo:
    async def test_update_fields(self, test_db):
        video = await create_video(url="https://youtu.be/upd123456ab", video_id="upd123456ab")
        updated = await update_video(video["id"], status="processing", title="Updated Title")
        assert updated["status"] == "processing"
        assert updated["title"] == "Updated Title"


class TestDeleteVideo:
    async def test_delete_existing(self, test_db):
        video = await create_video(url="https://youtu.be/del123456ab", video_id="del123456ab")
        result = await delete_video(video["id"])
        assert result is True
        assert await get_video_by_id(video["id"]) is None

    async def test_delete_nonexistent(self, test_db):
        result = await delete_video(9999)
        assert result is False


class TestGetNextQueuedVideo:
    async def test_picks_oldest_queued(self, test_db):
        v1 = await create_video(url="https://youtu.be/q1_12345678", video_id="q1_12345678", title="Oldest")
        await create_video(url="https://youtu.be/q2_12345678", video_id="q2_12345678", title="Newer")
        await update_video(v1["id"], status="processing")

        result = await get_next_queued_video()
        assert result is not None
        assert result["title"] == "Newer"

    async def test_returns_none_when_empty(self, test_db):
        result = await get_next_queued_video()
        assert result is None


class TestRowToDict:
    async def test_deserializes_json_fields(self, test_db):
        segments = [{"start": 0, "text": "Hello"}]
        summary = {"overview": "Test", "key_points": []}
        video = await create_video(url="https://youtu.be/json1234567", video_id="json1234567")
        await update_video(
            video["id"],
            transcript_segments=json.dumps(segments),
            summary_json=json.dumps(summary),
        )
        fetched = await get_video_by_id(video["id"])
        assert isinstance(fetched["transcript_segments"], list)
        assert fetched["transcript_segments"][0]["text"] == "Hello"
        assert isinstance(fetched["summary_json"], dict)
        assert fetched["summary_json"]["overview"] == "Test"

    async def test_none_json_fields_stay_none(self, test_db):
        video = await create_video(url="https://youtu.be/none1234567", video_id="none1234567")
        assert video["transcript_segments"] is None
        assert video["summary_json"] is None
