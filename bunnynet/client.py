"""Wrapper around the bunny.net APIs."""

import base64
import datetime
import hashlib
import logging
import urllib.parse
from typing import Any

from bunnynet.httpclient import HttpClient
from bunnynet.log_client import LogClient
from bunnynet.pull_zone_client import PullZoneClient
from bunnynet.storage_zone_client import StorageZoneClient


class BunnyClient:
    """Wrapper class around the bunny.net API."""

    log: logging.Logger
    _http_client: HttpClient

    pull_zones: PullZoneClient
    storage_zones: StorageZoneClient
    logs: LogClient

    def __init__(
        self,
        token: str,
        *,
        log: logging.Logger | None = None,
    ) -> None:
        """Construct a new client object.

        :param token: The API token to use.
        :param log: Any base logger to be used (one will be created if not supplied)
        """

        if log is not None:
            self.log = log.getChild("bunnynet")
        else:
            self.log = logging.getLogger("bunnynet")

        self._http_client = HttpClient(token, log=self.log)

        self.pull_zones = PullZoneClient(http_client=self._http_client, log=self.log)
        self.storage_zones = StorageZoneClient(
            http_client=self._http_client,
            log=self.log,
        )
        self.logs = LogClient(http_client=self._http_client, log=self.log)

    @staticmethod
    def get_storage_zone_client(token: str, log: logging.Logger) -> StorageZoneClient:
        """Get a storage zone client directly.

        :param token: The API token for auth
        :param log: The logger to use for debugging

        :returns: A new storage zone client.
        """

        if log is not None:
            log = log.getChild("bunnynet")
        else:
            log = logging.getLogger("bunnynet")

        http_client = HttpClient(token, log=log)

        return StorageZoneClient(http_client=http_client, log=log)

    def generate_url_signature(
        self,
        url: str,
        *,
        path: str | None = None,
        key: str,
        expiration: datetime.datetime,
        token_countries: list[str] | None = None,
        token_countries_blocked: list[str] | None = None,
    ) -> dict[str, Any]:
        """Generate a URL signature parameters so that it has a token which can be used to authenticate it.

        If you pass in a folder with the corresponding path, it will give access
        to that entire folder.

        :param url: The URL to sign. e.g. http://test.b-cdn.net/foo/bar/file.png
        :param path: The path to give access to with this token. e.g. "/foo/bar"
                     If not specified, the token will be valid for the URL only.
        :param key: The signing key for generating signatures
        :param expiration: The datetime that the token should expire
        :param token_countries: If specified, the token is only valid in these countries
        :param token_countries_blocked: If specified, the token will not be valid in these countries.

        :returns: The signature data which can be added to a URL later
        """
        parsed_url = urllib.parse.urlparse(url)
        parameters: dict[str, Any] = urllib.parse.parse_qs(parsed_url.query)

        if path:
            signature_path = path
            parameters["token_path"] = path
        else:
            signature_path = parsed_url.path

        if token_countries:
            parameters["token_countries"] = ",".join(token_countries)

        if token_countries_blocked:
            parameters["token_countries_blocked"] = ",".join(token_countries_blocked)

        parameter_data = "&".join([name + "=" + "".join(value) for name, value in parameters.items()])

        hashable_base = key + signature_path + str(int(expiration.timestamp())) + parameter_data
        token_bytes = base64.b64encode(hashlib.sha256(str.encode(hashable_base)).digest())
        token = token_bytes.decode().replace("\n", "").replace("+", "-").replace("/", "_").replace("=", "")

        result = {"token": token, "expires": int(expiration.timestamp())}

        for name, value in parameters.items():
            result[name] = value

        return result

    def sign_url(
        self,
        url: str,
        *,
        path: str | None = None,
        key: str,
        expiration: datetime.datetime,
        token_countries: list[str] | None = None,
        token_countries_blocked: list[str] | None = None,
    ) -> str:
        """Sign a URL so that it has a token which can be used to authenticate it.

        If you pass in a folder with the corresponding path, it will give access
        to that entire folder.

        :param url: The URL to sign. e.g. http://test.b-cdn.net/foo/bar/file.png
        :param path: The path to give access to with this token. e.g. "/foo/bar"
                     If not specified, the token will be valid for the URL only.
        :param key: The signing key for generating signatures
        :param expiration: The datetime that the token should expire
        :param token_countries: If specified, the token is only valid in these countries
        :param token_countries_blocked: If specified, the token will not be valid in these countries.

        :returns: The full URL with the signature added
        """

        parsed_url = urllib.parse.urlparse(url)

        signature = self.generate_url_signature(
            url,
            path=path,
            key=key,
            expiration=expiration,
            token_countries=token_countries,
            token_countries_blocked=token_countries_blocked,
        )

        return parsed_url.scheme + "://" + parsed_url.netloc + parsed_url.path + "?" + urllib.parse.urlencode(signature)
