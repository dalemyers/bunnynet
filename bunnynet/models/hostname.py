import deserialize


@deserialize.key("identifier", "id")
@deserialize.key("force_ssl", "ForceSSL")
@deserialize.auto_snake()
class Hostname:
    # The unique ID of the hostname
    identifier: int

    # The hostname value for the domain name
    value: str | None

    # Determines if the Force SSL feature is enabled
    force_ssl: bool

    # Determines if this is a system hostname controlled by bunny.net
    is_system_hostname: bool

    # Determines if the hostname has an SSL certificate configured
    has_certificate: bool

    # Contains the Base64Url encoded certificate for the hostname
    certificate: str | None

    # Contains the Base64Url encoded certificate key for the hostname
    certificate_key: str | None
