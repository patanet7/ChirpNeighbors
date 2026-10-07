"""Local headless WebSocket receiver for the current ESP32 client firmware."""

import argparse
import asyncio
import logging
from collections.abc import Callable

from websockets.asyncio.server import ServerConnection, serve

from app.services.audio_capture import AudioCapture
from app.services.audio_packet import MAX_PACKET_BYTES
from app.services.stream_handler import AudioStreamHandler

logger = logging.getLogger(__name__)


def log_capture(capture: AudioCapture) -> None:
    # No PCM, identifiers, device timers or observation details in logs.
    logger.info("Received PCM window: %d samples", len(capture.samples))


async def receive_audio(
    websocket: ServerConnection,
    *,
    sample_rate: int = 48000,
    chunk_duration_sec: float = 3.0,
    on_capture: Callable[[AudioCapture], None] = log_capture,
) -> None:
    """Own listener/consumer lifetimes together; callbacks must be nonblocking."""
    handler = AudioStreamHandler(
        sample_rate=sample_rate, chunk_duration_sec=chunk_duration_sec
    )

    async def consume() -> None:
        while (capture := await handler.get_capture()) is not None:
            on_capture(capture)

    try:
        async with asyncio.TaskGroup() as group:
            group.create_task(handler.listen(websocket))
            group.create_task(consume())
    finally:
        handler.shutdown()
        await websocket.close()


def audio_server(
    host: str = "127.0.0.1",
    port: int = 8080,
    *,
    sample_rate: int = 48000,
    chunk_duration_sec: float = 3.0,
    on_capture: Callable[[AudioCapture], None] = log_capture,
) -> serve:
    """Bound intake to one active device; reconnects start independent sessions.

    This local development receiver has no device authentication or TLS. Bind
    an explicit private interface only when testing hardware on a trusted LAN.
    """
    # Validate before binding or accepting a device.
    AudioStreamHandler(sample_rate=sample_rate, chunk_duration_sec=chunk_duration_sec)
    active = False

    async def accept(websocket: ServerConnection) -> None:
        nonlocal active
        if active:
            await websocket.close(code=1013, reason="Audio receiver is busy")
            return
        active = True
        try:
            await receive_audio(
                websocket,
                sample_rate=sample_rate,
                chunk_duration_sec=chunk_duration_sec,
                on_capture=on_capture,
            )
        finally:
            active = False

    return serve(
        accept,
        host,
        port,
        max_size=MAX_PACKET_BYTES,
        max_queue=8,
        compression=None,
        open_timeout=5,
        close_timeout=2,
    )


async def main(
    host: str = "127.0.0.1",
    port: int = 8080,
    sample_rate: int = 48000,
    chunk_duration_sec: float = 3.0,
) -> None:
    async with audio_server(
        host, port, sample_rate=sample_rate, chunk_duration_sec=chunk_duration_sec
    ):
        logger.info("Headless ESP32 audio intake listening on %s:%d", host, port)
        await asyncio.Future()  # asyncio.run cancels this task on Ctrl-C.


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8080)
    parser.add_argument("--sample-rate", type=int, default=48000)
    parser.add_argument("--chunk-duration-sec", type=float, default=3.0)
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main(**vars(args)))
    except KeyboardInterrupt:
        logger.info("Audio intake stopped")
