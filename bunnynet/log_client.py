"""Wrapper around the bunny.net storage zone APIs."""

import datetime
import logging
from typing import Iterator

from bunnynet.exceptions import BunnyException
from bunnynet.hashing import sha256 as SHA256
from bunnynet.httpclient import HttpClient
from bunnynet.models import StorageObject, StorageZone
from bunnynet.storage_endpoints import StorageEndpoint


class LogClient:
    """Wrapper class around the bunny.net log APIs."""

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
        self.log = log.getChild("logs")

    def get(
        self,
        *,
        pull_zone_id: int,
        date: datetime.date,
        status_codes: list[int],
        start_index: int = 0,
        end_index: int = 250,
    ) -> str:
        """Get a zone by its identifier.

        :param pull_zone_id: The identifier of the pull zone to get the logs for
        :param date: The date to get the logs for
        :param status_codes: Only get the logs matching these status codes

        :returns: The logs for the given date
        """

        status_codes_string = ",".join(map(str, status_codes))
        endpoint = (
            str(date.month).zfill(2)
            + "-"
            + str(date.day).zfill(2)
            + "-"
            + str(date.year % 100).zfill(2)
            + "/"
            + str(pull_zone_id)
            + ".log?download=false&status="
            + status_codes_string
            + "&search=&start="
            + str(start_index)
            + "&end="
            + str(end_index)
        )

        return self.http_client.get_raw(endpoint, domain="logging.bunnycdn.com")
