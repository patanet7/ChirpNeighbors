import asyncio
import websockets
import numpy as np

class AudioStreamHandler:
    def __init__(self, uri: str):
        self.uri = uri
        self.connected = False
        self.audio_queue = asyncio.Queue()
        self.stop_signal = False

    async def connect(self):
        while not self.stop_signal:
            try:
                print(f"[AudioStreamHandler] Connecting to {self.uri}...")
                async with websockets.connect(self.uri, max_size=None) as websocket:
                    print("[AudioStreamHandler] Connected!")
                    self.connected = True
                    await self._listen(websocket)
            except Exception as e:
                print(f"[AudioStreamHandler] Connection error: {e}")
                self.connected = False
                await asyncio.sleep(5)  # Wait before retrying

    async def _listen(self, websocket):
        try:
            async for message in websocket:
                if isinstance(message, bytes):
                    samples = np.frombuffer(message, dtype=np.int16)
                    await self.audio_queue.put(samples)
        except websockets.ConnectionClosed:
            print("[AudioStreamHandler] Connection closed.")
        except Exception as e:
            print(f"[AudioStreamHandler] Listen error: {e}")
        finally:
            self.connected = False

    async def get_audio_chunk(self):
        return await self.audio_queue.get()

    def shutdown(self):
        self.stop_signal = True
