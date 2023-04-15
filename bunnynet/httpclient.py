"""HTTP client for APIs"""

import logging
import urllib.parse
from typing import Any, Iterator, Type, TypeVar, cast

import deserialize
import requests

from bunnynet.exceptions import BunnyHTTPException
from bunnynet.storage_endpoints import StorageEndpoint

BASE_URL = "api.bunny.net"

T = TypeVar("T")


class HttpClient:
    """Base HTTP client for the API."""

    _token: str
    log: logging.Logger

    def __init__(
        self,
        token: str,
        *,
        log: logging.Logger,
    ) -> None:
        """Construct a new client object."""
        self.log = log.getChild("http")
        self._token = token

    def extract_data(self, response: requests.Response) -> Any:
        """Validate a response from the API and extract the data

        :param response: The response to validate

        :raises BunnyHTTPException: On any failure to validate

        :returns: Any data in the response
        """
        _ = self

        if not response.ok:
            raise BunnyHTTPException(response)

        return response.json()

    def get_raw(
        self,
        endpoint: str,
        *,
        attempts: int = 3,
        domain: str = BASE_URL,
    ) -> str:
        """Perform a GET to the endpoint specified.

        :param endpoint: The endpoint to perform the GET on
        :param attempts: Number of attempts remaining to try this call
        :param domain: Override the domain to something else

        :raises BunnyHTTPException: If something goes wrong in a call

        :returns: The response
        """

        url = "https://" + domain + "/" + endpoint

        raw_response = requests.get(
            url,
            headers={
                "AccessKey": self._token,
            },
            timeout=10,
        )

        if not raw_response.ok:
            if attempts > 1 and (raw_response.status_code >= 500):
                return self.get_raw(endpoint, attempts=attempts - 1)

            raise BunnyHTTPException(raw_response, "Failed to get data")

        return raw_response.text

    def get(
        self,
        endpoint: str,
        response_type: Type[T],
        *,
        attempts: int = 3,
        domain: str = BASE_URL,
    ) -> T:
        """Perform a GET to the endpoint specified.

        :param endpoint: The endpoint to perform the GET on
        :param response_type: The type of item the response contains
        :param attempts: Number of attempts remaining to try this call
        :param domain: Override the domain to something else

        :raises BunnyHTTPException: If something goes wrong in a call

        :returns: The response deserialized and cast to the passed in `response_type`
        """

        url = "https://" + domain + "/" + endpoint

        raw_response = requests.get(
            url,
            headers={
                "AccessKey": self._token,
            },
            timeout=10,
        )

        try:
            response_data = self.extract_data(raw_response)
        except BunnyHTTPException as ex:
            if attempts > 1 and (ex.response.status_code >= 500):
                return self.get(endpoint, response_type, attempts=attempts - 1)

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

        raw_response = requests.get(url, headers={"AccessKey": access_key or self._token}, timeout=10)

        try:
            response_data = self.extract_data(raw_response)
        except BunnyHTTPException as ex:
            if attempts > 1 and (ex.response.status_code >= 500):
                yield from self.get_list(endpoint, response_type, page=page, attempts=attempts - 1)
                return

            raise

        deserialized_data = cast(T, deserialize.deserialize(list[response_type], response_data))  # type: ignore

        if isinstance(deserialized_data, list):
            yield from deserialized_data
        else:
            yield deserialized_data

        # TODO
        if isinstance(response_data, dict) and response_data.get("HasMoreItems"):
            yield from self.get_list(endpoint, response_type, page=page + 1)

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

        raw_response = requests.put(url, data=body, headers=headers, timeout=10)

        try:
            response_data = self.extract_data(raw_response)
        except BunnyHTTPException as ex:
            if attempts > 1 and (ex.response.status_code >= 500):
                return self.get(endpoint, response_type, attempts=attempts - 1)

            raise

        if response_type == object:
            return response_data

        return cast(T, deserialize.deserialize(response_type, response_data))

    def delete(
        self,
        endpoint: str,
        response_type: Type[T],
        *,
        additional_headers: dict[str, Any] | None = None,
        attempts: int = 3,
        domain: str = BASE_URL,
        access_key: str | None = None,
    ) -> T:
        """Perform a DELETE to the endpoint specified.

        :param endpoint: The endpoint to perform the PUT to
        :param response_type: The type of item the response contains
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

        raw_response = requests.delete(url, headers=headers, timeout=10)

        try:
            response_data = self.extract_data(raw_response)
        except BunnyHTTPException as ex:
            if attempts > 1 and (ex.response.status_code >= 500):
                return self.get(endpoint, response_type, attempts=attempts - 1)

            raise

        if response_type == object:
            return response_data

        return cast(T, deserialize.deserialize(response_type, response_data))
