import asyncio
import time
import numpy as np
import sounddevice as sd
import pyqtgraph as pg
from pyqtgraph.Qt import QtWidgets, QtCore, QtGui # Use Qt bindings provided by pyqtgraph
import sys
import threading
import wave
import queue
import logging
import traceback
import signal
import concurrent.futures
import collections # For deque
from websockets.server import serve
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError

# === Configuration Constants ===
HOST = "0.0.0.0"  # Listen on all available network interfaces
PORT = 8080
SAMPLE_RATE = 48000
CHANNELS = 1
AUDIO_BYTES_PER_SAMPLE = 2  # For int16
EXPECTED_AUDIO_FORMAT = np.int16 # Corresponds to sampwidth=2 in wave
NUMPY_AUDIO_FORMAT = np.int16 # Numpy format for received bytes
SOUNDDEVICE_DTYPE = 'int16' # Sounddevice format

# Header format from ESP32 (Little-Endian)
# 4 bytes sequence (uint32_t) + 8 bytes timestamp (uint64_t)
HEADER_SIZE = 12
SEQ_NUM_BYTES = 4
TIMESTAMP_BYTES = 8

# Queue sizes (in number of messages/chunks) - prevents runaway memory usage
# Adjust based on expected chunk size and processing speed vs network speed
# Example: 100 chunks * 1024 bytes/chunk / (48000 samples/sec * 2 bytes/sample) ~= 1.06 sec buffer
PLAYBACK_QUEUE_MAX_SIZE = 100
VISUALIZER_QUEUE_MAX_SIZE = 50 # GUI doesn't need as deep a buffer

WAV_SAVE_INTERVAL_S = 5 # How often to save WAV chunks
WAV_FILE_PREFIX = "recording"
TIMING_PLOT_HISTORY = 500 # How many packets to show in timing plot

# === Logging Setup ===
logging.basicConfig(
    level=logging.INFO, # Set to logging.DEBUG for more verbose output
    format='%(asctime)s [%(levelname)s] [%(name)s:%(lineno)d] %(message)s', # Added line number
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("WebSocketServer")
# Reduce verbosity of libraries if desired
logging.getLogger("pyqtgraph").setLevel(logging.WARNING)
logging.getLogger("websockets").setLevel(logging.INFO)
logging.getLogger("sounddevice").setLevel(logging.WARNING)


# === Server State ===
clients = set()
packet_count_session = 0 # Packets since last client connect
total_bytes_session = 0  # Bytes since last client connect
bytes_last_second = 0
write_buffer = bytearray() # Buffer for WAV writing
playback_queue = asyncio.Queue(maxsize=PLAYBACK_QUEUE_MAX_SIZE)
visualizer_queue = queue.Queue(maxsize=VISUALIZER_QUEUE_MAX_SIZE) # Thread-safe queue for GUI
last_sequence = None
# Use deque for automatic history limit and better thread safety for append/read
# Store (sequence, timestamp_us, delta_us)
timestamp_log = collections.deque(maxlen=TIMING_PLOT_HISTORY + 50)

# Shutdown signalling
shutdown_event = asyncio.Event()
# Thread pool for blocking I/O (like file saving)
executor = concurrent.futures.ThreadPoolExecutor(max_workers=2, thread_name_prefix="BlockingIO")

# === WebSocket Handler ===
async def handler(websocket, path): # path argument is required by serve
    global packet_count_session, total_bytes_session, bytes_last_second, last_sequence
    clients.add(websocket)
    remote_ip, remote_port = websocket.remote_address
    client_id = f"{remote_ip}:{remote_port}"
    logger.info(f"Client connected: {client_id}")

    # Reset session stats for new client
    packet_count_session = 0
    total_bytes_session = 0
    bytes_last_second = 0
    last_sequence = None
    last_timestamp_us = None

    try:
        async for message in websocket:
            packet_count_session += 1
            message_len = len(message)
            total_bytes_session += message_len
            bytes_last_second += message_len

            if message_len >= HEADER_SIZE:
                try:
                    # --- Parse Header (Little-Endian) ---
                    seq = int.from_bytes(message[0:SEQ_NUM_BYTES], byteorder='little', signed=False)
                    timestamp_us = int.from_bytes(message[SEQ_NUM_BYTES:HEADER_SIZE], byteorder='little', signed=False)
                    audio_data = message[HEADER_SIZE:]
                    audio_len = len(audio_data)

                    logger.debug(f"[RECV {client_id}] Seq={seq}, Timestamp={timestamp_us} us, AudioLen={audio_len}")

                    # --- Sequence Check ---
                    if last_sequence is not None:
                        # Wrap expected sequence at 32 bits
                        expected = (last_sequence + 1) & 0xFFFFFFFF
                        if seq != expected:
                            logger.warning(f"Packet out of order from {client_id}: expected {expected}, got {seq}")
                    last_sequence = seq

                    # --- Timestamp/Jitter Check ---
                    if last_timestamp_us is not None:
                        delta_us = 0 # Default if timestamp didn't advance (unlikely for uint64)
                        if timestamp_us > last_timestamp_us: # Avoid negative delta on potential timer wrap or error
                            delta_us = timestamp_us - last_timestamp_us
                            timestamp_log.append((seq, timestamp_us, delta_us)) # Store data for timing plot
                            # Log if jitter > 100ms (adjust threshold as needed)
                            if delta_us > 100000:
                                logger.warning(f"Large Jitter from {client_id}: Packet {seq} delta: {delta_us / 1000.0:.2f} ms")
                        else:
                            logger.warning(f"Timestamp anomaly from {client_id}: current {timestamp_us} <= previous {last_timestamp_us}. Seq {seq}")
                    last_timestamp_us = timestamp_us # Update for next iteration

                    # --- Queue Data for Processing ---
                    try:
                        # Use put_nowait to avoid blocking the handler if queues are full
                        playback_queue.put_nowait(audio_data)
                        visualizer_queue.put_nowait(audio_data) # For GUI thread
                        write_buffer.extend(audio_data) # For WAV writer task
                    except asyncio.QueueFull:
                        logger.warning(f"Playback queue full for {client_id}. Discarding packet {seq}.")
                    except queue.Full:
                         logger.warning(f"Visualizer queue full for {client_id}. Discarding packet {seq}.")

                except ValueError as e:
                    logger.error(f"Error converting header bytes from {client_id}: {e}. MsgLen={message_len}")
                except Exception as e:
                    logger.error(f"Error processing message from {client_id}: {e}\n{traceback.format_exc()}")

            else:
                logger.warning(f"Received short message from {client_id}: Len={message_len}, expected >= {HEADER_SIZE}")

    except ConnectionClosedOK:
        logger.info(f"Client {client_id} disconnected gracefully.")
    except ConnectionClosedError as e:
         logger.warning(f"Client {client_id} connection closed with error: Code={e.code}, Reason='{e.reason}'")
    except Exception as e:
        # Catch potential errors during the async for message loop itself
        logger.error(f"Unexpected error in handler loop for {client_id}: {e}\n{traceback.format_exc()}")
    finally:
        if websocket in clients:
             clients.remove(websocket)
        logger.info(f"Client removed: {client_id}. Active clients: {len(clients)}")
        # Reset sequence tracking only if this was the last client
        if not clients:
            logger.info("Last client disconnected, resetting sequence tracking.")
            last_sequence = None
            timestamp_log.clear() # Clear timing log

# === Synchronous File Saving Function (for executor) ===
def save_wave_sync(filename, data_bytes, channels, sampwidth, framerate):
    """Saves audio data to a WAV file. Runs in executor thread."""
    try:
        with wave.open(filename, 'wb') as wf:
            wf.setnchannels(channels)
            wf.setsampwidth(sampwidth)
            wf.setframerate(framerate)
            wf.writeframes(data_bytes)
        logger.info(f"Finished saving {filename} ({len(data_bytes)} audio bytes)")
        return True
    except Exception as e:
        logger.error(f"Failed to save {filename}: {e}\n{traceback.format_exc()}")
        return False

# === Async WAV File Writer Task ===
async def wav_writer_task():
    global write_buffer
    file_counter = 0
    loop = asyncio.get_running_loop()
    logger.info("WAV writer task started.")

    while not shutdown_event.is_set():
        try:
            # Wait for the specified interval, but wake up sooner if shutdown is signaled
            await asyncio.wait_for(shutdown_event.wait(), timeout=WAV_SAVE_INTERVAL_S)
            # If we wake up because shutdown_event was set, break the loop
            if shutdown_event.is_set():
                logger.info("WAV writer task: Shutdown signal received.")
                break
        except asyncio.TimeoutError:
            # This is the normal case: timeout reached, proceed to check buffer
            pass

        try:
            if len(write_buffer) > 0:
                # Copy buffer and clear original immediately
                buffer_to_write = bytes(write_buffer) # Make immutable copy
                current_buffer_len = len(buffer_to_write)
                write_buffer = bytearray() # Clear original immediately

                filename = f"{WAV_FILE_PREFIX}_{file_counter:04d}.wav"
                file_counter += 1

                logger.info(f"Scheduling save for {filename} ({current_buffer_len} bytes)...")

                # Run the blocking save function in the executor
                await loop.run_in_executor(
                    executor,
                    save_wave_sync,
                    filename,
                    buffer_to_write,
                    CHANNELS,
                    AUDIO_BYTES_PER_SAMPLE,
                    SAMPLE_RATE
                )
            # else:
            #     logger.debug("wav_writer_task: No data in buffer to save.")

        except asyncio.CancelledError:
            logger.info("WAV writer task cancelled during operation.")
            break # Exit loop if cancelled
        except Exception as e:
            logger.error(f"Error in wav_writer_task main loop: {e}\n{traceback.format_exc()}")
            await asyncio.sleep(5) # Avoid fast error loops

    # Final save on shutdown if buffer still has data
    if len(write_buffer) > 0:
         logger.info("Performing final WAV save on shutdown...")
         final_buffer = bytes(write_buffer)
         filename = f"{WAV_FILE_PREFIX}_{file_counter:04d}_final.wav"
         # Use the sync function directly here as the event loop is stopping anyway
         save_wave_sync(filename, final_buffer, CHANNELS, AUDIO_BYTES_PER_SAMPLE, SAMPLE_RATE)

    logger.info("WAV writer task finished.")


# === Async Throughput Monitor Task ===
async def throughput_monitor_task():
    global bytes_last_second
    logger.info("Throughput monitor task started.")
    while not shutdown_event.is_set():
        try:
            # Wait for 1 second, but check shutdown event periodically
            await asyncio.wait_for(shutdown_event.wait(), timeout=1.0)
            if shutdown_event.is_set(): break # Exit if shutdown signaled
        except asyncio.TimeoutError:
             # Normal case: calculate and print status
            try:
                kbps = bytes_last_second / 1024.0
                active_client_count = len(clients)

                q_size = playback_queue.qsize() # Get current queue size

                if active_client_count == 0:
                    status = "Idle... Waiting for client."
                elif kbps == 0 and packet_count_session > 0:
                    status = f"Connected ({active_client_count}), no data flow..."
                else:
                    status = f"Clients:{active_client_count}|Pkts:{packet_count_session:<7}|Rate:{kbps:<7.2f} KB/s|Q:{q_size:<4}"

                print(f"\r{status}{' '*15}", end='', flush=True) # Overwrite line with padding
                bytes_last_second = 0
            except Exception as e:
                logger.error(f"Error calculating throughput: {e}")

        except asyncio.CancelledError:
            logger.info("Throughput monitor task cancelled.")
            break
        except Exception as e:
             logger.error(f"Error in throughput_monitor_task: {e}\n{traceback.format_exc()}")
             await asyncio.sleep(5) # Avoid fast error loops
    print() # Newline on exit
    logger.info("Throughput monitor task finished.")

# === Async Audio Playback Task ===
async def audio_player_task():
    stream = None
    audio_buffer = [] # List to hold numpy arrays
    logger.info("Audio player task started.")
    stream_started = False
    try:
        logger.info(f"Initializing audio output stream: SR={SAMPLE_RATE}, Ch={CHANNELS}, Format={SOUNDDEVICE_DTYPE}")
        stream = sd.OutputStream(samplerate=SAMPLE_RATE, channels=CHANNELS, dtype=SOUNDDEVICE_DTYPE, blocksize=4096) # Use larger blocksize
        stream.start()
        stream_started = True
        logger.info("Audio output stream started.")

        while not shutdown_event.is_set():
            try:
                # Wait for data, but with a timeout to allow checking shutdown_event
                data = await asyncio.wait_for(playback_queue.get(), timeout=0.1)

                # --- Process Data Chunk ---
                expected_bytes = AUDIO_BYTES_PER_SAMPLE * CHANNELS
                if len(data) % expected_bytes == 0 and len(data) > 0:
                    samples = np.frombuffer(data, dtype=NUMPY_AUDIO_FORMAT)
                    audio_buffer.append(samples) # Append numpy array
                    logger.debug(f"Added {len(samples)} samples to playback buffer.")
                elif len(data) > 0: # Log if non-empty but wrong size
                    logger.warning(f"Audio data chunk size ({len(data)}) not multiple of expected bytes per frame ({expected_bytes}). Skipping.")
                # --- End Process Data Chunk ---

                playback_queue.task_done() # Mark task as done

                # --- Play Buffer if Sufficient Data ---
                # Play buffer when enough data accumulates (e.g., ~250ms)
                target_samples = int(SAMPLE_RATE * 0.25) # 250ms buffer target
                buffered_samples = sum(len(x) for x in audio_buffer)

                if buffered_samples >= target_samples:
                    big_chunk = np.concatenate(audio_buffer)
                    audio_buffer.clear() # Clear list of arrays
                    try:
                        stream.write(big_chunk) # Write numpy array directly
                        logger.debug(f"Played {len(big_chunk)} samples from buffer. Remaining buffered: 0")
                    except sd.PortAudioError as pae:
                         logger.error(f"Sounddevice PortAudioError writing to stream: {pae}")
                         # Handle buffer underflow/overflow? Maybe just log and continue.
                         # If it happens repeatedly, might need to adjust buffer sizes/logic.
                    except Exception as write_e:
                         logger.error(f"Unexpected error writing to audio stream: {write_e}")

            except asyncio.TimeoutError:
                # No data received in timeout window, check if stream needs write
                if stream_started and len(audio_buffer) > 0 and stream.write_available >= sum(len(x) for x in audio_buffer):
                    # Try to play remaining buffer if queue is empty for a while
                    logger.debug("Playback queue empty, playing remaining buffer...")
                    big_chunk = np.concatenate(audio_buffer)
                    audio_buffer.clear()
                    try:
                        stream.write(big_chunk)
                        logger.debug(f"Played final {len(big_chunk)} samples from buffer.")
                    except Exception as final_write_e:
                         logger.error(f"Error writing final buffer: {final_write_e}")

                await asyncio.sleep(0.01) # Small sleep if queue empty
                continue # Continue loop to check shutdown_event again
            except asyncio.CancelledError:
                 logger.info("Audio player task cancelled.")
                 break # Exit loop immediately
            except Exception as e:
                logger.error(f"Error during audio playback loop: {e}\n{traceback.format_exc()}")
                audio_buffer.clear() # Clear buffer on error
                await asyncio.sleep(1) # Pause after error

    finally:
        if stream:
            try:
                logger.info("Stopping and closing audio output stream...")
                if stream_started:
                     if stream.active:
                         stream.stop()
                stream.close(ignore_errors=True) # Close stream even if stopped
                logger.info("Audio output stream closed.")
            except Exception as e:
                 logger.error(f"Error closing audio stream: {e}")
        logger.info("Audio player task finished.")


# === Plot for Timestamp Deltas ===
class TimingPlot(QtWidgets.QMainWindow):
    # Max number of delta points to display
    MAX_POINTS = TIMING_PLOT_HISTORY

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Packet Timing Deltas")
        self.resize(800, 400) # Set a default size
        self.layout_widget = pg.GraphicsLayoutWidget()
        self.setCentralWidget(self.layout_widget)
        self.plot_widget = self.layout_widget.addPlot(title="Inter-Packet Delta (ms)")
        self.plot_widget.setLabel('left', 'Delta (ms)')
        self.plot_widget.setLabel('bottom', 'Packet History (Newest ->)')
        self.plot_widget.showGrid(x=True, y=True, alpha=0.3)
        self.plot_widget.setLogMode(y=False) # Ensure Y axis is linear
        self.plot_widget.enableAutoRange('y', True) # Auto-adjust Y range
        self.curve = self.plot_widget.plot(pen=pg.mkPen('y', width=2))

        # Store data locally for plotting
        self.delta_data = collections.deque(maxlen=self.MAX_POINTS)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(200) # Update plot 5 times per second
        logger.debug("TimingPlot initialized.")

    def update_plot(self):
        try:
            # No need to copy the global deque here, use its current state
            if timestamp_log:
                # Extract delta values (index 2) and convert from us to ms
                # Get all available deltas since last update might be faster with deque
                # Note: If deque fills completely between updates, oldest data is lost
                # This approach simply plots the latest 'MAX_POINTS' available in the log
                current_deltas_ms = [x[2] / 1000.0 for x in list(timestamp_log)[-self.MAX_POINTS:]]
                if current_deltas_ms: # Check if list is not empty
                     self.curve.setData(current_deltas_ms)
                else:
                     self.curve.clear()
            else:
                # Clear plot if the global log is empty (e.g., client disconnected)
                self.curve.clear()
        except Exception as e:
             logger.error(f"[TimingPlot] Error updating plot: {e}\n{traceback.format_exc()}")


# === AudioVisualizer Class ===
class AudioVisualizer(QtWidgets.QMainWindow):
    # Keep buffer size reasonable for UI responsiveness
    WAVEFORM_BUFFER_SAMPLES = int(SAMPLE_RATE * 0.5) # Display ~0.5 seconds

    def __init__(self):
        super().__init__()
        self.setWindowTitle("ESP32 Audio Stream - Live Visualizer")
        self.resize(800, 600) # Set a default size
        central_widget = QtWidgets.QWidget()
        layout = QtWidgets.QVBoxLayout(central_widget)
        self.setCentralWidget(central_widget)

        # Peak Meter Plot
        self.peak_plot = pg.PlotWidget(title="Peak Meter")
        self.peak_plot.setMaximumHeight(100) # Limit height of peak meter
        self.peak_plot.setYRange(0, 1.05) # Range 0 to 1, slightly above for visibility
        self.peak_plot.setXRange(0, 1)
        self.peak_bar = pg.BarGraphItem(x=[0.5], height=[0], width=0.6, brush='g')
        self.peak_plot.addItem(self.peak_bar)
        self.peak_plot.hideAxis('bottom')
        self.peak_plot.hideAxis('left')
        layout.addWidget(self.peak_plot)

        # Waveform Plot
        self.waveform_plot = pg.PlotWidget(title="Scrolling Waveform")
        self.waveform_plot.setYRange(-1.1, 1.1)
        self.waveform_plot.setXRange(0, self.WAVEFORM_BUFFER_SAMPLES)
        self.waveform_plot.setLabel('left', 'Amplitude')
        self.waveform_plot.setLabel('bottom', 'Samples')
        self.waveform_plot.showGrid(x=True, y=True, alpha=0.3)
        self.curve = self.waveform_plot.plot(pen=pg.mkPen(color=(100, 200, 100), width=1)) # Greenish pen
        layout.addWidget(self.waveform_plot)

        # Internal buffer for waveform display
        self.sample_buffer = np.zeros(self.WAVEFORM_BUFFER_SAMPLES, dtype=np.float32)

        self.timer = QtCore.QTimer()
        self.timer.timeout.connect(self.update_plot)
        self.timer.start(33) # Aim for ~30fps update rate
        logger.debug("AudioVisualizer initialized.")

    def update_plot(self):
        updated = False
        peak = 0.0 # Track max peak across chunks processed this update cycle
        try:
            # Process all data currently in the queue
            while not visualizer_queue.empty():
                data = visualizer_queue.get_nowait()
                # Convert received bytes (int16) to float32 for plotting (-1.0 to 1.0)
                samples = np.frombuffer(data, dtype=NUMPY_AUDIO_FORMAT).astype(np.float32) / 32768.0

                if len(samples) > 0:
                    # Find peak for this chunk
                    chunk_peak = np.max(np.abs(samples))
                    peak = max(peak, chunk_peak) # Keep overall max peak for this update cycle

                    # Update scrolling waveform buffer
                    n = len(samples)
                    if n >= len(self.sample_buffer):
                        # If new chunk is larger than buffer, just take the end
                        self.sample_buffer[:] = samples[-len(self.sample_buffer):]
                    else:
                        # Shift old data left, add new data to the right
                        self.sample_buffer[:-n] = self.sample_buffer[n:]
                        self.sample_buffer[-n:] = samples
                    updated = True
                # Ensure queue item is marked done even if samples are empty
                visualizer_queue.task_done()

            # Only update plots if data was received in this cycle
            if updated:
                self.peak_bar.setOpts(height=[peak]) # Update peak meter
                # Update waveform plot - create X values matching buffer length
                x_values = np.arange(len(self.sample_buffer))
                self.curve.setData(x=x_values, y=self.sample_buffer)

        except queue.Empty:
            # No data in queue is normal when client is idle or disconnected
            pass
        except Exception as e:
            # Log error but don't crash the GUI thread
            logger.error(f"[Visualizer] Plot update error: {e}\n{traceback.format_exc()}")


# === Run Visualizer Thread ===
def run_visualizers():
    """ Function to run the PyQtGraph visualizers in a separate thread """
    logger.info("Starting Visualizer thread...")
    try:
        # Check if QApplication already exists (needed for some environments)
        app = QtWidgets.QApplication.instance()
        if app is None:
            app = QtWidgets.QApplication(sys.argv)

        audio_win = AudioVisualizer()
        timing_win = TimingPlot()
        audio_win.show()
        timing_win.show()

        logger.info("Visualizers ready. Starting Qt event loop.")
        # Start the Qt event loop. This will block until the windows are closed.
        app_exit_code = app.exec_()
        logger.info(f"Visualizer Qt event loop finished with code: {app_exit_code}")

    except Exception as e:
         # Catch any exceptions happening during GUI setup or execution
         logger.error(f"Fatal error in visualizer thread: {e}\n{traceback.format_exc()}")

# === Graceful Shutdown Handler ===
async def shutdown(sig, loop):
    """ Signals tasks to shut down """
    logger.warning(f"Received exit signal {sig.name}... Initiating shutdown.")
    shutdown_event.set() # Signal all waiting tasks

    # Allow some time for tasks to react to the event
    await asyncio.sleep(0.2)

    # Cancel all other running tasks forcefully after the event is set
    tasks = [t for t in asyncio.all_tasks() if t is not asyncio.current_task()]
    if tasks:
        logger.info(f"Cancelling {len(tasks)} outstanding tasks...")
        for task in tasks:
            task.cancel()
        # Wait for tasks to finish cancelling
        await asyncio.gather(*tasks, return_exceptions=True)
        logger.info("Outstanding tasks cancelled.")

    # Shutdown the thread pool executor, waiting for file saving
    logger.info("Shutting down thread pool executor (waiting for saves)...")
    # Wait=True ensures ongoing file saves complete before exiting
    executor.shutdown(wait=True)
    logger.info("Thread pool executor shut down.")

    # Stop the asyncio event loop
    logger.info("Stopping event loop.")
    loop.stop()

# === Main Execution ===
async def main():
    """ Main asynchronous entry point """
    loop = asyncio.get_running_loop()

    # Add signal handlers for graceful shutdown on SIGINT (Ctrl+C) and SIGTERM
    for sig_name in ('SIGINT', 'SIGTERM'):
        sig = getattr(signal, sig_name, None)
        if sig:
             try:
                 loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(shutdown(s, loop)))
                 logger.debug(f"Registered signal handler for {sig_name}")
             except NotImplementedError:
                 # Windows might not support add_signal_handler for SIGTERM fully
                 logger.warning(f"Could not register signal handler for {sig_name}")

    # Start the WebSocket server
    server_instance = None
    try:
        logger.info(f"Starting WebSocket server on ws://{HOST}:{PORT}")
        # Start server and keep track of the server object to close it later
        server_instance = await serve(handler, HOST, PORT)
        logger.info("Server started successfully.")

        # Start background tasks
        logger.info("Starting background tasks...")
        monitor_task = asyncio.create_task(throughput_monitor_task(), name="ThroughputMonitor")
        player_task = asyncio.create_task(audio_player_task(), name="AudioPlayer")
        writer_task = asyncio.create_task(wav_writer_task(), name="WavWriter")
        background_tasks = [monitor_task, player_task, writer_task]

        # Wait indefinitely until the shutdown event is set by the signal handler
        await shutdown_event.wait()
        logger.info("Shutdown event received in main task.")

    except OSError as e:
        logger.error(f"Failed to start server, likely port {PORT} is already in use: {e}")
    except Exception as e:
         logger.error(f"Error during main execution: {e}\n{traceback.format_exc()}")
    finally:
        # Cleanup server if it was started
        if server_instance:
            logger.info("Closing WebSocket server...")
            server_instance.close()
            try:
                # Wait briefly for server to close connections
                await asyncio.wait_for(server_instance.wait_closed(), timeout=2.0)
                logger.info("WebSocket server closed.")
            except asyncio.TimeoutError:
                 logger.warning("Timeout waiting for WebSocket server to close.")
            except Exception as e:
                 logger.error(f"Error during server close: {e}")


if __name__ == "__main__":
    logger.info("Starting application...")

    # Start the GUI in a separate, non-daemon thread if clean exit is desired,
    # otherwise daemon=True is simpler. If daemon=False, need signal handling in Qt.
    # For simplicity, keeping daemon=True.
    gui_thread = threading.Thread(target=run_visualizers, daemon=True, name="GUIThread")
    gui_thread.start()

    try:
        # Run the main asyncio event loop until shutdown
        asyncio.run(main())
    except KeyboardInterrupt:
        # This might not be caught if signal handlers are effective
        logger.info("Caught KeyboardInterrupt in main __name__ block.")
    finally:
        logger.info("Application finished.")
        # Executor is shut down within the shutdown() handler called by signals