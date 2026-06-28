"""HTTP client for APIs"""

import logging
import urllib.parse
from typing import Any, Iterator, Type, TypeVar, cast

import deserialize
import requests

from bunnynet.exceptions import BunnyHTTPException

BASE_URL = "api.bunny.net"

T = TypeVar("T")


class HttpClient:
    """Base HTTP client for the API."""

    _token: str
    log: logging.Logger
    timeout: float

    def __init__(
        self,
        token: str,
        *,
        log: logging.Logger,
        timeout: float = 10,
    ) -> None:
        """Construct a new client object.

        :param token: The API token to use.
        :param log: The logger to use for debugging.
        :param timeout: The timeout (in seconds) to apply to each HTTP request.
        """
        self.log = log.getChild("http")
        self._token = token
        self.timeout = timeout

    def extract_data(self, response: requests.Response) -> Any:
        """Validate a response from the API and extract the data

        :param response: The response to validate

        :raises BunnyHTTPException: On any failure to validate

        :returns: Any data in the response
        """
        _ = self

        if not response.ok:
            raise BunnyHTTPException.generate_from_response(response)

        # Some write endpoints (e.g. a 201/204 on POST) return an empty body.
        # response.json() would raise on those, so treat an empty body as no data.
        if not response.content:
            return None

        return response.json()

    def get_raw(
        self,
        endpoint: str,
        *,
        attempts: int = 3,
        domain: str = BASE_URL,
        access_key: str | None = None,
        timeout: float | None = None,
    ) -> bytes:
        """Perform a GET to the endpoint specified.

        :param endpoint: The endpoint to perform the GET on
        :param attempts: Number of attempts remaining to try this call
        :param domain: Override the domain to something else
        :param access_key: The access key to use instead of the default
        :param timeout: Override the client's default request timeout (in seconds)

        :raises BunnyHTTPException: If something goes wrong in a call

        :returns: The response
        """

        url = "https://" + domain + "/" + endpoint

        raw_response = requests.get(
            url,
            headers={
                "AccessKey": access_key or self._token,
            },
            timeout=self.timeout if timeout is None else timeout,
        )

        if not raw_response.ok:
            if attempts > 1 and (raw_response.status_code >= 500):
                return self.get_raw(
                    endpoint,
                    attempts=attempts - 1,
                    domain=domain,
                    access_key=access_key,
                    timeout=timeout,
                )

            raise BunnyHTTPException.generate_from_response(raw_response, "Failed to get data")

        return raw_response.content

    def get(
        self,
        endpoint: str,
        response_type: Type[T],
        *,
        attempts: int = 3,
        domain: str = BASE_URL,
        access_key: str | None = None,
    ) -> T:
        """Perform a GET to the endpoint specified.

        :param endpoint: The endpoint to perform the GET on
        :param response_type: The type of item the response contains
        :param attempts: Number of attempts remaining to try this call
        :param domain: Override the domain to something else
        :param access_key: The access key to use instead of the default

        :raises BunnyHTTPException: If something goes wrong in a call

        :returns: The response deserialized and cast to the passed in `response_type`
        """

        url = "https://" + domain + "/" + endpoint

        raw_response = requests.get(
            url,
            headers={
                "AccessKey": access_key or self._token,
            },
            timeout=self.timeout,
        )

        try:
            response_data = self.extract_data(raw_response)
        except BunnyHTTPException as ex:
            if attempts > 1 and (ex.response.status_code >= 500):
                return self.get(
                    endpoint,
                    response_type,
                    attempts=attempts - 1,
                    domain=domain,
                    access_key=access_key,
                )

            raise

        return cast(T, deserialize.deserialize(response_type, response_data))

    def get_list(
        self,
        endpoint: str,
        response_type: Type[T],
        *,
        page: int = 0,
        attempts: int = 3,
        parameters: dict[str, Any] | None = None,
        domain: str = BASE_URL,
        access_key: str | None = None,
    ) -> Iterator[T]:
        """Perform a GET to the endpoint specified.

        :param endpoint: The endpoint to perform the GET on
        :param response_type: The type of item the response contains
        :param attempts: Number of attempts remaining to try this call
        :param page: The page of results to start from
        :param domain: Override the domain to something else
        :param parameters: A dictionary of parameters to add to the URL
        :param access_key: The access key to use instead of the default

        :raises BunnyHTTPException: If something goes wrong in a call

        :returns: The raw response
        """

        params = urllib.parse.urlencode(parameters or {})

        url = "https://" + domain + "/" + endpoint + f"?page={page}"

        if params:
            url += "&" + params

        raw_response = requests.get(url, headers={"AccessKey": access_key or self._token}, timeout=self.timeout)

        try:
            response_data = self.extract_data(raw_response)
        except BunnyHTTPException as ex:
            if attempts > 1 and (ex.response.status_code >= 500):
                yield from self.get_list(
                    endpoint,
                    response_type,
                    page=page,
                    attempts=attempts - 1,
                    parameters=parameters,
                    domain=domain,
                    access_key=access_key,
                )
                return

            raise

        deserialized_data = cast(T, deserialize.deserialize(list[response_type], response_data))  # type: ignore

        if isinstance(deserialized_data, list):
            yield from deserialized_data
        else:
            yield deserialized_data

        if isinstance(response_data, dict) and response_data.get("HasMoreItems"):
            yield from self.get_list(
                endpoint,
                response_type,
                page=page + 1,
                parameters=parameters,
                domain=domain,
                access_key=access_key,
            )

    def put(
        self,
        endpoint: str,
        response_type: Type[T],
        body: bytes,
        *,
        additional_headers: dict[str, Any] | None = None,
        attempts: int = 3,
        domain: str = BASE_URL,
        access_key: str | None = None,
    ) -> T:
        """Perform a PUT to the endpoint specified.

        :param endpoint: The endpoint to perform the PUT to
        :param response_type: The type of item the response contains
        :param body: The body of the POST message
        :param attempts: Number of attempts remaining to try this call
        :param additional_headers: Any additional headers to add to the call
        :param domain: Override the domain to something else
        :param access_key: The access key to use instead of the default

        :raises BunnyHTTPException: If something goes wrong in a call

        :returns: The response deserialized and cast to the passed in `response_type`
        """

        url = "https://" + domain + "/" + endpoint

        headers = {
            "AccessKey": access_key or self._token,
            "Content-Type": "application/octet-stream",
            "Accept": "application/json",
        }

        if additional_headers:
            headers |= additional_headers

        raw_response = requests.put(url, data=body, headers=headers, timeout=self.timeout)

        try:
            response_data = self.extract_data(raw_response)
        except BunnyHTTPException as ex:
            if attempts > 1 and (ex.response.status_code >= 500):
                return self.put(
                    endpoint,
                    response_type,
                    body,
                    additional_headers=additional_headers,
                    attempts=attempts - 1,
                    domain=domain,
                    access_key=access_key,
                )

            raise

        if response_type == object:
            return response_data

        return cast(T, deserialize.deserialize(response_type, response_data))

    def post(
        self,
        endpoint: str,
        response_type: Type[T],
        body: dict[str, Any] | None = None,
        *,
        additional_headers: dict[str, Any] | None = None,
        attempts: int = 3,
        domain: str = BASE_URL,
        access_key: str | None = None,
    ) -> T:
        """Perform a POST to the endpoint specified.

        Unlike :meth:`put`, the body is JSON-encoded since the bunny.net write
        endpoints expect a JSON document.

        :param endpoint: The endpoint to perform the POST to
        :param response_type: The type of item the response contains. Pass `object` if the body is empty or unused.
        :param body: The JSON-serialisable body to send
        :param additional_headers: Any additional headers to add to the call
        :param attempts: Number of attempts remaining to try this call
        :param domain: Override the domain to something else
        :param access_key: The access key to use instead of the default

        :raises BunnyHTTPException: If something goes wrong in a call

        :returns: The response deserialized and cast to the passed in `response_type`
        """

        url = "https://" + domain + "/" + endpoint

        headers = {
            "AccessKey": access_key or self._token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        if additional_headers:
            headers |= additional_headers

        raw_response = requests.post(url, json=body, headers=headers, timeout=self.timeout)

        try:
            response_data = self.extract_data(raw_response)
        except BunnyHTTPException as ex:
            if attempts > 1 and (ex.response.status_code >= 500):
                return self.post(
                    endpoint,
                    response_type,
                    body,
                    additional_headers=additional_headers,
                    attempts=attempts - 1,
                    domain=domain,
                    access_key=access_key,
                )

            raise

        if response_type == object:
            return response_data

        return cast(T, deserialize.deserialize(response_type, response_data))

    def delete(
        self,
        endpoint: str,
        response_type: Type[T],
        *,
        body: dict[str, Any] | None = None,
        additional_headers: dict[str, Any] | None = None,
        attempts: int = 3,
        domain: str = BASE_URL,
        access_key: str | None = None,
    ) -> T:
        """Perform a DELETE to the endpoint specified.

        :param endpoint: The endpoint to perform the DELETE to
        :param response_type: The type of item the response contains
        :param body: An optional JSON-serialisable body to send with the request
        :param attempts: Number of attempts remaining to try this call
        :param additional_headers: Any additional headers to add to the call
        :param domain: Override the domain to something else
        :param access_key: The access key to use instead of the default

        :raises BunnyHTTPException: If something goes wrong in a call

        :returns: The response deserialized and cast to the passed in `response_type`
        """

        url = "https://" + domain + "/" + endpoint

        headers = {
            "AccessKey": access_key or self._token,
            "Content-Type": "application/octet-stream",
            "Accept": "application/json",
        }

        if additional_headers:
            headers |= additional_headers

        raw_response = requests.delete(url, json=body, headers=headers, timeout=self.timeout)

        try:
            response_data = self.extract_data(raw_response)
        except BunnyHTTPException as ex:
            if attempts > 1 and (ex.response.status_code >= 500):
                return self.delete(
                    endpoint,
                    response_type,
                    body=body,
                    additional_headers=additional_headers,
                    attempts=attempts - 1,
                    domain=domain,
                    access_key=access_key,
                )

            raise

        if response_type == object:
            return response_data

        return cast(T, deserialize.deserialize(response_type, response_data))
