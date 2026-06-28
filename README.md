# bunnynet

A Python client for the [bunny.net](https://bunny.net) APIs.

## Installation

```bash
pip install bunnynet
```

## Usage

Create a client with your bunny.net account API token:

```python
import bunnynet

client = bunnynet.BunnyClient("your-api-token")
```

Every request uses a default timeout of 10 seconds. Override it for all
requests by passing `timeout` (in seconds):

```python
client = bunnynet.BunnyClient("your-api-token", timeout=30)
```

### Storage zones

```python
# Iterate over every storage zone
for zone in client.storage_zones.get_all():
    print(zone.name)

# Look one up by id or name (returns None if it doesn't exist)
zone = client.storage_zones.get_by_name("my-zone")

# Upload, read and delete files
client.storage_zones.upload_text_file(
    storage_zone=zone,
    contents="Hello World",
    path="some/path",
    file_name="hello.txt",
)
text = client.storage_zones.get_text_file(storage_zone=zone, path="some/path", file_name="hello.txt")
client.storage_zones.delete_file(storage_zone=zone, path="some/path", file_name="hello.txt")
```

### Pull zones

```python
for zone in client.pull_zones.get_all():
    print(zone.name)
```

#### Provisioning a pull zone

The pull zone client can also create and configure zones:

```python
pull_zones = client.get_pull_zone_client()

zone = pull_zones.get_by_name("my-zone") or pull_zones.create(
    name="my-zone",
    origin_url="https://origin.example.com",
)

# Apply settings using bunny.net's PascalCase field names. -1 on
# CacheControlMaxAgeOverride tells bunny.net to respect the origin's
# Cache-Control headers.
pull_zones.update(zone.identifier, {
    "IgnoreQueryStrings": False,
    "EnableQueryStringOrdering": True,
    "CacheControlMaxAgeOverride": -1,
})

# Attach a custom hostname, issue a free Let's Encrypt certificate and force
# HTTPS. The hostname's CNAME must resolve to <zone>.b-cdn.net before the
# certificate can be issued.
pull_zones.add_hostname(zone.identifier, "cdn.example.com")
pull_zones.load_free_certificate("cdn.example.com")
pull_zones.set_force_ssl(zone.identifier, "cdn.example.com", force=True)
```

### Signed URLs

```python
import datetime

signed = client.sign_url(
    "https://example.b-cdn.net/foo/bar/file.png",
    key="your-token-authentication-key",
    expiration=datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=1),
)
```

### Purging the cache

```python
client.purge_url("https://example.b-cdn.net/foo/bar/file.png")
```

## Development

Install dependencies and run the tests with [Poetry](https://python-poetry.org):

```bash
poetry install
poetry run pytest
```

The integration tests in `tests/test_bunnynet.py` require a `BUNNY_TOKEN`
environment variable and are skipped when it is not set. The offline unit tests
in `tests/test_unit.py` always run.

## License

MIT
