import asyncio
import logging
from app.services.stream_handler import AudioStreamHandler
from app.services.audio_player import AudioPlayer
from app.services.audio_visualizer import AudioVisualizer

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def main():
    logger.info("Starting ESP32 Audio Stream Client...")

    stream_handler = AudioStreamHandler(
        uri="ws://192.168.1.118:8080",  # Adjust if ESP32 IP changes
        sample_rate=48000,
        chunk_duration_sec=3.0
    )

    audio_player = AudioPlayer(sample_rate=48000)
    audio_visualizer = AudioVisualizer(sample_rate=48000)

    # Wire the callbacks
    stream_handler.add_callback(audio_player.play_chunk)
    stream_handler.add_callback(audio_visualizer.update_plot)

    # Run both websocket listening and visualization loop
    await asyncio.gather(
        stream_handler.start(),
        asyncio.to_thread(audio_visualizer.start_loop)
    )

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Shutting down cleanly...")
