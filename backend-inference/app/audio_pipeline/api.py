"""Authenticated audio request API. No worker loop, model download or upload route."""

from __future__ import annotations

import asyncio
import importlib
import os
from pathlib import Path
from typing import assert_never
from uuid import uuid4

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .contracts import (
    AudioAnalyzeCommand,
    AudioEvent,
    AudioFailedEvent,
    AudioHealth,
    AudioHTTPError,
    AudioReadiness,
    RecordingRef,
)
from .gateway import (
    AuthenticationRequiredError,
    BFFTransport,
    HTTPRecordingStorage,
    SessionVerifier,
)
from .providers import (
    FIXTURE_TAXONOMY,
    InferenceProvider,
    ProviderConfigurationError,
    Taxonomy,
    UnconfiguredModelProvider,
    provider_provenance,
)
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
    taxonomy: Taxonomy = FIXTURE_TAXONOMY,
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
        taxonomy,
    )

    @app.exception_handler(RequestValidationError)
    async def invalid_request(
        request: Request, error: RequestValidationError
    ) -> JSONResponse:
        # Framework errors include rejected values; do not leak private evidence.
        return rejected("invalid_request", 422)

    @app.get("/healthz", response_model=AudioHealth)
    async def health() -> AudioHealth:
        return AudioHealth(version=1, status="alive")

    @app.get(
        "/readyz",
        response_model=AudioReadiness,
        responses={503: {"model": AudioReadiness}},
    )
    async def ready() -> JSONResponse:
        configured = False
        try:
            configured = (
                provider_provenance(service.provider).licenseStatus == "approved"
            )
        except ProviderConfigurationError:
            pass
        ready_for_requests = configured and verifier is not None
        return JSONResponse(
            AudioReadiness(
                version=1,
                ready=ready_for_requests,
                authentication="configured" if verifier else "unconfigured",
                model="configured" if configured else "unconfigured",
            ).model_dump(mode="json"),
            status_code=200 if ready_for_requests else 503,
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
            match event.error.code:
                case "recording_unavailable":
                    status = 404
                case "invalid_audio":
                    status = 422
                case "conflict" | "cancelled":
                    status = 409
                case "provider_blocked" | "provider_failure":
                    status = 503
                case unknown:
                    assert_never(unknown)
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
    manifest_path = os.environ.get("CHIRP_AUDIO_MODEL_MANIFEST")
    if manifest_path:
        # Optional numerical/native dependencies never enter the core import graph.
        try:
            module = importlib.import_module("app.audio_onnx.provider")
        except ImportError:
            raise RuntimeError(
                "Install requirements-audio-onnx.txt for local ONNX"
            ) from None
        factory: object = getattr(module, "ONNXProvider", None)
        if not callable(factory):
            raise ProviderConfigurationError("Unsupported optional provider adapter")
        provider: object = factory(Path(manifest_path))
        taxonomy: object = getattr(provider, "taxonomy", None)
        if not isinstance(provider, InferenceProvider) or not isinstance(
            taxonomy, Taxonomy
        ):
            raise ProviderConfigurationError("Unsupported optional provider adapter")
        return create_app(
            gateway=gateway,
            allow_development=local_development,
            provider=provider,
            taxonomy=taxonomy,
        )
    return create_app(gateway=gateway, allow_development=local_development)


app = from_environment()
