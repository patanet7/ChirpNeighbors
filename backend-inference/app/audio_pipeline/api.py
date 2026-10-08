"""Authenticated audio request API. No worker loop, model download or upload route."""

from __future__ import annotations

import asyncio
import os
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .contracts import (
    AudioAnalyzeCommand,
    AudioEvent,
    AudioFailedEvent,
    AudioHTTPError,
    RecordingRef,
)
from .gateway import (
    AuthenticationRequiredError,
    BFFTransport,
    HTTPRecordingStorage,
    SessionVerifier,
)
from .providers import FIXTURE_TAXONOMY, InferenceProvider, UnconfiguredModelProvider
from .service import (
    AudioService,
    Cancellation,
    Principal,
    RecordingAccessError,
    RecordingBytes,
)

MAX_COMMAND_BYTES = 4096


def rejected(code: str, status: int) -> JSONResponse:
    error = AudioHTTPError.model_validate(
        {
            "schemaVersion": 1,
            "kind": "audio.rejected",
            "code": code,
            "traceId": str(uuid4()),
        }
    )
    return JSONResponse(
        error.model_dump(mode="json"),
        status_code=status,
        headers={
            "cache-control": "private, no-store",
            "x-content-type-options": "nosniff",
        },
    )


class BoundedCommandBody:
    """Bound bytes before FastAPI JSON parsing, including unknown content length."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] != "http"
            or scope.get("method") != "POST"
            or scope.get("path") != "/v1/audio/analyze"
        ):
            await self.app(scope, receive, send)
            return
        body = bytearray()
        while True:
            message = await receive()
            if message["type"] != "http.request":
                await rejected("invalid_request", 400)(scope, receive, send)
                return
            block = message.get("body", b"")
            if len(body) + len(block) > MAX_COMMAND_BYTES:
                await rejected("request_too_large", 413)(scope, receive, send)
                return
            body.extend(block)
            if not message.get("more_body", False):
                break
        delivered = False

        async def replay() -> Message:
            nonlocal delivered
            if not delivered:
                delivered = True
                return {"type": "http.request", "body": bytes(body), "more_body": False}
            return await receive()

        await self.app(scope, replay, send)


class UnboundStorage:
    def assert_current(self, principal: Principal, recording: RecordingRef) -> None:
        raise RecordingAccessError

    def read(self, principal: Principal, recording: RecordingRef) -> RecordingBytes:
        raise RecordingAccessError


def create_app(
    *,
    gateway: BFFTransport | None = None,
    allow_development: bool = False,
    provider: InferenceProvider | None = None,
) -> FastAPI:
    """Only tests inject fixtures; environment never enables a fake model."""
    app = FastAPI(
        title="ChirpNeighbors owner audio API",
        version="1.0.0",
        docs_url=None,
        redoc_url=None,
    )
    app.add_middleware(BoundedCommandBody)
    verifier = (
        SessionVerifier(gateway, allow_development=allow_development)
        if gateway
        else None
    )
    service = AudioService(
        UnboundStorage(),
        provider if provider is not None else UnconfiguredModelProvider(),
        FIXTURE_TAXONOMY,
    )

    @app.exception_handler(RequestValidationError)
    async def invalid_request(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        # Framework errors include rejected values; do not leak private evidence.
        return rejected("invalid_request", 422)

    @app.get("/healthz")
    async def health() -> dict[str, str | int]:
        return {"version": 1, "status": "alive"}

    @app.get("/readyz")
    async def ready() -> JSONResponse:
        # There is intentionally no approved production model adapter yet.
        return JSONResponse(
            {
                "version": 1,
                "ready": False,
                "authentication": "configured" if verifier else "unconfigured",
                "model": "unconfigured",
            },
            status_code=503,
            headers={"cache-control": "no-store"},
        )

    @app.post(
        "/v1/audio/analyze",
        response_model=AudioEvent,
        responses={
            400: {"model": AudioHTTPError},
            401: {"model": AudioHTTPError},
            403: {"model": AudioHTTPError},
            404: {"model": AudioFailedEvent},
            409: {"model": AudioFailedEvent},
            413: {"model": AudioHTTPError},
            415: {"model": AudioHTTPError},
            422: {"model": AudioHTTPError | AudioFailedEvent},
            503: {"model": AudioHTTPError | AudioFailedEvent},
        },
    )
    async def analyze(command: AudioAnalyzeCommand, request: Request) -> JSONResponse:
        if gateway is None or verifier is None:
            return rejected("service_unavailable", 503)
        if request.headers.get("origin") != gateway.origin:
            return rejected("origin_rejected", 403)
        if (
            request.headers.get("content-type", "").split(";")[0].strip()
            != "application/json"
        ):
            return rejected("invalid_request", 415)
        cookie = request.headers.get("cookie", "")
        try:
            principal = await asyncio.to_thread(verifier.verify, cookie)
        except AuthenticationRequiredError:
            return rejected("authentication_required", 401)
        storage = HTTPRecordingStorage(gateway, principal, cookie)
        token = Cancellation()
        task = asyncio.create_task(
            asyncio.to_thread(
                service.analyze, principal, command, token, storage=storage
            )
        )
        try:
            while not task.done():
                await asyncio.wait({task}, timeout=0.1)
                if await request.is_disconnected():
                    token.cancel()
            event = await task
        except asyncio.CancelledError:
            token.cancel()
            raise
        status = 200
        if isinstance(event, AudioFailedEvent):
            status = {
                "recording_unavailable": 404,
                "invalid_audio": 422,
                "conflict": 409,
                "cancelled": 409,
                "provider_blocked": 503,
                "provider_failure": 503,
            }[event.error.code]
        return JSONResponse(
            event.model_dump(mode="json"),
            status_code=status,
            headers={
                "cache-control": "private, no-store",
                "x-content-type-options": "nosniff",
            },
        )

    return app


def from_environment() -> FastAPI:
    origin = os.environ.get("CHIRP_BFF_ORIGIN")
    local_development = os.environ.get("CHIRP_AUDIO_LOCAL_DEVELOPMENT") == "1"
    gateway = (
        BFFTransport(origin, allow_loopback_http=local_development) if origin else None
    )
    return create_app(gateway=gateway, allow_development=local_development)


app = from_environment()
