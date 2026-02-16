import asyncio
from unittest.mock import patch, AsyncMock

import pytest

import app.worker as worker_module


SAMPLE_VIDEO = {
    "id": 1,
    "url": "https://www.youtube.com/watch?v=test12345ab",
    "video_id": "test12345ab",
    "status": "queued",
    "attempt_count": 0,
}


async def _run_worker_once(get_queued_returns, process_side_effect=None):
    """Helper to run one iteration of the worker loop, then stop."""
    call_count = 0

    async def mock_get_next():
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            return get_queued_returns
        # After first call, stop the worker
        worker_module._worker_running = False
        return None

    mock_process = AsyncMock()
    if process_side_effect:
        mock_process.side_effect = process_side_effect

    mock_update = AsyncMock()

    with patch("app.pipeline.process_video", mock_process), \
         patch("app.database.get_next_queued_video", side_effect=mock_get_next), \
         patch("app.database.update_video", mock_update), \
         patch.dict("os.environ", {
             "WORKER_POLL_INTERVAL": "0",
             "MAX_RETRY_ATTEMPTS": "3",
             "RETRY_DELAY_SECONDS": "0",
         }):

        worker_module._worker_running = True
        try:
            await worker_module._worker_loop()
        except asyncio.CancelledError:
            pass

    return mock_process, mock_update


class TestWorkerPicksUpJob:
    async def test_processes_queued_job(self):
        mock_process, mock_update = await _run_worker_once(SAMPLE_VIDEO)

        mock_update.assert_any_call(1, status="processing")
        mock_process.assert_called_once_with(SAMPLE_VIDEO)


class TestWorkerRetryOnFailure:
    async def test_requeues_on_failure(self):
        video = {**SAMPLE_VIDEO, "attempt_count": 0}
        mock_process, mock_update = await _run_worker_once(
            video,
            process_side_effect=Exception("Transient error"),
        )

        update_calls = mock_update.call_args_list
        requeue_call = [c for c in update_calls if c.kwargs.get("status") == "queued"]
        assert len(requeue_call) == 1
        assert requeue_call[0].kwargs["attempt_count"] == 1


class TestWorkerPermanentFailure:
    async def test_marks_failed_after_max_retries(self):
        video = {**SAMPLE_VIDEO, "attempt_count": 2}
        mock_process, mock_update = await _run_worker_once(
            video,
            process_side_effect=Exception("Persistent error"),
        )

        update_calls = mock_update.call_args_list
        fail_call = [c for c in update_calls if c.kwargs.get("status") == "failed"]
        assert len(fail_call) == 1
        assert fail_call[0].kwargs["attempt_count"] == 3
        assert "Persistent error" in fail_call[0].kwargs["error_message"]


class TestWorkerIdlesWhenEmpty:
    async def test_does_not_process_when_no_jobs(self):
        mock_process = AsyncMock()
        call_count = 0

        async def mock_get_next():
            nonlocal call_count
            call_count += 1
            worker_module._worker_running = False
            return None

        with patch("app.pipeline.process_video", mock_process), \
             patch("app.database.get_next_queued_video", side_effect=mock_get_next), \
             patch("app.database.update_video", AsyncMock()), \
             patch.dict("os.environ", {"WORKER_POLL_INTERVAL": "0"}):

            worker_module._worker_running = True
            try:
                await worker_module._worker_loop()
            except asyncio.CancelledError:
                pass

        mock_process.assert_not_called()


class TestStartStopWorker:
    async def test_start_worker_returns_task_and_sets_running(self):
        with patch("app.worker._worker_loop", new_callable=AsyncMock) as mock_loop:
            task = await worker_module.start_worker()
            assert worker_module._worker_running is True
            assert asyncio.iscoroutine(task) or asyncio.isfuture(task)
            await worker_module.stop_worker(task)
            assert worker_module._worker_running is False

    async def test_stop_worker_cancels_task_and_logs(self):
        with patch("app.worker._worker_loop", new_callable=AsyncMock):
            task = await worker_module.start_worker()
            await worker_module.stop_worker(task)
            assert task.cancelled() or task.done()


class TestWorkerLoopEdgeCases:
    async def test_worker_loop_breaks_on_cancelled_error(self):
        async def mock_get_next():
            worker_module._worker_running = False
            raise asyncio.CancelledError()

        with patch("app.database.get_next_queued_video", side_effect=mock_get_next), \
             patch("app.database.update_video", AsyncMock()), \
             patch.dict("os.environ", {"WORKER_POLL_INTERVAL": "0"}):
            worker_module._worker_running = True
            await worker_module._worker_loop()

    async def test_worker_loop_handles_get_next_exception_and_continues(self):
        call_count = 0

        async def mock_get_next():
            nonlocal call_count
            call_count += 1
            if call_count == 1:
                raise RuntimeError("DB connection lost")
            worker_module._worker_running = False
            return None

        with patch("app.pipeline.process_video", AsyncMock()), \
             patch("app.database.get_next_queued_video", side_effect=mock_get_next), \
             patch("app.database.update_video", AsyncMock()), \
             patch.dict("os.environ", {"WORKER_POLL_INTERVAL": "0"}):
            worker_module._worker_running = True
            await worker_module._worker_loop()
        assert call_count == 2
