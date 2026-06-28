"""Wrapper around the bunny.net pull zone APIs."""

import logging
import urllib.parse
from typing import Any, Iterator

from bunnynet.exceptions import BunnyHTTPNotFoundException
from bunnynet.httpclient import HttpClient
from bunnynet.models import PullZone


class PullZoneClient:
    """Wrapper class around the bunny.net pull zone APIs."""

    log: logging.Logger
    http_client: HttpClient

    def __init__(
        self,
        *,
        http_client: HttpClient,
        log: logging.Logger,
    ) -> None:
        """Construct a new client object.

        :param http_client: The API HTTP client
        :param log: Any base logger to be used (one will be created if not supplied)
        """

        self.http_client = http_client
        self.log = log.getChild("pullzone")

    def get_all(self, *, include_certificate: bool = False) -> Iterator[PullZone]:
        """Get all storage zones.

        :param include_certificate: Set to true if the result hostnames should contain the SSL certificate.
        """

        parameters = {}

        if include_certificate:
            parameters["includeCertificate"] = "true"

        yield from self.http_client.get_list("pullzone", PullZone, parameters=parameters)

    def get(self, identifier: int) -> PullZone | None:
        """Get a zone by its identifier.

        :param identifier: The identifier of the zone to get

        :returns: The zone if found, None otherwise.
        """
        try:
            return self.http_client.get(f"pullzone/{identifier}", PullZone)
        except BunnyHTTPNotFoundException:
            return None

    def get_by_name(self, name: str) -> PullZone | None:
        """Get a zone by its name.

        :param name: The name of the zone to get

        :returns: The zone if found, None otherwise.
        """
        for zone in self.get_all():
            if zone.name == name:
                return zone
        return None

    def create(self, *, name: str, origin_url: str, zone_type: int = 0) -> PullZone:
        """Create a new pull zone.

        :param name: The name of the pull zone to create
        :param origin_url: The origin URL that the pull zone fetches files from
        :param zone_type: The pull zone tier (0 = standard/premium network, 1 = volume network)

        :returns: The newly created pull zone
        """
        body: dict[str, Any] = {"Name": name, "OriginUrl": origin_url, "Type": zone_type}
        return self.http_client.post("pullzone", PullZone, body)

    def update(self, identifier: int, settings: dict[str, Any]) -> PullZone:
        """Update the settings on a pull zone.

        :param identifier: The identifier of the pull zone to update
        :param settings: The settings to apply, using bunny.net's PascalCase keys
                         (e.g. ``{"IgnoreQueryStrings": False}``)

        :returns: The updated pull zone
        """
        return self.http_client.post(f"pullzone/{identifier}", PullZone, settings)

    def add_hostname(self, identifier: int, hostname: str) -> None:
        """Attach a custom hostname to a pull zone.

        :param identifier: The identifier of the pull zone
        :param hostname: The custom hostname to attach
        """
        self.http_client.post(f"pullzone/{identifier}/addHostname", object, {"Hostname": hostname})

    def remove_hostname(self, identifier: int, hostname: str) -> None:
        """Remove a custom hostname from a pull zone.

        :param identifier: The identifier of the pull zone
        :param hostname: The custom hostname to remove
        """
        self.http_client.delete(
            f"pullzone/{identifier}/removeHostname",
            object,
            body={"Hostname": hostname},
            additional_headers={"Content-Type": "application/json"},
        )

    def load_free_certificate(self, hostname: str) -> None:
        """Provision a free Let's Encrypt certificate for an attached hostname.

        The hostname's CNAME (``hostname -> <pullzone>.b-cdn.net``) must resolve
        before calling this: bunny.net validates ownership over HTTP-01 using
        that CNAME.

        :param hostname: The hostname to issue the certificate for
        """
        self.http_client.get_raw("pullzone/loadFreeCertificate?hostname=" + urllib.parse.quote(hostname))

    def set_force_ssl(self, identifier: int, hostname: str, *, force: bool = True) -> None:
        """Force HTTP requests to redirect to HTTPS for a hostname.

        :param identifier: The identifier of the pull zone
        :param hostname: The hostname to configure
        :param force: Set to false to disable the HTTP to HTTPS redirect
        """
        self.http_client.post(
            f"pullzone/{identifier}/setForceSSL",
            object,
            {"Hostname": hostname, "ForceSSL": force},
        )
