import datetime

import deserialize

from .pull_zone import PullZone


@deserialize.key("identifier", "id")
@deserialize.parser("date_modified", datetime.datetime.fromisoformat)
@deserialize.auto_snake()
class StorageZone:
    # The ID of the storage zone
    identifier: int

    # The ID of the user that owns the storage zone
    user_id: str | None

    # The name of the storage zone
    name: str | None

    # The API access key or FTP password
    password: str | None

    # The date when the zone was last modified
    date_modified: datetime.datetime

    # Determines if the zone was deleted or not
    deleted: bool

    # The total amount of storage used by this zone
    storage_used: int

    # The total number of files stored by this zone
    files_stored: int

    # The main region used by the storage zone
    region: str | None

    # The replication regions enabled for this storage zone
    replication_regions: list[str] | None

    # The list of pull zones connected to this storage zone
    pull_zones: list[PullZone] | None

    # The read-only API access key or FTP password
    read_only_password: str | None

    # Determines if the storage zone will rewrite 404 status codes to 200 status codes
    rewrite_404_to_200: bool

    # The custom 404 error path that will be returned in case of a missing file
    custom_404_file_path: str | None

    # Determines the storage hostname for this zone
    storage_hostname: str | None

    # Determines the storage zone tier that is storing the data
    zone_tier: int

    # Determines if the storage zone is currently enabling a new replication region
    replication_change_in_progress: bool

    # The custom price override for this zone
    price_override: float  # This should be decimal, but the API returns a float, so we've already lost the information

    # The Storage Zone specific pricing discount
    discount: int
