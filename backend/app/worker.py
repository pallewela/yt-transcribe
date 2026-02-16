import asyncio
import logging

logger = logging.getLogger(__name__)

_worker_running = False


async def start_worker() -> asyncio.Task:
    global _worker_running
    _worker_running = True
    task = asyncio.create_task(_worker_loop())
    logger.info("Background worker started")
    return task


async def stop_worker(task: asyncio.Task):
    global _worker_running
    _worker_running = False
    task.cancel()
    try:
        await task
    except asyncio.CancelledError:
        pass
    logger.info("Background worker stopped")


async def _worker_loop():
    """Placeholder worker loop — will be implemented in task group 6."""
    from app.pipeline import process_video
    from app.database import get_next_queued_video, update_video
    import os

    poll_interval = int(os.getenv("WORKER_POLL_INTERVAL", "5"))
    max_retries = int(os.getenv("MAX_RETRY_ATTEMPTS", "3"))
    retry_delay = int(os.getenv("RETRY_DELAY_SECONDS", "30"))

    while _worker_running:
        try:
            video = await get_next_queued_video()
            if video is None:
                await asyncio.sleep(poll_interval)
                continue

            await update_video(video["id"], status="processing")
            try:
                await process_video(video)
            except Exception as e:
                attempt = video["attempt_count"] + 1
                if attempt < max_retries:
                    logger.warning(f"Video {video['id']} failed (attempt {attempt}), will retry: {e}")
                    await update_video(
                        video["id"],
                        status="queued",
                        attempt_count=attempt,
                        error_message=str(e),
                    )
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"Video {video['id']} permanently failed after {attempt} attempts: {e}")
                    await update_video(
                        video["id"],
                        status="failed",
                        attempt_count=attempt,
                        error_message=str(e),
                    )
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.exception(f"Worker loop error: {e}")
            await asyncio.sleep(poll_interval)
