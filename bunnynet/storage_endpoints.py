"""Storage endpoints."""

import enum

from .exceptions import BunnyException


class StorageEndpoint(enum.Enum):
    """Represents the storage endpoint which may be used."""

    FALKENSTEIN = "storage.bunnycdn.com"
    NEW_YORK = "ny.storage.bunnycdn.com"
    LOS_ANGELES = "la.storage.bunnycdn.com"
    SINGAPORE = "sg.storage.bunnycdn.com"
    SYDNEY = "syd.storage.bunnycdn.com"

    @staticmethod
    def from_name(name: str) -> "StorageEndpoint":
        """Convert a region code to a StorageEndpoint.

        :param name: The region code/name

        :raises BunnyException: If the name doesn't match anything known.

        :returns: A storage endpoint
        """
        match name:
            case "DE":
                return StorageEndpoint.FALKENSTEIN
            case "NY":
                return StorageEndpoint.NEW_YORK
            case "LA":
                return StorageEndpoint.LOS_ANGELES
            case "SG":
                return StorageEndpoint.SINGAPORE
            case "SYD":
                return StorageEndpoint.SYDNEY

        raise BunnyException(f"Unknown storage endpoint: '{name}'")
