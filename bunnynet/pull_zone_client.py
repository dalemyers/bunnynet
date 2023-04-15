"""Wrapper around the bunny.net pull zone APIs."""

import logging
from typing import Iterator

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
            parameters["includeCertificate"] = True

        yield from self.http_client.get_list("pullzone", PullZone)

    def get(self, identifier: int) -> PullZone | None:
        """Get a zone by its identifier.

        :param identifier: The identifier of the zone to get

        :returns: The zone if found, None otherwise.
        """
        return self.http_client.get(f"pullzone/{identifier}", PullZone)

    def get_by_name(self, name: str) -> PullZone | None:
        """Get a zone by its name.

        :param name: The name of the zone to get

        :returns: The zone if found, None otherwise.
        """
        for zone in self.get_all():
            if zone.name == name:
                return zone
        return None
