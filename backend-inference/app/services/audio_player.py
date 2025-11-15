import asyncio
import numpy as np
import sounddevice as sd

class AudioPlayer:
    def __init__(self, stream_handler, sample_rate=48000, buffer_size=1024):
        self.stream_handler = stream_handler
        self.sample_rate = sample_rate
        self.buffer_size = buffer_size
        self.playing = False

    async def start(self):
        self.playing = True
        try:
            async with sd.OutputStream(
                samplerate=self.sample_rate,
                blocksize=self.buffer_size,
                dtype='int16',
                channels=1,
                callback=self.callback
            ):
                while self.playing:
                    await asyncio.sleep(0.1)
        except Exception as e:
            print(f"Audio output error: {e}")

    def stop(self):
        self.playing = False

    def callback(self, outdata, frames, time_info, status):
        try:
            audio = asyncio.run_coroutine_threadsafe(
                self.stream_handler.get_audio_chunk(),
                asyncio.get_event_loop()
            ).result(timeout=0.05)
            if audio is None:
                outdata.fill(0)
            else:
                outdata[:, 0] = audio[:frames]
        except Exception as e:
            outdata.fill(0)
            print(f"Playback callback error: {e}")