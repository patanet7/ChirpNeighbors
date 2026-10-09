"""Fixed-origin browser-session verifier and private media gateway.

Only the trusted SvelteKit BFF resolves an opaque cookie. This module never reads
owner headers, decodes cookies, follows redirects or accepts a caller-selected URL.
"""

from __future__ import annotations

from collections.abc import Callable
from datetime import UTC, datetime
from ipaddress import IPv4Address, IPv6Address
from urllib.parse import urlsplit

import httpx
from pydantic import ValidationError

from app.models.session_verifier import SESSION_VERIFIER_ADAPTER

from .contracts import AudioRecordingPermit, RecordingRef
from .pcm import MAX_BYTES
from .service import Principal, RecordingAccessError, RecordingBytes


class AuthenticationRequiredError(RuntimeError):
    """Safe unauthenticated, expired or untrusted verifier response."""


class GatewayUnavailableError(RuntimeError):
    """Do not expose upstream URLs, cookies, body contents or diagnostics."""


def trusted_origin(value: str, *, allow_loopback_http: bool = False) -> str:
    parts = urlsplit(value)
    host = parts.hostname
    if host and ":" in host:
        host = IPv6Address(host).compressed
    if (
        not host
        or parts.username is not None
        or parts.password is not None
        or parts.path not in ("", "/")
        or parts.query
        or parts.fragment
        or "\\" in value
        or any(ord(character) <= 32 or ord(character) >= 127 for character in value)
        or (
            parts.scheme != "https"
            and not (
                allow_loopback_http
                and parts.scheme == "http"
                and host in ("localhost", "127.0.0.1", "::1")
            )
        )
    ):
        raise ValueError(
            "Configure an HTTPS BFF origin or explicit loopback development origin"
        )
    # Origin headers serialize lowercase hosts, compressed IPv6 and no default
    # port. Comparing them with the raw environment string rejects valid callers.
    # Keep a deliberately narrow ASCII authority syntax: Python and browsers
    # disagree about percent-encoded hosts and legacy numeric IPv4 spellings.
    if "%" in host or not host.strip("."):
        raise ValueError("Configure a literal ASCII host without percent encoding")
    if ":" in host:
        host = f"[{host}]"
    else:
        if any(
            character not in "abcdefghijklmnopqrstuvwxyz0123456789._-"
            for character in host
        ):
            raise ValueError("Configure an ASCII DNS host or IP address")
        last_label = host.rstrip(".").rsplit(".", 1)[-1]
        hex_label = last_label.startswith("0x") and all(
            character in "0123456789abcdef" for character in last_label[2:]
        )
        if last_label.isdigit() or hex_label:
            if str(IPv4Address(host)) != host:
                raise ValueError("Configure canonical dotted-decimal IPv4")
    # Accessing port validates malformed or out-of-range values during startup.
    port = parts.port
    default_port = 443 if parts.scheme == "https" else 80
    suffix = f":{port}" if port is not None and port != default_port else ""
    return f"{parts.scheme}://{host}{suffix}"


class BFFTransport:
    def __init__(
        self,
        origin: str,
        *,
        allow_loopback_http: bool = False,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        self.origin = trusted_origin(origin, allow_loopback_http=allow_loopback_http)
        self.transport = transport

    def get(self, path: str, *, cookie: str, maximum: int, media_type: str) -> bytes:
        if not path.startswith("/api/") or "?" in path or "#" in path or "\\" in path:
            raise GatewayUnavailableError
        if (
            not cookie
            or len(cookie) > 8192
            or any(ord(char) < 32 or ord(char) >= 127 for char in cookie)
        ):
            raise AuthenticationRequiredError
        try:
            # A fresh client prevents cookie-jar state leaking across owners. No
            # ambient proxies, default auth or redirect-based cookie forwarding.
            with httpx.Client(
                timeout=5,
                follow_redirects=False,
                trust_env=False,
                transport=self.transport,
            ) as client:
                with client.stream(
                    "GET",
                    self.origin + path,
                    headers={"cookie": cookie, "accept": media_type},
                ) as response:
                    if response.status_code in (401, 403):
                        raise AuthenticationRequiredError
                    if (
                        response.status_code != 200
                        or response.headers.get("content-type", "")
                        .split(";")[0]
                        .strip()
                        != media_type
                    ):
                        raise GatewayUnavailableError
                    output = bytearray()
                    for block in response.iter_bytes(chunk_size=65536):
                        if len(output) + len(block) > maximum:
                            raise GatewayUnavailableError
                        output.extend(block)
                    return bytes(output)
        except httpx.HTTPError:
            raise GatewayUnavailableError from None


class SessionVerifier:
    def __init__(
        self,
        gateway: BFFTransport,
        *,
        allow_development: bool = False,
        clock: Callable[[], datetime] = lambda: datetime.now(UTC),
    ) -> None:
        self.gateway = gateway
        self.allow_development = allow_development
        self.clock = clock

    def verify(self, cookie: str) -> Principal:
        try:
            payload = self.gateway.get(
                "/api/session",
                cookie=cookie,
                maximum=4096,
                media_type="application/json",
            )
            identity = SESSION_VERIFIER_ADAPTER.validate_json(payload)["identity"]
            if identity is None or (
                identity["mode"] == "development" and not self.allow_development
            ):
                raise AuthenticationRequiredError
            expiry = identity.get("expiresAt")
            if expiry is not None and datetime.fromisoformat(expiry) <= self.clock():
                raise AuthenticationRequiredError
            return Principal(identity["ownerId"])
        except (ValidationError, GatewayUnavailableError):
            raise AuthenticationRequiredError from None


class HTTPRecordingStorage:
    """Session-bound snapshots. No promise of atomic external derived writes."""

    def __init__(
        self, gateway: BFFTransport, principal: Principal, cookie: str
    ) -> None:
        self.gateway = gateway
        self.principal = principal
        self.cookie = cookie

    def _permit(
        self, principal: Principal, recording: RecordingRef
    ) -> AudioRecordingPermit:
        if principal != self.principal:
            raise RecordingAccessError
        try:
            payload = self.gateway.get(
                f"/api/recordings/{recording.id}/analysis-permit",
                cookie=self.cookie,
                maximum=4096,
                media_type="application/json",
            )
            permit = AudioRecordingPermit.model_validate_json(payload)
            if permit.recording != recording:
                raise RecordingAccessError
            return permit
        except (AuthenticationRequiredError, GatewayUnavailableError, ValidationError):
            raise RecordingAccessError from None

    def assert_current(self, principal: Principal, recording: RecordingRef) -> None:
        self._permit(principal, recording)

    def read(self, principal: Principal, recording: RecordingRef) -> RecordingBytes:
        permit = self._permit(principal, recording)
        try:
            data = self.gateway.get(
                f"/api/recordings/{recording.id}/audio",
                cookie=self.cookie,
                maximum=MAX_BYTES,
                media_type="audio/wav",
            )
        except (AuthenticationRequiredError, GatewayUnavailableError):
            raise RecordingAccessError from None
        self._permit(principal, recording)
        return RecordingBytes(data, synthetic_fixture=permit.syntheticFixture)
