import datetime

import deserialize


def dateparser(value: str) -> datetime.datetime:
    """Parse the date stamps to datetime objects.

    :param value: The raw string

    :returns: The parsed datetime
    """
    date_str, second_fraction = value.split(".")
    timestamp = datetime.datetime.fromisoformat(date_str)
    hundredths = int(second_fraction, base=10)
    timestamp += datetime.timedelta(milliseconds=hundredths * 10)
    return timestamp


@deserialize.parser("last_changed", dateparser)
@deserialize.parser("date_created", dateparser)
@deserialize.auto_snake()
class StorageObject:
    guid: str
    storage_zone_name: str
    path: str
    object_name: str
    length: int
    last_changed: datetime.datetime
    server_id: int
    array_number: int
    is_directory: bool
    user_id: str
    content_type: str
    date_created: datetime.datetime
    storage_zone_id: int
    checksum: str | None
    replicated_zones: str | None  # Comma separated
