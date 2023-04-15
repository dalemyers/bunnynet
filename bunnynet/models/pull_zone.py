import datetime

import deserialize

from .bunny_ai_image_blueprint import BunnyAiImageBlueprint
from .edge_rule import EdgeRule
from .hostname import Hostname
from .pull_zone_type import PullZoneType


@deserialize.key("identifier", "id")
@deserialize.key("enable_geo_zone_us", "EnableGeoZoneUS")
@deserialize.key("enable_geo_zone_eu", "EnableGeoZoneEU")
@deserialize.key("enable_geo_zone_asia", "EnableGeoZoneASIA")
@deserialize.key("enable_geo_zone_sa", "EnableGeoZoneSA")
@deserialize.key("enable_geo_zone_af", "EnableGeoZoneAF")
@deserialize.key("pull_zone_type", "type")
@deserialize.key("zone_security_include_hash_remote_ip", "ZoneSecurityIncludeHashRemoteIP")
@deserialize.key("connection_limit_per_ip_count", "ConnectionLimitPerIPCount")
@deserialize.key("enable_webp_vary", "EnableWebPVary")
@deserialize.key("aws_signing_enabled", "AWSSigningEnabled")
@deserialize.key("aws_signing_key", "AWSSigningKey")
@deserialize.key("aws_signing_secret", "AWSSigningSecret")
@deserialize.key("aws_signing_region_name", "AWSSigningRegionName")
@deserialize.key("logging_ip_anonymization_enabled", "LoggingIPAnonymizationEnabled")
@deserialize.key("enable_tls1", "EnableTLS1")
@deserialize.key("enable_tls1_1", "EnableTLS1_1")
@deserialize.key("verify_origin_ssl", "VerifyOriginSSL")
@deserialize.key("optimizer_enable_webp", "OptimizerEnableWebP")
@deserialize.key("optimizer_minify_css", "OptimizerMinifyCSS")
@deserialize.key("optimizer_minify_javascript", "OptimizerMinifyJavaScript")
@deserialize.key("origin_retry_5xx_responses", "OriginRetry5XXResponses")
@deserialize.key("enable_auto_ssl", "EnableAutoSSL")
@deserialize.key("shield_ddos_protection_type", "ShieldDDosProtectionType")
@deserialize.key("shield_ddos_protection_enabled", "ShieldDDosProtectionEnabled")
@deserialize.key("eu_us_discount", "EUUSDiscount")
@deserialize.parser("date_modified", datetime.datetime.fromisoformat)
@deserialize.auto_snake()
class PullZone:
    # The unique ID of the pull zone.
    identifier: int

    # The name of the pull zone.
    name: str | None

    # The origin URL of the pull zone where the files are fetched from.
    origin_url: str | None

    # Determines if the Pull Zone is currently enabled, active and running
    enabled: bool

    # The list of hostnames linked to this Pull Zone
    hostnames: list[Hostname]

    # The ID of the storage zone that the pull zone is linked to
    storage_zone_id: int

    # The ID of the edge script that the pull zone is linked to
    edge_script_id: int

    # The list of referrer hostnames that are allowed to access the pull zone. Requests containing the header Referer: hostname that is not on the list will be rejected. If empty, all the referrers are allowed
    allowed_referrers: list[str] | None

    # The list of referrer hostnames that are allowed to access the pull zone. Requests containing the header Referer: hostname that is not on the list will be rejected. If empty, all the referrers are allowed
    blocked_referrers: list[str] | None

    # The list of IPs that are blocked from accessing the pull zone. Requests coming from the following IPs will be rejected. If empty, all the IPs will be allowed
    blocked_ips: list[str] | None

    # Determines if the delivery from the North American region is enabled for this pull zone
    enable_geo_zone_us: bool

    # Determines if the delivery from the European region is enabled for this pull zone
    enable_geo_zone_eu: bool

    # Determines if the delivery from the Asian / Oceanian region is enabled for this pull zone
    enable_geo_zone_asia: bool

    # Determines if the delivery from the South American region is enabled for this pull zone
    enable_geo_zone_sa: bool

    # Determines if the delivery from the Africa region is enabled for this pull zone
    enable_geo_zone_af: bool

    # True if the URL secure token authentication security is enabled
    zone_security_enabled: bool

    # The security key used for secure URL token authentication
    zone_security_key: str | None

    # True if the zone security hash should include the remote IP
    zone_security_include_hash_remote_ip: bool

    # True if the Pull Zone is ignoring query strings when serving cached objects
    ignore_query_strings: bool

    # The monthly limit of bandwidth in bytes that the pullzone is allowed to use
    monthly_bandwidth_limit: int

    # The amount of bandwidth in bytes that the pull zone used this month
    monthly_bandwidth_used: int

    # The total monthly charges for this so zone so far
    monthly_charges: float

    # Determines if the Pull Zone should forward the current hostname to the origin
    add_host_header: bool

    # Determines the host header that will be sent to the origin
    origin_host_header: str | None

    # The type of the pull zone.
    pull_zone_type: PullZoneType

    # The list of extensions that will return the CORS headers
    access_control_origin_header_extensions: list[str] | None

    # Determines if the CORS headers should be enabled
    enable_access_control_origin_header: bool

    # Determines if the cookies are disabled for the pull zone
    disable_cookies: bool

    # The list of budget redirected countries with the two-letter Alpha2 ISO codes
    budget_redirected_countries: list[str] | None

    # The list of blocked countries with the two-letter Alpha2 ISO codes
    blocked_countries: list[str] | None

    # If true the server will use the origin shield feature
    enable_origin_shield: bool

    # The override cache time for the pull zone
    cache_control_max_age_override: int

    # The override cache time for the pull zone for the end client
    cache_control_public_max_age_override: int

    # Excessive requests are delayed until their number exceeds the maximum burst size.
    burst_size: int

    # Max number of requests per IP per second
    request_limit: int

    # If true, access to root path will return a 403 error
    block_root_path_access: bool

    # If true, POST requests to the zone will be blocked
    block_post_requests: bool

    # The maximum rate at which the zone will transfer data in kb/s. 0 for unlimited
    limit_rate_per_second: float

    # The amount of data after the rate limit will be activated
    limit_rate_after: float

    # The number of connections limited per IP for this zone
    connection_limit_per_ip_count: int

    # The custom price override for this zone
    price_override: float

    # Determines if the Add Canonical Header is enabled for this Pull Zone
    add_canonical_header: bool

    # Determines if the logging is enabled for this Pull Zone
    enable_logging: bool

    # Determines if the cache slice (Optimize for video) feature is enabled for the Pull Zone
    enable_cache_slice: bool

    # Determines if smart caching is enabled for this zone
    enable_smart_cache: bool

    # The list of edge rules on this Pull Zone
    edge_rules: list[EdgeRule]

    # Determines if the WebP Vary feature is enabled.
    enable_webp_vary: bool

    # Determines if the AVIF Vary feature is enabled.
    enable_avif_vary: bool

    # Determines if the Country Code Vary feature is enabled.
    enable_country_code_vary: bool

    # Determines if the Mobile Vary feature is enabled.
    enable_mobile_vary: bool

    # Determines if the Cookie Vary feature is enabled.
    enable_cookie_vary: bool

    # Contains the list of vary parameters that will be used for vary cache by cookie string. If empty, cookie vary will not be used.
    cookie_vary_parameters: list[str] | None

    # Determines if the Hostname Vary feature is enabled.
    enable_hostname_vary: bool

    # The CNAME domain of the pull zone for setting up custom hostnames
    cname_domain: str | None

    # Determines if the AWS Signing is enabled
    aws_signing_enabled: bool

    # The AWS Signing region key
    aws_signing_key: str | None

    # The AWS Signing region secret
    aws_singing_secret: str | None

    # The AWS Signing region name
    aws_signing_region_name: str | None

    # ?
    logging_ip_anonymization_enabled: bool

    # Determines if the TLS 1 is enabled on the Pull Zone
    enable_tls1: bool

    # Determines if the TLS 11.1 is enabled on the Pull Zone
    enable_tls1_1: bool

    # Determines if the Pull Zone should verify the origin SSL certificate
    verify_origin_ssl: bool

    # Determines if custom error page code should be enabled.
    error_page_enable_custom_code: bool

    # Contains the custom error page code that will be returned
    error_page_custom_code: str | None

    # Determines if the statuspage widget should be displayed on the error pages
    error_page_enable_statuspage_widget: bool

    # The statuspage code that will be used to build the status widget
    error_page_statuspage_code: str | None

    # Determines if the error pages should be whitelabel or not
    error_page_whitelabel: bool

    # The zone code of the origin shield
    origin_shield_zone_code: str | None

    # Determines if the log forawrding is enabled
    log_forwarding_enabled: bool

    # The log forwarding hostname
    log_forwarding_hostname: str | None

    # The log forwarding port
    log_forwarding_port: int

    # The log forwarding token value
    log_forwarding_token: str | None

    # Determines the log forwarding protocol type
    log_forwarding_protocol: int

    # Determines if the permanent logging feature is enabled
    logging_save_to_storage: bool

    # The ID of the logging storage zone that is configured for this Pull Zone
    logging_storage_zone_id: int

    # Determines if the zone will follow origin redirects
    follow_redirects: bool

    # The ID of the video library that the zone is linked to
    video_library_id: int

    # The ID of the DNS record tied to this pull zone
    dns_record_id: int

    # The ID of the DNS zone tied to this pull zone
    dns_zone_id: int

    # The cached version of the DNS record value
    dns_record_value: str | None

    # Determines if the optimizer should be enabled for this zone
    optimizer_enabled: bool

    # Determines the maximum automatic image size for desktop clients
    optimizer_desktop_max_width: int

    # Determines the maximum automatic image size for mobile clients
    optimizer_mobile_max_width: int

    # Determines the image quality for desktop clients
    optimizer_image_quality: int

    # Determines the image quality for mobile clients
    optimizer_mobile_image_quality: int

    # Determines if the WebP optimization should be enabled
    optimizer_enable_webp: bool

    # Determines the image manipulation should be enabled
    optimizer_enable_manipulation_engine: bool

    # Determines if the CSS minifcation should be enabled
    optimizer_minify_css: bool

    # Determines if the JavaScript minifcation should be enabled
    optimizer_minify_javascript: bool

    # Determines if image watermarking should be enabled
    optimizer_watermark_enabled: bool

    # Sets the URL of the watermark image
    optimizer_watermark_url: str | None

    # Sets the position of the watermark image
    optimizer_watermark_position: int

    # Sets the offset of the watermark image
    optimizer_watermark_offset: float

    # Sets the minimum image size to which the watermark will be added
    optimizer_watermark_min_image_size: int

    # Determines if the automatic image optimization should be enabled
    optimizer_automatic_optimization_enabled: bool

    # The IP of the storage zone used for Perma-Cache
    perma_cache_storage_zone_id: int

    # The number of retries to the origin server
    origin_retries: int

    # The amount of seconds to wait when connecting to the origin. Otherwise the request will fail or retry.
    origin_connect_timeout: int

    # The amount of seconds to wait when waiting for the origin reply. Otherwise the request will fail or retry.
    origin_response_timeout: int

    # Determines if we should use stale cache while cache is updating
    use_stale_while_updating: bool

    # Determines if we should use stale cache while the origin is offline
    use_stale_while_offline: bool

    # Determines if we should retry the request in case of a 5XX response.
    origin_retry_5xx_responses: bool

    # Determines if we should retry the request in case of a connection timeout.
    origin_retry_connection_timeout: bool

    # Determines if we should retry the request in case of a response timeout.
    origin_retry_response_timeout: bool

    # Determines the amount of time that the CDN should wait before retrying an origin request.
    origin_retry_delay: int

    # Contains the list of vary parameters that will be used for vary cache by query str. If empty, all parameters will be used to construct the key
    querystr_vary_parameters: list[str] | None

    # Determines if the origin shield concurrency limit is enabled.
    origin_shield_enable_concurrency_limit: bool

    # Determines the number of maximum concurrent requests allowed to the origin.
    origin_shield_max_concurrent_requests: int

    # ?
    enable_safe_hop: bool

    # Determines if bunny.net should be caching error responses
    cache_error_responses: bool

    # Determines the max queue wait time
    origin_shield_queue_max_wait_time: int

    # Determines the max number of origin requests that will remain in the queu
    origin_shield_max_queued_requests: int

    # Contains the list of optimizer classes
    optimizer_classes: list[dict] | None

    # Determines if the optimizer class list should be enforced
    optimizer_force_classes: bool

    # Determines if cache update is performed in the background.
    use_background_update: bool

    # If set to true, any hostnames added to this Pull Zone will automatically enable SSL.
    enable_auto_ssl: bool

    # If set to true the query str ordering property is enabled.
    enable_query_string_ordering: bool

    # Gets the log anonymization type for this pull zone
    log_anonymization_type: int

    # 1
    log_format: int

    # 1
    log_forwarding_format: int

    # 1 2
    shield_ddos_protection_type: int

    # ?
    shield_ddos_protection_enabled: bool

    # The type of the origin for this Pull Zone
    origin_type: int

    # Determines if request coalescing is currently enabled.
    enable_request_coalescing: bool

    # Determines the lock time for coalesced requests.
    request_coalescing_timeout: int

    # Returns the link short preview value for the pull zone origin connection.
    origin_link_value: str | None

    # If true, the built-in let's encrypt is disabled and requests are passed to the origin.
    disable_lets_encrypt: bool

    # ?
    enable_bunny_image_ai: bool

    # ?
    bunny_ai_image_blueprints: list[BunnyAiImageBlueprint] | None

    # Determines if the preloading screen is currently enabled
    preloading_screen_enabled: bool

    # The custom preloading screen code
    preloading_screen_code: str | None

    # The preloading screen logo URL
    preloading_screen_logo_url: str | None

    # The currently configured preloading screem theme. (0 - Light, 1 - Dark)
    preloading_screen_theme: int

    # The delay in miliseconds after which the preloading screen will be desplayed
    preloading_screen_delay: int

    # The Pull Zone specific pricing discount for EU and US region.
    eu_us_discount: int

    # The Pull Zone specific pricing discount for South America region.
    south_america_discount: int

    # The Pull Zone specific pricing discount for Africa region.
    africa_discount: int

    # The Pull Zone specific pricing discount for Asia & Oceania region.
    asia_oceania_discount: int

    # The list of routing filters enabled for this zone
    routing_filters: list[str]
