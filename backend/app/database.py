import json
import os
from datetime import datetime, timezone
from typing import Optional

import aiosqlite

DATABASE_PATH = os.getenv("DATABASE_PATH", "data/yt_transcribe.db")


async def get_db() -> aiosqlite.Connection:
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)
    db = await aiosqlite.connect(DATABASE_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA foreign_keys=ON")
    return db


async def init_db():
    db = await get_db()
    try:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                url TEXT NOT NULL,
                video_id TEXT NOT NULL,
                title TEXT,
                duration INTEGER,
                status TEXT NOT NULL DEFAULT 'queued',
                transcript_source TEXT,
                transcript_segments TEXT,
                transcript_text TEXT,
                summary_json TEXT,
                error_message TEXT,
                attempt_count INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL,
                completed_at TEXT
            )
        """)
        await db.execute("""
            CREATE UNIQUE INDEX IF NOT EXISTS idx_videos_video_id
            ON videos(video_id)
        """)
        await db.commit()
    finally:
        await db.close()


async def create_video(url: str, video_id: str, title: Optional[str] = None,
                       duration: Optional[int] = None) -> dict:
    db = await get_db()
    try:
        now = datetime.now(timezone.utc).isoformat()
        cursor = await db.execute(
            """INSERT INTO videos (url, video_id, title, duration, status, created_at)
               VALUES (?, ?, ?, ?, 'queued', ?)""",
            (url, video_id, title, duration, now)
        )
        await db.commit()
        return await get_video_by_id(cursor.lastrowid, db)
    finally:
        await db.close()


async def get_video_by_id(video_id: int, db: Optional[aiosqlite.Connection] = None) -> Optional[dict]:
    close_db = db is None
    if db is None:
        db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM videos WHERE id = ?", (video_id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        return _row_to_dict(row)
    finally:
        if close_db:
            await db.close()


async def get_video_by_video_id(yt_video_id: str) -> Optional[dict]:
    db = await get_db()
    try:
        cursor = await db.execute("SELECT * FROM videos WHERE video_id = ?", (yt_video_id,))
        row = await cursor.fetchone()
        if row is None:
            return None
        return _row_to_dict(row)
    finally:
        await db.close()


async def get_all_videos(status: Optional[str] = None) -> list[dict]:
    db = await get_db()
    try:
        if status:
            cursor = await db.execute(
                "SELECT * FROM videos WHERE status = ? ORDER BY created_at DESC",
                (status,)
            )
        else:
            cursor = await db.execute("SELECT * FROM videos ORDER BY created_at DESC")
        rows = await cursor.fetchall()
        return [_row_to_dict(row) for row in rows]
    finally:
        await db.close()


async def update_video(video_id: int, **kwargs) -> Optional[dict]:
    db = await get_db()
    try:
        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)
        values.append(video_id)
        await db.execute(
            f"UPDATE videos SET {', '.join(fields)} WHERE id = ?",
            values
        )
        await db.commit()
        return await get_video_by_id(video_id, db)
    finally:
        await db.close()


async def delete_video(video_id: int) -> bool:
    db = await get_db()
    try:
        cursor = await db.execute("DELETE FROM videos WHERE id = ?", (video_id,))
        await db.commit()
        return cursor.rowcount > 0
    finally:
        await db.close()


async def get_next_queued_video() -> Optional[dict]:
    db = await get_db()
    try:
        cursor = await db.execute(
            "SELECT * FROM videos WHERE status = 'queued' ORDER BY created_at ASC LIMIT 1"
        )
        row = await cursor.fetchone()
        if row is None:
            return None
        return _row_to_dict(row)
    finally:
        await db.close()


def _row_to_dict(row) -> dict:
    d = dict(row)
    if d.get("transcript_segments"):
        d["transcript_segments"] = json.loads(d["transcript_segments"])
    if d.get("summary_json"):
        d["summary_json"] = json.loads(d["summary_json"])
    return d
