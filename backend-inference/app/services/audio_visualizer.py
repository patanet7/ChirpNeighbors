import numpy as np
import matplotlib.pyplot as plt
import threading
import time

class AudioVisualizer:
    def __init__(self, stream_handler, interval=0.1):
        """
        Visualize incoming audio data in real-time.
        :param stream_handler: Instance of StreamHandler.
        :param interval: Time between updates in seconds.
        """
        self.stream_handler = stream_handler
        self.interval = interval
        self.running = False

    def start(self):
        self.running = True
        threading.Thread(target=self._update_loop, daemon=True).start()

    def stop(self):
        self.running = False

    def _update_loop(self):
        plt.ion()
        fig, ax = plt.subplots()
        x = np.linspace(0, self.stream_handler.chunk_size / self.stream_handler.sample_rate, self.stream_handler.chunk_size)
        line, = ax.plot(x, np.zeros_like(x))
        ax.set_ylim([-1.1, 1.1])
        ax.set_xlim([0, x[-1]])
        ax.set_xlabel('Time (seconds)')
        ax.set_ylabel('Amplitude')
        ax.set_title('Live Audio Waveform')

        while self.running:
            chunk = self.stream_handler.get_chunk()
            if chunk is not None and len(chunk) > 0:
                samples = np.frombuffer(chunk, dtype=np.int16).astype(np.float32) / 32768.0
                if len(samples) < self.stream_handler.chunk_size:
                    samples = np.pad(samples, (0, self.stream_handler.chunk_size - len(samples)))
                line.set_ydata(samples)
                fig.canvas.draw()
                fig.canvas.flush_events()
            time.sleep(self.interval)

        plt.ioff()
        plt.close()
