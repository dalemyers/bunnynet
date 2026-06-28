"""Offline unit tests that do not require a live bunny.net token."""

# pylint: disable=missing-param-doc

import base64
import datetime
import hashlib
import logging

import pytest
import requests

import bunnynet
from bunnynet.exceptions import (
    BunnyException,
    BunnyHTTPBadRequestException,
    BunnyHTTPConflictException,
    BunnyHTTPException,
    BunnyHTTPForbiddenException,
    BunnyHTTPInternalServerErrorException,
    BunnyHTTPNotFoundException,
    BunnyHTTPUnauthorizedException,
)
from bunnynet.hashing import sha256
from bunnynet.log_client import LogClient
from bunnynet.storage_endpoints import StorageEndpoint


def test_sha256_is_uppercase_hex() -> None:
    """The hashing helper returns an upper-case hex digest."""
    digest = sha256(b"Hello World")
    assert digest == hashlib.sha256(b"Hello World").hexdigest().upper()
    assert digest == digest.upper()


@pytest.mark.parametrize(
    "code,endpoint",
    [
        ("DE", StorageEndpoint.FALKENSTEIN),
        ("UK", StorageEndpoint.LONDON),
        ("NY", StorageEndpoint.NEW_YORK),
        ("LA", StorageEndpoint.LOS_ANGELES),
        ("SG", StorageEndpoint.SINGAPORE),
        ("SYD", StorageEndpoint.SYDNEY),
        ("BR", StorageEndpoint.SAO_PAULO),
        ("JH", StorageEndpoint.JOHANNESBURG),
        ("SE", StorageEndpoint.STOCKHOLM),
    ],
)
def test_storage_endpoint_from_name(code: str, endpoint: StorageEndpoint) -> None:
    """Known region codes map to the expected endpoint."""
    assert StorageEndpoint.from_name(code) is endpoint


def test_storage_endpoint_from_name_unknown() -> None:
    """An unknown region code raises a BunnyException."""
    with pytest.raises(BunnyException):
        StorageEndpoint.from_name("ZZ")


@pytest.mark.parametrize(
    "status,exception_type",
    [
        (400, BunnyHTTPBadRequestException),
        (401, BunnyHTTPUnauthorizedException),
        (403, BunnyHTTPForbiddenException),
        (404, BunnyHTTPNotFoundException),
        (409, BunnyHTTPConflictException),
        (500, BunnyHTTPInternalServerErrorException),
        (418, BunnyHTTPException),
    ],
)
def test_exception_mapping(status: int, exception_type: type) -> None:
    """Status codes map to the matching exception subclass."""
    response = requests.Response()
    response.status_code = status

    exception = BunnyHTTPException.generate_from_response(response, "boom")

    assert type(exception) is exception_type  # pylint: disable=unidiomatic-typecheck
    assert exception.response is response


class _FakeHttpClient:
    """Records the arguments passed to get_raw so endpoint building can be checked."""

    def __init__(self) -> None:
        self.calls: list[dict] = []

    def get_raw(self, endpoint: str, **kwargs) -> bytes:
        """Record the call and return canned log contents.

        :param endpoint: The endpoint that was requested
        :param kwargs: Any other keyword arguments forwarded by the client

        :returns: Canned log file contents
        """
        self.calls.append({"endpoint": endpoint, **kwargs})
        return b"log-contents"


def test_log_client_builds_expected_endpoint() -> None:
    """The log endpoint encodes the date as MM-DD-YY and forwards the parameters."""
    fake = _FakeHttpClient()
    client = LogClient(http_client=fake, log=logging.getLogger("test"))  # type: ignore[arg-type]

    result = client.get(
        pull_zone_id=1330830,
        date=datetime.date(year=2023, month=4, day=15),
        status_codes=[200, 404],
        start_index=0,
        end_index=250,
    )

    assert result == "log-contents"
    assert fake.calls == [
        {
            "endpoint": "04-15-23/1330830.log?download=false&status=200,404&search=&start=0&end=250",
            "domain": "logging.bunnycdn.com",
        }
    ]


def _reference_token(key: str, signature_path: str, expires: int, parameters: dict[str, str]) -> str:
    """Independently re-implement the bunny.net token algorithm to pin behaviour."""
    parameter_data = "&".join(f"{name}={parameters[name]}" for name in sorted(parameters))
    hashable_base = key + signature_path + str(expires) + parameter_data
    raw = base64.b64encode(hashlib.sha256(hashable_base.encode()).digest()).decode()
    return raw.replace("\n", "").replace("+", "-").replace("/", "_").replace("=", "")


def _client() -> bunnynet.BunnyClient:
    return bunnynet.BunnyClient("unused-token")


def test_generate_url_signature_basic() -> None:
    """A simple URL produces a url-safe token and the expected expiry."""
    expiration = datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc)
    expires = int(expiration.timestamp())

    signature = _client().generate_url_signature(
        "http://test.b-cdn.net/foo/bar/file.png",
        key="secret",
        expiration=expiration,
    )

    assert signature["expires"] == expires
    token = signature["token"]
    for forbidden in ("+", "/", "=", "\n"):
        assert forbidden not in token
    assert token == _reference_token("secret", "/foo/bar/file.png", expires, {})


def test_generate_url_signature_includes_token_path() -> None:
    """When a path is supplied it is signed and surfaced as token_path."""
    expiration = datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc)
    expires = int(expiration.timestamp())

    signature = _client().generate_url_signature(
        "http://test.b-cdn.net/foo/bar/file.png",
        path="/foo/bar",
        key="secret",
        expiration=expiration,
    )

    assert signature["token_path"] == "/foo/bar"
    assert signature["token"] == _reference_token("secret", "/foo/bar", expires, {"token_path": "/foo/bar"})


def test_generate_url_signature_is_order_independent() -> None:
    """Existing query parameters are sorted, so their order must not change the token."""
    expiration = datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc)
    client = _client()

    first = client.generate_url_signature(
        "http://test.b-cdn.net/file.png?a=1&b=2",
        key="secret",
        expiration=expiration,
    )
    second = client.generate_url_signature(
        "http://test.b-cdn.net/file.png?b=2&a=1",
        key="secret",
        expiration=expiration,
    )

    assert first["token"] == second["token"]


def test_generate_url_signature_with_countries() -> None:
    """Country restrictions are folded into the signed parameters."""
    expiration = datetime.datetime(2030, 1, 1, tzinfo=datetime.timezone.utc)
    expires = int(expiration.timestamp())

    signature = _client().generate_url_signature(
        "http://test.b-cdn.net/file.png",
        key="secret",
        expiration=expiration,
        token_countries=["US", "GB"],
        token_countries_blocked=["CN"],
    )

    expected = _reference_token(
        "secret",
        "/file.png",
        expires,
        {"token_countries": "US,GB", "token_countries_blocked": "CN"},
    )
    assert signature["token"] == expected
    assert signature["token_countries"] == "US,GB"
    assert signature["token_countries_blocked"] == "CN"
