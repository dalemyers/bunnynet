"""Storage endpoints."""

import enum

from .exceptions import BunnyException

# Maps the region code returned by the bunny.net API (StorageZone.region) to the
# storage hostname that serves that region.
_REGION_CODE_TO_ENDPOINT: "dict[str, StorageEndpoint]"


class StorageEndpoint(enum.Enum):
    """Represents the storage endpoint which may be used."""

    FALKENSTEIN = "storage.bunnycdn.com"
    LONDON = "uk.storage.bunnycdn.com"
    NEW_YORK = "ny.storage.bunnycdn.com"
    LOS_ANGELES = "la.storage.bunnycdn.com"
    SINGAPORE = "sg.storage.bunnycdn.com"
    SYDNEY = "syd.storage.bunnycdn.com"
    SAO_PAULO = "br.storage.bunnycdn.com"
    JOHANNESBURG = "jh.storage.bunnycdn.com"
    STOCKHOLM = "se.storage.bunnycdn.com"

    @staticmethod
    def from_name(name: str) -> "StorageEndpoint":
        """Convert a region code to a StorageEndpoint.

        :param name: The region code/name

        :raises BunnyException: If the name doesn't match anything known.

        :returns: A storage endpoint
        """
        endpoint = _REGION_CODE_TO_ENDPOINT.get(name)

        if endpoint is None:
            raise BunnyException(f"Unknown storage endpoint: '{name}'")

        return endpoint


_REGION_CODE_TO_ENDPOINT = {
    "DE": StorageEndpoint.FALKENSTEIN,
    "UK": StorageEndpoint.LONDON,
    "NY": StorageEndpoint.NEW_YORK,
    "LA": StorageEndpoint.LOS_ANGELES,
    "SG": StorageEndpoint.SINGAPORE,
    "SYD": StorageEndpoint.SYDNEY,
    "BR": StorageEndpoint.SAO_PAULO,
    "JH": StorageEndpoint.JOHANNESBURG,
    "SE": StorageEndpoint.STOCKHOLM,
}
