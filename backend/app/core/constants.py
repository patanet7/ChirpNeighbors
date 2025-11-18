"""Centralized constants for ChirpNeighbors backend."""

from typing import TypedDict


class BirdSpecies(TypedDict):
    """Type definition for bird species data."""

    code: str
    common_name: str
    scientific_name: str


# Mock bird species data for testing/development
# TODO: Replace with actual database when species table is implemented
MOCK_BIRD_SPECIES: list[BirdSpecies] = [
    {
        "code": "amecro",
        "common_name": "American Crow",
        "scientific_name": "Corvus brachyrhynchos",
    },
    {
        "code": "amerob",
        "common_name": "American Robin",
        "scientific_name": "Turdus migratorius",
    },
    {
        "code": "norcad",
        "common_name": "Northern Cardinal",
        "scientific_name": "Cardinalis cardinalis",
    },
    {
        "code": "baleag",
        "common_name": "Bald Eagle",
        "scientific_name": "Haliaeetus leucocephalus",
    },
    {
        "code": "blujay",
        "common_name": "Blue Jay",
        "scientific_name": "Cyanocitta cristata",
    },
    {
        "code": "rebwoo",
        "common_name": "Red-bellied Woodpecker",
        "scientific_name": "Melanerpes carolinus",
    },
    {
        "code": "mouque",
        "common_name": "Mourning Dove",
        "scientific_name": "Zenaida macroura",
    },
]


# Processing status constants
class ProcessingStatus:
    """Audio processing status values."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# API response status constants
class ResponseStatus:
    """Standard API response status values."""

    SUCCESS = "success"
    ERROR = "error"
    CREATED = "created"
    UPDATED = "updated"


# HTTP status codes for common operations
class StatusCodes:
    """Common HTTP status codes."""

    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    NOT_FOUND = 404
    INTERNAL_ERROR = 500


# API endpoints (for reference and testing)
class APIEndpoints:
    """API endpoint paths."""

    # Device endpoints
    DEVICE_REGISTER = "/api/v1/devices/register"
    DEVICE_HEARTBEAT = "/api/v1/devices/{device_id}/heartbeat"
    DEVICE_GET = "/api/v1/devices/{device_id}"
    DEVICE_LIST = "/api/v1/devices/"

    # Audio endpoints
    AUDIO_UPLOAD = "/api/v1/audio/upload"
    AUDIO_RECORDING_GET = "/api/v1/audio/recordings/{file_id}"
    AUDIO_RECORDINGS_LIST = "/api/v1/audio/recordings"

    # Bird endpoints
    BIRDS_SPECIES_LIST = "/api/v1/birds/species"
    BIRDS_SPECIES_GET = "/api/v1/birds/species/{species_id}"
    BIRDS_SEARCH = "/api/v1/birds/search"


# Error messages
class ErrorMessages:
    """Standard error messages."""

    DEVICE_NOT_FOUND = "Device {device_id} not found. Please register first."
    RECORDING_NOT_FOUND = "Recording {file_id} not found"
    INVALID_FILE_FORMAT = "Unsupported file format. Supported: {formats}"
    FILE_TOO_LARGE = "File size ({size} MB) exceeds maximum allowed ({max_size} MB)"
    NO_FILENAME = "No filename provided"
    DEVICE_REGISTER_FIRST = "Device {device_id} not found. Please register device first."
