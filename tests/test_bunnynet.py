"""Tests for the package."""

import datetime
import os
import sys
import uuid

import dotenv
import pytest
import requests

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import bunnynet  # pylint: disable=wrong-import-order

dotenv.load_dotenv()

TOKEN = os.environ["BUNNY_TOKEN"]

# pylint: disable=redefined-outer-name,missing-param-doc


@pytest.fixture(scope="session")
def client() -> bunnynet.BunnyClient:
    """Get a client for testing.

    :returns: A new client
    """
    return bunnynet.BunnyClient(TOKEN)


def test_get_storage_zone(client: bunnynet.BunnyClient):
    """Test getting storage zones."""
    zones = list(client.storage_zones.get_all())
    zone = zones[0]

    id_zone = client.storage_zones.get(zone.identifier)
    name_zone = client.storage_zones.get_by_name(zone.name or "")

    assert id_zone is not None
    assert name_zone is not None

    assert zone.identifier == id_zone.identifier
    assert zone.identifier == name_zone.identifier


def test_get_pull_zone(client: bunnynet.BunnyClient):
    """Test getting pull zones."""
    storage_zones = list(client.storage_zones.get_all())
    storage_zone = storage_zones[0]

    assert storage_zone.pull_zones is not None
    pull_zone = storage_zone.pull_zones[0]

    id_zone = client.pull_zones.get(pull_zone.identifier)
    name_zone = client.pull_zones.get_by_name(pull_zone.name or "")

    assert id_zone is not None
    assert name_zone is not None

    assert pull_zone.identifier == id_zone.identifier
    assert pull_zone.identifier == name_zone.identifier


def test_list_files(client: bunnynet.BunnyClient):
    """Test listing files"""

    storage_zones = list(client.storage_zones.get_all())
    storage_zone = storage_zones[0]

    all_contents = list(client.storage_zones.list_files(storage_zone=storage_zone, path="/"))
    assert len(all_contents) > 0


def test_upload_text_file(client: bunnynet.BunnyClient):
    """Test uploading a text file."""

    storage_zone = list(client.storage_zones.get_all())[0]

    client.storage_zones.upload_text_file(
        storage_zone_name=storage_zone.name or "",
        contents="Hello World",
        path="client_id/project_id/environment_id",
        file_name=str(uuid.uuid4()) + ".json",
    )


def test_delete_file(client: bunnynet.BunnyClient):
    """Test deleting a file."""

    storage_zone = list(client.storage_zones.get_all())[0]
    name = str(uuid.uuid4()) + ".json"

    client.storage_zones.upload_text_file(
        storage_zone_name=storage_zone.name or "",
        contents="Hello World",
        path="client_id/project_id/environment_id",
        file_name=name,
    )

    client.storage_zones.delete_file(
        storage_zone_name=storage_zone.name or "",
        path="client_id/project_id/environment_id",
        file_name=name,
    )


def test_get_file(client: bunnynet.BunnyClient):
    """Test getting a file."""

    storage_zone = list(client.storage_zones.get_all())[0]
    name = str(uuid.uuid4()) + ".json"

    client.storage_zones.upload_text_file(
        storage_zone_name=storage_zone.name or "",
        contents="Hello World",
        path="client_id/project_id/environment_id",
        file_name=name,
    )

    data = client.storage_zones.get_text_file(
        storage_zone_name=storage_zone.name or "",
        path="client_id/project_id/environment_id",
        file_name=name,
    )

    print(data)


def test_get_logs(client: bunnynet.BunnyClient):
    """Test getting the logs a file."""

    # TODO: Get from file storage

    client.logs.get(
        pull_zone_id=1330830,
        date=datetime.date(year=2023, month=4, day=15),
        status_codes=[100, 200, 300, 400, 500],
        start_index=0,
        end_index=10000,
    )


def test_purge_url(client: bunnynet.BunnyClient):
    """Test purging a file."""

    storage_zone = list(client.storage_zones.get_all())[0]
    name = str(uuid.uuid4()) + ".json"

    client.storage_zones.upload_text_file(
        storage_zone_name=storage_zone.name or "",
        contents="Hello World",
        path="client_id/project_id/environment_id",
        file_name=name,
    )

    assert storage_zone.pull_zones is not None
    pull_zone = storage_zone.pull_zones[0]

    url = (
        "https://"
        + (pull_zone.name or "")
        + "."
        + (pull_zone.cname_domain or "")
        + f"/client_id/project_id/environment_id/{name}"
    )

    contents = requests.get(url, timeout=10).text

    assert contents == "Hello World"

    client.storage_zones.upload_text_file(
        storage_zone_name=storage_zone.name or "",
        contents="Something else",
        path="client_id/project_id/environment_id",
        file_name=name,
    )

    contents = requests.get(url, timeout=10).text

    assert contents == "Hello World"

    client.purge_url(url)

    contents = requests.get(url, timeout=10).text

    assert contents == "Something else"
