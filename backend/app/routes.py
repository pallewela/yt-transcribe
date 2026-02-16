import asyncio
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from app.database import (
    create_video,
    delete_video,
    get_all_videos,
    get_video_by_id,
    get_video_by_video_id,
)
from app.youtube import extract_video_id, fetch_video_metadata, validate_youtube_url

router = APIRouter()


class VideoSubmitRequest(BaseModel):
    url: str


class BatchSubmitRequest(BaseModel):
    urls: list[str]


class VideoResponse(BaseModel):
    id: int
    url: str
    video_id: str
    title: Optional[str] = None
    duration: Optional[int] = None
    status: str
    transcript_source: Optional[str] = None
    transcript_segments: Optional[list] = None
    transcript_text: Optional[str] = None
    summary_json: Optional[dict] = None
    error_message: Optional[str] = None
    attempt_count: int = 0
    created_at: str
    completed_at: Optional[str] = None


@router.post("/videos", response_model=VideoResponse)
async def submit_video(request: VideoSubmitRequest):
    if not validate_youtube_url(request.url):
        raise HTTPException(status_code=400, detail="Invalid YouTube URL")

    yt_id = extract_video_id(request.url)

    existing = await get_video_by_video_id(yt_id)
    if existing:
        return existing

    meta = await asyncio.to_thread(fetch_video_metadata, request.url)
    if meta.get("error"):
        video = await create_video(
            url=request.url, video_id=yt_id, title=None, duration=None
        )
        from app.database import update_video
        video = await update_video(video["id"], status="failed", error_message=f"Video unavailable: {meta['error']}")
        return video

    video = await create_video(
        url=request.url,
        video_id=yt_id,
        title=meta.get("title"),
        duration=meta.get("duration"),
    )
    return video


class BatchResultItem(BaseModel):
    url: str
    success: bool
    video: Optional[VideoResponse] = None
    error: Optional[str] = None


class BatchSubmitResponse(BaseModel):
    results: list[BatchResultItem]


@router.post("/videos/batch", response_model=BatchSubmitResponse)
async def submit_videos_batch(request: BatchSubmitRequest):
    results = []
    for url in request.urls:
        url = url.strip()
        if not url:
            continue
        if not validate_youtube_url(url):
            results.append(BatchResultItem(url=url, success=False, error="Invalid YouTube URL"))
            continue

        yt_id = extract_video_id(url)
        existing = await get_video_by_video_id(yt_id)
        if existing:
            results.append(BatchResultItem(url=url, success=True, video=existing))
            continue

        try:
            meta = await asyncio.to_thread(fetch_video_metadata, url)
            if meta.get("error"):
                video = await create_video(url=url, video_id=yt_id)
                from app.database import update_video
                video = await update_video(video["id"], status="failed",
                                           error_message=f"Video unavailable: {meta['error']}")
                results.append(BatchResultItem(url=url, success=True, video=video))
            else:
                video = await create_video(
                    url=url, video_id=yt_id,
                    title=meta.get("title"), duration=meta.get("duration"),
                )
                results.append(BatchResultItem(url=url, success=True, video=video))
        except Exception as e:
            results.append(BatchResultItem(url=url, success=False, error=str(e)))

    return BatchSubmitResponse(results=results)


@router.get("/videos", response_model=list[VideoResponse])
async def list_videos(status: Optional[str] = Query(None)):
    return await get_all_videos(status=status)


@router.get("/videos/{video_id}", response_model=VideoResponse)
async def get_video(video_id: int):
    video = await get_video_by_id(video_id)
    if video is None:
        raise HTTPException(status_code=404, detail="Video not found")
    return video


@router.delete("/videos/{video_id}")
async def remove_video(video_id: int):
    deleted = await delete_video(video_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Video not found")
    return {"detail": "Video deleted"}
