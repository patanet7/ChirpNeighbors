"""The current ESP32 wire format; independent of transport and audio devices."""

from dataclasses import dataclass
from datetime import UTC, datetime
from struct import Struct

import numpy as np
from numpy.typing import NDArray

# esp32-client/src/main.cpp: packed uint32 sequence + uint64 esp_timer_get_time.
HEADER = Struct("<IQ")
MAX_PACKET_SAMPLES = 2048 // 4  # 32-bit I2S read, converted to 16-bit mono PCM.
MAX_PACKET_BYTES = HEADER.size + MAX_PACKET_SAMPLES * 2


class AudioPacketError(ValueError):
    """A message cannot be interpreted as the configured 16-bit PCM format."""


@dataclass(frozen=True)
class AudioPacket:
    sequence: int
    device_uptime_us: int
    received_at: datetime
    samples: NDArray[np.int16]


def parse_audio_packet(message: bytes) -> AudioPacket:
    """Strip exactly 12 header bytes, then decode little-endian signed PCM.

    Firmware has no format negotiation. The device MUST be configured for mono
    16-bit output; an even-length 24-bit payload cannot be detected reliably.
    Uptime is a device timer at packet creation, not a UTC observation time.
    """
    if not isinstance(message, bytes):
        raise AudioPacketError("Expected a binary audio message")
    if len(message) < HEADER.size:
        raise AudioPacketError("Truncated audio packet header")
    payload_size = len(message) - HEADER.size
    if payload_size == 0 or payload_size % 2:
        raise AudioPacketError("Expected nonempty, aligned 16-bit PCM")
    if len(message) > MAX_PACKET_BYTES:
        raise AudioPacketError("Audio packet exceeds the firmware buffer limit")
    sequence, uptime = HEADER.unpack_from(message)
    return AudioPacket(
        sequence=sequence,
        device_uptime_us=uptime,
        received_at=datetime.now(UTC),
        samples=np.frombuffer(message, dtype="<i2", offset=HEADER.size),
    )
