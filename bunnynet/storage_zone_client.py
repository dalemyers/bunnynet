"""Wrapper around the bunny.net storage zone APIs."""

import logging
from typing import Iterator

from bunnynet.exceptions import BunnyException
from bunnynet.hashing import sha256 as SHA256
from bunnynet.httpclient import HttpClient
from bunnynet.models import StorageObject, StorageZone
from bunnynet.storage_endpoints import StorageEndpoint


class StorageZoneClient:
    """Wrapper class around the bunny.net storage APIs."""

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
        self.log = log.getChild("storagezone")

    def get_all(self, *, include_deleted: bool = False) -> Iterator[StorageZone]:
        """Get all storage zones.

        :param include_deleted: Set to true to include deleted storage zones in the query.
        """

        parameters = {}

        if include_deleted:
            parameters["includeDeleted"] = True

        yield from self.http_client.get_list("storagezone", StorageZone, parameters=parameters)

    def get(self, identifier: int) -> StorageZone | None:
        """Get a zone by its identifier.

        :param identifier: The identifier of the zone to get

        :returns: The zone if found, None otherwise.
        """
        return self.http_client.get(f"storagezone/{identifier}", StorageZone)

    def get_by_name(self, name: str) -> StorageZone | None:
        """Get a zone by its name.

        :param name: The name of the zone to get

        :returns: The zone if found, None otherwise.
        """
        for zone in self.get_all():
            if zone.name == name:
                return zone
        return None

    def _resolve_storage_zone(
        self, *, storage_zone_name: str | None = None, storage_zone: StorageZone | None = None
    ) -> StorageZone:
        if storage_zone is not None:
            return storage_zone

        if storage_zone_name is None:
            raise BunnyException(
                "The `storage_zone` and `storage_zone_name` were both None. At least one must be provided."
            )

        storage_zone = self.get_by_name(storage_zone_name)

        if storage_zone is None:
            raise BunnyException(f"Failed to find storage zone named '{storage_zone_name}'")

        return storage_zone

    def list_files(
        self, *, storage_zone_name: str | None = None, storage_zone: StorageZone | None = None, path: str
    ) -> Iterator[StorageObject]:
        """List the files in a storage zone under the given path.

        Either the storage zone or the storage zone name must be provided. The
        former will be used in the case where both are provided.

        :param storage_zone_name: The name of the storage zone to list
        :param storage_zone: The storage zone to liust
        :param path: The path to list under

        :raises BunnyException: If the storage zone is not found, or both storage zone and storage zone name are None.
        """

        storage_zone = self._resolve_storage_zone(storage_zone_name=storage_zone_name, storage_zone=storage_zone)

        yield from self.http_client.get_list(
            endpoint=f"{storage_zone.name}/{path}/",
            response_type=StorageObject,
            domain=StorageEndpoint.from_name(storage_zone.region or "").value,
            access_key=storage_zone.password,
        )

    def upload_file(
        self,
        *,
        storage_zone_name: str | None = None,
        storage_zone: StorageZone | None = None,
        contents: bytes,
        path: str,
        file_name: str,
        sha256: str | None = None,
    ) -> None:
        """Upload a file.

        Either the storage zone or the storage zone name must be provided. The
        former will be used in the case where both are provided.

        :param storage_zone_name: The name of the storage zone to list
        :param storage_zone: The storage zone to liust
        :param contents: The contents of the file
        :param path: The path of the file
        :param file_name: The name of the file
        :param sha256: An optional SHA256 checksum for the API to validate against
        """

        storage_zone = self._resolve_storage_zone(storage_zone_name=storage_zone_name, storage_zone=storage_zone)

        additional_headers = {}

        if sha256:
            additional_headers["Checksum"] = sha256.upper()

        self.http_client.put(
            endpoint=f"{storage_zone.name}/{path}/{file_name}",
            response_type=object,
            body=contents,
            additional_headers=additional_headers,
            domain=StorageEndpoint.from_name(storage_zone.region or "").value,
            access_key=storage_zone.password,
        )

    def upload_text_file(
        self,
        *,
        storage_zone_name: str | None = None,
        storage_zone: StorageZone | None = None,
        contents: str,
        path: str,
        file_name: str,
    ) -> None:
        """Upload a text file.

        Either the storage zone or the storage zone name must be provided. The
        former will be used in the case where both are provided.

        :param storage_zone_name: The name of the storage zone to list
        :param storage_zone: The storage zone to liust
        :param contents: The contents of the text file
        :param path: The path of the file
        :param file_name: The name of the file
        """

        raw_contents = contents.encode("utf-8")

        self.upload_file(
            storage_zone_name=storage_zone_name,
            storage_zone=storage_zone,
            contents=raw_contents,
            path=path,
            file_name=file_name,
            sha256=SHA256(raw_contents),
        )

    def delete_file(
        self,
        *,
        storage_zone_name: str | None = None,
        storage_zone: StorageZone | None = None,
        path: str,
        file_name: str,
    ) -> None:
        """Delete a file.

        Either the storage zone or the storage zone name must be provided. The
        former will be used in the case where both are provided.

        :param storage_zone_name: The name of the storage zone to list
        :param storage_zone: The storage zone to list
        :param path: The path of the file
        :param file_name: The name of the file
        """

        storage_zone = self._resolve_storage_zone(storage_zone_name=storage_zone_name, storage_zone=storage_zone)

        self.http_client.delete(
            endpoint=f"{storage_zone.name}/{path}/{file_name}",
            response_type=object,
            domain=StorageEndpoint.from_name(storage_zone.region or "").value,
            access_key=storage_zone.password,
        )
