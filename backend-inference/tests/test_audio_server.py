"""Actual loopback WebSockets and entrypoint checks, without ESP32 hardware."""

import asyncio
import contextlib
import os
import struct
import subprocess
import sys
import unittest
from unittest.mock import patch

from websockets.asyncio.client import connect
from websockets.exceptions import ConnectionClosed

from app.main import audio_server, main, receive_audio


def wire(sequence, samples, uptime):
    return struct.pack("<IQ", sequence, uptime) + struct.pack(
        f"<{len(samples)}h", *samples
    )


class HeadlessTests(unittest.TestCase):
    def test_import_and_help_do_not_load_playback_plotting_or_inference(self):
        script = """
import importlib.abc
import sys
class BlockOptional(importlib.abc.MetaPathFinder):
    def find_spec(self, fullname, path=None, target=None):
        if fullname.split('.')[0] in {
            'sounddevice', 'matplotlib', 'pyqtgraph',
            'birdnetlib', 'tensorflow', 'torch'
        }:
            raise RuntimeError('Unexpected optional import: ' + fullname)
sys.meta_path.insert(0, BlockOptional())
import app.main
import app.services.stream_handler
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            text=True,
            timeout=10,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        result = subprocess.run(
            [sys.executable, "-B", "-m", "app.main", "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("--sample-rate", result.stdout)


class ServerTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.captures = asyncio.Queue()
        self.server = await audio_server(
            port=0,
            sample_rate=10,
            chunk_duration_sec=0.5,
            on_capture=self.captures.put_nowait,
        )
        port = self.server.sockets[0].getsockname()[1]
        self.uri = f"ws://127.0.0.1:{port}/"

    async def asyncTearDown(self):
        self.server.close()
        await asyncio.wait_for(self.server.wait_closed(), 3)

    async def wait_for_session_end(self):
        async def wait():
            # connections excludes closing sockets; handlers also have to finish
            # so the single-device slot is released before the next connection.
            while self.server.handlers:
                await asyncio.sleep(0.001)

        await asyncio.wait_for(wait(), 1)

    async def test_websocket_delivers_capture_and_accepts_reconnect(self):
        async with connect(self.uri, proxy=None) as client:
            await client.send(wire(400, [99, 99], 40000))
        await self.wait_for_session_end()
        self.assertTrue(self.captures.empty())
        async with connect(self.uri, proxy=None) as client:
            await client.send(b"bad")
            await client.send(wire(0, [-32768, -1], 1000))
            await client.send(wire(0, [99], 1000))  # Duplicate.
            await client.send(wire(1, [0, 1, 32767], 2000))
            capture = await asyncio.wait_for(self.captures.get(), 1)
            self.assertEqual(capture.samples.tolist(), [-32768, -1, 0, 1, 32767])
            self.assertIsNone(capture.observed_at)
            self.assertEqual(capture.first_device_uptime_us, 1000)
        await self.wait_for_session_end()
        self.assertTrue(self.captures.empty())

    async def test_second_device_is_rejected_without_mixing_streams(self):
        async with connect(self.uri, proxy=None) as first:
            async with connect(self.uri, proxy=None) as second:
                await asyncio.wait_for(second.wait_closed(), 1)
                self.assertEqual(second.close_code, 1013)
            await first.send(wire(0, [1, 2, 3, 4, 5], 1000))
            self.assertEqual(
                (await asyncio.wait_for(self.captures.get(), 1)).samples.tolist(),
                [1, 2, 3, 4, 5],
            )

    async def test_oversize_frame_is_closed_at_transport_boundary(self):
        async with connect(self.uri, proxy=None) as client:
            await client.send(wire(0, [0] * 513, 1000))
            await asyncio.wait_for(client.wait_closed(), 1)
            self.assertEqual(client.close_code, 1009)
        await self.wait_for_session_end()
        self.assertTrue(self.captures.empty())

    async def test_server_shutdown_closes_idle_socket_and_finishes_handlers(self):
        async with connect(self.uri, proxy=None) as client:
            self.server.close()
            await asyncio.wait_for(self.server.wait_closed(), 3)
            await asyncio.wait_for(client.wait_closed(), 1)
            self.assertEqual(client.close_code, 1001)
            self.assertFalse(self.server.handlers)

    async def test_callback_failure_cancels_listener_and_closes_socket(self):
        def broken(capture):
            raise RuntimeError("synthetic consumer failure")

        from websockets.asyncio.server import serve

        failure = asyncio.Future()

        async def accept(socket):
            try:
                await receive_audio(
                    socket, sample_rate=10, chunk_duration_sec=0.5, on_capture=broken
                )
            except ExceptionGroup as error:
                failure.set_result(error)
            else:
                failure.set_result(None)

        async with serve(accept, "127.0.0.1", 0, close_timeout=1) as server:
            uri = f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}/"
            async with connect(uri, proxy=None) as client:
                await client.send(wire(0, [1, 2, 3, 4, 5], 1000))
                await asyncio.wait_for(client.wait_closed(), 1)
                with self.assertRaises(ConnectionClosed):
                    await client.recv()
            error = await asyncio.wait_for(failure, 1)
            self.assertIsInstance(error, ExceptionGroup)
            self.assertEqual(len(error.exceptions), 1)
            self.assertRegex(str(error.exceptions[0]), "synthetic consumer failure")

    async def test_main_entrypoint_binds_receiver_and_cleans_up_on_cancellation(self):
        ready = asyncio.Future()

        @contextlib.asynccontextmanager
        async def observed_server(*args, **kwargs):
            async with audio_server(*args, **kwargs) as server:
                ready.set_result(server)
                yield server

        with patch("app.main.audio_server", observed_server):
            task = asyncio.create_task(main(port=0))
            server = await asyncio.wait_for(ready, 1)
            uri = f"ws://127.0.0.1:{server.sockets[0].getsockname()[1]}/"
            async with connect(uri, proxy=None) as client:
                task.cancel()
                with self.assertRaises(asyncio.CancelledError):
                    await asyncio.wait_for(task, 3)
                await asyncio.wait_for(client.wait_closed(), 1)
            self.assertFalse(server.handlers)
