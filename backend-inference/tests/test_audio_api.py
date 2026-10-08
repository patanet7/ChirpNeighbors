"""Local mock BFF transport: real verifier/gateway/API code, no Google/model claim."""

from __future__ import annotations

import json
import unittest
from datetime import UTC, datetime
from uuid import uuid4

import httpx

from app.audio_pipeline.api import create_app
from app.audio_pipeline.contracts import AUDIO_EVENT_ADAPTER, AudioHTTPError
from app.audio_pipeline.export_openapi import openapi_document
from app.audio_pipeline.fixtures import FIXTURE_OWNER, fixture_command, synthetic_wav
from app.audio_pipeline.gateway import (
    AuthenticationRequiredError,
    BFFTransport,
    GatewayUnavailableError,
    HTTPRecordingStorage,
    SessionVerifier,
    trusted_origin,
)
from app.audio_pipeline.providers import SyntheticFixtureProvider
from app.audio_pipeline.service import Principal, RecordingAccessError

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
        ):
            with self.subTest(origin=origin), self.assertRaises(ValueError):
                trusted_origin(origin, allow_loopback_http=True)
        with self.assertRaises(ValueError):
            trusted_origin("http://127.0.0.1:5173")
        self.assertEqual(
            trusted_origin("http://127.0.0.1:5173", allow_loopback_http=True),
            "http://127.0.0.1:5173",
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


if __name__ == "__main__":
    unittest.main()
