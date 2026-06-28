"""Offline unit tests for the POST transport and pull-zone write methods."""

# pylint: disable=missing-param-doc

import logging
from unittest import mock

import pytest

import bunnynet
from bunnynet.exceptions import BunnyHTTPException
from bunnynet.httpclient import HttpClient
from bunnynet.models import PullZone
from bunnynet.pull_zone_client import PullZoneClient


def _response(*, ok: bool = True, status_code: int = 200, content: bytes = b"", json_value=None):
    """Build a fake requests.Response-like object for mocking."""
    response = mock.Mock()
    response.ok = ok
    response.status_code = status_code
    response.content = content
    response.json.return_value = json_value
    return response


def _http_client() -> HttpClient:
    return HttpClient("the-token", log=logging.getLogger("test"))


def test_post_sends_json_body_and_headers() -> None:
    """post JSON-encodes the body and sends the JSON content type."""
    client = _http_client()

    with mock.patch("bunnynet.httpclient.requests") as requests_mock:
        requests_mock.post.return_value = _response(content=b"")

        result = client.post("pullzone", object, {"Name": "zone", "Type": 0})

    assert result is None
    requests_mock.post.assert_called_once()
    _, kwargs = requests_mock.post.call_args
    assert kwargs["json"] == {"Name": "zone", "Type": 0}
    assert kwargs["headers"]["Content-Type"] == "application/json"
    assert kwargs["headers"]["AccessKey"] == "the-token"


def test_post_uses_access_key_override() -> None:
    """An explicit access key overrides the default token."""
    client = _http_client()

    with mock.patch("bunnynet.httpclient.requests") as requests_mock:
        requests_mock.post.return_value = _response(content=b"")

        client.post("pullzone", object, {"Name": "zone"}, access_key="other-key")

    _, kwargs = requests_mock.post.call_args
    assert kwargs["headers"]["AccessKey"] == "other-key"


def test_post_retries_post_on_5xx() -> None:
    """A 5xx response retries the POST (not a GET) with the same body."""
    client = _http_client()

    with mock.patch("bunnynet.httpclient.requests") as requests_mock:
        requests_mock.post.side_effect = [
            _response(ok=False, status_code=500),
            _response(content=b""),
        ]

        client.post("pullzone", object, {"Name": "zone"})

    assert requests_mock.post.call_count == 2
    requests_mock.get.assert_not_called()


def test_post_raises_after_exhausting_attempts() -> None:
    """When retries run out the original exception is raised."""
    client = _http_client()

    with mock.patch("bunnynet.httpclient.requests") as requests_mock:
        requests_mock.post.return_value = _response(ok=False, status_code=500)

        with pytest.raises(BunnyHTTPException):
            client.post("pullzone", object, {"Name": "zone"}, attempts=2)

    assert requests_mock.post.call_count == 2


def test_delete_sends_body() -> None:
    """delete forwards an optional JSON body."""
    client = _http_client()

    with mock.patch("bunnynet.httpclient.requests") as requests_mock:
        requests_mock.delete.return_value = _response(content=b"")

        client.delete("pullzone/5/removeHostname", object, body={"Hostname": "cdn.example.com"})

    _, kwargs = requests_mock.delete.call_args
    assert kwargs["json"] == {"Hostname": "cdn.example.com"}


def test_extract_data_tolerates_empty_body() -> None:
    """An empty (e.g. 204) body does not blow up and returns None."""
    client = _http_client()
    response = _response(content=b"")

    assert client.extract_data(response) is None
    response.json.assert_not_called()


def test_default_timeout_is_used() -> None:
    """Requests use the client's default timeout when none is configured."""
    client = _http_client()

    with mock.patch("bunnynet.httpclient.requests") as requests_mock:
        requests_mock.get.return_value = _response(content=b"data")

        client.get_raw("purge")

    _, kwargs = requests_mock.get.call_args
    assert kwargs["timeout"] == 10


def test_configured_timeout_is_used() -> None:
    """A timeout configured on the client is applied to requests."""
    client = HttpClient("the-token", log=logging.getLogger("test"), timeout=42)

    with mock.patch("bunnynet.httpclient.requests") as requests_mock:
        requests_mock.post.return_value = _response(content=b"")

        client.post("pullzone", object, {"Name": "zone"})

    _, kwargs = requests_mock.post.call_args
    assert kwargs["timeout"] == 42


def test_get_raw_timeout_override() -> None:
    """A per-call timeout overrides the client default on get_raw."""
    client = HttpClient("the-token", log=logging.getLogger("test"), timeout=10)

    with mock.patch("bunnynet.httpclient.requests") as requests_mock:
        requests_mock.get.return_value = _response(content=b"data")

        client.get_raw("pullzone/loadFreeCertificate?hostname=cdn.example.com", timeout=60)

    _, kwargs = requests_mock.get.call_args
    assert kwargs["timeout"] == 60


def test_bunny_client_timeout_propagates() -> None:
    """BunnyClient forwards its timeout to the underlying HTTP client."""
    bunny = bunnynet.BunnyClient("token", timeout=25)

    assert bunny._http_client.timeout == 25  # pylint: disable=protected-access


def _pull_zone_client() -> tuple[PullZoneClient, mock.Mock]:
    http_client = mock.Mock()
    client = PullZoneClient(http_client=http_client, log=logging.getLogger("test"))
    return client, http_client


def test_create_posts_expected_body() -> None:
    """create sends the bunny.net PascalCase fields."""
    client, http_client = _pull_zone_client()

    client.create(name="my-zone", origin_url="https://origin.example.com")

    http_client.post.assert_called_once_with(
        "pullzone",
        PullZone,
        {"Name": "my-zone", "OriginUrl": "https://origin.example.com", "Type": 0},
    )


def test_update_posts_settings_to_zone_endpoint() -> None:
    """update posts the settings dict to the zone endpoint."""
    client, http_client = _pull_zone_client()

    client.update(42, {"IgnoreQueryStrings": False})

    http_client.post.assert_called_once_with("pullzone/42", PullZone, {"IgnoreQueryStrings": False})


def test_add_hostname_posts_hostname() -> None:
    """add_hostname posts to the addHostname endpoint."""
    client, http_client = _pull_zone_client()

    client.add_hostname(42, "cdn.example.com")

    http_client.post.assert_called_once_with("pullzone/42/addHostname", object, {"Hostname": "cdn.example.com"})


def test_remove_hostname_deletes_with_body() -> None:
    """remove_hostname deletes with a JSON body and content type."""
    client, http_client = _pull_zone_client()

    client.remove_hostname(42, "cdn.example.com")

    http_client.delete.assert_called_once_with(
        "pullzone/42/removeHostname",
        object,
        body={"Hostname": "cdn.example.com"},
        additional_headers={"Content-Type": "application/json"},
    )


def test_load_free_certificate_builds_endpoint() -> None:
    """load_free_certificate URL-encodes the hostname and uses a longer timeout."""
    client, http_client = _pull_zone_client()

    client.load_free_certificate("cdn.example.com")

    http_client.get_raw.assert_called_once_with("pullzone/loadFreeCertificate?hostname=cdn.example.com", timeout=60)


def test_load_free_certificate_timeout_override() -> None:
    """The certificate timeout can be overridden by the caller."""
    client, http_client = _pull_zone_client()

    client.load_free_certificate("cdn.example.com", timeout=120)

    http_client.get_raw.assert_called_once_with("pullzone/loadFreeCertificate?hostname=cdn.example.com", timeout=120)


def test_set_force_ssl_posts_expected_body() -> None:
    """set_force_ssl posts the hostname and force flag."""
    client, http_client = _pull_zone_client()

    client.set_force_ssl(42, "cdn.example.com")

    http_client.post.assert_called_once_with(
        "pullzone/42/setForceSSL",
        object,
        {"Hostname": "cdn.example.com", "ForceSSL": True},
    )


def test_get_pull_zone_client_shares_http_client() -> None:
    """BunnyClient.get_pull_zone_client reuses the same HTTP client."""
    bunny = bunnynet.BunnyClient("token")

    pz_client = bunny.get_pull_zone_client()

    assert isinstance(pz_client, PullZoneClient)
    assert pz_client.http_client is bunny._http_client  # pylint: disable=protected-access
