"""Local mock BFF transport: real verifier/gateway/API code, no Google/model claim."""

from __future__ import annotations

import asyncio
import contextlib
import json
import threading
import unittest
from collections.abc import Awaitable, Callable
from datetime import UTC, datetime
from unittest.mock import patch
from uuid import uuid4

import httpx
from starlette.types import ASGIApp, Message, Scope

from app.audio_pipeline.api import BoundedCommandBody, create_app
from app.audio_pipeline.contracts import (
    AUDIO_EVENT_ADAPTER,
    AudioAnalyzeCommand,
    AudioEvent,
    AudioHTTPError,
)
from app.audio_pipeline.export_openapi import openapi_document
from app.audio_pipeline.fixtures import FIXTURE_OWNER, fixture_command, synthetic_wav
from app.audio_pipeline.gateway import (
    AuthenticationRequiredError,
    BFFTransport,
    GatewayUnavailableError,
    HTTPRecordingStorage,
    RequestGateway,
    SessionVerifier,
    trusted_origin,
)
from app.audio_pipeline.pcm import Chunk
from app.audio_pipeline.providers import Prediction, SyntheticFixtureProvider
from app.audio_pipeline.service import (
    AnalysisCancelledError,
    AudioService,
    Cancellation,
    Principal,
    RecordingAccessError,
    RecordingStorage,
)

ORIGIN = "https://owner-app.invalid"
COOKIE = "session=explicit-test-session"


def account() -> dict[str, object]:
    return {
        "version": 1,
        "identity": {
            "mode": "account",
            "ownerId": FIXTURE_OWNER.owner_id,
            "label": "Synthetic test account",
            "expiresAt": "2100-01-01T00:00:00Z",
        },
    }


class MockBFF:
    def __init__(self) -> None:
        self.audio = synthetic_wav(tone=True)
        self.command = fixture_command(self.audio)
        self.requests: list[httpx.Request] = []
        self.revoked = False
        self.deleted = False
        self.synthetic = True
        self.generation = 1
        self.failure: str | None = None
        self.failure_path = "analysis-permit"

    def handle(self, request: httpx.Request) -> httpx.Response:
        self.requests.append(request)
        cookie = request.headers.get("cookie")
        if self.revoked or cookie not in (COOKIE, "session=foreign-test-session"):
            return httpx.Response(401, json={"version": 1, "identity": None})
        if request.url.path == "/api/session":
            payload = account()
            if cookie != COOKIE:
                payload = {
                    "version": 1,
                    "identity": {
                        "mode": "account",
                        "ownerId": "foreign-owner",
                        "label": "Other test account",
                        "expiresAt": "2100-01-01T00:00:00Z",
                    },
                }
            return httpx.Response(
                200, json=payload, headers={"set-cookie": "unwanted=never-forward"}
            )
        if self.deleted or cookie != COOKIE:
            return httpx.Response(404, json={"error": "unavailable"})
        if request.url.path.endswith("/" + self.failure_path):
            if self.failure == "503":
                return httpx.Response(503, json={"private": "gateway-diagnostic"})
            if self.failure == "transport":
                raise httpx.ReadTimeout("private-gateway-address", request=request)
            if self.failure == "forbidden":
                return httpx.Response(403, json={"private": "access-denied"})
        if (
            request.url.path
            == f"/api/recordings/{self.command.recording.id}/analysis-permit"
        ):
            return httpx.Response(
                200,
                json={
                    "version": 1,
                    "recording": {
                        **self.command.recording.model_dump(),
                        "generation": self.generation,
                    },
                    "syntheticFixture": self.synthetic,
                },
            )
        if request.url.path == f"/api/recordings/{self.command.recording.id}/audio":
            return httpx.Response(
                200, content=self.audio, headers={"content-type": "audio/wav"}
            )
        return httpx.Response(404)

    def gateway(self) -> BFFTransport:
        return BFFTransport(ORIGIN, transport=httpx.MockTransport(self.handle))


class SessionVerifierTests(unittest.TestCase):
    def test_fixed_endpoint_no_owner_headers_or_cookie_jar_reuse(self) -> None:
        bff = MockBFF()
        verifier = SessionVerifier(bff.gateway())
        self.assertEqual(verifier.verify(COOKIE), FIXTURE_OWNER)
        self.assertEqual(
            verifier.verify("session=foreign-test-session"), Principal("foreign-owner")
        )
        self.assertEqual(
            [str(r.url) for r in bff.requests], [ORIGIN + "/api/session"] * 2
        )
        self.assertEqual(
            bff.requests[1].headers["cookie"], "session=foreign-test-session"
        )
        self.assertTrue(
            all(
                "owner-id" not in request.headers
                and "authorization" not in request.headers
                for request in bff.requests
            )
        )

    def test_untrusted_origin_configuration_rejected(self) -> None:
        for origin in (
            "http://owner-app.invalid",
            "file:///tmp/private",
            "https://name:secret@owner-app.invalid",
            "https://owner-app.invalid/api/session",
            "https://owner-app.invalid?url=elsewhere",
            "https://owner-app.invalid#fragment",
            "https://owner-app.invalid:99999",
            "https://owner-app.invalid\n",
            "https://owner-app.invalid\\hidden",
            "https://%6fwner-app.invalid",
            "https://owner-app.invalid%2e",
            "https://@owner-app.invalid",
            "https://:@owner-app.invalid",
            "https://owner^app.invalid",
            "https://owner|app.invalid",
            "https://.",
            "https://127.1",
            "https://0177.0.0.1",
            "https://0x7f000001",
            "https://2130706433",
            "https://127.0.0.1.",
            "https://example.1",
            "https://[::1%25zone]",
            "https://[::invalid]",
        ):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                trusted_origin(origin, allow_loopback_http=True)
        with self.assertRaises(ValueError):
            trusted_origin("http://127.0.0.1:5173")
        self.assertEqual(
            trusted_origin("http://127.0.0.1:5173", allow_loopback_http=True),
            "http://127.0.0.1:5173",
        )

    def test_trusted_origin_matches_browser_serialization_for_supported_authorities(
        self,
    ) -> None:
        cases = {
            "HTTPS://OWNER-APP.INVALID:443/": ORIGIN,
            "https://OWNER-APP.INVALID:8443/": "https://owner-app.invalid:8443",
            "https://OWNER-APP.INVALID./": "https://owner-app.invalid.",
            "https://[2001:0DB8:0:0:0:0:0:1]:443/": "https://[2001:db8::1]",
            "https://127.0.0.1:443/": "https://127.0.0.1",
            "HTTP://LOCALHOST:80/": "http://localhost",
            "http://[0:0:0:0:0:0:0:1]:80/": "http://[::1]",
        }
        for configured, expected in cases.items():
            with self.subTest(configured=configured):
                self.assertEqual(
                    trusted_origin(configured, allow_loopback_http=True), expected
                )

    def test_session_rejected_for_expired_null_unknown_and_development(self) -> None:
        for payload in (
            {"version": 1, "identity": None},
            {**account(), "ownerId": "injected"},
            {
                "version": 1,
                "identity": {
                    "mode": "account",
                    "ownerId": "a",
                    "label": "test",
                    "expiresAt": "2026-10-08T00:00:00Z",
                },
            },
            {
                "version": 1,
                "identity": {"mode": "development", "ownerId": "a", "label": "test"},
            },
            {
                "version": 1,
                "identity": {"mode": "account", "ownerId": "a", "label": "test"},
            },
        ):
            gateway = BFFTransport(
                ORIGIN,
                transport=httpx.MockTransport(
                    lambda request: httpx.Response(200, json=payload)
                ),
            )
            verifier = SessionVerifier(
                gateway, clock=lambda: datetime(2026, 10, 8, tzinfo=UTC)
            )
            with (
                self.subTest(payload=payload),
                self.assertRaises(AuthenticationRequiredError),
            ):
                verifier.verify(COOKIE)

    def test_explicit_development_flag_only(self) -> None:
        payload = {
            "version": 1,
            "identity": {
                "mode": "development",
                "ownerId": "fixture",
                "label": "Development fixture",
            },
        }
        gateway = BFFTransport(
            ORIGIN,
            transport=httpx.MockTransport(
                lambda request: httpx.Response(200, json=payload)
            ),
        )
        self.assertEqual(
            SessionVerifier(gateway, allow_development=True).verify(COOKIE),
            Principal("fixture"),
        )

    def test_redirects_oversized_malformed_and_unavailable_verifier_fail_closed(
        self,
    ) -> None:
        for response in (
            httpx.Response(302, headers={"location": "https://exfiltration.invalid"}),
            httpx.Response(
                200, text="x" * 4097, headers={"content-type": "application/json"}
            ),
            httpx.Response(
                200,
                text="{private malformed body",
                headers={"content-type": "application/json"},
            ),
            httpx.Response(200, text="<html>login</html>"),
            httpx.Response(503, json={"message": "private diagnostic"}),
        ):
            calls: list[str] = []

            def handler(request: httpx.Request) -> httpx.Response:
                calls.append(str(request.url))
                return response

            verifier = SessionVerifier(
                BFFTransport(ORIGIN, transport=httpx.MockTransport(handler))
            )
            with self.assertRaises(AuthenticationRequiredError) as raised:
                verifier.verify(COOKIE)
            self.assertEqual(calls, [ORIGIN + "/api/session"])
            self.assertNotIn("private", str(raised.exception))

    def test_network_errors_and_invalid_cookie_are_safe(self) -> None:
        def unavailable(request: httpx.Request) -> httpx.Response:
            raise httpx.ConnectError("private gateway address", request=request)

        verifier = SessionVerifier(
            BFFTransport(ORIGIN, transport=httpx.MockTransport(unavailable))
        )
        for cookie in (COOKIE, "", "session=x\r\nowner-id:foreign", "x" * 8193):
            with self.assertRaises(AuthenticationRequiredError) as raised:
                verifier.verify(cookie)
            self.assertEqual(str(raised.exception), "")


class RecordingGatewayTests(unittest.TestCase):
    def test_owner_bytes_and_generation_snapshot(self) -> None:
        bff = MockBFF()
        storage = HTTPRecordingStorage(bff.gateway(), FIXTURE_OWNER, COOKIE)
        value = storage.read(FIXTURE_OWNER, bff.command.recording)
        self.assertEqual(value.data, bff.audio)
        self.assertTrue(value.synthetic_fixture)
        bff.generation = 2
        with self.assertRaises(RecordingAccessError):
            storage.assert_current(FIXTURE_OWNER, bff.command.recording)

    def test_foreign_principal_fails_before_network_and_revocation_fences(self) -> None:
        bff = MockBFF()
        storage = HTTPRecordingStorage(bff.gateway(), FIXTURE_OWNER, COOKIE)
        with self.assertRaises(RecordingAccessError):
            storage.read(Principal("forged-owner"), bff.command.recording)
        self.assertEqual(bff.requests, [])
        bff.revoked = True
        with self.assertRaises(RecordingAccessError):
            storage.assert_current(FIXTURE_OWNER, bff.command.recording)

    def test_audio_response_limit_and_type(self) -> None:
        for response in (
            httpx.Response(
                200, content=b"x" * 101, headers={"content-type": "audio/wav"}
            ),
            httpx.Response(200, json={"url": "private"}),
        ):
            gateway = BFFTransport(
                ORIGIN, transport=httpx.MockTransport(lambda request: response)
            )
            with self.assertRaises(GatewayUnavailableError):
                gateway.get(
                    "/api/recordings/test/audio",
                    cookie=COOKIE,
                    maximum=100,
                    media_type="audio/wav",
                )


class AudioAPITests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self) -> None:
        self.bff = MockBFF()
        self.client = httpx.AsyncClient(
            transport=httpx.ASGITransport(
                app=create_app(
                    gateway=self.bff.gateway(), provider=SyntheticFixtureProvider()
                )
            ),
            base_url="https://audio.invalid",
        )
        self.addAsyncCleanup(self.client.aclose)

    async def post(self, *, cookie: str = COOKIE) -> httpx.Response:
        return await self.client.post(
            "/v1/audio/analyze",
            content=self.bff.command.model_dump_json(),
            headers={
                "origin": ORIGIN,
                "content-type": "application/json",
                "cookie": cookie,
            },
        )

    async def test_canonical_browser_origin_reaches_configured_gateway_only(
        self,
    ) -> None:
        gateway = BFFTransport(
            "HTTPS://OWNER-APP.INVALID:443/",
            transport=httpx.MockTransport(self.bff.handle),
        )
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(
                app=create_app(gateway=gateway, provider=SyntheticFixtureProvider())
            ),
            base_url="https://audio.invalid",
        ) as client:
            for origin, status in (("https://other.invalid", 403), (ORIGIN, 200)):
                response = await client.post(
                    "/v1/audio/analyze",
                    content=self.bff.command.model_dump_json(),
                    headers={
                        "origin": origin,
                        "content-type": "application/json",
                        "cookie": COOKIE,
                    },
                )
                self.assertEqual(response.status_code, status, response.text)
                if status == 403:
                    self.assertEqual(self.bff.requests, [])
        self.assertTrue(self.bff.requests)
        self.assertTrue(
            all(
                str(request.url).startswith(ORIGIN + "/api/")
                for request in self.bff.requests
            )
        )

    async def test_authenticated_synthetic_analysis_through_actual_adapter_stack(
        self,
    ) -> None:
        response = await self.post()
        self.assertEqual(response.status_code, 200, response.text)
        event = AUDIO_EVENT_ADAPTER.validate_json(response.content)
        self.assertEqual(event.kind, "audio.completed")
        self.assertIn("no-store", response.headers["cache-control"])
        self.assertTrue(
            all(request.headers["cookie"] == COOKIE for request in self.bff.requests)
        )

    async def test_reverify_session_before_cached_result_and_foreign_owner_isolation(
        self,
    ) -> None:
        self.assertEqual((await self.post()).status_code, 200)
        self.assertEqual(
            (await self.post(cookie="session=foreign-test-session")).status_code, 404
        )
        self.bff.revoked = True
        response = await self.post()
        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            AudioHTTPError.model_validate_json(response.content).code,
            "authentication_required",
        )

    async def test_delete_invalidates_cached_result(self) -> None:
        self.assertEqual((await self.post()).status_code, 200)
        self.bff.deleted = True
        self.assertEqual((await self.post()).status_code, 404)

    async def test_actual_uploads_refuse_fixture_classifier(self) -> None:
        self.bff.synthetic = False
        response = await self.post()
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["error"]["code"], "provider_blocked")

    async def test_same_request_recovers_after_permit_or_audio_gateway_outage(
        self,
    ) -> None:
        for path in ("analysis-permit", "audio"):
            for failure in ("503", "transport"):
                with self.subTest(path=path, failure=failure):
                    self.bff.command = fixture_command(
                        self.bff.audio, request_id=str(uuid4())
                    )
                    self.bff.failure_path, self.bff.failure = path, failure
                    original = self.bff.command
                    failed = await self.post()
                    self.assertEqual(failed.status_code, 404)
                    self.assertEqual(
                        failed.json()["error"],
                        {"code": "recording_unavailable", "retryable": False},
                    )
                    self.assertNotIn("private", failed.text)
                    self.bff.command = original.model_copy(
                        update={"reviewThreshold": 0.7}
                    )
                    self.assertEqual((await self.post()).status_code, 409)
                    self.bff.command = original
                    self.bff.failure = None
                    recovered = await self.post()
                    self.assertEqual(recovered.status_code, 200, recovered.text)
                    event = AUDIO_EVENT_ADAPTER.validate_json(recovered.content)
                    self.assertEqual(event.requestId, original.requestId)
                    self.assertEqual(event.traceId, original.traceId)
                    self.assertEqual((await self.post()).json(), recovered.json())

    async def test_cached_result_loses_evidence_but_not_request_binding_on_outage(
        self,
    ) -> None:
        original = self.bff.command
        complete = await self.post()
        self.assertEqual(complete.status_code, 200)
        self.bff.failure = "503"
        self.assertEqual((await self.post()).status_code, 404)
        self.bff.failure = None
        self.bff.command = original.model_copy(update={"reviewThreshold": 0.7})
        self.assertEqual((await self.post()).status_code, 409)
        self.bff.command = original
        recovered = await self.post()
        self.assertEqual(recovered.status_code, 200)
        self.assertEqual(recovered.json(), complete.json())

    async def test_access_retry_never_restores_foreign_deleted_or_changed_generation(
        self,
    ) -> None:
        self.bff.failure = "503"
        self.assertEqual((await self.post()).status_code, 404)
        self.bff.failure = None
        for _ in range(2):
            foreign = await self.post(cookie="session=foreign-test-session")
            self.assertEqual(foreign.status_code, 404)
            self.assertNotIn("rawCandidates", foreign.text)
        for failure in ("forbidden", "503"):
            self.bff.failure = failure
            for _ in range(2):
                unavailable = await self.post()
                self.assertEqual(unavailable.status_code, 404)
                self.assertNotIn("rawCandidates", unavailable.text)
        self.bff.failure = None
        self.bff.deleted = True
        for _ in range(2):
            self.assertEqual((await self.post()).status_code, 404)
        self.bff.deleted = False
        self.bff.generation += 1
        for _ in range(2):
            self.assertEqual((await self.post()).status_code, 404)
        self.assertFalse(
            any(request.url.path.endswith("/audio") for request in self.bff.requests)
        )

    async def test_fresh_api_after_gateway_recovery_rechecks_current_access(
        self,
    ) -> None:
        self.bff.failure = "transport"
        self.assertEqual((await self.post()).status_code, 404)
        self.bff.failure = None
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(
                app=create_app(
                    gateway=self.bff.gateway(), provider=SyntheticFixtureProvider()
                )
            ),
            base_url="https://audio.invalid",
        ) as restarted:
            response = await restarted.post(
                "/v1/audio/analyze",
                content=self.bff.command.model_dump_json(),
                headers={
                    "origin": ORIGIN,
                    "content-type": "application/json",
                    "cookie": COOKIE,
                },
            )
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json()["requestId"], self.bff.command.requestId)
            self.bff.deleted = True
            response = await restarted.post(
                "/v1/audio/analyze",
                content=self.bff.command.model_dump_json(),
                headers={
                    "origin": ORIGIN,
                    "content-type": "application/json",
                    "cookie": COOKIE,
                },
            )
            self.assertEqual(response.status_code, 404)

    async def test_unconfigured_model_and_service_readiness_fail_closed(self) -> None:
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=create_app()), base_url=ORIGIN
        ) as client:
            self.assertEqual((await client.get("/healthz")).status_code, 200)
            self.assertEqual((await client.get("/readyz")).status_code, 503)
            response = await client.post(
                "/v1/audio/analyze", json=self.bff.command.model_dump(mode="json")
            )
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json()["code"], "service_unavailable")
        async with httpx.AsyncClient(
            transport=httpx.ASGITransport(app=create_app(gateway=self.bff.gateway())),
            base_url=ORIGIN,
        ) as client:
            response = await client.post(
                "/v1/audio/analyze",
                content=self.bff.command.model_dump_json(),
                headers={
                    "origin": ORIGIN,
                    "content-type": "application/json",
                    "cookie": COOKIE,
                },
            )
            self.assertEqual(response.status_code, 503)
            self.assertEqual(response.json()["error"]["code"], "provider_blocked")
            self.assertFalse(
                any(
                    request.url.path.endswith("/audio") for request in self.bff.requests
                )
            )

    async def test_origin_missing_wrong_and_client_owner_header_never_authorize(
        self,
    ) -> None:
        for origin in (None, "https://attacker.invalid"):
            headers = {
                "content-type": "application/json",
                "cookie": COOKIE,
                "owner-id": FIXTURE_OWNER.owner_id,
            }
            if origin is not None:
                headers["origin"] = origin
            response = await self.client.post(
                "/v1/audio/analyze",
                content=self.bff.command.model_dump_json(),
                headers=headers,
            )
            self.assertEqual(response.status_code, 403)
        response = await self.client.post(
            "/v1/audio/analyze",
            content=self.bff.command.model_dump_json(),
            headers={
                "origin": ORIGIN,
                "content-type": "application/json",
                "owner-id": FIXTURE_OWNER.owner_id,
            },
        )
        self.assertEqual(response.status_code, 401)

    async def test_bounded_json_and_sanitized_validation_errors(self) -> None:
        headers = {
            "origin": ORIGIN,
            "content-type": "application/json",
            "cookie": COOKIE,
        }
        oversized = await self.client.post(
            "/v1/audio/analyze", content=b"x" * 4097, headers=headers
        )
        self.assertEqual(oversized.status_code, 413)
        for content in (
            "{broken-secret",
            json.dumps(
                {
                    **self.bff.command.model_dump(mode="json"),
                    "ownerId": "private-owner-secret",
                }
            ),
        ):
            response = await self.client.post(
                "/v1/audio/analyze", content=content, headers=headers
            )
            self.assertEqual(response.status_code, 422)
            self.assertNotIn("secret", response.text)
            self.assertEqual(
                AudioHTTPError.model_validate_json(response.content).code,
                "invalid_request",
            )

    async def test_operational_responses_use_closed_authority(self) -> None:
        from app.audio_pipeline.contracts import AudioHealth, AudioReadiness

        health = await self.client.get("/healthz")
        self.assertEqual(health.status_code, 200)
        self.assertEqual(
            AudioHealth.model_validate_json(health.content).status, "alive"
        )
        readiness = await self.client.get("/readyz")
        value = AudioReadiness.model_validate_json(readiness.content)
        self.assertEqual(readiness.status_code, 200 if value.ready else 503)
        document = (await self.client.get("/openapi.json")).json()
        for path in ("/healthz", "/readyz"):
            self.assertIn("content", document["paths"][path]["get"]["responses"]["200"])
        self.assertIn("503", document["paths"]["/readyz"]["get"]["responses"])

    async def test_openapi_is_generated_from_pydantic_wire_models(self) -> None:
        document = (await self.client.get("/openapi.json")).json()
        self.assertIn("AudioAnalyzeCommand", document["components"]["schemas"])
        self.assertIn("AudioCompletedEvent", document["components"]["schemas"])
        self.assertFalse(
            document["components"]["schemas"]["AudioAnalyzeCommand"][
                "additionalProperties"
            ]
        )
        self.assertNotIn("/upload", document["paths"])
        self.assertEqual(document, json.loads(openapi_document()))
        for status in ("400", "401", "403", "404", "409", "413", "415", "422", "503"):
            self.assertIn(
                status, document["paths"]["/v1/audio/analyze"]["post"]["responses"]
            )


HTTPHandler = Callable[[str, asyncio.StreamWriter], Awaitable[None]]


class LocalHTTP:
    """Actual loopback sockets; stalled handlers observe peer EOF before cleanup."""

    def __init__(self, handler: HTTPHandler) -> None:
        self.handler = handler
        self.paths: list[str] = []
        self.active: set[asyncio.Task[None]] = set()
        self.entered = asyncio.Event()
        self.disconnected = asyncio.Event()

    async def start(self) -> str:
        self.server = await asyncio.start_server(self.accept, "127.0.0.1", 0)
        return f"http://127.0.0.1:{self.server.sockets[0].getsockname()[1]}"

    async def accept(
        self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter
    ) -> None:
        task = asyncio.current_task()
        assert task is not None
        self.active.add(task)
        children: list[asyncio.Task[object]] = []
        try:
            headers = await reader.readuntil(b"\r\n\r\n")
            path = headers.split(b" ", 2)[1].decode("ascii")
            self.paths.append(path)
            self.entered.set()

            async def respond() -> None:
                await self.handler(path, writer)

            response = asyncio.create_task(respond())
            disconnected = asyncio.create_task(reader.read())
            children.extend((response, disconnected))
            await asyncio.wait(
                {response, disconnected}, return_when=asyncio.FIRST_COMPLETED
            )
            if disconnected.done() and not response.done():
                self.disconnected.set()
        finally:
            for child in children:
                child.cancel()
            await asyncio.gather(*children, return_exceptions=True)
            writer.close()
            with contextlib.suppress(ConnectionError):
                await writer.wait_closed()
            self.active.discard(task)

    async def close(self) -> None:
        self.server.close()
        await self.server.wait_closed()
        tasks = tuple(self.active)
        for task in tasks:
            task.cancel()
        await asyncio.gather(*tasks, return_exceptions=True)


async def write_response(
    writer: asyncio.StreamWriter, body: bytes, *, media_type: str = "application/json"
) -> None:
    writer.write(
        f"HTTP/1.1 200 OK\r\nContent-Type: {media_type}\r\n"
        f"Content-Length: {len(body)}\r\nConnection: close\r\n\r\n".encode()
        + body
    )
    await writer.drain()


class TransportDeadlineTests(unittest.IsolatedAsyncioTestCase):
    async def server(
        self, handler: HTTPHandler, *, deadline: float = 0.12
    ) -> tuple[LocalHTTP, BFFTransport]:
        server = LocalHTTP(handler)
        origin = await server.start()
        self.addAsyncCleanup(server.close)
        return server, BFFTransport(
            origin, allow_loopback_http=True, deadline_seconds=deadline
        )

    async def test_total_deadline_closes_stalled_and_dripping_headers_and_body(
        self,
    ) -> None:
        for mode in ("stalled-headers", "dripping-headers", "dripping-body"):
            with self.subTest(mode=mode):
                blocks = 0

                async def slow(path: str, writer: asyncio.StreamWriter) -> None:
                    nonlocal blocks
                    if mode == "stalled-headers":
                        await asyncio.Event().wait()
                    if mode == "dripping-body":
                        writer.write(
                            b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                            b"Transfer-Encoding: chunked\r\n\r\n"
                        )
                    while True:
                        writer.write(b"1\r\nx\r\n" if mode == "dripping-body" else b"H")
                        await writer.drain()
                        blocks += 1
                        await asyncio.sleep(0.015)

                server, gateway = await self.server(slow)
                started = asyncio.get_running_loop().time()
                with self.assertRaises(GatewayUnavailableError) as error:
                    await gateway.aget(
                        "/api/session",
                        cookie=COOKIE,
                        maximum=4096,
                        media_type="application/json",
                    )
                elapsed = asyncio.get_running_loop().time() - started
                self.assertLess(elapsed, 1)
                self.assertEqual(str(error.exception), "")
                await asyncio.wait_for(server.disconnected.wait(), 1)
                if mode != "stalled-headers":
                    self.assertGreater(blocks, 1)
                count = blocks
                await asyncio.sleep(0.04)
                self.assertEqual(blocks, count)
                self.assertEqual(server.paths, ["/api/session"])

    async def test_external_cancellation_closes_socket_without_waiting_for_deadline(
        self,
    ) -> None:
        async def blocked(path: str, writer: asyncio.StreamWriter) -> None:
            await asyncio.Event().wait()

        server, gateway = await self.server(blocked, deadline=5)
        task = asyncio.create_task(
            gateway.aget(
                "/api/session",
                cookie=COOKIE,
                maximum=4096,
                media_type="application/json",
            )
        )
        await asyncio.wait_for(server.entered.wait(), 1)
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await asyncio.wait_for(task, 1)
        await asyncio.wait_for(server.disconnected.wait(), 1)
        self.assertEqual(server.paths, ["/api/session"])

    async def test_loopback_bounds_malformed_lengths_encodings_and_redirects(
        self,
    ) -> None:
        prefix = b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
        cases = (
            prefix + b"Content-Length: 4097\r\n\r\n",
            prefix + b"Content-Length: nope\r\n\r\n",
            prefix + b"Content-Length: 1\r\nContent-Length: 2\r\n\r\nxx",
            prefix + b"Content-Encoding: gzip\r\nContent-Length: 0\r\n\r\n",
            prefix
            + b"Transfer-Encoding: chunked\r\n\r\n1001\r\n"
            + b"x" * 4097
            + b"\r\n0\r\n\r\n",
            prefix + b"Content-Length: 10\r\n\r\nx",
            b"HTTP/1.1 302 Found\r\nLocation: /api/stolen\r\nContent-Length: 0\r\n\r\n",
            b"HTTP/1.1 503 Failed\r\nContent-Length: 0\r\n\r\n",
        )
        for raw in cases:
            with self.subTest(response=raw[:100]):

                async def response(path: str, writer: asyncio.StreamWriter) -> None:
                    writer.write(raw)
                    await writer.drain()

                server, gateway = await self.server(response)
                with self.assertRaises(GatewayUnavailableError) as error:
                    await gateway.aget(
                        "/api/session",
                        cookie=COOKIE,
                        maximum=4096,
                        media_type="application/json",
                    )
                self.assertEqual(str(error.exception), "")
                self.assertEqual(server.paths, ["/api/session"])

    async def test_shared_deadline_covers_sequence_and_rejects_later_calls(
        self,
    ) -> None:
        count = 0

        async def response(path: str, writer: asyncio.StreamWriter) -> None:
            nonlocal count
            count += 1
            if count == 3:
                await asyncio.Event().wait()
            await asyncio.sleep(0.06)
            await write_response(writer, b"{}")

        server, gateway = await self.server(response, deadline=1)
        scope = RequestGateway(gateway, deadline_seconds=0.3)
        self.addAsyncCleanup(scope.aclose)
        for _ in range(2):
            self.assertEqual(
                await asyncio.to_thread(
                    scope.get,
                    "/api/session",
                    cookie=COOKIE,
                    maximum=4096,
                    media_type="application/json",
                ),
                b"{}",
            )
        with self.assertRaises(GatewayUnavailableError):
            await asyncio.to_thread(
                scope.get,
                "/api/session",
                cookie=COOKIE,
                maximum=4096,
                media_type="application/json",
            )
        await asyncio.wait_for(server.disconnected.wait(), 1)
        before = len(server.paths)
        with self.assertRaises(GatewayUnavailableError):
            await scope.aget(
                "/api/session",
                cookie=COOKIE,
                maximum=4096,
                media_type="application/json",
            )
        self.assertEqual(len(server.paths), before)
        self.assertEqual(before, 3)

    async def test_closed_bridge_prevents_pending_and_new_worker_network_calls(
        self,
    ) -> None:
        async def blocked(path: str, writer: asyncio.StreamWriter) -> None:
            await asyncio.Event().wait()

        server, gateway = await self.server(blocked, deadline=5)
        scope = RequestGateway(gateway)
        worker = asyncio.create_task(
            asyncio.to_thread(
                scope.get,
                "/api/session",
                cookie=COOKIE,
                maximum=4096,
                media_type="application/json",
            )
        )
        await asyncio.wait_for(server.entered.wait(), 1)
        await scope.aclose()
        with self.assertRaises(AnalysisCancelledError):
            await asyncio.wait_for(worker, 1)
        await asyncio.wait_for(server.disconnected.wait(), 1)
        with self.assertRaises(AnalysisCancelledError):
            await asyncio.to_thread(
                scope.get,
                "/api/session",
                cookie=COOKIE,
                maximum=4096,
                media_type="application/json",
            )
        self.assertEqual(server.paths, ["/api/session"])

    async def test_sync_wrapper_uses_total_async_deadline(self) -> None:
        async def blocked(path: str, writer: asyncio.StreamWriter) -> None:
            await asyncio.Event().wait()

        server, gateway = await self.server(blocked)
        with self.assertRaises(GatewayUnavailableError):
            await asyncio.wait_for(
                asyncio.to_thread(
                    gateway.get,
                    "/api/session",
                    cookie=COOKIE,
                    maximum=4096,
                    media_type="application/json",
                ),
                1,
            )
        await asyncio.wait_for(server.disconnected.wait(), 1)


class RequestCancellationTests(unittest.IsolatedAsyncioTestCase):
    def request(
        self, app: ASGIApp, origin: str, body: bytes
    ) -> tuple[asyncio.Task[None], asyncio.Queue[Message], list[Message]]:
        messages: asyncio.Queue[Message] = asyncio.Queue()
        messages.put_nowait({"type": "http.request", "body": body, "more_body": False})
        output: list[Message] = []

        async def send(message: Message) -> None:
            output.append(message)

        scope: Scope = {
            "type": "http",
            "asgi": {"version": "3.0"},
            "http_version": "1.1",
            "method": "POST",
            "path": "/v1/audio/analyze",
            "scheme": "https",
            "query_string": b"",
            "headers": [
                (b"origin", origin.encode()),
                (b"cookie", COOKIE.encode()),
                (b"content-type", b"application/json"),
            ],
        }

        async def dispatch() -> None:
            await app(scope, messages.get, send)

        return asyncio.create_task(dispatch()), messages, output

    async def test_disconnect_and_shutdown_cancel_auth_permit_and_media_then_retry(
        self,
    ) -> None:
        for stage in ("session", "analysis-permit", "audio"):
            for shutdown in (False, True):
                with self.subTest(stage=stage, shutdown=shutdown):
                    bff = MockBFF()
                    stalled = asyncio.Event()
                    enabled = True
                    finished_workers: list[bool] = []
                    analyze = AudioService.analyze

                    def observed(
                        service: AudioService,
                        principal: Principal,
                        command: AudioAnalyzeCommand,
                        cancellation: Cancellation | None = None,
                        *,
                        storage: RecordingStorage | None = None,
                    ) -> AudioEvent:
                        try:
                            return analyze(
                                service,
                                principal,
                                command,
                                cancellation,
                                storage=storage,
                            )
                        finally:
                            finished_workers.append(True)

                    async def handle(path: str, writer: asyncio.StreamWriter) -> None:
                        if enabled and path.endswith("/" + stage):
                            stalled.set()
                            media_type = (
                                "audio/wav" if stage == "audio" else "application/json"
                            )
                            writer.write(
                                f"HTTP/1.1 200 OK\r\nContent-Type: {media_type}\r\n"
                                "Transfer-Encoding: chunked\r\n\r\n1\r\nx\r\n".encode()
                            )
                            await writer.drain()
                            await asyncio.Event().wait()
                        response = bff.handle(
                            httpx.Request(
                                "GET", ORIGIN + path, headers={"cookie": COOKIE}
                            )
                        )
                        await write_response(
                            writer,
                            response.content,
                            media_type=response.headers.get(
                                "content-type", "application/json"
                            ),
                        )

                    server = LocalHTTP(handle)
                    origin = await server.start()
                    self.addAsyncCleanup(server.close)
                    app = create_app(
                        gateway=BFFTransport(origin, allow_loopback_http=True),
                        provider=SyntheticFixtureProvider(),
                    )
                    with patch.object(AudioService, "analyze", observed):
                        task, incoming, output = self.request(
                            app, origin, bff.command.model_dump_json().encode()
                        )
                        await asyncio.wait_for(stalled.wait(), 1)
                        if shutdown:
                            task.cancel()
                        else:
                            incoming.put_nowait({"type": "http.disconnect"})
                        with self.assertRaises(asyncio.CancelledError):
                            await asyncio.wait_for(task, 1)
                        await asyncio.wait_for(server.disconnected.wait(), 1)
                        self.assertEqual(output, [])
                        self.assertEqual(
                            len(finished_workers), 0 if stage == "session" else 1
                        )
                        count = len(server.paths)
                        await asyncio.sleep(0.03)
                        self.assertEqual(len(server.paths), count)
                        enabled = False
                        retry, _, result = self.request(
                            app, origin, bff.command.model_dump_json().encode()
                        )
                        await asyncio.wait_for(retry, 3)
                        self.assertEqual(result[0]["status"], 200)
                        body = next(
                            item["body"]
                            for item in result
                            if item["type"] == "http.response.body"
                        )
                        self.assertEqual(
                            AUDIO_EVENT_ADAPTER.validate_json(body).kind,
                            "audio.completed",
                        )

    async def test_repeated_shutdown_joins_cooperative_inference_before_return(
        self,
    ) -> None:
        entered = threading.Event()
        release = threading.Event()
        finished = threading.Event()

        class BlockedProvider(SyntheticFixtureProvider):
            def infer(
                self, chunk: Chunk, *, idempotency_key: str
            ) -> tuple[Prediction, ...]:
                entered.set()
                try:
                    release.wait(3)
                    return super().infer(chunk, idempotency_key=idempotency_key)
                finally:
                    finished.set()

        bff = MockBFF()
        app = create_app(gateway=bff.gateway(), provider=BlockedProvider())
        task, _, output = self.request(
            app, ORIGIN, bff.command.model_dump_json().encode()
        )
        try:
            self.assertTrue(await asyncio.to_thread(entered.wait, 2))
            task.cancel()
            await asyncio.sleep(0.02)
            task.cancel()
            await asyncio.sleep(0.02)
            self.assertFalse(task.done())
            self.assertFalse(finished.is_set())
        finally:
            release.set()
        with self.assertRaises(asyncio.CancelledError):
            await asyncio.wait_for(task, 1)
        self.assertTrue(finished.is_set())
        self.assertEqual(output, [])

    async def test_expired_shared_budget_refuses_final_fence_after_inference(
        self,
    ) -> None:
        entered = threading.Event()
        release = threading.Event()

        class PausedProvider(SyntheticFixtureProvider):
            def infer(
                self, chunk: Chunk, *, idempotency_key: str
            ) -> tuple[Prediction, ...]:
                entered.set()
                release.wait(3)
                return super().infer(chunk, idempotency_key=idempotency_key)

        bff = MockBFF()
        app = create_app(
            gateway=bff.gateway(),
            provider=PausedProvider(),
            request_deadline_seconds=0.2,
        )
        task, _, output = self.request(
            app, ORIGIN, bff.command.model_dump_json().encode()
        )
        try:
            self.assertTrue(await asyncio.to_thread(entered.wait, 2))
            calls = len(bff.requests)
            await asyncio.sleep(0.22)
            # IO expiry does not claim to terminate the native inference call.
            self.assertFalse(task.done())
        finally:
            release.set()
        await asyncio.wait_for(task, 1)
        self.assertEqual(output[0]["status"], 404)
        self.assertEqual(len(bff.requests), calls)
        event = AUDIO_EVENT_ADAPTER.validate_json(output[1]["body"])
        self.assertEqual(event.kind, "audio.failed")
        self.assertNotIn(b"rawCandidates", output[1]["body"])


class CommandBodyDeadlineTests(unittest.IsolatedAsyncioTestCase):
    async def test_oversize_response_send_is_outside_body_read_deadline(self) -> None:
        output: list[Message] = []

        async def downstream(
            scope: Scope,
            receive: Callable[[], Awaitable[Message]],
            send: Callable[[Message], Awaitable[None]],
        ) -> None:
            self.fail("Oversized input must not enter the application")

        async def receive() -> Message:
            return {"type": "http.request", "body": b"x" * 4097, "more_body": False}

        async def send(message: Message) -> None:
            output.append(message)
            await asyncio.sleep(0.03)

        scope: Scope = {"type": "http", "method": "POST", "path": "/v1/audio/analyze"}
        await BoundedCommandBody(downstream, deadline_seconds=0.01)(
            scope, receive, send
        )
        self.assertEqual(
            [
                message["status"]
                for message in output
                if message["type"] == "http.response.start"
            ],
            [413],
        )
        self.assertEqual(
            AudioHTTPError.model_validate_json(output[1]["body"]).code,
            "request_too_large",
        )

    async def test_total_body_deadline_cancels_receive_before_parse_or_auth(
        self,
    ) -> None:
        calls: list[str] = []
        output: list[Message] = []
        receiving = False

        async def downstream(
            scope: Scope,
            receive: Callable[[], Awaitable[Message]],
            send: Callable[[Message], Awaitable[None]],
        ) -> None:
            calls.append("downstream")

        async def drip() -> Message:
            nonlocal receiving
            receiving = True
            try:
                await asyncio.sleep(0.025)
                calls.append("chunk")
                return {"type": "http.request", "body": b"secret", "more_body": True}
            finally:
                receiving = False

        async def send(message: Message) -> None:
            output.append(message)

        scope: Scope = {"type": "http", "method": "POST", "path": "/v1/audio/analyze"}
        await asyncio.wait_for(
            BoundedCommandBody(downstream, deadline_seconds=0.09)(scope, drip, send), 1
        )
        self.assertGreater(calls.count("chunk"), 1)
        self.assertNotIn("downstream", calls)
        self.assertFalse(receiving)
        self.assertEqual(output[0]["status"], 400)
        self.assertIn((b"cache-control", b"private, no-store"), output[0]["headers"])
        body = output[1]["body"]
        self.assertEqual(
            AudioHTTPError.model_validate_json(body).code, "invalid_request"
        )
        self.assertNotIn(b"secret", body)

    async def test_body_disconnect_and_shutdown_do_not_enter_downstream(self) -> None:
        entered = asyncio.Event()
        downstream_called = False
        output: list[Message] = []

        async def downstream(
            scope: Scope,
            receive: Callable[[], Awaitable[Message]],
            send: Callable[[Message], Awaitable[None]],
        ) -> None:
            nonlocal downstream_called
            downstream_called = True

        async def send(message: Message) -> None:
            output.append(message)

        async def disconnected() -> Message:
            return {"type": "http.disconnect"}

        async def stalled() -> Message:
            entered.set()
            await asyncio.Event().wait()
            raise AssertionError("unreachable")

        app = BoundedCommandBody(downstream)
        scope: Scope = {"type": "http", "method": "POST", "path": "/v1/audio/analyze"}
        await app(scope, disconnected, send)
        task = asyncio.create_task(app(scope, stalled, send))
        await entered.wait()
        task.cancel()
        with self.assertRaises(asyncio.CancelledError):
            await task
        self.assertFalse(downstream_called)
        self.assertEqual(output, [])


if __name__ == "__main__":
    unittest.main()
